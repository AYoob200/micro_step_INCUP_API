"""
Example usage of the Decomposition Agent with Gemini API.
Demonstrates JSON-only output from Dopamine Coach.
"""

import json
from decomposition_agent import DecompositionAgent
from config import ConfigGemini, ModelProviderGemini


def example_basic_usage():
    """Basic example: Decompose a single user intention - JSON only output."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Decomposition (Gemini - JSON Output)")
    print("=" * 60 + "\n")

    agent = DecompositionAgent()

    user_input = "I need to redesign my database schema for better performance"

    print(f"User Input: {user_input}\n")

    result = agent.decompose(user_input)

    print("JSON Output:")
    print(result.to_json())

    is_valid, errors = result.validate_all()
    print(f"\nValidation Status: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        for error in errors:
            print(f"  - {error}")


def example_json_output():
    """Output only JSON format."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: JSON Output Format")
    print("=" * 60 + "\n")

    agent = DecompositionAgent()
    user_input = "Build an authentication system with OAuth2"

    print(f"User Input: {user_input}\n")

    result = agent.decompose(user_input)
    print(result.to_json())


def example_validation():
    """Validate against AI Constitution rules."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: AI Constitution Compliance Check")
    print("=" * 60 + "\n")

    agent = DecompositionAgent()
    user_input = "Create a mobile app for task management"

    print(f"User Input: {user_input}\n")

    result = agent.decompose(user_input)
    print(result.to_json())

    is_valid, errors = result.validate_all()
    print(f"\nValidation: {'PASSED' if is_valid else 'FAILED'}")


def example_batch_processing():
    """Process multiple intentions at once."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 60 + "\n")

    agent = DecompositionAgent()

    user_inputs = [
        "Set up CI/CD pipeline for my project",
        "Migrate data from MongoDB to PostgreSQL",
        "Implement API rate limiting",
    ]

    print("Processing multiple intentions:\n")

    results = agent.batch_decompose(user_inputs)

    for user_input, result in results.items():
        if result:
            print(f"\n{'='*60}")
            print(f"Input: {user_input}")
            print(f"JSON Output:")
            print(result.to_json())
        else:
            print(f"\n{'='*60}")
            print(f"Input: {user_input}")
            print("Failed to decompose")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DOPAMINE COACH - GEMINI DECOMPOSITION AGENT")
    print("JSON OUTPUT ONLY")
    print("=" * 60)

    example_basic_usage()

    print("\n" + "=" * 60)
    print("END OF EXAMPLES")
    print("=" * 60 + "\n")
