# Yardstick Assignment — Key Features & Technology Summary

This document summarizes the main technologies and features added to the `Yardstick_Assignment` module as part of the assignment.

---

## 🛠️ Technologies Used

- **FastAPI**:  
  High-performance API framework for building web services in Python.

- **Pydantic**:  
  Data validation and settings management using Python type hints.

- **Groq API**:  
  Used for LLM (Large Language Model) chat completions and text summarization.

- **Transformers** ( this code is committed ):  
  (Commented out) For tokenization and model loading from Hugging Face.

---

## 🚀 Key Features Implemented

- **API Endpoints with FastAPI**:
  - `/v2/getResponse`: Accepts user queries and returns AI-generated responses using Groq.
  - (Commented) `/v1/loginPage`: Handles authentication with Hugging Face tokens.

- **Request Data Validation**:
  - Used `Pydantic` models to validate and structure incoming API data.

- **Conversation Summarization**:
  - Custom logic to summarize conversation history for efficient context handling.
  - Summarization triggered when message/token count exceeds a limit.

- **Token Management**:
  - Tracks and limits token usage across messages to ensure boundaries are respected.

- **Support for LLM Integration**:
  - Integrates Groq’s API for generating responses and summaries.

---

## 💡 Example Code Snippets

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatCompletionMessageParam(BaseModel):
    role: str
    content: str
    GroqApiKey: str
    care_about_task2: bool

@app.post('/v2/getResponse')
async def get_response(userquery: ChatCompletionMessageParam):
    # LLM logic here
```

---

## 📂 Additional Notes

- The code is modular and ready for extension with additional endpoints or models.
- Some advanced features (like tokenization with Hugging Face) are commented for future use.
- All main logic is located in `getResponse.py` and `__init__.py`.

---

## 🔗 References

- [Yardstick_Assignment folder on GitHub](https://github.com/gspeter-max/internShalaProject/tree/253f73e0e76c661baf3776221aa47d1e8ee9fbad/Yardstick_Assignment)
