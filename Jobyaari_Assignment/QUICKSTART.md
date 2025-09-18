# Quickstart: Jobyaari_Assignment API

## Prerequisites

- Python 3.8+
- Google Drive & Sheets API credentials (`client_secrets.json`, `credentials.json`)
- .env file with API keys (Groq, ElevenLabs, Pexels, etc.)
- Install dependencies:
  ```bash
  pip install fastapi pydantic pygsheets pydrive numpy python-dotenv requests
  ```

## Running the API

1. **Clone the repository** and navigate to Jobyaari_Assignment:

   ```bash
   git clone https://github.com/gspeter-max/internShalaProject.git
   cd internShalaProject/Jobyaari_Assignment
   ```

2. **Set up your environment variables** in `.env` (see README for required keys).

3. **Add your Google API credentials** to the folder.

4. **Start the FastAPI app**:

   ```bash
   uvicorn Jobyaari_Assignment.__init__:app --reload
   ```

## Example Usage

1. **Run agents pipeline**:
   - POST `/v2/runAgents` with user input (see runner.py for request model).

2. **Generate voice**:
   - POST `/v2/getVoice` with text or script.

3. **Update Google Sheet**:
   - POST `/v2/sendToGoogleSheet` with formatted data.

4. **Upload to Drive**:
   - POST `/v2/storeToDrive` with file paths.
