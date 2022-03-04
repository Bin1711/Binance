import yaml
from datetime import datetime
from dateutil.relativedelta import relativedelta

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('env.py'))))
from get_data import get_data

class Params():
    def __init__(self, file_path = 'hyperparams.yaml'):
        with open('hyperparams.yaml') as file:
            hyperparams = yaml.full_load(file)
        
        self.hyperparams = hyperparams
        
        self.syms = hyperparams['syms']
        self.num_assets = len(self.syms)
        
        self.num_features = 6 #open, high, low, close, volume, VWAP
        self.window = hyperparams['window']
        
        self.freq = hyperparams['frequency']
        
        self.num_extracted_features = hyperparams['num_extracted_features']
        
        self.conv1 = hyperparams['conv1']
        self.conv2 = hyperparams['conv2']
        
        self.dim_model = hyperparams['dim_model']
        self.dim_inner_hidden = hyperparams['dim_inner_hidden']
        
        self.qty_head = hyperparams['qty_head']
        self.dim_k = hyperparams['dim_k']
        self.dim_v = hyperparams['dim_v']
        
        self.dropout = hyperparams['dropout']
        self.attn_dropout = hyperparams['attn_dropout']
        
        self.start_time = datetime.now()
        days, hours, minutes = hyperparams['time_budget']
        self.end_time = self.start_time + relativedelta(days = days, hours = hours, minutes=minutes)
        
        self.start_date = hyperparams['start_date']
        
        self.data = get_data(self.syms, self.freq, self.start_date)
    
    def reset_time(self):
        self.start_time = datetime.now()
        days, hours, minutes = self.hyperparams['time_budget']
        self.end_time = self.start_time + relativedelta(days = days, hours = hours, minutes=minutes)
        