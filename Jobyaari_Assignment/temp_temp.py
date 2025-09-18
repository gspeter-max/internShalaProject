# # import requests 

# # headers = {
# #         "Content-Type": "application/json"
# #     }

# # json_data = {
# #     "user_prompt": f"generate video for ai and machine learning ",
# #     "voice_id": 'bIHbv24MWmeRgasZH58o',
# #     "video_name": f'video1' 
# # }

# # response = requests.post(
# #     'http://127.0.0.1:8000/v2/getFullVideo' ,
# #     headers = headers,
# #     json = json_data   
# #     )

# import Pexels
# from Pexels import Client 

# client = Client( token  = 'cJdOJotlCPiPpwTm9qfsio8kcWjkOkv1dH6YVvrhrhVzJZM6RA9YOrk6')
# response = client.search_photos(
#     query= 'job notification from google',
#     size = 'medium'
# )
# return print(response.photos[0].src.original)