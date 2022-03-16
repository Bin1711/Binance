import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('upload_alpha.py'))))

from toolss import gdrive

folder_name = 'Alpha'
alpha_name = 'alpha_002.pkl'
path_to_alpha = 'alpha/shared_model.pkl'

folders = gdrive.drive.ListFile(
    {'q': "title='" + folder_name + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
for folder in folders:
    if folder['title'] == folder_name:
        file2 = gdrive.drive.CreateFile({'parents': [{'id': folder['id']}],
                                         'title': alpha_name})
        file2.SetContentFile(path_to_alpha)
        file2.Upload()
        print('Alpha uploaded')