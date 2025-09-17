from dotenv import load_dotenv
import requests 
from Pexels import Client 
import os 
from fastapi import APIRouter
import json 
from pydantic import BaseModel
import typing 
from dotenv import load_dotenv

load_dotenv() 

video_router = APIRouter()

class __VideoInput( BaseModel):
    user_prompt : typing.Union[ str, typing.Dict]

class __output_format( BaseModel ):
    response  : typing.Union[str, typing.Dict[str, str]]

@video_router.post('/v2/getVideo', response_model= __output_format )
async def get_video( user_input : __VideoInput):

    try:
        client = Client( token = os.environ.get('PEXELS_API_KEY')) 

        if isinstance( user_input.user_prompt, str): 
            url = 'http://127.0.0.1:8000/v2/getVideoScript'
            headers = {'Content-Type': "application/json"}
            json_data = {"content": user_input.user_prompt}

            __response = requests.post( url = url , headers = headers, json = json_data )
            response_content = json.loads(__response.text)['full_script']

        else: 
            response_content = user_input.user_prompt['generated_content']

        video_response = client.search_videos(
            query =  response_content,
            per_page=10
        )

        # final_video = None
        # max_duration_index = None
        # max_duration = 0
        # for index, _videos in enumerate(video_response.videos):
        #     if _videos.duration > max_duration :
        #         max_duration = _videos.duration
        #         max_duration_index = index 
            
        #     if _videos.duration == 20:
        #         final_video = _videos
        #         break 
            
        # if final_video is None:
        #     final_video = video_response.videos[ max_duration_index ]
        
        final_video = video_response.videos[0]

        data_url = final_video.video_files

        for video_obj in data_url:
            if (video_obj.file_type == 'video/mp4') and (video_obj.height == 1920 or video_obj.width == 1080):
                if video_obj.link:
                    data_url = video_obj.link
                
            else:
                if video_obj.file_type == 'video/mp4':
                    if video_obj.link:
                        data_url = video_obj.link

            response = requests.get(data_url) 
            if response.status_code == 200:
                with open('Jobyaari_Assignment/video.mp4', 'wb') as f:
                    f.write(response.content)
            else:
                print(f"❌ Failed to download video. Status code: {response.status_code}")

        return  {"response" : {"message": f"file is stored at {os.getcwd()}/video.mp4", "status": "success"}}
    except Exception as e:
        return  {"response": {"error": f"get Error during generating video : {e}", "status" : "failed"}}


