"""Contract tests for Task API endpoints"""
import pytest
from httpx import AsyncClient
from fastapi import status

from src.main import app
from src.models.task import Task


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_tasks_without_auth(test_session):
    """Test GET /api/tasks without authentication returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/tasks")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_task_without_auth(test_session):
    """Test POST /api/tasks without authentication returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/tasks",
            json={"title": "Test Task", "description": "Test Description"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_task_with_empty_title(test_session, mock_jwt_token):
    """Test POST /api/tasks with empty title returns 400"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/tasks",
            json={"title": "", "description": None},
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Task title is required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_task_with_long_title(test_session, mock_jwt_token):
    """Test POST /api/tasks with title > 200 characters returns 422"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/tasks",
            json={"title": "x" * 201, "description": None},
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
        )
        # FastAPI returns 422 for validation errors
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_full_task_workflow(test_session, mock_user_id):
    """Test complete task CRUD workflow with multi-user isolation

    1. Create task for User A
    2. Get User A's tasks
    3. Update task
    4. Toggle completion
    5. Delete task
    6. User B cannot see User A's task
    """
    from jose import jwt

    # User A and User B tokens
    user_a_token = jwt.encode({"sub": "user-a"}, "test-secret", algorithm="HS256")
    user_b_token = jwt.encode({"sub": "user-b"}, "test-secret", algorithm="HS256")

    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. User A creates task
        create_response = await client.post(
            "/api/tasks",
            json={"title": "User A's Task", "description": "Owned by User A"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        task = create_response.json()
        task_id = task["id"]
        assert task["user_id"] == "user-a"
        assert task["is_complete"] is False

        # 2. Get User A's tasks
        get_response = await client.get(
            "/api/tasks", headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert get_response.status_code == status.HTTP_200_OK
        user_a_tasks = get_response.json()
        assert len(user_a_tasks) == 1
        assert user_a_tasks[0]["id"] == task_id

        # 3. User A updates task
        update_response = await client.put(
            f"/api/tasks/{task_id}",
            json={"title": "User A's Updated Task", "description": "Updated"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_task = update_response.json()
        assert updated_task["title"] == "User A's Updated Task"

        # 4. User A toggles completion
        toggle_response = await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        assert toggle_response.status_code == status.HTTP_200_OK
        completed_task = toggle_response.json()
        assert completed_task["is_complete"] is True

        # 5. User A deletes task
        delete_response = await client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 6. Verify task is gone
        get_after_delete = await client.get(
            "/api/tasks", headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND

        # 7. User B cannot access User A's task (even before deletion)
        # Try to access the deleted task ID
        user_b_get = await client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        assert user_b_get.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]


@pytest.mark.asyncio
async def test_multi_user_isolation(test_session):
    """Test multi-user data isolation: User B cannot see User A's tasks"""
    from jose import jwt

    user_a_token = jwt.encode({"sub": "user-a"}, "test-secret", algorithm="HS256")
    user_b_token = jwt.encode({"sub": "user-b"}, "test-secret", algorithm="HS256")

    async with AsyncClient(app=app, base_url="http://test") as client:
        # User A creates task
        await client.post(
            "/api/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # User A creates another task
        await client.post(
            "/api/tasks",
            json={"title": "Another Task from A"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # User B creates task
        await client.post(
            "/api/tasks",
            json={"title": "User B's Task"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        # User A sees only their tasks (2 tasks)
        user_a_response = await client.get(
            "/api/tasks", headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert user_a_response.status_code == status.HTTP_200_OK
        user_a_tasks = user_a_response.json()
        assert len(user_a_tasks) == 2
        assert all(task["user_id"] == "user-a" for task in user_a_tasks)

        # User B sees only their task (1 task)
        user_b_response = await client.get(
            "/api/tasks", headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert user_b_response.status_code == status.HTTP_200_OK
        user_b_tasks = user_b_response.json()
        assert len(user_b_tasks) == 1
        assert user_b_tasks[0]["user_id"] == "user-b"
