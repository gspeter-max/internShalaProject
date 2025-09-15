from groq import Groq
import os
import typing
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

load_dotenv() 
Script_router  = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DEFAULT_MODEL = 'llama-3.3-70b-versatile' 

class args_for_video_generation_content(BaseModel):
    content: str = Field(..., description="The topic or main idea for the video.")
    model_name: typing.Optional[str] = Field(DEFAULT_MODEL, description="The Groq model to use for generation.")

class SceneDescription(BaseModel):
    scene: int = Field(..., description="The scene number, e.g., 1, 2, 3.")
    visuals: str = Field(..., description="A detailed description of what should be on screen.")
    voiceover_part: str = Field(..., description="The exact part of the script spoken during this scene.")
    keyword_for_search: str = Field(..., description="A simple keyword to find stock footage for this scene (e.g., 'ancient rome colosseum').")

class VideoScriptBlueprint(BaseModel):
    title: str = Field(..., description="A catchy, viral title for the video.")
    hook: str = Field(..., description="The first 1-3 seconds of the video, designed to grab attention.")
    duration: str = Field( ..., description = "make sure the total duration of video scription is 18s ")
    full_script: str = Field(..., description="The complete voiceover script.")
    scenes: typing.List[SceneDescription] = Field(..., description="A scene-by-scene breakdown of the video.")
    music_suggestion: str = Field(..., description="A suggestion for background music mood (e.g., 'Epic Orchestral', 'Mysterious Lofi').")


async def create_master_prompt(user_topic: str) -> list:
    system_prompt = """
        You are a world-class viral video scriptwriter and director for platforms like TikTok, YouTube Shorts, and Instagram Reels.
        Your task is to take a user's topic and transform it into a complete, production-ready video blueprint.
        The output MUST be a JSON object that strictly follows this format:
        {
        "title": "A short, catchy, viral title",
        "hook": "The first sentence of the script (1-3 seconds) that is extremely attention-grabbing.",
        "duration": "make sure the that duration of video script is 18s",
        "full_script": "The entire voiceover script, concise and engaging, around 100-150 words.",
        "scenes": [
            {
            "scene": 1,
            "visuals": "A detailed description of the visuals for this part of the script.",
            "voiceover_part": "The part of the script that is spoken during this scene.",
            "keyword_for_search": "A simple 2-4 word search term for finding stock video for this scene."
            }
        ],
        "music_suggestion": "A suggestion for the mood of the background music."
        }

        RULES:
            1.  The hook must be powerful and create immediate curiosity.
            2.  The total script length must be suitable for a short video (under 60 seconds).
            3.  Break the script down into at least 3-5 logical scenes.
            4.  The 'visuals' description must be vivid and clear.
            5.  The 'keyword_for_search' must be simple and effective for a site like Pexels or Pixabay.
            6.  Do NOT add any text or explanation outside of the JSON object. Your entire response must be the JSON itself.
"""
    
    user_prompt = f"Generate a complete video blueprint for the following topic: '{user_topic}'"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

@Script_router.post('/v2/getVideoScript', response_model=VideoScriptBlueprint)
async def get_content_for_video_generation(video_generate_args: args_for_video_generation_content ):
    print(f"Generating script for topic: '{video_generate_args.content}' using model '{video_generate_args.model_name}'")

    messages = await create_master_prompt(video_generate_args.content)
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=video_generate_args.model_name,
            temperature=0.7,  
            response_format={"type": "json_object"}, 
        )
        response_content = response.choices[0].message.content
        print("Raw response from model:", response_content)

        try:
            blueprint_data = json.loads(response_content)
            return VideoScriptBlueprint(**blueprint_data)

        except json.JSONDecodeError:
            print("Error: Model did not return valid JSON.")
            raise HTTPException(status_code=500, detail="Failed to parse JSON response from the AI model.")

    except Exception as e:
        print(f"An error occurred with the Groq API: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while communicating with the AI model.")
