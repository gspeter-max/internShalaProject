from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 

auth = GoogleAuth('settings.yaml') 
auth.LocalWebserverAuth()
my_drive = GoogleDrive( auth ) 

all_files = my_drive.ListFile({'q': '"root" in parents and  trashed = False'}).GetList()
for files in all_files:
    files.Delete()

created_file = my_drive.CreateFile({'title': "video.mp4"})
created_file.SetContentFile('final_video.mp4')

created_file.Upload() 

created_file.InsertPermission(
        {
            "type": "anyone",
            "value" : "anyone",
            "role" : "reader"
            }
        ) 

print("========")
print( my_drive.ListFile())
print('=======')
file_list = my_drive.ListFile( {'q': "title = 'video.mp4' and trashed = False"}).GetList() 

if file_list:
    public_link = file_list[0]['alternateLink']
    print( f' link : {public_link}') 

else:
    print('file is not found') 


