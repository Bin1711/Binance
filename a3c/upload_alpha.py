import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('upload_alpha.py'))))

from toolss import gdrive

folderName = 'Alpha'  # Please set the folder name.
alphaName = 'alpha_002.pkl'

folders = gdrive.drive.ListFile(
    {'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
for folder in folders:
    if folder['title'] == folderName:
        file2 = gdrive.drive.CreateFile({'parents': [{'id': folder['id']}],
                                         'title': alphaName})
        file2.SetContentFile('alpha/shared_model.pkl')
        file2.Upload()
        print('Alpha uploaded')