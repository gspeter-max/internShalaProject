from pygsheets import authorize 
import json
from fastapi import APIRouter
from pydantic import BaseModel 
import typing 

googleSheetRouter = APIRouter() 

class __update_sheet_output( BaseModel ):
    response : str 

class  __update_sheet_input( BaseModel ):
    data : typing.List[typing.List]


@googleSheetRouter.post('/v2/sendToGoogleSheet', response_model = __update_sheet_output)
def update_sheet( data : __update_sheet_input):

    try:
        client = authorize( service_account_file = 'quantum-toolbox-446207-v3-a291551572f4.json' )
        sheet = client.open('sheet')
        working_sheet = sheet.worksheet_by_title('workingsheet')

        working_sheet.update_values(crange= 'A1', values = data )
        cells = working_sheet.range('1:1', returnas = 'cells')[0]

        for cell in cells:
            cell.set_text_format('bold', True)


        colors_cells = working_sheet.range('B:B', returnas = 'cells')
        print(colors_cells)
        for cell in colors_cells:
            cell = cell[0]
            if cell.value == '':
                break 
            status_value = cell.value 

            COLOR_GREEN = (0.8, 0.9, 0.8, 1)
            COLOR_RED = (0.9, 0.8, 0.8, 1)
            COLOR_PURPLE = (0.85, 0.8, 0.9, 1)
            COLOR_WHITE = (1, 1, 1, 1) 

            print(f"Status is '{status_value}'. Applying color...")


            if status_value.lower().strip() == 'post live':
                cell.color = COLOR_GREEN
                
            elif status_value == 'Run GPT-1':
                cell.color = COLOR_RED

            elif status_value == 'GPT Updated':
                cell.color = COLOR_PURPLE

            else:
                cell.color = COLOR_WHITE
            
        
        return  {'response': "data is correctly sended to the google sheet"} 
        
    except Exception as e:
        return  {"response": {"error": f"get an error during send data to google sheet  due to : {e}"}}