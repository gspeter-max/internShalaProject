# Jobyaari_Assignment

## Overview

Jobyaari_Assignment is a FastAPI-based backend project that automates the generation of viral video scripts and related content using LLMs (Groq, ElevenLabs, etc.), and integrates with Google Drive and Google Sheets for content storage and management. The API is capable of:

- Scraping trending topics
- Generating formatted content for Google Sheets
- Producing Instagram and YouTube video content
- Generating voice-overs using ElevenLabs
- Uploading files (videos, thumbnails) to Google Drive
- Generating YouTube thumbnails and classifying content types

## Main Features & Endpoints

- **/v2/runAgents**: Orchestrates the full workflow, from scraping to generation and file upload.
- **/v2/getFormatedContent**: Generates structured content for Google Sheets.
- **/v2/getInstaContent**: Produces Instagram post content for given titles.
- **/v2/getYoutubeVideos**: Generates YouTube video assets and links.
- **/v2/getVoice**: Converts generated scripts or user-provided text to voice using ElevenLabs.
- **/v2/storeToDrive**: Uploads files (videos, thumbnails) to Google Drive.
- **/v2/generate_thumbnail**: Creates YouTube thumbnails from topic titles.
- **/v2/sendToGoogleSheet**: Updates Google Sheets with generated data.

## How it Works

1. **Topic Discovery**: Uses scraping and preset keyword lists to discover trending topics.
2. **Content Generation**: Employs LLMs to generate scripts, social media posts, and video assets.
3. **Voice-Over**: Converts scripts into voice files via ElevenLabs.
4. **File Storage**: Uploads generated media to Google Drive.
5. **Data Output**: Formats all output for easy integration into Sheets or social platforms.

## Technologies Used

- FastAPI
- Pydantic
- Google Drive & Sheets API (pygsheets, PyDrive)
- Groq (LLM)
- ElevenLabs (Text-to-Speech)
- Numpy, dotenv, Pexels API

## Folder Structure

- `agents.py`: Core logic for generating content, classification, prompts, and assets.
- `runner.py`: Main orchestration of backend workflow.
- `getVoice.py`: Handles voice synthesis.
- `getVideo.py`, `getFullVideo.py`: Video generation endpoints.
- `SendToGoogle/sendorUpdate.py`: Drive and Sheets integration.
- `imortant_information.txt`: Misc notes and reminders.
- `__init__.py`: FastAPI app setup and router inclusion.

## Quickstart

See [QUICKSTART.md](QUICKSTART.md) for API setup and usage!

---

## What I’ve Done:

- Designed and implemented multi-step content pipeline for job-related video/social content
- Automated Google Drive and Sheets integration for seamless publishing
- Added classification and thumbnail generation using LLMs
- Integrated ElevenLabs for natural-sounding voice-overs
- Modularized endpoints for easy extension

---
