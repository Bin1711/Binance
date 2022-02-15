import numpy as np
import torch 
import torch.nn as nn 
import torch.nn.functional as F
import attention
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
    def __init__(self, num_inputs, num_output, *args, **kwargs):
        super(ActorCritic, self).__init__()
        self.as_super = super(ActorCritic, self)
        self.as_super.__init__(*args, **kwargs)

        #define layers, page 12 in paper

        self.conv1 = nn.Conv2d(16, 8, 1, stride = 2)
        self.conv2 = nn.Conv2d(16, 5, 1, stride = 4)

        self.fc1 = nn.Linear(944, num_output)

        self.self_attention_encoder = attention.SelfAttentionEncoderLayer(...)

        self.critic_linear = nn.Linear(...)
        self.actor_linear = nn.Linear(...)
        self.actor_softmax = nn.Softmax()

        self.apply(weights_init) # initilizing the weights of the model with random weights
        
        self.actor_linear.bias.data.fill_(0) # initializing the actor bias with zeros
        self.critic_linear.bias.data.fill_(0) # initializing the critic bias with zeros

    def forward(self, inputs):
        x = F.elu(self.conv1(inputs))
        x = F.elu(self.conv2(x))
        x = F.elu(self.conv3(x))
        x = self.self_attention_encoder(x)
        x = self.self_attention_encoder(x)
        x = self.self_attention_encoder(x)
        act = self.actor_linear(x)
        act = self.actor_softmax(act)
        value = self.critic_linear(x)
        return act, value 