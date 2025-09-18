from fastapi import APIRouter
from Jobyaari_Assignment.SendToGoogle.scrapeData import getResponse  
from pydantic import BaseModel 
import typing
from Jobyaari_Assignment.agents import generate_data_for_sheet, __generate_data_for_sheet_input

runnerRouter = APIRouter() 

kw_list = ['admit card releases', 'job notifications', 'results']
class __getResponse_input( BaseModel):
        kw_list: list[str]
class __getResponse_output( BaseModel):
        response : typing.Dict[str, typing.Any]

@runnerRouter.post("/v2/runAgents", response_model = __getResponse_output )
async def _getResponse( userInput : __getResponse_input ):
    # raw_data = getResponse(kw_list = userInput.kw_list )
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
        '''
    generate_data_for_sheet_input = __generate_data_for_sheet_input(raw_content= raw_data)
    sheet_data = await generate_data_for_sheet( generate_data_for_sheet_input )
    return {"response" : {"content": sheet_data['response']['content']}}

    
