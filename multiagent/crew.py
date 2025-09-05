import os 
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from multiagent.tools.custom_tool import ( 
    ConvertPromptToTerminalCommand, 
    TerminalExecution, 
    ImageGenerationTool, 
    SendImageInTelegramChannel, 
    SendTextInTelegramChannel 
    ) 
import os
import torch 
from transformers import AutoModelForCausalLM , AutoTokenizer 



# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-w   ith-decorator



class custom_model( LLM ):

    def __init__( self , model_id = 'NousResearch/Hermes-3-Llama-3.2-3B'):
        self.llm = AutoModelForCausalLM.from_pretrained( model_id , torch_dtype = torch.float16 ) 
        self.tokenizer = AutoTokenizer.from_pretrained( model_id ) 
    def _call( self , prompt : str , **kwargs) -> str :

        self.tokenizer.pad_token = self.tokenizer.eos_token
        input_ids = self.tokenizer( prompt, return_tensors = 'pt', truncation = True, padding = True ) 
        llm_response = self.llm.generate( **input_ids, max_new_tokens = 100 )
        return self.tokenizer.batch_decode( llm_response[-1], skip_special_tokens = True)


@CrewBase
class Multiagent():
    """Multiagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    

    llm = custom_model()
    
        # llm = LLM(
        #         model = 'gemini/gemini-1.5-flash',
        #         api_key = os.environ.get('GOOGLE_API_KEY', '')
        #         )

    @agent
    def Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['Researcher'], # type: ignore[index]
            verbose=True,
            respect_context_window= True,
            max_iter = 3,
            max_rpm = 1,
            # reasoning = True,
            # max_reasoning_attempts=1,
            multimodal = True,
            inject_data = True,
            tools = [ SerperDevTool()],
            llm = self.llm
        )

    @agent
    def SummaryWriter(self) -> Agent:
        return Agent(
            config=self.agents_config['SummaryWriter'], # type: ignore[index]
            verbose=True,
            max_iter = 3,
            max_rpm = 2,
            multimodal = True,
            # reasoning= True,
            # max_reasoning_attempts= 1,
            inject_data = True,
            respect_context_window= True,
            llm = self.llm,
            tools =[]
        )

    @agent
    def Visualizer(self) -> Agent:
        return Agent(
            config=self.agents_config['Visualizer'], # type: ignore[index]
            verbose=True,
            max_iter = 3,
            # reasoning= True,
            # max_reasoning_attempts= 1,
            max_rpm= 2,
            multimodal = True,
            inject_data = True,
            respect_context_window= True,
            llm = self.llm,
            tools = [ ConvertPromptToTerminalCommand() , TerminalExecution() , ImageGenerationTool() ]
        )

    @agent
    def translator(self) -> Agent:
        return Agent(
            config=self.agents_config['translator'], # type: ignore[index]
            verbose=True,
            max_iter = 3,
            max_rpm = 2,
            # reasoning= True,
            # max_reasoning_attempts = 1,
            multimodal = True,
            inject_data = True,
            respect_context_window= True,
            llm = self.llm,
            tools = []
        )

    @agent
    def telegram_sender(self) -> Agent:
        return Agent(
            config = self.agents_config['telegram_sender'],
            verbose= True,
            max_iter = 3,
            max_rpm= 2,
            multimodal = True,
            inject_data = True,
            respect_context_window= True,
            llm = self.llm,
            tools= [SendImageInTelegramChannel(), SendTextInTelegramChannel()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def summary_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config['summary_writer_task'], # type: ignore[index]
            output_file='report.md'
            )
    
    @task
    def visualization_task(self) -> Task:
        return Task(
            config=self.tasks_config['visualization_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task 
    def translation_task( self ) -> Task:
        return Task(
            config = self.tasks_config['translation_task'],
            output_file = 'report.md'
        )
    @task
    def send_summary_task(self) -> Task:
        return Task(
            config = self.tasks_config['send_summary_task'],
            output_file='report.md'
        )

    @task 
    def send_image_task(self) -> Task:
        return Task(
            config = self.tasks_config['send_image_task'],
            output_file = 'report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Multiagent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        print('crew is called')
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
