
import base64
from datetime import datetime
import os
import subprocess
import typing
from io import BytesIO
import google 
from  google import genai 
import requests
from crewai import LLM
from crewai.tools import BaseTool
from PIL import Image
from pydantic import BaseModel, Field


latest_text_sended = [] 
class TerminalCommandInput(BaseModel):
    """Input for the PromptToTerminalCommandTool. Specifies the natural language instruction."""
    prompt: str = Field(..., description="A clear, natural language instruction to be converted into a single, executable shell command. For example: 'List all files in the current directory including hidden ones'.")

class ExecutionInput(BaseModel):
    """Input for the TerminalCodeExecutor tool. Specifies the commands to run."""
    commands: typing.List[str] = Field(..., description="A list of one or more valid shell command strings to execute sequentially. These should typically be the direct output from the PromptToTerminalCommandTool.")

class ImageGeneratorInput(BaseModel):
    """Input for the ImageGenerationTool. Describes the desired visual asset."""
    prompt: str = Field(
        ...,
        description=(
            "A hyper-detailed, multi-sentence description for the image generation AI. To maximize quality, provide a complete scene specification. "
            "Structure your prompt with these elements: "
            "1. **SUBJECT:** The core concept (e.g., 'A professional bar chart'). "
            "2. **CONTEXT:** What the subject is doing or showing (e.g., 'comparing Q1 vs Q2 revenue for Project X'). "
            "3. **DETAILS:** Specific labels, data points, or elements to include (e.g., 'with clearly labeled axes for 'Revenue in USD' and 'Quarter', showing Q1 at $50k and Q2 at $85k'). "
            "4. **STYLE:** The artistic direction (e.g., 'in a minimalist, clean, corporate style, photorealistic'). "
            "5. **COMPOSITION & COLOR:** The layout and palette (e.g., 'eye-level view, using a professional blue and dark gray color palette')."
        )
    )
    generation_provider: typing.Literal['stabilityai', 'google-gemini', 'huggingface-model'] = Field(
        'google-gemini',
        description=(
            "Specifies which backend AI model service to use for image generation. This is a critical parameter for ensuring task success. "
            "AGENT STRATEGY: If a generation attempt fails (e.g., due to rate limits, content policies, or a temporary outage), your immediate next action should be to re-run this tool with the exact same 'prompt' but selecting a different 'generation_provider' from the available list."
        )
    )

class SendTextInTelegramInput(BaseModel):
    """Input for the SendTextInTelegramChannel tool."""
    Content: str = Field(..., desrcription="The complete and final text message content to be sent to the Telegram channel. This should be a polished piece of information, like a summary or report.")

class WriteFileAndCreateInput(BaseModel):
    """Input for the WriteFileAndCreateTool. Defines the file's name, format, and content."""
    content: str = Field(..., description="The string content to be written into the file.")
    file_name: str = Field(..., description="The base name of the file, without the extension. E.g., 'research_notes'.")
    file_format: str = Field(..., description="The file extension, without the dot. E.g., 'md', 'txt', 'json'.")

class ReadFileAndSummarizeInput(BaseModel):
    """Input for the ReadFileAndSummarizeTool. Specifies the file to be read and understood."""
    file_name: str = Field(..., description="The base name of the file to read, without the extension. E.g., 'research_notes'.")
    file_format: str = Field(..., description="The file extension, without the dot. E.g., 'md', 'txt', 'png'.")

class SendImageInTelegramInput(BaseModel):
    """
    Input for the SendImageInTelegramChannel tool.
    This tool is designed to be parameter-less as its function is fixed: find and send 'image.png'.
    """
    pass # No arguments are needed as the tool has a single, predetermined function.

# --- Tool Definitions: The Agent's Capabilities ---

class getCurrentTime(BaseTool):
    """A tool to get the current system time in a standardized format."""
    name: str = "getCurrentTime"
    description: str = "Returns the current date and time in ISO 8601 format. Use this to timestamp reports or to fetch information relevant to the present moment."

    async def _run(self) -> str:
        """Fetches the current time and returns it as a string."""
        try:
            return datetime.now().isoformat()
        except Exception as e:
            return f"Error fetching current time: {e}"

class getPreviousSentContent(BaseTool):
    """A short-term memory tool to check recently sent messages."""
    name: str = 'getPreviousSentContent'
    description: str = (
        "Retrieves the latest text messages received on your Telegram during the current run. "
        "This tool ensures agents only capture new messages (avoiding duplicates) and enables "
        "seamless continuity by allowing them to reference or build upon prior user inputs. "
        "Ideal for workflows where agents must stay synchronized with real-time user updates "
        "while maintaining conversation state."
    )
    async def _run(self) -> str:
        """Returns the list of recently sent messages."""
        global latest_text_sended
        if not latest_text_sended:
            return "No text content has been sent yet in this session."
        return f"Previously sent content in this session: {str(latest_text_sended)}. AGENT ACTION: Use this information to ensure your next message is new and relevant."


class WriteFileAndCreateTool( BaseTool ):
    name : str = "WriteFileAndCreateTool"
    description: str = "Creates a new file with a specified name and format, and writes string content into it. Essential for saving research, notes, or structured data for later use by other agents."

    args_schema : typing.Optional[BaseTool] = WriteFileAndCreateInput

    async def _run( self, content : str , file_name : str , file_format : str ):
        if isinstance( content , bytes):
            file_read_format = 'wb'
        else:
            file_read_format = 'w'

        try:
            with open(f'./{file_name}.{file_format}', file_read_format) as f:
                f.write(content ) 
            return f'{file_name}.{file_format} is created and content writing is complete and save at ./{file_name}.{file_format}'
        
        except Exception as e:
            return f'{file_name}.{file_format} file creation is failed with error : {e}'
            


class ReadFileAndSummarizeTool( BaseTool ):
    name : str = 'ReadFileAndSummarizeTool'
    description: str = "Reads the content of a specified file (text or image) and uses a multimodal AI to generate a concise summary of its contents. Perfect for understanding data saved by other agents."
    args_schema : typing.Optional[ BaseModel ] = ReadFileAndSummarizeInput

    async def _run( self, file_name : str , file_format : str ):
        
        try: 
            client = google.genai.Client( api_key = os.environ.get('GOOGLE_API_KEY',))
            
            with open(f'{file_name}.{file_format}', 'rb') as f:
                image_data = f.read()

            mime_type = f'image/{file_format}' if file_format in ['png', 'jpeg', 'jpg'] else 'text/plain'
            content = google.genai.types.Part.from_bytes(
                data = image_data ,
                mime_type = mime_type
            )

            content_config= google.genai.types.GenerateContentConfig(
            thinkingConfig= google.genai.types.ThinkingConfig(
                includeThoughts = False,
                thinkingBudget = 2000
            )

            )
            response = client.models.generate_content(
            model = 'gemini-1.5-pro',
            contents = [content,"Summarize the content of this file."],
            config = content_config
            )

            return response.text 
        except Exception as e:
            return f'RealFileAndSummarizeTool is failed due to this error : {e}'


class ConvertPromptToTerminalCommand(BaseTool):
    """
    ## Natural Language to Shell Command Interpreter

    **Purpose & Use Case:**
    This tool is the agent's interface to the command line. It translates a high-level goal (e.g., "Check the available disk space") into the precise syntax a computer understands (e.g., `df -h`). It should be the *first* step in any workflow that requires system interaction.

    **Workflow Integration:**
    This tool is a producer. Its output, a clean command string, is designed to be passed *directly* into the `commands` argument of the `TerminalCodeExecutor` tool.
    """
    name: str = 'PromptToTerminalCommandTool'
    description: str = (
        "Translates a natural-language instruction into a valid, single-line shell command. "
        "Use this as the first step for any task requiring system operations. "
        "CRITICAL: The tool returns ONLY the command string, with no extra explanations or formatting."
    )
    args_schema: typing.Type[BaseModel] = TerminalCommandInput

    async def _run(self, prompt: str) -> str:
        """
        Takes a natural language prompt and uses an LLM to generate a shell command.

        Args:
            prompt: The natural language instruction from the agent.

        Returns:
            A string containing the generated shell command, ready for execution.
        """
        # --- The core logic for selecting an LLM remains unchanged ---
        
        try:
            llm = LLM(
                    model='gemini/gemini-1.5-pro',
                    api_key=os.environ.get('GOOGLE_API_KEY', None)
                ) 
        except Exception as e:
            try:
                llm = LLM(
                    model="meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8",
                    temperature=0.8,
                    stop=["END"],
                    seed=42,
                    api_key = os.environ.get('LLAMA_API_KEY', None)
                )
            except Exception as e:
                try:
                    llm = LLM(
                        model="anthropic/claude-3-sonnet-20240229-v1:0",
                        temperature=0.7,
                        api_key = os.environ.get('ANTHROPIC_API_KEY', None)
                    )
                except Exception as e:
                    try:
                        llm = LLM(
                            model="mistral/mistral-large-latest",
                            temperature=0.7,
                            api_key= os.environ.get('MISTRAL_API_KEY', None)
                        )
                    except Exception as e:
                        try:
                            llm = LLM(
                                model="nvidia_nim/meta/llama3-70b-instruct",
                                temperature=0.7,
                                api_key = os.environ.get('NVIDIA_API_KEY', None)
                            )
                        except Exception as e:
                            return f'Error: Unable to load any LLM for command generation. Details: {e}'

        response = llm.call(
            messages=f'''You are an expert shell command generator. Your sole task is to convert the user's request into a single, valid shell command.
                Return ONLY the raw command. Do not add explanations, markdown backticks, or any other text.
                Request: "{prompt}"'''
        )
        return response.strip()

class TerminalExecution(BaseTool):
    """
    ## Secure Shell Command Executor

    **Purpose & Use Case:**
    This tool provides a controlled and observable environment for an agent to interact with the operating system. It executes commands and captures all output (both standard and error), giving the agent complete feedback on the result of its actions.

    **Workflow Integration:**
    This tool is a consumer. It takes the command string generated by `PromptToTerminalCommandTool` and runs it. The agent must then analyze the output (stdout/stderr) to understand the system's state and determine its next action.
    """
    name: str = "TerminalCodeExecutor"
    description: str = (
        "Executes a list of shell commands directly in the system terminal and returns their complete output. "
        "This tool is essential for any task requiring direct system interaction, file manipulation, or data gathering from the OS."
    )
    args_schema: typing.Type[BaseModel] = ExecutionInput

    async def _run(self, commands: typing.List[str]) -> str:
        """
        Executes a list of shell commands and returns their collected output.

        Args:
            commands: A list of command strings to execute.

        Returns:
            A string representation of a list, where each item is the stdout or stderr for a command, providing a complete execution log.
        """
        OutputList = []
        for cmd in commands:
            try:
                process_output = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
                if process_output.stderr:
                    OutputList.append(f"Command '{cmd}' resulted in an ERROR: {process_output.stderr.strip()}")
                else:
                    OutputList.append(process_output.stdout.strip())
            except Exception as e:
                OutputList.append(f"CRITICAL FAILURE executing command '{cmd}': {e}")
        return str(OutputList)

class ImageGenerationTool(BaseTool):
    """
    ## AI-Powered Visual Asset Generator

    **Purpose & Use Case:**
    Creates high-quality images, charts, diagrams, or illustrations from a detailed text description. An agent should use this tool when a task's final output requires a visual component to convey information more effectively.

    **Workflow Integration:**
    This tool is a producer with a side effect: it creates a file named `image.png` in the current directory. This action is a *mandatory prerequisite* for using the `SendImageInTelegramChannel` tool.
    """
    name: str = 'ImageGenerationTool'
    description: str = (
        "Generates a visual asset (like a chart or diagram) from a detailed text prompt and saves it to a local file named 'image.png'. "
        "This tool MUST be called and must succeed before you can use the 'SendImageInTelegramChannel' tool."
    )
    args_schema: typing.Type[BaseModel] = ImageGeneratorInput

    async def _run(self, prompt: str, generation_provider: str = 'google-gemini') -> str:
        """
        Generates an image based on the prompt and selected provider, saving it to './image.png'.

        Args:
            prompt: A detailed, descriptive prompt for the image to be generated.
            generation_provider: The backend service to use for generation.

        Returns:
            A confirmation message indicating success and the file path, or an instructional error message on failure.
        """
        image_path = './image.png'
        
        if generation_provider.lower() == 'stabilityai':
            # --- Logic remains unchanged ---
            url = 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image'
            headers = {'Authorization': 'Bearer YOUR_STABILITY_API_KEY', "Content-Type": 'application/json'} # Note: Hardcoded key is not ideal
            json_data = {'text_prompts': [{'text': prompt}], 'samples': 1, 'steps': 50}
            try:
                response = requests.post(url=url, headers=headers, json=json_data)
                response.raise_for_status()
                response_baset64 = response.json()['artifacts'][0]['base64']
                image_data = base64.b64decode(response_baset64)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                return f"SUCCESS: Image generation complete. File saved to '{image_path}'. You may now proceed with the 'SendImageInTelegramChannel' tool."
            except Exception as e:
                return f"ERROR: StabilityAI generation failed: {e}. AGENT ACTION: Retry this task using a different 'generation_provider' like 'google-gemini'."

        if generation_provider.lower() == 'google-gemini':
            # --- Logic remains unchanged ---
            try:
                client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])
                response = client.models.generate_content(model='gemini-2.0-flash-preview-image-generation', contents=prompt, config=genai.types.GenerateContentConfig(responseModalities=['IMAGE', 'TEXT']))
                img_data = next((part.inline_data.data for part in response.candidates[0].content.parts if part.inline_data), None)
                if img_data is None:
                    return "ERROR: Google Gemini generation failed: No image data was returned by the API. AGENT ACTION: Retry this task using a different 'generation_provider'."
                img = Image.open(BytesIO(img_data))
                img.save(image_path)
                return f"SUCCESS: Image generated and saved to '{image_path}'. You can now use the 'SendImageInTelegramChannel' tool to dispatch it."
            except Exception as e:
                return f"ERROR: Google Gemini generation failed: {e}. AGENT ACTION: Retry this task using a different 'generation_provider' like 'stabilityai'."
        
        if generation_provider.lower() == 'huggingface-model':
            return "ERROR: The 'huggingface-model' provider is not yet implemented. AGENT ACTION: Please select either 'stabilityai' or 'google-gemini'."

        return f"ERROR: Invalid 'generation_provider' specified. AGENT ACTION: Please choose from the available options."

class SendTextInTelegramChannel(BaseTool):
    """
    ## Telegram Text Message Dispatcher

    **Purpose & Use Case:**
    This is a final delivery tool for text-based outputs. An agent uses this to transmit its final findings, summaries, or reports to the designated Telegram channel for human review.

    **Workflow Integration:**
    This tool is a consumer of text. It typically runs at the *end* of a task chain, after an agent has formulated its complete, final answer.
    """
    name: str = 'SendTextInTelegramChannel'
    description: str = "Sends a final, polished text message to the configured Telegram channel. Use this for delivering all text-based reports and summaries."
    args_schema: typing.Type[BaseModel] = SendTextInTelegramInput
    bot_api_key: str = os.environ.get('bot_api_key')
    chat_id: str = os.environ.get('telegram_chat_id')

    async def _run(self, Content: str) -> str:
        """
        Sends a given text string to the configured Telegram channel via HTTP POST request.

        Args:
            Content: The message text to be sent.

        Returns:
            A string indicating the result of the API call, including the HTTP status code for confirmation.
        """
        if not self.bot_api_key or not self.chat_id:
            return "Error: Cannot send message. Telegram 'bot_api_key' or 'telegram_chat_id' is not configured in the environment."
        
        try:
            post_url = f'https://api.telegram.org/bot{self.bot_api_key}/sendMessage'
            data = {'chat_id': self.chat_id, 'text': Content}
            response = requests.post(post_url, data=data)
            global latest_text_sended
            latest_text_sended.append(Content)

            return f"Delivery Confirmation: Telegram API responded with status {response.status_code}. Response body: {response.text}"
        except Exception as e:
            return f'SendTextInTelegramChannel is failed due to error : {e}'

class SendImageInTelegramChannel(BaseTool):
    """
    ## Telegram Image Dispatcher

    **Purpose & Use Case:**
    This is a final delivery tool for visual content. An agent should use this tool *only after* the `ImageGenerationTool` has successfully created the `image.png` file.

    **Workflow Integration:**
    This tool is a consumer of a file. It acts as the second, final part of a two-step "generate then send" process. It requires no arguments because its target file is always `image.png` in the current directory.
    """
    name: str = 'SendImageInTelegramChannel'
    description: str = "Finds the 'image.png' file in the current directory and sends it to the configured Telegram channel. CRITICAL: The 'ImageGenerationTool' must be used successfully immediately before calling this tool."
    args_schema: typing.Type[BaseModel] = SendImageInTelegramInput
    bot_api_key: str = os.environ.get('bot_api_key')
    chat_id: str = os.environ.get('telegram_chat_id')

    async def _run(self) -> str:
        """
        Finds 'image.png', loads it, and sends it as a photo to the configured Telegram channel.

        Returns:
            A string indicating the result of the API call, or an error if the file is missing.
        """
        if not self.bot_api_key or not self.chat_id:
            return "Error: Cannot send image. Telegram 'bot_api_key' or 'telegram_chat_id' is not configured in the environment."
        image_path = './image.png'
        if not os.path.exists(image_path):
            return "CRITICAL ERROR: File 'image.png' not found. You must run the 'ImageGenerationTool' immediately before this step to create the file."
        post_url = f'https://api.telegram.org/bot{self.bot_api_key}/sendPhoto'
        try:
            with open(image_path, 'rb') as img_file:
                files = {'photo': img_file}
                data = {'chat_id': self.chat_id}
                response = requests.post(post_url, files=files, data=data)
            return f"Delivery Confirmation: Telegram API responded with status {response.status_code}. Response body: {response.text}"
        except Exception as e:
            return f"An unexpected error occurred while sending the image: {e}"

class getUpdateFromUser( BaseTool ):
    name : str = 'getUpdateFromUser'
    description: str = (
        "Fetches the most recent user update from a connected Telegram channel or chat. "
        "This tool connects to the Telegram Bot API using the configured `bot_api_key`, "
        "retrieves the latest message/update every time it is called (e.g., every 20s in a loop), "
        "and returns the text content of the last user message or channel post. "
        "Agents should use this tool whenever they need to continuously monitor Telegram for "
        "new instructions, commands, or updates provided by the user in real time."
    )

    async def _run(self):
        try:
            url = f"https://api_telegram.org/bot{os.environ.get('bot_api_key','<bot_api_key>')}/getUpdates"
            response = requests.get(url)
            json_response = response.json()

            actual_user_input = '' 
            for index, user_input in enumerate(reversed(json_response['result'])):
                if index > 3:
                    break 
                actual_user_input += user_input['channel_post']['text']

            return f'latest user udpate : {actual_user_input}'

        except Exception as e:
            return f'getUpdateFromUser Tool is failed due to error : {e}'

            