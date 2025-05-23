import yaml
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class Transgrade:
    def __init__(self):
        # Load configs from YAML files on initialization
        config_dir = Path(__file__).parent / "config"
        self.agents_config = self._load_yaml(config_dir / "agents.yaml")
        self.tasks_config = self._load_yaml(config_dir / "tasks.yaml")

    def _load_yaml(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise Exception(f"Config file not found: {filepath}")
        except yaml.YAMLError as e:
            raise Exception(f"YAML error in {filepath}: {e}")

    @agent
    def qa_extraction_agent(self) -> Agent:
        return Agent(
            role=self.agents_config['qa_extraction_agent']['role'],
            goal=self.agents_config['qa_extraction_agent']['goal'],
            backstory=self.agents_config['qa_extraction_agent']['backstory'],
            allow_delegation=self.agents_config['qa_extraction_agent'].get('allow_delegation', False),
            verbose=True
        )
        
    @agent
    def context_agent(self) -> Agent:
        return Agent(
            role=self.agents_config['context_agent']['role'],
            goal=self.agents_config['context_agent']['goal'],
            backstory=self.agents_config['context_agent']['backstory'],
            allow_delegation=self.agents_config['context_agent'].get('allow_delegation', False),
            verbose=True
        )

    @task
    def qa_extraction_task(self) -> Task:
        return Task(
            description=self.tasks_config['qa_extraction_task']['description'],
            expected_output=self.tasks_config['qa_extraction_task']['expected_output'],
            agent=self.qa_extraction_agent(),
            output_file='qa_output.md'  # Output file path
        )
        
    @task
    def contextual_task(self) -> Task:
        return Task(
            description=self.tasks_config['contextual_task']['description'],
            expected_output=self.tasks_config['contextual_task']['expected_output'],
            agent=self.context_agent(),
            output_file='context_output.md'  # Output file path
        )

    @crew
    def crew(self) -> Crew:
        """Creates the crew to process OCR data, extract Q&A, and then build context"""
        return Crew(
            agents=[self.qa_extraction_agent(), self.context_agent()],
            tasks=[self.qa_extraction_task(), self.contextual_task()],
            process=Process.sequential,  # Important to ensure tasks run in order
            verbose=True
        )