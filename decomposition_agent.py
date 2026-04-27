"""
Decomposition Agent for Gemini API
Transforms user intentions into concrete, actionable task breakdowns.
Uses Gemini v4-flash models for intelligent task decomposition.
"""

import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai

from config import ConfigGemini, ModelProviderGemini
from system_prompt import get_system_prompt


class DecompositionStep:
    """Data class representing a single step within a task."""

    def __init__(
        self,
        step_id: int,
        step_title: str,
        description: str,
        estimated_time: int,
        primary_verb: str,
        deliverable: str,
        novelty_hook: str,
        passion_anchor: Optional[str],
        urgency_cue: Optional[str],
        incup_tags: str,
    ):
        self.step_id = step_id
        self.step_title = step_title
        self.description = description
        self.estimated_time = estimated_time
        self.primary_verb = primary_verb
        self.deliverable = deliverable
        self.novelty_hook = novelty_hook
        self.passion_anchor = passion_anchor
        self.urgency_cue = urgency_cue
        self.incup_tags = incup_tags

    def to_dict(self) -> Dict:
        """Convert step to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "step_title": self.step_title,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "primary_verb": self.primary_verb,
            "deliverable": self.deliverable,
            "novelty_hook": self.novelty_hook,
            "passion_anchor": self.passion_anchor,
            "urgency_cue": self.urgency_cue,
            "incup_tags": self.incup_tags,
        }

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate step according to Dopamine Coach constraints."""
        if not (
            ConfigGemini.MIN_LAUNCH_TASK_MINUTES
            <= self.estimated_time
            <= ConfigGemini.MAX_FLOW_MINUTES
        ):
            return (
                False,
                f"Step must be {ConfigGemini.MIN_LAUNCH_TASK_MINUTES}-{ConfigGemini.MAX_FLOW_MINUTES} minutes, got {self.estimated_time}",
            )

        if not self.primary_verb or len(self.primary_verb.split()) > 1:
            return False, "primary_verb must be a single action verb"

        if not self.step_title:
            return False, "step_title cannot be empty"

        valid_tags = {"Interest", "Novelty", "Challenge", "Urgency", "Passion"}
        if not self.incup_tags or self.incup_tags not in valid_tags:
            return (
                False,
                f"incup_tags must be one of {valid_tags}, got {self.incup_tags}",
            )

        return True, None


class DecompositionWorkblock:
    """Container for a complete task decomposition with all steps."""

    def __init__(
        self,
        task_id: int,
        task_title: str,
        task_priority: str,
        intent_priority: str,
        estimated_total_session_time: int,
        total_steps: int,
        steps: List[DecompositionStep],
        raw_response: str,
    ):
        self.task_id = task_id
        self.task_title = task_title
        self.task_priority = task_priority
        self.intent_priority = intent_priority
        self.estimated_total_session_time = estimated_total_session_time
        self.total_steps = total_steps
        self.steps = steps
        self.raw_response = raw_response

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(
            {
                "task": {
                    "task_id": self.task_id,
                    "task_title": self.task_title,
                    "task_priority": self.task_priority,
                    "intent_priority": self.intent_priority,
                    "estimated_total_session_time": self.estimated_total_session_time,
                    "total_steps": self.total_steps,
                    "steps": [step.to_dict() for step in self.steps],
                }
            },
            indent=2,
        )

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "task": {
                "task_id": self.task_id,
                "task_title": self.task_title,
                "task_priority": self.task_priority,
                "intent_priority": self.intent_priority,
                "estimated_total_session_time": self.estimated_total_session_time,
                "total_steps": self.total_steps,
                "steps": [step.to_dict() for step in self.steps],
            }
        }

    def validate_all(self) -> tuple[bool, List[str]]:
        """Validate all steps and task constraints."""
        errors = []

        valid_task_priorities = {"High", "Mid", "Low"}
        if self.task_priority not in valid_task_priorities:
            errors.append(f"Invalid task_priority: {self.task_priority}")

        valid_intent_priorities = {"High", "Medium", "Low"}
        if self.intent_priority not in valid_intent_priorities:
            errors.append(f"Invalid intent_priority: {self.intent_priority}")

        if self.total_steps != len(self.steps):
            errors.append(
                f"total_steps ({self.total_steps}) does not match steps array length ({len(self.steps)})"
            )

        expected_time = sum(step.estimated_time for step in self.steps)
        if self.estimated_total_session_time != expected_time:
            errors.append(
                f"estimated_total_session_time ({self.estimated_total_session_time}) does not match sum of step times ({expected_time})"
            )

        for step in self.steps:
            is_valid, error = step.validate()
            if not is_valid:
                errors.append(f"Step {step.step_id}: {error}")

        return len(errors) == 0, errors


class DecompositionAgent:
    """
    Decomposition Agent using Gemini API.
    Transforms user intentions into task breakdowns using Gemini v4-flash models.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Decomposition Agent for Gemini."""
        ModelProviderGemini.validate_provider()

        self.api_key = api_key or ModelProviderGemini.get_api_key()
        self.model = ConfigGemini.MODEL_ID
        self.logger = self._setup_logging()

        # Configure Google GenAI client
        genai.configure(api_key=self.api_key)

        self.logger.info(
            f"Gemini Decomposition Agent initialized with model: {self.model}"
        )

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the agent."""
        logger = logging.getLogger(__name__)
        logger.setLevel(ConfigGemini.LOG_LEVEL)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def decompose(
        self, user_input: str, validate: bool = True
    ) -> DecompositionWorkblock:
        """Decompose a user intention into actionable steps using Gemini."""
        self.logger.info(f"Decomposing user input: {user_input[:100]}...")

        try:
            # Create model instance with system instruction
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=get_system_prompt(),
                generation_config=genai.types.GenerationConfig(
                    temperature=ConfigGemini.TEMPERATURE,
                    max_output_tokens=ConfigGemini.MAX_TOKENS,
                ),
            )

            response = model.generate_content(user_input)
            raw_response = response.text
            self.logger.debug(f"Raw API response: {raw_response}")

            result = self._parse_response(raw_response)

            if validate and ConfigGemini.ENABLE_JSON_VALIDATION:
                is_valid, errors = result.validate_all()
                if not is_valid:
                    self.logger.warning(f"Validation errors: {errors}")
                    if self.logger.level == logging.DEBUG:
                        raise ValueError(f"Task validation failed: {errors}")
                else:
                    self.logger.info("All steps validated successfully")

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Decomposition failed: {e}")
            raise

    def _parse_response(self, response_text: str) -> DecompositionWorkblock:
        """Parse JSON response from API into DecompositionWorkblock object."""
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]

        json_str = json_str.strip()
        parsed = json.loads(json_str)
        task_data = parsed.get("task", {})

        steps = []
        for step_data in task_data.get("steps", []):
            step = DecompositionStep(
                step_id=(
                    int(step_data.get("step_id", 0)) if step_data.get("step_id") else 0
                ),
                step_title=step_data.get("step_title", ""),
                description=step_data.get("description", ""),
                estimated_time=step_data.get("estimated_time", 0),
                primary_verb=step_data.get("primary_verb", ""),
                deliverable=step_data.get("deliverable", ""),
                novelty_hook=step_data.get("novelty_hook", "none"),
                passion_anchor=step_data.get("passion_anchor"),
                urgency_cue=step_data.get("urgency_cue"),
                incup_tags=step_data.get("incup_tags", "Interest"),
            )
            steps.append(step)

        workblock = DecompositionWorkblock(
            task_id=int(task_data.get("task_id", 1)) if task_data.get("task_id") else 1,
            task_title=task_data.get("task_title", ""),
            task_priority=task_data.get("task_priority", "Mid"),
            intent_priority=task_data.get("intent_priority", "Medium"),
            estimated_total_session_time=task_data.get(
                "estimated_total_session_time", 0
            ),
            total_steps=task_data.get("total_steps", len(steps)),
            steps=steps,
            raw_response=response_text,
        )

        return workblock

    def batch_decompose(
        self, user_inputs: List[str]
    ) -> Dict[str, DecompositionWorkblock]:
        """Decompose multiple user inputs using Gemini."""
        results = {}
        for user_input in user_inputs:
            try:
                results[user_input] = self.decompose(user_input)
            except Exception as e:
                self.logger.error(f"Failed to decompose '{user_input}': {e}")
                results[user_input] = None

        return results
