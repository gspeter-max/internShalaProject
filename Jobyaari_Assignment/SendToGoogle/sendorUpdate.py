from pygsheets import authorize 
import json
import subprocess 
from fastapi import APIRouter
import inspect
from pydantic import BaseModel 
from pathlib import Path 
import typing 
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

google_send_router  = APIRouter() 

class __update_sheet_output( BaseModel ):
    response : str 

class  __update_sheet_input( BaseModel ):
    data : typing.List[typing.List]


@google_send_router.post('/v2/sendToGoogleSheet', response_model = __update_sheet_output)
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

class __sendDrive_output( BaseModel ):
    response : typing.Dict[str, typing.Union[typing.List, str]]

class __sendDrive_input( BaseModel ):
    fileStoredPath : typing.List[str]

@google_send_router.post( '/v2/storeToDrive', response_model= __sendDrive_output)
def sendDrive(userInput : __sendDrive_input ):

    try:
        file_links = []

        file_path = Path(__file__).resolve().parent 
        full_path_of_secrets = file_path / "client_secrets.json"
        full_path_of_credentials = file_path / "credentials.json"

        auth = GoogleAuth()
        auth.LoadClientConfigFile(client_config_file= str(full_path_of_secrets ) )
        auth.LoadCredentialsFile(credentials_file= str( full_path_of_credentials))
        auth.LocalWebserverAuth()
        my_drive = GoogleDrive( auth ) 

        

        all_files = my_drive.ListFile({'q': '"root" in parents and  trashed = False'}).GetList()
        for files in all_files:
            files.Delete()

        for index, file_path in enumerate(userInput.fileStoredPath):
            fileType = file_path.split('.')[-1]
            created_file = my_drive.CreateFile({'title': f"file_{index}.{fileType}"})

            created_file.SetContentFile(file_path)
            created_file.Upload() 
            created_file.InsertPermission(
                    {
                        "type": "anyone",
                        "value" : "anyone",
                        "role" : "reader"
                        }
                    )
            file_list = my_drive.ListFile( {'q': f"title = 'file_{index}.{fileType}' and trashed = False"}).GetList() 

            if file_list:
                public_link = file_list[0]['alternateLink']
                file_links.append( public_link )
                subprocess.call( f'rm -rf {file_path}')

            else:
                file_links.append('None')

        return {"response" : {"file_links" : file_links , "status" : " Ok "}}

    except Exception as e:
        return {"response" : {"error" : e, "file_links" : [] , "status" : "failed"}}

