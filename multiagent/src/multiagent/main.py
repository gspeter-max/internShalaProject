import os 
#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from urllib3 import response

from multiagent.crew import Multiagent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': ' generates a daily financial market summary after US Market is close',
        'current_year': str(datetime.now().year),
        'language': 'english'
    }
    
    try:
        print('try is entred')
        response =  Multiagent().crew().kickoff(inputs=inputs)
        print('response is getted')
        print(response)
        return response 

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

res = run()
print(res)
