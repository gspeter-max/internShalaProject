from fastapi import FastAPI
from Jobyaari_Assignment.getScript import  Script_router
from Jobyaari_Assignment.getVoice import Voice_router
from Jobyaari_Assignment.getVideo import video_router
from Jobyaari_Assignment.getFullVideo import full_video_generation_router

app = FastAPI(
    title="Viral Video Script Generator API",
    description="An API to generate production-ready video scripts using LLMs on Groq.",
)

app.include_router( Voice_router )
app.include_router( Script_router)
app.include_router( video_router )
app.include_router( full_video_generation_router )

