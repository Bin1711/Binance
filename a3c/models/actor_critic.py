import numpy as np
import torch 
import torch.nn as nn 
import torch.nn.functional as F
from models import attention
# Initializing the weights of the neural network in an optimal way for the learning
def weights_init(m):
    classname = m.__class__.__name__ # python trick that will look for the type of connection in the object "m" (convolution or full connection)
    if classname.find('Linear') != -1: # if the connection is a full connection
        weight_shape = list(m.weight.data.size()) # list containing the shape of the weights in the object "m"
        fan_in = weight_shape[1] # dim1
        fan_out = weight_shape[0] # dim0
        w_bound = np.sqrt(6. / (fan_in + fan_out)) # weight bound
        m.weight.data.uniform_(-w_bound, w_bound) # generating some random weights of order inversely proportional to the size of the tensor of weights
        m.bias.data.fill_(0) # initializing all the bias with zeros


class ActorCritic(torch.nn.Module):
    def __init__(self, params, *args, **kwargs):
        super(ActorCritic, self).__init__()
        self.as_super = super(ActorCritic, self)
        self.as_super.__init__(*args, **kwargs)
        self.params = params
        
        num_features = params.num_features #6: open, high, low, close, volume, VWAP
        num_assets = params.num_assets
        window = params.window 
        
        num_extracted_features = params.num_extracted_features #16
        conv1_kernel, conv1_stride = params.conv1 # (8, 1), 4
        conv2_kernel, conv2_stride = params.conv2 # (5, 1), 2
        
        dim_model = params.dim_model # 400
        dim_inner_hidden = params.dim_inner_hidden # 400
        
        qty_head = params.qty_head # 8
        dim_k = params.dim_k
        dim_v = params.dim_v
        
        dropout = params.dropout # 0.1
        attn_dropout = params.attn_dropout # 0.1
        
        #define layers, page 12 in paper
        self.conv1 = nn.Conv2d(num_features, num_extracted_features, conv1_kernel, stride = conv1_stride)
        self.conv2 = nn.Conv2d(num_extracted_features, num_extracted_features, conv2_kernel, stride = conv2_stride)
        
        # create temp_X and run through conv layers to defind the shape for fc1
        temp_X = torch.randn(1, num_features, window, num_features)
        temp_X = self.conv1(temp_X)
        temp_X = self.conv2(temp_X)
        flatten_length = len(temp_X.flatten())
        
        self.fc1 = nn.Linear(flatten_length, dim_model)
        
        self.self_attention_encoder1 = attention.SelfAttentionEncoderLayer(dim_model, dim_inner_hidden, qty_head, dim_k, dim_v, dropout, attn_dropout)
        self.self_attention_encoder2 = attention.SelfAttentionEncoderLayer(dim_model, dim_inner_hidden, qty_head, dim_k, dim_v, dropout, attn_dropout)
        self.self_attention_encoder3 = attention.SelfAttentionEncoderLayer(dim_model, dim_inner_hidden, qty_head, dim_k, dim_v, dropout, attn_dropout)

        self.critic_linear = nn.Linear(num_assets*dim_model, num_assets)
        self.actor_linear = nn.Linear(num_assets*dim_model, num_assets)
        self.actor_softmax = nn.Softmax()

        self.apply(weights_init) # initilizing the weights of the model with random weights
        
        self.actor_linear.bias.data.fill_(0) # initializing the actor bias with zeros
        self.critic_linear.bias.data.fill_(0) # initializing the critic bias with zeros

    def forward(self, inputs):
        # inputs.shape = (num_assets, window, features)
        extracted_features = []
        for i in range(inputs.shape[0]):
            x = inputs[i] # x.shape = (window, features)
            x = x.repeat(x.shape[1], 1, 1) # (window, features) -> (features, window, features) |||| (channel_in = features)
            x = F.elu(self.conv1(x.unsqueeze(0))) # (batch, channel_out, H_out, W_out)
            x = F.elu(self.conv2(x)) # (batch, channel_out, H_out, W_out)
            x = self.fc1(x.flatten()) # dim_model
            extracted_features.append(x.flatten())
            
        extracted_features = torch.tensor(extracted_features).unsqueeze(0) # (batch, num_assets, dim_model)
        
        x, attention = self.self_attention_encoder1(extracted_features)
        x, attention = self.self_attention_encoder2(x)
        x, attention = self.self_attention_encoder3(x)
        
        act = self.actor_linear(x.flatten())
        act = self.actor_softmax(act)
        value = self.critic_linear(x.flatten())
        return act, value 