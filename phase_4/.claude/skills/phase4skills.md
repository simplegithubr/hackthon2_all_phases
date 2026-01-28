# Phase 4 MCP Skills for Kubernetes Deployment

These skills provide MCP-compatible functions for containerizing apps, generating Helm charts, deploying to Minikube, and checking cluster health.

```python
import subprocess
import tempfile
import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

# Mock database integration for MCP compatibility
class DatabaseManager:
    def __init__(self):
        # In a real MCP setup, this would connect to the actual database
        pass

    def save_deployment_record(self, deployment_data: Dict[str, Any]) -> str:
        """Save deployment record to database"""
        # Mock implementation - in real MCP this would persist to the shared database
        deployment_id = f"deploy_{hash(str(deployment_data)) % 10000}"
        print(f"Saved deployment record with ID: {deployment_id}")
        return deployment_id

    def get_deployment_record(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve deployment record from database"""
        # Mock implementation
        return {"id": deployment_id, "status": "completed", "timestamp": "2026-01-27T10:00:00Z"}

# Global database manager instance
db_manager = DatabaseManager()

def execute_command(cmd: list, cwd: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
    """Execute a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "stdout": "",
            "stderr": "",
            "return_code": -1
        }

def containerize_app(
    app_path: str,
    image_name: str,
    image_tag: str = "latest",
    dockerfile_path: Optional[str] = None,
    build_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Containerize an application by building a Docker image using Gordon or CLI.

    Args:
        app_path: Path to the application source code
        image_name: Name for the Docker image
        image_tag: Tag for the Docker image (default: latest)
        dockerfile_path: Optional path to custom Dockerfile
        build_context: Optional build context path

    Returns:
        Dict containing the result of the containerization process
    """
    try:
        # Determine build context
        context_path = build_context or app_path

        # Build the Docker image
        cmd = ["docker", "build", "-t", f"{image_name}:{image_tag}", "."]

        if dockerfile_path:
            cmd.insert(2, "-f")
            cmd.insert(3, dockerfile_path)

        # Check if Gordon is available and preferred
        gordon_result = execute_command(["which", "gordon"])
        if gordon_result["success"]:
            # Use Gordon if available
            cmd = ["gordon", "build", "-t", f"{image_name}:{image_tag}", "."]
            if dockerfile_path:
                cmd.insert(2, "-f")
                cmd.insert(3, dockerfile_path)

        result = execute_command(cmd, cwd=context_path)

        if result["success"]:
            # Save to database
            deployment_data = {
                "type": "containerization",
                "app_path": app_path,
                "image_name": image_name,
                "image_tag": image_tag,
                "status": "success",
                "context_path": context_path
            }
            deployment_id = db_manager.save_deployment_record(deployment_data)

            return {
                "success": True,
                "message": f"Docker image {image_name}:{image_tag} built successfully",
                "deployment_id": deployment_id,
                "image_name": image_name,
                "image_tag": image_tag
            }
        else:
            return {
                "success": False,
                "error": f"Failed to build Docker image: {result['stderr']}",
                "stdout": result["stdout"],
                "stderr": result["stderr"]
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during containerization: {str(e)}"
        }

def generate_helm_chart(
    app_name: str,
    destination_path: str,
    app_version: str = "0.1.0",
    description: str = "Auto-generated Helm chart",
    maintainer: Optional[str] = None,
    values_override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a Helm chart for an application using kubectl-ai or standard Helm tools.

    Args:
        app_name: Name of the application
        destination_path: Path where the Helm chart will be generated
        app_version: Version of the application (default: 0.1.0)
        description: Description of the chart
        maintainer: Maintainer information
        values_override: Values to override in the default chart

    Returns:
        Dict containing the result of the Helm chart generation
    """
    try:
        # Create destination directory if it doesn't exist
        Path(destination_path).mkdir(parents=True, exist_ok=True)

        # Check if kubectl-ai is available
        kubectl_ai_result = execute_command(["which", "kubectl-ai"])

        if kubectl_ai_result["success"]:
            # Use kubectl-ai to generate Helm chart
            cmd = [
                "kubectl-ai",
                "generate",
                "helm-chart",
                "--name", app_name,
                "--destination", destination_path,
                "--version", app_version,
                "--description", description
            ]

            if maintainer:
                cmd.extend(["--maintainer", maintainer])

            result = execute_command(cmd)
        else:
            # Fall back to standard Helm commands
            # First, create a new chart using Helm
            cmd = ["helm", "create", app_name]
            temp_dir = tempfile.mkdtemp()
            result = execute_command(cmd, cwd=temp_dir)

            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create Helm chart: {result['stderr']}"
                }

            # Move the chart to the destination
            source_chart_path = os.path.join(temp_dir, app_name)
            dest_chart_path = os.path.join(destination_path, app_name)

            # Copy the chart to destination
            copy_cmd = ["cp", "-r", source_chart_path, dest_chart_path]
            copy_result = execute_command(copy_cmd)

            if not copy_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to move Helm chart: {copy_result['stderr']}"
                }

            # Update Chart.yaml with provided information
            chart_yaml_path = os.path.join(dest_chart_path, "Chart.yaml")
            if os.path.exists(chart_yaml_path):
                with open(chart_yaml_path, 'r') as f:
                    chart_content = yaml.safe_load(f)

                chart_content['name'] = app_name
                chart_content['version'] = app_version
                chart_content['description'] = description

                if maintainer:
                    chart_content['maintainers'] = [{"name": maintainer}]

                with open(chart_yaml_path, 'w') as f:
                    yaml.dump(chart_content, f)

        if result["success"] or copy_result.get("success", True):
            # Apply values override if provided
            if values_override:
                values_yaml_path = os.path.join(destination_path, app_name, "values.yaml")
                if os.path.exists(values_yaml_path):
                    with open(values_yaml_path, 'r') as f:
                        values_content = yaml.safe_load(f)

                    # Deep merge values
                    def deep_merge(base_dict, override_dict):
                        for key, value in override_dict.items():
                            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                                deep_merge(base_dict[key], value)
                            else:
                                base_dict[key] = value

                    deep_merge(values_content, values_override)

                    with open(values_yaml_path, 'w') as f:
                        yaml.dump(values_content, f)

            # Save to database
            deployment_data = {
                "type": "helm_chart_generation",
                "app_name": app_name,
                "destination_path": destination_path,
                "version": app_version,
                "status": "success"
            }
            deployment_id = db_manager.save_deployment_record(deployment_data)

            return {
                "success": True,
                "message": f"Helm chart for {app_name} generated successfully at {destination_path}",
                "deployment_id": deployment_id,
                "chart_path": os.path.join(destination_path, app_name)
            }
        else:
            return {
                "success": False,
                "error": f"Failed to generate Helm chart: {result.get('stderr', copy_result.get('stderr'))}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during Helm chart generation: {str(e)}"
        }

def deploy_to_minikube(
    helm_chart_path: str,
    release_name: str,
    namespace: str = "default",
    values_file: Optional[str] = None,
    kube_context: Optional[str] = None,
    upgrade_if_exists: bool = True
) -> Dict[str, Any]:
    """
    Deploy a Helm chart to Minikube using Helm CLI and kagent for optimization.

    Args:
        helm_chart_path: Path to the Helm chart
        release_name: Name for the Helm release
        namespace: Target namespace (default: default)
        values_file: Optional values file to customize the deployment
        kube_context: Kubernetes context to use
        upgrade_if_exists: Whether to upgrade if release already exists

    Returns:
        Dict containing the result of the deployment process
    """
    try:
        # First ensure Minikube is running
        minikube_status = execute_command(["minikube", "status"])
        if not minikube_status["success"]:
            start_result = execute_command(["minikube", "start"])
            if not start_result["success"]:
                return {
                    "success": False,
                    "error": f"Could not start Minikube: {start_result['stderr']}"
                }

        # Prepare Helm command
        if upgrade_if_exists:
            cmd = ["helm", "upgrade", "--install", release_name, helm_chart_path]
        else:
            cmd = ["helm", "install", release_name, helm_chart_path]

        cmd.extend(["--namespace", namespace, "--create-namespace", "--wait"])

        if values_file:
            cmd.extend(["-f", values_file])

        if kube_context:
            cmd.extend(["--kube-context", kube_context])

        # Execute Helm deployment
        result = execute_command(cmd, timeout=600)  # Longer timeout for deployment

        if result["success"]:
            # Use kagent for optimization if available
            kagent_result = execute_command(["which", "kagent"])
            if kagent_result["success"]:
                optimization_cmd = [
                    "kagent", "optimize",
                    "--namespace", namespace,
                    "--release", release_name
                ]
                opt_result = execute_command(optimization_cmd)
                if opt_result["success"]:
                    print(f"kagent optimization completed for {release_name}")
                else:
                    print(f"kagent optimization failed: {opt_result['stderr']}")

            # Save to database
            deployment_data = {
                "type": "minikube_deployment",
                "helm_chart_path": helm_chart_path,
                "release_name": release_name,
                "namespace": namespace,
                "status": "success",
                "values_file": values_file
            }
            deployment_id = db_manager.save_deployment_record(deployment_data)

            return {
                "success": True,
                "message": f"Successfully deployed {release_name} to Minikube in namespace {namespace}",
                "deployment_id": deployment_id,
                "release_name": release_name,
                "namespace": namespace
            }
        else:
            return {
                "success": False,
                "error": f"Failed to deploy to Minikube: {result['stderr']}",
                "stdout": result["stdout"],
                "stderr": result["stderr"]
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during Minikube deployment: {str(e)}"
        }

def check_cluster(
    namespace: str = "default",
    analyze_resources: bool = True,
    check_health: bool = True,
    use_kagent: bool = True
) -> Dict[str, Any]:
    """
    Check the health of the Minikube cluster using kagent and standard tools.

    Args:
        namespace: Namespace to analyze (default: default)
        analyze_resources: Whether to analyze resources in the namespace
        check_health: Whether to check overall cluster health
        use_kagent: Whether to use kagent for advanced analysis

    Returns:
        Dict containing the cluster analysis results
    """
    try:
        cluster_info = {
            "namespace": namespace,
            "checks_performed": [],
            "resources": {},
            "health_status": {},
            "recommendations": []
        }

        # Check Minikube status
        minikube_status = execute_command(["minikube", "status"])
        if minikube_status["success"]:
            cluster_info["checks_performed"].append("minikube_status")
            cluster_info["health_status"]["minikube"] = "running"
        else:
            cluster_info["health_status"]["minikube"] = "stopped"
            cluster_info["recommendations"].append("Minikube is not running. Start it with 'minikube start'")

        # Check kubectl connectivity
        kubectl_version = execute_command(["kubectl", "version", "--client"])
        if kubectl_version["success"]:
            cluster_info["checks_performed"].append("kubectl_client")
        else:
            cluster_info["recommendations"].append("kubectl is not properly configured")

        # Get cluster info if accessible
        if check_health:
            # Get nodes
            nodes_result = execute_command(["kubectl", "get", "nodes", "-o", "json"])
            if nodes_result["success"]:
                cluster_info["checks_performed"].append("cluster_nodes")
                try:
                    nodes_data = json.loads(nodes_result["stdout"])
                    cluster_info["resources"]["nodes"] = len(nodes_data.get("items", []))
                    # Check node status
                    for node in nodes_data.get("items", []):
                        node_name = node["metadata"]["name"]
                        node_status = "Unknown"
                        for condition in node.get("status", {}).get("conditions", []):
                            if condition["type"] == "Ready":
                                node_status = condition["status"]
                                break
                        if node_status != "True":
                            cluster_info["recommendations"].append(f"Node {node_name} is not ready")
                except json.JSONDecodeError:
                    cluster_info["recommendations"].append("Could not parse nodes data")

        # Analyze resources in namespace
        if analyze_resources:
            # Get pods
            pods_result = execute_command(["kubectl", "get", "pods", "-n", namespace, "-o", "json"])
            if pods_result["success"]:
                cluster_info["checks_performed"].append("namespace_pods")
                try:
                    pods_data = json.loads(pods_result["stdout"])
                    cluster_info["resources"]["pods"] = len(pods_data.get("items", []))

                    # Check pod statuses
                    for pod in pods_data.get("items", []):
                        pod_name = pod["metadata"]["name"]
                        phase = pod["status"].get("phase", "Unknown")
                        if phase not in ["Running", "Succeeded"]:
                            cluster_info["recommendations"].append(f"Pod {pod_name} is in {phase} state")
                except json.JSONDecodeError:
                    cluster_info["recommendations"].append("Could not parse pods data")

        # Use kagent for advanced analysis if available and requested
        if use_kagent:
            kagent_result = execute_command(["which", "kagent"])
            if kagent_result["success"]:
                kagent_analysis = execute_command([
                    "kagent", "analyze",
                    "--namespace", namespace,
                    "--format", "json"
                ])

                if kagent_analysis["success"]:
                    cluster_info["checks_performed"].append("kagent_analysis")
                    try:
                        kagent_data = json.loads(kagent_analysis["stdout"])
                        cluster_info["kagent_analysis"] = kagent_data

                        # Extract recommendations from kagent if available
                        if "recommendations" in kagent_data:
                            cluster_info["recommendations"].extend(kagent_data["recommendations"])
                    except json.JSONDecodeError:
                        cluster_info["recommendations"].append("Could not parse kagent analysis data")
                else:
                    cluster_info["recommendations"].append(f"kagent analysis failed: {kagent_analysis['stderr']}")

        # Save to database
        deployment_data = {
            "type": "cluster_check",
            "namespace": namespace,
            "status": "completed",
            "analysis": cluster_info
        }
        deployment_id = db_manager.save_deployment_record(deployment_data)

        cluster_info["deployment_id"] = deployment_id
        cluster_info["success"] = True

        return cluster_info

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during cluster check: {str(e)}"
        }

# Tool schemas for MCP integration
SKILL_SCHEMAS = {
    "containerize_app": {
        "name": "containerize_app",
        "description": "Containerize an application by building a Docker image using Gordon or CLI",
        "parameters": {
            "type": "object",
            "properties": {
                "app_path": {
                    "type": "string",
                    "description": "Path to the application source code"
                },
                "image_name": {
                    "type": "string",
                    "description": "Name for the Docker image"
                },
                "image_tag": {
                    "type": "string",
                    "description": "Tag for the Docker image",
                    "default": "latest"
                },
                "dockerfile_path": {
                    "type": "string",
                    "description": "Optional path to custom Dockerfile"
                },
                "build_context": {
                    "type": "string",
                    "description": "Optional build context path"
                }
            },
            "required": ["app_path", "image_name"]
        }
    },
    "generate_helm_chart": {
        "name": "generate_helm_chart",
        "description": "Generate a Helm chart for an application using kubectl-ai or standard Helm tools",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application"
                },
                "destination_path": {
                    "type": "string",
                    "description": "Path where the Helm chart will be generated"
                },
                "app_version": {
                    "type": "string",
                    "description": "Version of the application",
                    "default": "0.1.0"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the chart",
                    "default": "Auto-generated Helm chart"
                },
                "maintainer": {
                    "type": "string",
                    "description": "Maintainer information"
                },
                "values_override": {
                    "type": "object",
                    "description": "Values to override in the default chart"
                }
            },
            "required": ["app_name", "destination_path"]
        }
    },
    "deploy_to_minikube": {
        "name": "deploy_to_minikube",
        "description": "Deploy a Helm chart to Minikube using Helm CLI and kagent for optimization",
        "parameters": {
            "type": "object",
            "properties": {
                "helm_chart_path": {
                    "type": "string",
                    "description": "Path to the Helm chart"
                },
                "release_name": {
                    "type": "string",
                    "description": "Name for the Helm release"
                },
                "namespace": {
                    "type": "string",
                    "description": "Target namespace",
                    "default": "default"
                },
                "values_file": {
                    "type": "string",
                    "description": "Optional values file to customize the deployment"
                },
                "kube_context": {
                    "type": "string",
                    "description": "Kubernetes context to use"
                },
                "upgrade_if_exists": {
                    "type": "boolean",
                    "description": "Whether to upgrade if release already exists",
                    "default": True
                }
            },
            "required": ["helm_chart_path", "release_name"]
        }
    },
    "check_cluster": {
        "name": "check_cluster",
        "description": "Check the health of the Minikube cluster using kagent and standard tools",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to analyze",
                    "default": "default"
                },
                "analyze_resources": {
                    "type": "boolean",
                    "description": "Whether to analyze resources in the namespace",
                    "default": True
                },
                "check_health": {
                    "type": "boolean",
                    "description": "Whether to check overall cluster health",
                    "default": True
                },
                "use_kagent": {
                    "type": "boolean",
                    "description": "Whether to use kagent for advanced analysis",
                    "default": True
                }
            },
            "required": []
        }
    }
}

# MCP-compatible function dispatcher
def run_skill(skill_name: str, skill_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP-compatible function to run the appropriate skill based on the skill name.

    Args:
        skill_name: Name of the skill to run
        skill_args: Arguments for the skill

    Returns:
        Dict containing the result of the skill execution
    """
    skill_functions = {
        "containerize_app": containerize_app,
        "generate_helm_chart": generate_helm_chart,
        "deploy_to_minikube": deploy_to_minikube,
        "check_cluster": check_cluster
    }

    if skill_name not in skill_functions:
        return {
            "success": False,
            "error": f"Unknown skill: {skill_name}",
            "available_skills": list(skill_functions.keys())
        }

    try:
        # Call the appropriate skill function
        return skill_functions[skill_name](**skill_args)
    except TypeError as e:
        return {
            "success": False,
            "error": f"Invalid arguments for skill {skill_name}: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing skill {skill_name}: {str(e)}"
        }
```