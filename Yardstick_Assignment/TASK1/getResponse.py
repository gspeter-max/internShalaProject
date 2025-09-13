# from transformers import  AutoTokenizer 
import typing 
from groq import Groq 
from fastapi import FastAPI
# from dotenv import load_dotenv
from pydantic import BaseModel 
import os

app = FastAPI() 
class ChatCompletionMessageParam( BaseModel ):
    role : str 
    content : typing.Union[dict[str, str], str ]
    GroqApiKey: str 



class CreateSummary:
    def __init__(self):
        self.summary = [] 


# tokenizer =  AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-hf')
maximum_tokens = 1000 
global_token_counter = 0 
keep_noOf_message = 20
k_messages_feed_into_llm = 3
max_token_posible_in_output = 100

if keep_noOf_message < k_messages_feed_into_llm:
    raise RuntimeError(f'keep_noOf_message must be lower than k_messages_feed_into_llm  ( {keep_noOf_message} < {k_messages_feed_into_llm  }) ')

def summarization_logic( summarizationClass : CreateSummary , client ):

    for index, actual_content in enumerate(reversed(summarizationClass.summary)):
        if index >= keep_noOf_message:
            content = summarizationClass.summary[ index: ]
        else:
            content = actual_content

        llm_response = client.chat.completions.create(
            messages =[
                {
                    "role": "user",
                    "content": f"Summarize the following text into the shortest possible version while preserving all essential \
                        information and eliminating redundancy. Ensure no important detail is lost. The result must be concise,\
                             precise, and information-dense. Text: {content}"
                }
            ],
            model = 'gemma2-9b-it'
        )
        response = llm_response.choices[0].message.content
        summarizationClass.summary.append(response)

_summary_class = CreateSummary() 

@app.post('/v2/getResponse')
def get_response(userquery : ChatCompletionMessageParam ):
    global global_token_counter
    global _summary_class 
    try:

        client = Groq( api_key = userquery.GroqApiKey )
        # input_tokens = tokenizer(userquery.content).input_ids
        input_tokens = userquery.content

        if (len(input_tokens) >= maximum_tokens):
            return {"error": f"input tokens >= {maximum_tokens}"}
        else:
            global_token_counter += len(input_tokens)

        if  ((global_token_counter + len(input_tokens)) >= maximum_tokens):
            summarization_logic( summarizationClass= _summary_class , client = client)
        
        if len(_summary_class.summary) <= k_messages_feed_into_llm:
            content = f"past summary of conversation : {_summary_class.summary} \n\n" + f"current user_qestion : {userquery.content}" 
        else:
            content = f"past summary of conversation : {_summary_class.summary[:k_messages_feed_into_llm]} \n\n" + f"current user_qestion : {userquery.content}" 
            
        response = client.chat.completions.create(
            messages=[
                {
                    "role": userquery.role,
                    "content" : content
                }
            ],
            model = 'gemma2-9b-it'
        ).choices[0].message.content
        
        # if len(tokenizer.tokenize(response)) >= max_token_posible_in_output:
        if len(response) >= max_token_posible_in_output:

            _o4th_path = int(len(response) / 5) 
            return_response = f'{response[:_o4th_path]} </---------/>  {response[-_o4th_path :]}'
        else:
            return_response = response

        _summary_class.summary.append(f'userquery : {userquery.content}  llmRespose : {response}')
        return {'response' : return_response }  
    
    except Exception as e:
        return {"error": "got error during getting response from llm due to : {e}"}

