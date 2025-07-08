#!/usr/bin/env python
"""
Flask API wrapper for Transgrade crew
Run this as a separate service: python transgrade_api.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import warnings
from datetime import datetime
import os
import requests
import json
from transgrade.crew import Transgrade

# Suppress warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Base URL for your Django API
BASE_URL = "http://localhost:8000"

def get_key_json_from_api(subject_id):
    """
    Retrieve key JSON from PostgreSQL database via Django API using subject ID
    """
    try:
        # Make GET request to key-ocr endpoint with subject_id parameter
        url = f"{BASE_URL}/key-ocr/?subject_id={subject_id}"
        response = requests.get(url)
       
        if response.status_code == 404:
            raise Exception(f"Key OCR not found for subject ID: {subject_id}")
        elif response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
       
        data = response.json()
       
        print(f"Retrieved key OCR for subject: {data['subject_name']}")
        print(f"Class: {data['class_name']}")
       
        return data['key_json']
   
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to Django API. Make sure the server is running on localhost:8000")
    except Exception as e:
        raise Exception(f"Error retrieving key JSON from API: {e}")

@app.route('/api/run-transgrade', methods=['POST'])
def run_transgrade():
    try:
        data = request.get_json()
        subject_id = data.get('subject_id')
       
        if not subject_id:
            return jsonify({'error': 'subject_id is required'}), 400
       
        print(f"Processing subject ID: {subject_id}")
       
        # Get key JSON from PostgreSQL via API
        print(f"Retrieving key JSON from PostgreSQL for subject ID: {subject_id}")
        key_json = get_key_json_from_api(subject_id)
        print("Key JSON retrieved successfully from PostgreSQL")
       
        # Prepare inputs with only key JSON
        inputs = {
            'text': key_json  # Only the key JSON from PostgreSQL
        }
       
        print("Running Crew pipeline with key JSON only...")
       
        # Run the Crew pipeline
        crew_result = Transgrade().crew().kickoff(inputs=inputs)
        print("Pipeline execution completed successfully!")
       
        # Check for output files
        qa_output_path = 'qa_output.md'
        context_output_path = 'context_output.md'
       
        output_files = {}
        if os.path.exists(qa_output_path):
            with open(qa_output_path, 'r', encoding='utf-8') as f:
                output_files['qa_output'] = f.read()
        if os.path.exists(context_output_path):
            with open(context_output_path, 'r', encoding='utf-8') as f:
                output_files['context_output'] = f.read()
       
        response_data = {
            'success': True,
            'message': 'Pipeline execution completed successfully!',
            'crew_result': str(crew_result),
            'output_files': output_files
        }
       
        if hasattr(crew_result, 'dict'):
            response_data['crew_result_dict'] = crew_result.dict()
           
        return jsonify(response_data)
       
    except Exception as e:
        print(f"Error in run_transgrade: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Optional: Get list of available subjects"""
    try:
        url = f"{BASE_URL}/subjects/"  # Adjust endpoint as needed
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Could not fetch subjects'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("Starting Transgrade Flask API on http://localhost:5001")
    print("Health check available at: http://localhost:5001/health")
    print("API endpoint: http://localhost:5001/api/run-transgrade")
    app.run(host='0.0.0.0', port=5001, debug=True)
