from oauth2client.tools import _CLIENT_SECRETS_MESSAGE
import json
import typing
from pydantic import BaseModel
from groq import Groq 
import requests
import os 
from fastapi import APIRouter

make_content_router = APIRouter()

# tools = [
#             {
#                 "type" : "function",
#                 "function": {
#                     "name": "name  of the function",
#                     "description": "description of function",
#                     "parameters": {
#                         "type" : "object",
#                         "properties": {
#                             "parameters1": {
#                                 "type" : "string",
#                                 "description": "description about the parameters1"
#                                 },
#                             "parameters2": {
#                                 "type" : "string",
#                                 "description": "description about the parameters2"
#                                 }
#                             },
#                         required = ["parameter1","parameter2"]
#                     }
#                 }
#             },
#         ] 


async def create_prompt( raw_content , content_type ):

    if content_type.lower() == 'sheet':

        system_instruction = ''' 
        You are an intelligent and precise data processing AI. Your primary function is to filter and format a raw list of strings into a structured, single-line Python 2D list string. You are an expert at applying logical rules to categorize data accurately.

            ### YOUR TASK
            I will provide a multi-line string containing two Python variables: a `raw_content` list of topics and a `job_keywords` list. Your job is to process every item in the `raw_content` list. For each item, you must decide if it is relevant by checking if it contains any of the words from the `job_keywords` list. Based on this decision, you will format each item into a 9-element inner list and combine them into a final 2D list string.

            ### COLUMN LOGIC
            Each inner list you generate MUST contain exactly 9 string elements, in this specific order:

            1.  **"Idea Generation"**: The original trending topic string from the `raw_content` list.
            2.  **"Posting Status"**: This is a CONDITIONAL field.
                *   If the "Idea Generation" string contains **ANY** of the words from the `job_keywords` list (case-insensitive), you MUST set this value to the string **"Under Review"**.
                *   If the "Idea Generation" string does **NOT** contain any of the keywords, you MUST set this value to the string **"Not Relevant"**.
            3.  **"GPT 1"**: Set this to "Pending Categorization" if status is "Under Review", otherwise set to "N/A".
            4.  **"GPT 2"**: Set this to "N/A".
            5.  **"Youtube Reel Link"**: Set this to "N/A".
            6.  **"Instagram Post Content"**: Set this to "N/A".
            7.  **"Blog Link"**: Set this to "N/A".
            8.  **"Youtube Thumbnail Link"**: Set this to "N/A".
            9.  **"Timestamp"**: Set this to "N/A".

            ### EXAMPLE
            **Input from user:**
            raw_content = [
            "SSC CGL result 2024 tier 2",
            "Jawan movie box office collection"
                ]
            job_keywords = ['result', 'recruitment', 'admit card', 'vacancy', 'job', 'exam', 'notification']


            **Your required output (MUST BE A SINGLE LINE):**
            `[["Idea Generation", "Posting Status", "GPT 1", "GPT 2", "Youtube Reel Link", "Instagram Post Content", "Blog Link", "Youtube Thumbnail Link", "Timestamp"], ["SSC CGL result 2024 tier 2", "Under Review", "Pending Categorization", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"], ["Jawan movie box office collection", "Not Relevant", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]]`

            ### ABSOLUTE CONSTRAINTS
            -   Your response MUST be a single string.
            -   Do NOT use multiple lines or pretty-printing. The entire 2D list must be on one line.
            -   Do NOT add any text, explanations, or conversation before or after the list string.
            -   Do NOT add the word `python` or use markdown backticks.
            -   Ensure all strings within the list are correctly quoted with double quotes.

        '''   
    if content_type.lower() == 'insta':
        system_instruction = '''
            You are an expert Instagram copywriter. Your only job is to write a complete, ready-to-post caption with hashtags based on the user's topic.

            Your output must be a single block of text, ready to be copied and pasted directly into Instagram.

            Follow these strict rules for your response:

            1.  **NO HEADINGS:** Do NOT use any headings like "Caption:", "Visual Suggestion:", or "Hashtags:".
            2.  **CAPTION FIRST:**
                *   Start with a strong, attention-grabbing hook, often using emojis (like 🚨 or ✨).
                *   Write the main body using short, easy-to-read paragraphs with line breaks.
                *   Integrate relevant emojis naturally throughout the text to add personality and break up sentences.
                *   End the caption with a clear question or a call to action to encourage comments.
            3.  **HASHTAGS LAST:**
                *   Immediately after the final line of the caption, add a blank line.
                *   Then, provide a list of 7-10 relevant hashtags. Each hashtag must start with #.

            Your entire response should be just the caption followed by the hashtags, and nothing else.
        '''
    else:
        system_instruction = 'None'
    
    prompt = [
        {
            "role": "system",
            "content": system_instruction
        },
        {
            "role": "user",
            "content": raw_content
        }
    ]
    return prompt 


# raw_content = ''' [
#     "India vs Australia T20",
#     "SSC CGL result 2024 tier 2",
#     "Jawan movie box office collection",
#     "UP Police constable recruitment notification",
#     "Chandrayaan 3 update",
#     "IBPS Clerk admit card download",
#     "Diwali 2024 date",
#     "RRB Group D vacancy",
#     "State Bank of India job openings",
#     "G20 Summit Delhi",
#     "UPSC Civil Services exam date"
# ]
# job_keywords = ['result', 'recruitment', 'admit card', 'vacancy', 'job', 'exam', 'notification']
# '''
class __generate_data_for_sheet_output( BaseModel ):
    pass 

class __generate_data_for_sheet_input( BaseModel ):
    pass 

@make_content_router.post('/v2/getFormatedContent')
async def generate_data_for_sheet():
    raw_content = ''' [
    "India vs Australia T20",
    "SSC CGL result 2024 tier 2",
    "Jawan movie box office collection",
    "UP Police constable recruitment notification",
    "Chandrayaan 3 update",
    "IBPS Clerk admit card download",
    "Diwali 2024 date",
    "RRB Group D vacancy",
    "State Bank of India job openings",
    "G20 Summit Delhi",
    "UPSC Civil Services exam date"
    ]
    job_keywords = ['result', 'recruitment', 'admit card', 'vacancy', 'job', 'exam', 'notification']    
    '''
    client = Groq( api_key = os.environ['GROQ_API_KEY'])
    message = await create_prompt( raw_content , content_type= 'sheet') 
    response  = client.chat.completions.create(
        messages = message, 
        model = 'llama-3.3-70b-versatile'
        )
    
    return eval(response.choices[0].message.content) 

class __generate_insta_post_input( BaseModel ):
    title_data : typing.List[str]
    
class __generate_insta_post_output( BaseModel ):
    response : typing.Union[str , typing.Dict[str, typing.Union[typing.List, str]]]

@make_content_router.post('/v2/getInstaContent', response_model = __generate_insta_post_output )
async def generate_insta_post(userInput : __generate_insta_post_input ):
    insta_content = [] 
    try:
        for titles in userInput.title_data:
            client = Groq( api_key = os.environ['GROQ_API_KEY'])
            message = await create_prompt(titles, content_type ='insta')
            response = client.chat.completions.create(
                messages = message,
                model = 'llama-3.3-70b-versatile'
            )
            insta_content.append( response.choices[0].message.content )
        
        return {"response": "👍 Done", "content" : insta_content }
    
    except Exception as e:
        return {"response": " 🤯 Faliure", "content" : [f'error: {e}']}

class __generate_youtube_videos_input( BaseModel ):
    video_topics : typing.List[str]

class __generate_youtube_videos_output( BaseModel ):
    response : typing.Union[str, typing.Dict[str, typing.Union[typing.List[str], str]]]

@make_content_router.post('/v2/getYoutubeVideos', response_model= __generate_youtube_videos_output )
async def generate_youtube_videos( userInput : __generate_youtube_videos_input ):
    youtube_video_paths = [] 
    headers = {
        "Content-Type": "application/json"
    }

    for index,topic in enumerate(userInput.video_topics):

        json_data = {
            "user_prompt": f"generate video for {topic}",
            "voice_id": 'bIHbv24MWmeRgasZH58o',
            "video_name": f'video{index}' 
        }
        try:
            response = requests.post(
                'http://127.0.0.1:8000/v2/getFullVideo' ,
                headers = headers,
                json = json_data   
                )
            
            full_path = response.json()['response']['full_path']

        except Exception as e:
            youtube_video_paths.append('NOT_GENERATED')
            return  {"response": {"error": f"get Error during calling generate_youtube_videos function for generating video : {e}", "status" : "failed"}}

        youtube_video_paths.append(full_path)
    
    return {"response" : {"videos_path" : youtube_video_paths, "Status": "Done"}}