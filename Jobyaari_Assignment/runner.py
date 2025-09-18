from fastapi import APIRouter
from Jobyaari_Assignment.SendToGoogle.scrapeData import getResponse  
from pydantic import BaseModel 
import typing
import ast 
import numpy as np
from Jobyaari_Assignment.agents import (
    generate_data_for_sheet, 
    __generate_data_for_sheet_input,
    __generate_insta_post_input,
    generate_insta_post,
    __generate_youtube_videos_input,
    generate_youtube_videos,
    content_generation_input,
    gpt1,
    get_thumbnail
)

from Jobyaari_Assignment.SendToGoogle.sendorUpdate import (
    __sendDrive_input,
    sendDrive,
    __update_sheet_input,
    update_sheet
)
runnerRouter = APIRouter() 

kw_list = ['admit card releases', 'job notifications', 'results']
class __getResponse_input( BaseModel):
        kw_list: list[str]
class __getResponse_output( BaseModel):
        response : typing.Dict[str, typing.Any]

@runnerRouter.post("/v2/runAgents", response_model = __getResponse_output )
async def _getResponse( userInput : __getResponse_input ):
    try:
        # raw_data = getResponse(kw_list = userInput.kw_list ) # this is not work ( too many requests error)
        print('default raw data is used for this process ')
        raw_data = ''' [
                "India vs Australia T20",
                "SSC CGL result 2024 tier 2",
                "Jawan movie box office collection",
                "UP Police constable recruitment notification",
                "Chandrayaan 3 update",
                "IBPS Clerk admit card download",
                "Diwali 2024 date",
                "RRB Group D vacancy",
                "State Bank of India job openings",
                "G20 Summit Delhi",
                "UPSC Civil Services exam date"
            ]
            job_keywords = ['result', 'recruitment', 'admit card', 'vacancy', 'job', 'exam', 'notification']    
        #     '''
        print(f"raw data : {raw_data}")
        generate_data_for_sheet_input = __generate_data_for_sheet_input(raw_content= raw_data)
        sheet_data = await generate_data_for_sheet( generate_data_for_sheet_input )
        sheet_data = ast.literal_eval(sheet_data['response']['content'])

        # geting insta content
        _working_array = np.array(sheet_data)
        working_array = _working_array[1:,0].tolist()
        generate_insta_post_input = __generate_insta_post_input( title_data = working_array )
        insta_content = await generate_insta_post( userInput = generate_insta_post_input)
        insta_content = insta_content['content']
        _working_array[1:,6] = insta_content

        # youtube video generation
        generate_youtube_videos_input = __generate_youtube_videos_input( video_topics= working_array )
        youtube_video_path_list = await generate_youtube_videos( userInput = generate_youtube_videos_input )
        youtube_video_path_list = youtube_video_path_list['response']['videos_path']

        # upload in drive 
        sendDrive_input = __sendDrive_input( fileStoredPath= youtube_video_path_list)
        drive_files_link = await sendDrive( userInput = sendDrive_input )
        drive_files_link = drive_files_link['response']['file_links']
        _working_array[1:,4] = drive_files_link

        # generate thumbnail
        thumbnail_input = content_generation_input( topic_titles = working_array )
        thumbnail_paths = await get_thumbnail( userInput = thumbnail_input )
        thumbnail_paths = thumbnail_paths['response']['content']

        # upload in drive 
        sendDrive_input = __sendDrive_input( fileStoredPath= thumbnail_paths)
        drive_files_link = await sendDrive( userInput = sendDrive_input )
        drive_files_link = drive_files_link['response']['file_links']
        _working_array[1:,5] = drive_files_link
        
        # status classification 
        gpt1_input = content_generation_input( topic_titles = working_array )
        status_classification = await gpt1( userInput = gpt1_input )
        status_classification = status_classification['response']['content']
        _working_array[1:,1] = status_classification

        # update in google sheet
        update_sheet_input = __update_sheet_input( sheet_data = _working_array.tolist() )
        sheet_data = await update_sheet( userInput = update_sheet_input )
        sheet_data = sheet_data['response']


        return {"response" : {"content": sheet_data }}
    except Exception as e:
        return {"response" : {"content": [], "error": str(e)}}
    