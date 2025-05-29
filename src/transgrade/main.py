#!/usr/bin/env python
import sys
import os
import json
import warnings
import logging
import requests
from datetime import datetime
from flask import Flask, jsonify

from transgrade.crew import Transgrade

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Django API configuration
DJANGO_API_BASE_URL = "https://00c4-124-123-191-159.ngrok-free.app"

# -------------------------------
# 🔍 Function to get KeyOCR by subject_id
# -------------------------------
def get_key_ocr_by_subject_id(subject_id: str):
    """Retrieve KeyOCR data from Django API by subject_id"""
    try:
        # Make API request to get KeyOCR data
        url = f"{DJANGO_API_BASE_URL}/key-ocr/?subject_id={subject_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            key_ocr_data = response.json()
            return key_ocr_data, None
        elif response.status_code == 404:
            return None, f"KeyOCR not found for subject_id: {subject_id}"
        else:
            return None, f"API error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, "Failed to connect to Django API. Make sure the server is running on localhost:8000"
    except requests.exceptions.RequestException as e:
        return None, f"API request error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None, f"Error retrieving KeyOCR: {str(e)}"

# -------------------------------
# 🔄 Function to update KeyOCR context
# -------------------------------
def update_key_ocr_context(subject_id: str, context: str):
    """Update KeyOCR context via Django API"""
    try:
        url = f"{DJANGO_API_BASE_URL}/key-ocr/"
        data = {
            'subject_id': subject_id,
            'context': context
            # Removed key_json field entirely - we only want to update context
        }
        
        response = requests.put(url, json=data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            return True, "KeyOCR context updated successfully"
        else:
            return False, f"Failed to update KeyOCR context: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"API request error: {str(e)}"
    except Exception as e:
        return False, f"Error updating KeyOCR: {str(e)}"

# -------------------------------
# 🧠 Core CrewAI pipeline logic (modified)
# -------------------------------
def run_crew_pipeline(subject_id: str):
    try:
        # Get KeyOCR data from Django API
        key_ocr_data, error = get_key_ocr_by_subject_id(subject_id)
        
        if error:
            return False, error
        
        if not key_ocr_data or 'key_json' not in key_ocr_data:
            return False, f"KeyOCR data not found or invalid for subject_id: {subject_id}"
        
        # Extract the key_json for processing - pass directly without converting to string
        key_json = key_ocr_data['key_json']
        
        # Prepare inputs for CrewAI pipeline - pass key_json directly as received
        inputs = {'text': key_json}
        
        # Run CrewAI pipeline
        crew_result = Transgrade().crew().kickoff(inputs=inputs)
        
        # Process crew result - only convert to string if absolutely necessary for storage
        if hasattr(crew_result, 'text'):
            crew_result_text = crew_result.text
        elif hasattr(crew_result, 'dict'):
            crew_result_text = json.dumps(crew_result.dict())
        elif isinstance(crew_result, (list, dict)):
            crew_result_text = json.dumps(crew_result)
        elif crew_result is None:
            return False, "crew_result is None"
        else:
            crew_result_text = str(crew_result)
        
        # Update the KeyOCR context with the crew result
        update_success, update_message = update_key_ocr_context(subject_id, crew_result_text)
        
        if not update_success:
            logger.warning(f"Failed to update KeyOCR context: {update_message}")
        
        return True, f"Success: Crew result processed for subject_id {subject_id} ({key_ocr_data.get('subject_name', 'Unknown Subject')} - {key_ocr_data.get('class_name', 'Unknown Class')}). {update_message if update_success else 'Note: Failed to update context in database.'}"

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return False, f"Error: {str(e)}"

# -------------------------------
# 🚀 Flask App inside run()
# -------------------------------
def run():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'

    @app.route('/')
    def index():
        return jsonify({
            "message": "Transgrade API is running",
            "usage": "Access /run/<subject_id> to process a subject",
            "health_check": "/health"
        })

    @app.route('/run/<subject_id>', methods=['GET'])
    def run_pipeline_route(subject_id):
        """Direct API endpoint to run crew pipeline with subject_id"""
        if not subject_id:
            return jsonify({
                "status": "error",
                "message": "Subject ID is required"
            }), 400
        
        logger.info(f"Processing crew pipeline for subject_id: {subject_id}")
        success, message = run_crew_pipeline(subject_id)
        
        return jsonify({
            "status": "success" if success else "error",
            "subject_id": subject_id,
            "message": message
        }), 200 if success else 500

    # Health check endpoint to verify Django API connectivity
    @app.route('/health')
    def health_check():
        try:
            response = requests.get(f"{DJANGO_API_BASE_URL}/subjects/", timeout=5)
            if response.status_code == 200:
                return jsonify({"status": "healthy", "django_api": "connected"})
            else:
                return jsonify({"status": "unhealthy", "django_api": "error", "details": f"Status: {response.status_code}"})
        except Exception as e:
            return jsonify({"status": "unhealthy", "django_api": "disconnected", "error": str(e)})

    app.run(debug=True)

# -------------------------------
# Optional CLI: train, test, replay
# -------------------------------
def train():
    inputs = {'current_year': str(datetime.now().year)}
    try:
        Transgrade().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"Error training the crew: {e}")

def replay():
    try:
        Transgrade().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"Error replaying: {e}")

def test():
    inputs = {'current_year': str(datetime.now().year)}
    try:
        Transgrade().crew().test(n_iterations=int(sys.argv[2]), eval_llm=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"Error testing the crew: {e}")

# -------------------------------
# 🧭 Main entry
# -------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "run":
            run()  # 🔥 Start Flask app
        elif cmd == "train":
            if len(sys.argv) < 4:
                print("Usage: python main.py train <n_iterations> <filename>")
            else:
                train()
        elif cmd == "replay":
            if len(sys.argv) < 3:
                print("Usage: python main.py replay <task_id>")
            else:
                replay()
        elif cmd == "test":
            if len(sys.argv) < 4:
                print("Usage: python main.py test <n_iterations> <eval_llm>")
            else:
                test()
        else:
            print("Invalid command. Use: run | train | replay | test")
    else:
        print("Usage: python main.py <run|train|replay|test>")