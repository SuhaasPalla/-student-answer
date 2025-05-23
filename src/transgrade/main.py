#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import json
import os

from transgrade.crew import Transgrade

# Suppress warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    # Sample input - directly pass dict object without json.dumps()
    inputs = {
    'text': (
        "Social Studies Question Answer Key\n"
        "Section I (1×5=5M)\n"
        "1) What do you understand by Resource?\n"
        "A) Resources are naturally occurring or human-made materials that have utility and value for humans. They include natural" "resources (like minerals, water, forests), human resources (knowledge, skills), and human-made resources (buildings,"
        "technology). Resources are characterized by utility, availability, and potential for development. Their value can change\n"
        "based on technological development, cultural preferences, and economic factors.\n"
        "2) Which states in India are rich in minerals and coal deposits?\n"
        "A) Jharkhand, Chhattisgarh, Odisha, West Bengal, and Madhya Pradesh are particularly rich in minerals and coal deposits." "Jharkhand and Chhattisgarh together form part of the Chota Nagpur plateau which contains some of India's largest mineral"
        "reserves. Other mineral-rich states include Maharashtra (manganese), Karnataka (iron ore), and Rajasthan (zinc, copper).\n"
        "3) Which report in 1987 introduced the concept of Sustainable Development?\n"
        "A) The  Our Common Future report, also known as the Brundtland Report, published by the World Commission on" "Environment and Development (WCED) in 1987, introduced the concept of 'Sustainable Development'. The report defined"
        "sustainable development as development that meets the needs of the present without compromising the ability of future\n"
        "generations to meet their own needs.\n"
        "4) What is the total geographical area of India?\n"
        "A) The total geographical area of India is approximately 3.287 million square kilometers (or about 328.7 million hectares)." "This makes India the seventh-largest country in the world by land area."
        "5) How much degraded land is in India?\n"
        "A) Approximately 96.4 million hectares (about 29.32% of India's total geographical area) is degraded land in India. This" "includes land affected by water and wind erosion, salinity, soil acidity, waterlogging, and other forms of land degradation."
        "Section II (2×1=2M)\n"
        "6) What do you understand by International resources? Give example.\n"
        "A) International resources are resources that are regulated by international institutions and are not owned by a single country." "They exist beyond national boundaries and are governed by international agreements and conventions."
        "Examples include:\n"
        "The ocean resources beyond territorial waters (international waters)\n"
        "Antarctica, which is regulated by the Antarctic Treaty System\n"
        ".\n"
        "Outer space and celestial bodies as defined by the Outer Space Treaty\n"
        "The atmosphere as a shared global resource\n"
        "Certain international river systems shared by multiple countries\n"
        "Section III (4×2=8M)\n"
        "7) Mention some features of arid soil.\n"
        "A)|Features of arid soil include:" "Light texture with sandy or sandy-loam consistency"
        "Low organic matter content due to sparse vegetation\n"
        "High mineral content, particularly salts\n"
        "Low moisture retention capacity\n"
        "High pH value (alkaline in nature)\n"
        "Low in nitrogen and often phosphorus\n"
        "Presence of calcium carbonate and gypsum\n"
        "Susceptible to wind erosion\n"
        "Light color (typically reddish-brown to pale brown)\n"
        "Poorly developed soil profile with thin horizons\n"
        "8) Explain the role of humans in resource development.\n"
        "A) Humans play a crucial role in resource development through:" "1."
        "Identification and discovery of resources through research and exploration\n"
        "2.\n"
        "3.\n"
        "Development of technology to access, extract, and process resources more efficiently\n"
        "Creation of infrastructure for resource utilization and distribution\n"
        "4.\n"
        "Transformation of natural materials into more valuable forms through manufacturing\n"
        "5.\n"
        "Conservation and sustainable management practices to prevent resource depletion\n"
        "6.\n"
        "Creation of human-made resources through knowledge, skills and innovation\n"
        "7.\n"
        "Resource planning and policy implementation for optimal resource allocation\n"
    )
}

    try:
        # Run the crew with sequential tasks - qa_extraction followed by contextual
        crew_result = Transgrade().crew().kickoff(inputs=inputs)
        
        # Print task results and save to files
        print("Pipeline execution completed successfully!")
        print("Task results available at:")
        
        # Check if output files were created
        qa_output_path = 'qa_output.md'
        context_output_path = 'context_output.md'
        
        if os.path.exists(qa_output_path):
            print(f"- Q&A Extraction output: {qa_output_path}")
            
        if os.path.exists(context_output_path):
            print(f"- Context output: {context_output_path}")
        
        # Print raw results for debugging
        print("\nRaw result:", crew_result)
        print("Result type:", type(crew_result))
        
        if hasattr(crew_result, 'dict'):
            print("Result dict:", crew_result.dict())
            
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'text': {
            "extracted_text": [
                # Your training data here
            ]
        },
        'current_year': str(datetime.now().year)
    }
    try:
        Transgrade().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task ID.
    """
    try:
        Transgrade().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'text': {
            "extracted_text": [
                # Your test data here
            ]
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
        run()