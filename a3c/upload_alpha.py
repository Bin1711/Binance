import numpy as np
import torch
import torch.nn.functional as F
import pickle
import dill
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('upload_alpha.py'))))
from toolss import gdrive

class Alpha():
    def __init__(self, shared_model):
        self.model = shared_model
        
        self.syms = shared_model.params.syms
        self.window = shared_model.params.window
        self.frequency = shared_model.params.freq
    
    def _get_state(self, data):
        states = []
        for i, sym in enumerate(self.syms):
            df = data[sym]
            assert df.shape == (self.window, 6)
            df = df.values
            df = df/df.max(axis=0) #(df - df.mean(axis=0)) / df.std(axis=0)
            states.append(df)
        
        self.state = torch.from_numpy(np.array(states))
    
    def allocate(self, data):
        self._get_state(data)
        n = 100
        action, mu, var, value = self.model.act(self.state)
        for _ in range(n):
            action, mu, var, value = self.model.act(self.state)
            action += action
        action /= (n+1)
        
        action = F.softmax(action, dim = 0)
        #action = F.normalize(action, p = 1, dim = 0)
        action = action.numpy()
        
        allocation = {}
        for i, sym in enumerate(self.syms):
            allocation[sym] = action[i]
        return allocation


folder_name = 'Alpha' #name of folder on drive
alpha_name = 'alpha_005.pkl' # name of alpha on drive
path_to_model = 'alpha/shared_model.pkl'
path_to_alpha = 'alpha/' + alpha_name

# read object model
with open(path_to_model, 'rb') as f:
    shared_model = pickle.load(f)

# create object alpha
alpha = Alpha(shared_model)

# save object alpha
with open(path_to_alpha, 'wb') as f:
    dill.dump(alpha, f)

# upload object alpha to drive
folders = gdrive.drive.ListFile(
    {'q': "title='" + folder_name + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
for folder in folders:
    if folder['title'] == folder_name:
        file2 = gdrive.drive.CreateFile({'parents': [{'id': folder['id']}],
                                         'title': alpha_name})
        file2.SetContentFile(path_to_alpha)
        file2.Upload()
        print('Alpha uploaded')