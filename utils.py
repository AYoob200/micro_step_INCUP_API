"""
Utilities for JSON formatting, validation, and response handling.
"""

import json
from typing import Dict, Any, Optional
from enum import Enum


class OutputFormat(Enum):
    """Available output formats for decomposition results."""

    JSON = "json"
    DICT = "dict"
    PRETTY_JSON = "pretty_json"


class JSONFormatter:
    """Handles formatting of decomposition results in JSON format."""

    @staticmethod
    def to_json(result: "DecompositionWorkblock", pretty: bool = False) -> str:
        """
        Format result as JSON.

        Args:
            result: DecompositionWorkblock object
            pretty: Whether to pretty-print with indentation

        Returns:
            JSON string
        """
        data = result.to_dict()
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent)


class ResponseValidator:
    """Validates API responses and task decompositions."""

    @staticmethod
    def validate_json_structure(data: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate that response has correct JSON structure.

        Args:
            data: Parsed JSON data

        Returns:
            (is_valid, error_message)
        """
        if "task" not in data:
            return False, "Missing 'task' key in response"

        task_data = data["task"]
        if not isinstance(task_data, dict):
            return False, "'task' must be a dictionary"

        if "steps" not in task_data:
            return False, "Missing 'steps' key in task"

        if not isinstance(task_data["steps"], list):
            return False, "'steps' must be an array"

        if len(task_data["steps"]) == 0:
            return False, "'steps' array cannot be empty"

        required_task_fields = [
            "task_id",
            "task_title",
            "task_priority",
            "intent_priority",
            "estimated_total_session_time",
            "total_steps",
        ]

        for field in required_task_fields:
            if field not in task_data:
                return False, f"Task: Missing required field '{field}'"

        required_step_fields = [
            "step_id",
            "step_title",
            "decomposition",
            "estimated_time",
            "primary_verb",
            "deliverable",
            "novelty_hook",
            "incup_tags",
        ]

        for i, step in enumerate(task_data["steps"]):
            for field in required_step_fields:
                if field not in step:
                    return False, f"Step {i}: Missing required field '{field}'"

            if not isinstance(step["estimated_time"], int):
                return (
                    False,
                    f"Step {i}: estimated_time must be an integer, got {type(step['estimated_time'])}",
                )

        return True, None

    @staticmethod
    def check_constitution_compliance(
        result: "DecompositionWorkblock",
    ) -> Dict[str, Any]:
        """
        Deep validation of AI Constitution compliance.
        Returns detailed compliance report.

        Args:
            result: DecompositionWorkblock object

        Returns:
            Compliance report dictionary
        """
        report = {
            "compliant": True,
            "violations": [],
            "warnings": [],
        }

        # Check task-level constraints
        valid_priorities = {"High", "Mid", "Low"}
        if result.task_priority not in valid_priorities:
            report["violations"].append(
                f"Invalid task_priority: {result.task_priority}"
            )
            report["compliant"] = False

        valid_intent = {"High", "Medium", "Low"}
        if result.intent_priority not in valid_intent:
            report["violations"].append(
                f"Invalid intent_priority: {result.intent_priority}"
            )
            report["compliant"] = False

        for step in result.steps:
            # Check mono-action rule (single verb)
            verb_parts = step.primary_verb.split()
            if len(verb_parts) > 1:
                report["violations"].append(
                    f"Step {step.step_id}: primary_verb must be single verb, got '{step.primary_verb}'"
                )
                report["compliant"] = False

            # Check time constraints
            if not (5 <= step.estimated_time <= 25):
                report["violations"].append(
                    f"Step {step.step_id}: estimated_time must be 5-25 minutes, got {step.estimated_time}"
                )
                report["compliant"] = False

            # Check INCUP tags
            if not step.incup_tags or len(step.incup_tags) != 1:
                report["violations"].append(
                    f"Step {step.step_id}: Must have exactly one INCUP tag, got {len(step.incup_tags)}"
                )
                report["compliant"] = False

        return report
