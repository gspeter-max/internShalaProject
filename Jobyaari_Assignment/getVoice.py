import os
from dotenv import load_dotenv
import json 
import elevenlabs
import requests
import typing 
from pydantic import BaseModel 
from elevenlabs import ElevenLabs
from fastapi import APIRouter

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

        url = 'http://127.0.0.1:8000/v2/getVideoScript'
        headers = {'Content-Type': "application/json"}
        json_data = { "content": voiceInput.user_prompt}
        __response = requests.post( url = url , headers = headers, json = json_data )

        response_content = json.loads(__response.text)['full_script']
    
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
