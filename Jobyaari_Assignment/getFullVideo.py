import subprocess
import json
from Jobyaari_Assignment.getScript import args_for_video_generation_content, get_content_for_video_generation 
from Jobyaari_Assignment.getVideo import get_video, __VideoInput
from Jobyaari_Assignment.getVoice import __getVoice , __voice_input
import requests 
from fastapi import APIRouter
import typing 
import os 
from moviepy import CompositeVideoClip
import moviepy 
from pydantic import BaseModel 

full_video_generation_router = APIRouter()

class __getFullVideoOutput( BaseModel ):
    response : typing.Union[str, typing.Dict[str, str ]]

class __getFullVideoInput( BaseModel ):
    user_prompt : str 
    voice_id : str 
    video_name : str 


@full_video_generation_router.post('/v2/getFullVideo', response_model= __getFullVideoOutput)
async def get_full_video(user_input : __getFullVideoInput):
    try:    
        content_generation_args = args_for_video_generation_content( content = user_input.user_prompt)
        generated_script = await get_content_for_video_generation( content_generation_args )

        text_caption = moviepy.TextClip(text = generated_script.full_script, font_size = 20, color = 'black')
        # voice_url = 'http://127.0.0.1:8000/v2/getVoice'
        # headers = {"Content-Type": "application/json"}
        # json_data = {
        #     "voice_id": user_input.voice_id,
        #     "user_prompt": user_input.user_prompt
        # }
        # response = requests.post( url = voice_url, headers= headers , json = json_data )

        user_prompt = { "generated_content": generated_script.full_script }
        voice_generation_args = __voice_input( voice_id = user_input.voice_id, user_prompt= user_prompt)
        response = await __getVoice( voice_generation_args )
        print(response)

        # video_url = 'http://127.0.0.1:8000/v2/getVideo'
        # video_json = {
        #     "user_prompt": user_input.user_prompt
        # }
        # response = requests.post( url = video_url, headers = headers, json = video_json ) 
        # print(response.content)
        video_generation_args = __VideoInput( user_prompt = user_prompt)
        response = await get_video( video_generation_args ) 
        print(response)


        video_file = moviepy.VideoFileClip('Jobyaari_Assignment/video.mp4')
        audio_file = moviepy.AudioFileClip('Jobyaari_Assignment/music.mp3')


        final_duration = min( video_file.duration, audio_file.duration)
        final_audio = audio_file.subclipped( end_time = final_duration )
        final_video = video_file.subclipped( end_time = final_duration )

        final_video = final_video.with_audio(final_audio)
        final_text = text_caption.subclipped( final_video.duration )


        _final_video = CompositeVideoClip([final_video, final_text])
        _final_video.duration = final_video.duration


        _final_video.write_videofile(f'Jobyaari_Assignment/{user_input.video_name}.mp4')
        subprocess.call('rm -rf Jobyaari_Assignment/video.mp4 Jobyaari_Assignment/music.mp3',shell = True )
        return {"response" : {"message": f"file is stored at {os.getcwd()}/video.mp4", "status": "success","full_path": f"Jobyaari_Assignment/{user_input.video_name}.mp4"}}
    
    except Exception as e:
        return {"response": {"error": f"get Error during generating video : {e}", "status" : "failed"}}
