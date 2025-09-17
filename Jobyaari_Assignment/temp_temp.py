import requests 

headers = {
        "Content-Type": "application/json"
    }

json_data = {
    "user_prompt": f"generate video for ai and machine learning ",
    "voice_id": 'bIHbv24MWmeRgasZH58o',
    "video_name": f'video1' 
}

response = requests.post(
    'http://127.0.0.1:8000/v2/getFullVideo' ,
    headers = headers,
    json = json_data   
    )