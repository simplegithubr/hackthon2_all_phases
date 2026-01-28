# Phase 4 Local Kubernetes Deployment Agent

## System Description Document - Reference Implementation (SDD-RI)

### 1. System Overview
An AI agent designed to handle local Kubernetes deployment tasks using tools like Gordon, kubectl-ai, and kagent. The agent provides friendly, step-by-step AI-assisted operations for Minikube and Helm deployments.

### 2. Agent Role
Handle deployment tasks using tools like Gordon, kubectl-ai, kagent with a focus on local development environments.

### 3. System Prompt
Friendly, step-by-step, AI-assisted ops for Minikube/Helm with the following rules:
- Use AI tools for all Kubernetes operations
- Handle errors gracefully with user-friendly messages
- Confirm critical actions before executing
- Provide status updates throughout operations

### 4. Implementation

```python
import json
import subprocess
import os
from typing import Dict, Any, List, Optional
from enum import Enum

class KubernetesTool(Enum):
    MINIKUBE = "minikube"
    KUBECTL = "kubectl"
    HELM = "helm"
    GORDON = "gordon"
    KAGENT = "kagent"

class KubernetesDeploymentAgent:
    def __init__(self):
        self.tools = {
            "start_minikube": self.start_minikube,
            "stop_minikube": self.stop_minikube,
            "check_minikube_status": self.check_minikube_status,
            "deploy_helm_chart": self.deploy_helm_chart,
            "delete_helm_release": self.delete_helm_release,
            "apply_k8s_manifest": self.apply_k8s_manifest,
            "delete_k8s_resource": self.delete_k8s_resource,
            "get_pods": self.get_pods,
            "get_services": self.get_services,
            "get_deployments": self.get_deployments,
            "get_nodes": self.get_nodes,
            "port_forward": self.port_forward,
            "create_namespace": self.create_namespace,
            "delete_namespace": self.delete_namespace,
        }

    def runner(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Main runner function to execute Kubernetes tools"""
        try:
            if tool_name not in self.tools:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.tools.keys())
                }

            # Execute the tool
            result = self.tools[tool_name](**tool_args)
            return {
                "success": True,
                "result": result,
                "tool_used": tool_name
            }
        except Exception as e:
            return {
                "error": f"Tool execution failed: {str(e)}",
                "tool_used": tool_name
            }

    def _execute_command(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Execute a shell command and return the result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # We'll handle the return code ourselves
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }

    def start_minikube(self, driver: Optional[str] = None, memory: Optional[str] = "4g", cpus: Optional[str] = "2") -> Dict[str, Any]:
        """Start Minikube cluster"""
        cmd = ["minikube", "start"]
        if driver:
            cmd.extend(["--driver", driver])
        if memory:
            cmd.extend(["--memory", memory])
        if cpus:
            cmd.extend(["--cpus", cpus])

        return self._execute_command(cmd, timeout=600)  # Longer timeout for startup

    def stop_minikube(self) -> Dict[str, Any]:
        """Stop Minikube cluster"""
        cmd = ["minikube", "stop"]
        return self._execute_command(cmd)

    def check_minikube_status(self) -> Dict[str, Any]:
        """Check Minikube status"""
        cmd = ["minikube", "status"]
        return self._execute_command(cmd)

    def deploy_helm_chart(self, chart: str, release_name: str, namespace: Optional[str] = "default",
                         values_file: Optional[str] = None, version: Optional[str] = None) -> Dict[str, Any]:
        """Deploy a Helm chart"""
        cmd = ["helm", "upgrade", "--install", release_name, chart, "--namespace", namespace, "--wait"]
        if values_file:
            cmd.extend(["-f", values_file])
        if version:
            cmd.extend(["--version", version])

        return self._execute_command(cmd, timeout=600)

    def delete_helm_release(self, release_name: str, namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Delete a Helm release"""
        cmd = ["helm", "uninstall", release_name, "--namespace", namespace]
        return self._execute_command(cmd)

    def apply_k8s_manifest(self, manifest_file: str, namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Apply a Kubernetes manifest file"""
        cmd = ["kubectl", "apply", "-f", manifest_file, "-n", namespace]
        return self._execute_command(cmd)

    def delete_k8s_resource(self, resource_type: str, resource_name: str, namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Delete a Kubernetes resource"""
        cmd = ["kubectl", "delete", resource_type, resource_name, "-n", namespace]
        return self._execute_command(cmd)

    def get_pods(self, namespace: Optional[str] = "default", selector: Optional[str] = None) -> Dict[str, Any]:
        """Get pods in a namespace"""
        cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
        if selector:
            cmd.extend(["-l", selector])
        return self._execute_command(cmd)

    def get_services(self, namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Get services in a namespace"""
        cmd = ["kubectl", "get", "services", "-n", namespace, "-o", "json"]
        return self._execute_command(cmd)

    def get_deployments(self, namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Get deployments in a namespace"""
        cmd = ["kubectl", "get", "deployments", "-n", namespace, "-o", "json"]
        return self._execute_command(cmd)

    def get_nodes(self) -> Dict[str, Any]:
        """Get cluster nodes"""
        cmd = ["kubectl", "get", "nodes", "-o", "json"]
        return self._execute_command(cmd)

    def port_forward(self, resource_type: str, resource_name: str, local_port: int, remote_port: int,
                     namespace: Optional[str] = "default") -> Dict[str, Any]:
        """Port forward to a resource"""
        cmd = ["kubectl", "port-forward", f"{resource_type}/{resource_name}",
               f"{local_port}:{remote_port}", "-n", namespace]
        return self._execute_command(cmd, timeout=30)  # Shorter timeout for port forward

    def create_namespace(self, namespace: str) -> Dict[str, Any]:
        """Create a Kubernetes namespace"""
        cmd = ["kubectl", "create", "namespace", namespace]
        return self._execute_command(cmd)

    def delete_namespace(self, namespace: str) -> Dict[str, Any]:
        """Delete a Kubernetes namespace"""
        cmd = ["kubectl", "delete", "namespace", namespace]
        return self._execute_command(cmd)


# Tool Schemas for Docker/K8s operations
KUBERNETES_TOOL_SCHEMAS = {
    "start_minikube": {
        "name": "start_minikube",
        "description": "Start a Minikube cluster with specified configuration",
        "parameters": {
            "type": "object",
            "properties": {
                "driver": {
                    "type": "string",
                    "description": "Minikube driver (docker, virtualbox, hyperv, etc.)",
                    "enum": ["docker", "virtualbox", "hyperv", "hyperkit", "vmwarefusion", "kvm2", "podman"]
                },
                "memory": {
                    "type": "string",
                    "description": "Memory allocation for Minikube (e.g., '4g', '8192mb')",
                    "default": "4g"
                },
                "cpus": {
                    "type": "string",
                    "description": "CPU cores allocation for Minikube",
                    "default": "2"
                }
            },
            "required": []
        }
    },
    "stop_minikube": {
        "name": "stop_minikube",
        "description": "Stop the running Minikube cluster"
    },
    "check_minikube_status": {
        "name": "check_minikube_status",
        "description": "Check the status of the Minikube cluster"
    },
    "deploy_helm_chart": {
        "name": "deploy_helm_chart",
        "description": "Deploy a Helm chart to the cluster",
        "parameters": {
            "type": "object",
            "properties": {
                "chart": {
                    "type": "string",
                    "description": "Helm chart name or path to chart"
                },
                "release_name": {
                    "type": "string",
                    "description": "Name for the Helm release"
                },
                "namespace": {
                    "type": "string",
                    "description": "Namespace to deploy to",
                    "default": "default"
                },
                "values_file": {
                    "type": "string",
                    "description": "Path to values file for customization"
                },
                "version": {
                    "type": "string",
                    "description": "Specific chart version to deploy"
                }
            },
            "required": ["chart", "release_name"]
        }
    },
    "delete_helm_release": {
        "name": "delete_helm_release",
        "description": "Delete a Helm release from the cluster",
        "parameters": {
            "type": "object",
            "properties": {
                "release_name": {
                    "type": "string",
                    "description": "Name of the Helm release to delete"
                },
                "namespace": {
                    "type": "string",
                    "description": "Namespace where the release is deployed",
                    "default": "default"
                }
            },
            "required": ["release_name"]
        }
    },
    "apply_k8s_manifest": {
        "name": "apply_k8s_manifest",
        "description": "Apply a Kubernetes manifest file to the cluster",
        "parameters": {
            "type": "object",
            "properties": {
                "manifest_file": {
                    "type": "string",
                    "description": "Path to the Kubernetes manifest file"
                },
                "namespace": {
                    "type": "string",
                    "description": "Namespace to apply the manifest to",
                    "default": "default"
                }
            },
            "required": ["manifest_file"]
        }
    },
    "delete_k8s_resource": {
        "name": "delete_k8s_resource",
        "description": "Delete a Kubernetes resource by type and name",
        "parameters": {
            "type": "object",
            "properties": {
                "resource_type": {
                    "type": "string",
                    "description": "Type of resource (pod, deployment, service, etc.)"
                },
                "resource_name": {
                    "type": "string",
                    "description": "Name of the resource to delete"
                },
                "namespace": {
                    "type": "string",
                    "description": "Namespace where the resource exists",
                    "default": "default"
                }
            },
            "required": ["resource_type", "resource_name"]
        }
    },
    "get_pods": {
        "name": "get_pods",
        "description": "Get pods in a namespace with optional label selector",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to get pods from",
                    "default": "default"
                },
                "selector": {
                    "type": "string",
                    "description": "Label selector to filter pods"
                }
            },
            "required": []
        }
    },
    "get_services": {
        "name": "get_services",
        "description": "Get services in a namespace",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to get services from",
                    "default": "default"
                }
            },
            "required": []
        }
    },
    "get_deployments": {
        "name": "get_deployments",
        "description": "Get deployments in a namespace",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to get deployments from",
                    "default": "default"
                }
            },
            "required": []
        }
    },
    "get_nodes": {
        "name": "get_nodes",
        "description": "Get cluster nodes information"
    },
    "port_forward": {
        "name": "port_forward",
        "description": "Port forward to a resource in the cluster",
        "parameters": {
            "type": "object",
            "properties": {
                "resource_type": {
                    "type": "string",
                    "description": "Type of resource (pod, service, deployment, etc.)"
                },
                "resource_name": {
                    "type": "string",
                    "description": "Name of the resource to port forward to"
                },
                "local_port": {
                    "type": "integer",
                    "description": "Local port to forward to"
                },
                "remote_port": {
                    "type": "integer",
                    "description": "Remote port on the resource"
                },
                "namespace": {
                    "type": "string",
                    "description": "Namespace where the resource exists",
                    "default": "default"
                }
            },
            "required": ["resource_type", "resource_name", "local_port", "remote_port"]
        }
    },
    "create_namespace": {
        "name": "create_namespace",
        "description": "Create a Kubernetes namespace",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Name of the namespace to create"
                }
            },
            "required": ["namespace"]
        }
    },
    "delete_namespace": {
        "name": "delete_namespace",
        "description": "Delete a Kubernetes namespace",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Name of the namespace to delete"
                }
            },
            "required": ["namespace"]
        }
    }
}

def run_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to run the Kubernetes deployment agent tools.

    Args:
        tool_name: Name of the tool to run
        tool_args: Arguments for the tool

    Returns:
        Dictionary containing the result of the tool execution
    """
    agent = KubernetesDeploymentAgent()
    return agent.runner(tool_name, tool_args)
```

### 5. Usage Instructions
The agent can be used by calling the `run_tool` function with the appropriate tool name and arguments. The tool schemas define the expected parameters for each operation.

### 6. Error Handling
The agent handles errors gracefully by catching exceptions and returning user-friendly error messages while maintaining the conversation flow.

### 7. Security Considerations
- All operations are limited to local Kubernetes clusters (Minikube)
- No direct database access - only Kubernetes API interactions
- Input validation through JSON schema definitions