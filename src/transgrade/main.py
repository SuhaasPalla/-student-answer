#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import os

# Firebase imports
import firebase_admin
from firebase_admin import credentials, firestore

from transgrade.crew import Transgrade

# Suppress warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Initialize Firebase Admin SDK with Firestore
cred = credentials.Certificate("./src/transgrade/transgrade-5244b-firebase-adminsdk-fbsvc-130d7fde7f.json")
firebase_admin.initialize_app(cred)

def run():
    try:
        # Hardcoded student ID
        student_id = "student_cf17322b"

        # Firestore client
        fs = firestore.client()

        # Fetch student document
        doc_ref = fs.collection("student_answers").document(student_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise Exception(f"Document 'student_answers/{student_id}' not found in Firestore.")

        doc_data = doc.to_dict()
        keyocr_list = doc_data.get("Keyocr")

        if not keyocr_list or not isinstance(keyocr_list, list) or 'formatted_text' not in keyocr_list[0]:
            raise Exception(f"'formatted_text' not found in student_answers/{student_id}/Keyocr[0]")

        formatted_text = keyocr_list[0]['formatted_text']

        inputs = {
            'text': formatted_text
        }

        # Run the Crew pipeline
        crew_result = Transgrade().crew().kickoff(inputs=inputs)

        print("Pipeline execution completed successfully!")
        print("Task results available at:")

        qa_output_path = 'qa_output.md'
        context_output_path = 'context_output.md'

        if os.path.exists(qa_output_path):
            print(f"- Q&A Extraction output: {qa_output_path}")
        if os.path.exists(context_output_path):
            print(f"- Context output: {context_output_path}")

        # Prepare crew_result to store (convert to dict or string)
        data_to_store = None
        if hasattr(crew_result, 'dict'):
            # Convert crew_result to dictionary if possible
            data_to_store = crew_result.dict()
        else:
            # Otherwise store string representation
            data_to_store = str(crew_result)

        # Update the same student document with 'context' field storing crew_result
        doc_ref.update({
            'context': data_to_store,
            'context_updated_at': firestore.SERVER_TIMESTAMP
        })

        print(f"Crew result stored in Firestore under 'student_answers/{student_id}/context'.")

        print("\nRaw result:", crew_result)
        print("Result type:", type(crew_result))
        if hasattr(crew_result, 'dict'):
            print("Result dict:", crew_result.dict())

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    inputs = {
        'text': {
            "extracted_text": []
        },
        'current_year': str(datetime.now().year)
    }
    try:
        Transgrade().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    try:
        Transgrade().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    inputs = {
        'text': {
            "extracted_text": []
        },
        'current_year': str(datetime.now().year)
    }
    try:
        Transgrade().crew().test(n_iterations=int(sys.argv[2]), eval_llm=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "run":
            run()
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
            print("Invalid command. Use 'run', 'train', 'replay', or 'test'.")
    else:
        print("Usage: python main.py run")
