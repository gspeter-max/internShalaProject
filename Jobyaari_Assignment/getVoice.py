import os
from dotenv import load_dotenv
import json 
import elevenlabs
import requests
import typing 
from pydantic import BaseModel 
from elevenlabs import ElevenLabs
from fastapi import APIRouter
from Jobyaari_Assignment.getScript import args_for_video_generation_content, get_content_for_video_generation

Voice_router = APIRouter()
load_dotenv()

class __voice_input( BaseModel ):
    voice_id : str 
    user_prompt : typing.Union[str, typing.Dict[str, str]]

class __return_output( BaseModel):
    full_file_name : str 

@Voice_router.post('/v2/getVoice', response_model = __return_output)
async def __getVoice(voiceInput : __voice_input):
    client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])

    if isinstance( voiceInput.user_prompt, str):

        get_content_for_video_generation_input = args_for_video_generation_content(
            content = voiceInput.user_prompt
        )
        response = get_content_for_video_generation(
            video_generate_args= get_content_for_video_generation_input
        )
        response_content = response['full_script']
    
    elif isinstance( voiceInput.user_prompt, typing.Dict):
        response_content  = voiceInput.user_prompt['generated_content']

    response = client.text_to_speech.convert(
        voice_id= voiceInput.voice_id,
        text= response_content,
        output_format='mp3_22050_32',
        voice_settings= elevenlabs.types.voice_settings.VoiceSettings(
            stability= 0.4,
            similarity_boost= 0.7
        ),
        model_id='eleven_multilingual_v2'
    )

    all_bytes = b''.join(response)
    with open('Jobyaari_Assignment/music.mp3', 'wb') as f:
        f.write(all_bytes)

    return  {"full_file_name": "Jobyaari_Assignment/video.mp4"}
