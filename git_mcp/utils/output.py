"""Output formatting utilities for git-mcp."""

import json
import yaml
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import box
from datetime import datetime

from ..platforms.base import Resource


class OutputFormatter:
    """Handles different output formats for git-mcp."""

    def __init__(self, format_type: str = "table"):
        self.format_type = format_type.lower()
        self.console = Console()

    def format_resources(
        self, resources: List[Resource], fields: Optional[List[str]] = None
    ) -> None:
        """Format a list of resources for output."""
        if not resources:
            self.console.print("No resources found.", style="yellow")
            return

        if self.format_type == "json":
            self._format_json(resources)
        elif self.format_type == "yaml":
            self._format_yaml(resources)
        else:  # table format
            self._format_table(resources, fields)

    def format_single_resource(self, resource: Resource) -> None:
        """Format a single resource for detailed output."""
        if self.format_type == "json":
            self._format_json([resource])
        elif self.format_type == "yaml":
            self._format_yaml([resource])
        else:
            self._format_resource_details(resource)

    def _format_table(
        self, resources: List[Resource], fields: Optional[List[str]] = None
    ) -> None:
        """Format resources as a table."""
        if not resources:
            return

        # Determine fields to show based on resource type
        resource_type = resources[0].resource_type
        default_fields = self._get_default_fields(resource_type)
        show_fields = fields or default_fields

        table = Table(box=box.ROUNDED)

        # Add columns
        for field in show_fields:
            table.add_column(field.replace("_", " ").title(), overflow="fold")

        # Add rows
        for resource in resources:
            row_data = []
            for field in show_fields:
                value = self._get_field_value(resource, field)
                row_data.append(str(value) if value is not None else "")
            table.add_row(*row_data)

        self.console.print(table)

    def _format_resource_details(self, resource: Resource) -> None:
        """Format a single resource with detailed information."""
        tree = Tree(
            f"[bold blue]{resource.resource_type.value.title()}: {resource.title}[/bold blue]"
        )

        # Basic information
        basic_info = tree.add("[bold]Basic Information[/bold]")
        basic_info.add(f"ID: {resource.id}")
        basic_info.add(f"Platform: {resource.platform}")
        basic_info.add(f"URL: {resource.url}")

        if resource.state:
            basic_info.add(f"State: {resource.state.value}")

        if resource.created_at:
            basic_info.add(f"Created: {self._format_datetime(resource.created_at)}")

        if resource.updated_at:
            basic_info.add(f"Updated: {self._format_datetime(resource.updated_at)}")

        # People
        if resource.author or resource.assignee:
            people_info = tree.add("[bold]People[/bold]")
            if resource.author:
                people_info.add(f"Author: {resource.author}")
            if resource.assignee:
                people_info.add(f"Assignee: {resource.assignee}")

        # Labels
        if resource.labels:
            labels_info = tree.add("[bold]Labels[/bold]")
            labels_info.add(", ".join(resource.labels))

        # Description
        if resource.description:
            desc_info = tree.add("[bold]Description[/bold]")
            desc_info.add(
                resource.description[:200] + "..."
                if len(resource.description) > 200
                else resource.description
            )

        # Resource-specific fields
        self._add_resource_specific_fields(tree, resource)

        self.console.print(tree)

    def _format_json(self, resources: List[Resource]) -> None:
        """Format resources as JSON."""
        data = [self._resource_to_dict(resource) for resource in resources]
        json_str = json.dumps(data, indent=2, default=str, ensure_ascii=False)
        self.console.print(json_str)

    def _format_yaml(self, resources: List[Resource]) -> None:
        """Format resources as YAML."""
        data = [self._resource_to_dict(resource) for resource in resources]
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        self.console.print(yaml_str)

    def _resource_to_dict(self, resource: Resource) -> Dict[str, Any]:
        """Convert resource to dictionary for serialization."""
        data = {
            "id": resource.id,
            "title": resource.title,
            "platform": resource.platform,
            "type": resource.resource_type.value,
            "url": resource.url,
            "state": resource.state.value if resource.state else None,
            "created_at": resource.created_at.isoformat()
            if resource.created_at
            else None,
            "updated_at": resource.updated_at.isoformat()
            if resource.updated_at
            else None,
            "author": resource.author,
            "assignee": resource.assignee,
            "labels": resource.labels,
            "description": resource.description,
        }

        # Add resource-specific fields
        if hasattr(resource, "project_id"):
            data["project_id"] = resource.project_id
        if hasattr(resource, "namespace"):
            data["namespace"] = resource.namespace
        if hasattr(resource, "source_branch"):
            data["source_branch"] = resource.source_branch
        if hasattr(resource, "target_branch"):
            data["target_branch"] = resource.target_branch

        return data

    def _get_default_fields(self, resource_type) -> List[str]:
        """Get default fields to display for each resource type."""
        from ..platforms.base import ResourceType

        field_mapping = {
            ResourceType.PROJECT: [
                "id",
                "title",
                "namespace",
                "visibility",
                "updated_at",
            ],
            ResourceType.ISSUE: [
                "id",
                "title",
                "state",
                "author",
                "assignee",
                "updated_at",
            ],
            ResourceType.MERGE_REQUEST: [
                "id",
                "title",
                "state",
                "source_branch",
                "target_branch",
                "author",
            ],
        }

        return field_mapping.get(resource_type, ["id", "title", "state", "updated_at"])

    def _get_field_value(self, resource: Resource, field: str) -> Any:
        """Get field value from resource."""
        if hasattr(resource, field):
            value = getattr(resource, field)
            if isinstance(value, datetime):
                return self._format_datetime(value)
            elif hasattr(value, "value"):  # Enum
                return value.value
            return value
        return None

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for display."""
        return dt.strftime("%Y-%m-%d %H:%M")

    def _add_resource_specific_fields(self, tree: Tree, resource: Resource) -> None:
        """Add resource-type-specific fields to the tree."""
        from ..platforms.base import ResourceType

        if resource.resource_type == ResourceType.PROJECT:
            if hasattr(resource, "namespace") and resource.namespace:
                project_info = tree.add("[bold]Project Info[/bold]")
                project_info.add(f"Namespace: {resource.namespace}")
                if hasattr(resource, "visibility"):
                    project_info.add(f"Visibility: {resource.visibility}")
                if hasattr(resource, "default_branch"):
                    project_info.add(f"Default Branch: {resource.default_branch}")

        elif resource.resource_type == ResourceType.ISSUE:
            # Show due date and milestone for issues
            if hasattr(resource, "due_date") and resource.due_date:
                issue_info = tree.add("[bold]Issue Info[/bold]")
                issue_info.add(f"Due Date: {self._format_datetime(resource.due_date)}")
            if hasattr(resource, "milestone") and resource.milestone:
                if not hasattr(self, "_issue_info_added"):  # Avoid duplicate sections
                    issue_info = tree.add("[bold]Issue Info[/bold]")
                    self._issue_info_added = True
                issue_info.add(f"Milestone: {resource.milestone}")

            # Show comments if available
            if resource.metadata and "comments" in resource.metadata:
                comments = resource.metadata["comments"]
                if comments:
                    comments_info = tree.add(f"[bold]Comments ({len(comments)})[/bold]")
                    for comment in comments:
                        comment_time = (
                            self._format_datetime(comment["created_at"])
                            if comment["created_at"]
                            else "Unknown time"
                        )
                        comment_node = comments_info.add(
                            f"💬 {comment['author']} - {comment_time}"
                        )
                        # Truncate long comments
                        body = (
                            comment["body"][:150] + "..."
                            if len(comment["body"]) > 150
                            else comment["body"]
                        )
                        comment_node.add(body)

        elif resource.resource_type == ResourceType.MERGE_REQUEST:
            if hasattr(resource, "source_branch") and resource.source_branch:
                mr_info = tree.add("[bold]Merge Request Info[/bold]")
                mr_info.add(f"Source Branch: {resource.source_branch}")
                if hasattr(resource, "target_branch") and resource.target_branch:
                    mr_info.add(f"Target Branch: {resource.target_branch}")
                if hasattr(resource, "draft") and resource.draft:
                    mr_info.add("Status: Draft")

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"✓ {message}", style="green")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"✗ {message}", style="red")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"⚠ {message}", style="yellow")

    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"ℹ {message}", style="blue")
