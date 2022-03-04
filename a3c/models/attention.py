import numpy as np
import torch 
import torch.nn as nn 
import torch.nn.functional as F

#tham khao o day: https://github.com/yukioichida/self-attention-encoder/blob/master/model.py
class ScaledDotProductAttention(nn.Module):
    ''' Scaled Dot-Product Attention '''

    def __init__(self, dim_model, attn_dropout=0.1):
        # root square of dimension size
        super(ScaledDotProductAttention, self).__init__()
        self.temper = np.power(dim_model, 0.5)
        self.softmax = nn.Softmax(dim=1)
        self.attention_dropout = nn.Dropout(attn_dropout)

    def forward(self, q, k, v):
        ''' Returns the softmax scores and attention tensor '''
        attention = torch.matmul(q, k.transpose(-2, -1)) / self.temper
        attention = self.softmax(attention)
        attention = self.attention_dropout(attention)
        output = torch.bmm(attention, v)
        return output, attention

class MultiHeadAttention(nn.Module):
    '''Multihead Attention'''
    def __init__(self, qty_head, dim_model, dim_k, dim_v, dropout=0.1, attn_dropout=0.1):
        super(MultiHeadAttention, self).__init__()

        self.qty_head = qty_head
        self.dim_k = dim_k
        self.dim_v = dim_v
        self.dim_model = dim_model

        self.weight_q = nn.Parameter(torch.FloatTensor(qty_head, dim_model, dim_k)).double()
        self.weight_k = nn.Parameter(torch.FloatTensor(qty_head, dim_model, dim_k)).double()
        self.weight_v = nn.Parameter(torch.FloatTensor(qty_head, dim_model, dim_v)).double()        

        self.attention_model = ScaledDotProductAttention(dim_model, attn_dropout=attn_dropout)

        self.layer_norm = nn.LayerNorm(dim_model).double()
        # V vectors of each head are concatenated
        self.projection = nn.Linear(qty_head * dim_v, dim_model).double()

        self.dropout = nn.Dropout(dropout)

        #init weights 
        torch.nn.init.xavier_normal_(self.weight_q)
        torch.nn.init.xavier_normal_(self.weight_k)
        torch.nn.init.xavier_normal_(self.weight_v)

    def forward(self, q, k, v):
        residual = q

        batch_size, q_len, dim_model = q.size()
        _, k_len, _ = k.size()
        _, v_len, _ = v.size()

        # Reshaping considering number of heads
        q_vector = q.repeat(self.qty_head, 1, 1).double()
        k_vector = k.repeat(self.qty_head, 1, 1).double()
        v_vector = v.repeat(self.qty_head, 1, 1).double()
        
        q_vector = torch.bmm(q_vector, self.weight_q).double()
        k_vector = torch.bmm(k_vector, self.weight_k).double()
        v_vector = torch.bmm(v_vector, self.weight_v).double()

        outputs, attentions = self.attention_model(q_vector, k_vector, v_vector)

        outputs = torch.cat(torch.split(outputs, batch_size, dim=0), dim=-1).double()
        outputs = self.projection(outputs).double()
        outputs = self.dropout(outputs).double()

        return self.layer_norm(outputs + residual).double(), attentions

class PositionwiseFeedForward(nn.Module):
    ''' A two-feed-forward-layer module '''

    def __init__(self, dim_hidden, dim_inner_hidden, dropout=0.1):
        super(PositionwiseFeedForward, self).__init__()
        self.layer_1 = nn.Conv1d(dim_hidden, dim_inner_hidden, 1)  # position-wise
        self.layer_1 = self.layer_1.double()
        
        self.layer_2 = nn.Conv1d(dim_inner_hidden, dim_hidden, 1)  # position-wise
        self.layer_2 = self.layer_2.double()
        
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(dim_hidden)
        self.layer_norm = self.layer_norm.double()
        
        self.relu = nn.ReLU()
        self.relu = self.relu.double()

    def forward(self, x):
        residual = x = x.double()
        # print("Input of fnn {}".format(x.size()))
        # print("transposed Input of fnn {}".format(x.transpose(1, 2).size()))
        output = self.relu(self.layer_1(x.transpose(1, 2).double()).double())
        # print("First convolution of fnn {}".format(output.size()))
        output = self.layer_2(output.double()).transpose(2, 1)
        # print("Second convolution of fnn {}".format(output.size()))
        output = self.dropout(output.double())
        return self.layer_norm(output + residual)


class SelfAttentionEncoderLayer(nn.Module):
    ''' Transformer encoder layer '''

    def __init__(self, dim_model, dim_inner_hidden, qty_head, dim_k, dim_v, dropout=0.1, attn_dropout=0.1):
        super(SelfAttentionEncoderLayer, self).__init__()
        self.self_attention = MultiHeadAttention(qty_head, dim_model, dim_k, dim_v, dropout=dropout, attn_dropout=attn_dropout)
        self.feedforward = PositionwiseFeedForward(dim_model, dim_inner_hidden, dropout)

    def forward(self, input_tensor):
        output, attention = self.self_attention(input_tensor, input_tensor, input_tensor)
        output = self.feedforward(output)
        return output, attention