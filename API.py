"""
Flask API for the Decomposition Agent
Accepts user input and returns decomposed tasks as JSON.
"""

import json
import logging
from flask import Flask, request, jsonify
from decomposition_agent import DecompositionAgent


# Initialize Flask app
app = Flask(__name__)
# Preserve JSON key order
app.json.ensure_ascii = False
app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agent
agent = DecompositionAgent()


@app.route("/decompose", methods=["POST"])
def decompose():
    """
    API endpoint to decompose a user intention into actionable steps.

    Expected request format:
    {
        "user_input": "Your task or intention here"
    }

    Returns:
    JSON response with decomposed task structure or error message
    """
    try:
        # Parse JSON request
        data = request.get_json()

        # Validate request format
        if not data or "user_input" not in data:
            return (
                jsonify(
                    {
                        "error": "Invalid request format",
                        "message": "Request must contain 'user_input' field",
                        "expected_format": {"user_input": "str"},
                    }
                ),
                400,
            )

        user_input = data.get("user_input")

        # Validate user_input is a string
        if not isinstance(user_input, str) or not user_input.strip():
            return (
                jsonify(
                    {
                        "error": "Invalid user_input",
                        "message": "user_input must be a non-empty string",
                    }
                ),
                400,
            )

        logger.info(f"Processing user input: {user_input}")

        # Decompose the user intention
        result = agent.decompose(user_input)

        # Return as JSON
        response_data = result.to_dict()
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Decomposition Agent API"}), 200


@app.route("/", methods=["GET"])
def index():
    """API documentation endpoint."""
    return (
        jsonify(
            {
                "service": "Decomposition Agent API",
                "version": "1.0",
                "endpoints": {
                    "/decompose": {
                        "method": "POST",
                        "description": "Decompose a user intention into actionable steps",
                        "request_format": {"user_input": "str"},
                        "example_request": {
                            "user_input": "I need to redesign my database schema for better performance"
                        },
                        "response_format": {
                            "task": {
                                "task_id": "int",
                                "task_title": "str",
                                "task_priority": "str",
                                "intent_priority": "str",
                                "estimated_total_session_time": "int",
                                "total_steps": "int",
                                "steps": "array of step objects",
                            }
                        },
                    },
                    "/health": {
                        "method": "GET",
                        "description": "Health check endpoint",
                    },
                    "/": {"method": "GET", "description": "API documentation"},
                },
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Run Flask app
    # Set debug=False for production
    app.run(host="0.0.0.0", port=5000, debug=True)
