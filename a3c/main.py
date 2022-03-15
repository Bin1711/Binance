from __future__ import print_function

import argparse
import os

import torch
import torch.multiprocessing as mp
from pathos.threading import ThreadPool

import my_optim

from models.actor_critic import ActorCritic
from training import train_and_test
from testing import test

from params import Params
import pickle
import dill
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description='A3C')
parser.add_argument('--lr', type=float, default=7*1e-7,
                    help='learning rate (default: 7x10^-7)')
parser.add_argument('--gamma', type=float, default=0.99,
                    help='discount factor for rewards (default: 0.99)')
parser.add_argument('--gae-lambda', type=float, default=1.00,
                    help='lambda parameter for GAE (default: 1.00)')
parser.add_argument('--entropy-coef', type=float, default=0.01,
                    help='entropy term coefficient (default: 0.01)')
parser.add_argument('--value-loss-coef', type=float, default=0.5,
                    help='value loss coefficient (default: 0.5)')
parser.add_argument('--max-grad-norm', type=float, default=50,
                    help='value loss coefficient (default: 50)')
parser.add_argument('--seed', type=int, default=1,
                    help='random seed (default: 1)')
parser.add_argument('--num-processes', type=int, default=3,
                    help='how many workers to use (default: 4)')
parser.add_argument('--num-steps', type=int, default=6,
                    help='number of forward steps in A3C (default: 20)')
parser.add_argument('--max-episode-length', type=int, default=1000000,
                    help='maximum length of an episode (default: 1000000)')
parser.add_argument('--epoch', type=int, default=20000,
                    help='epoch (default: 100000)')
parser.add_argument('--no-shared', default=True,
                    help='use an optimizer without shared momentum.')
parser.add_argument('--load-params', default=True,
                    help='load parameters or read from pickel.load.')
parser.add_argument('--load-shared-model', default=True,
                    help='load model and continue traning.')

if __name__ == '__main__':
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = ""
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    
    if args.load_params:
        f = open('alpha/params.pkl', 'rb')
        params = pickle.load(f)
        f.close()
        params.reset_time()
    else:
        params = Params()
        with open('alpha/params.pkl', 'wb') as f:
            pickle.dump(params, f)
            f.close()
    
    if args.load_shared_model:
        with open('alpha/shared_model.pkl', 'rb') as f:
            shared_model = dill.load(f)
    else:
        shared_model = ActorCritic(params)
        shared_model.share_memory()    
    
    if args.no_shared:
        optimizer = None
    else:
        optimizer = my_optim.SharedAdam(shared_model.parameters(), lr=args.lr)
        optimizer.share_memory()
        
    counter = mp.Value('i', 0)
    lock = mp.Lock()

    pool = ThreadPool(args.num_processes)
    for _, R_L, last_episode_rewards in pool.imap(train_and_test, 
                                                 [i for i in range(args.num_processes)],
                                                 [args] * args.num_processes, 
                                                 [shared_model] * args.num_processes,
                                                 [params] * args.num_processes,
                                                 [counter] * args.num_processes,
                                                 [lock] * args.num_processes,
                                                 [optimizer] * args.num_processes):
        plt.figure(figsize=(15,5))
        plt.title('Losses ' + str(_))
        plt.plot(R_L)
        plt.show()
        
        plt.figure(figsize=(15,5))
        plt.title('Rewards of last episode ' + str(_))
        plt.plot(last_episode_rewards)
        plt.show()
        
    pool.close()
    pool.join()
    with open('alpha/shared_model.pkl', 'wb') as f:
        dill.dump(shared_model, f)
    
    episode_rewards = test(args, shared_model, params)
    
    plt.plot(np.cumsum(episode_rewards))
    plt.show()
    
    plt.plot(np.cumprod(np.array(episode_rewards)+1))
    plt.show()
    
    print('Positive count: ', sum([1 for x in episode_rewards if x>0]))
    print('Negative count: ', sum([1 for x in episode_rewards if x<=0]))
    print('Positive pct: ', sum([1 for x in episode_rewards if x>0])/len(episode_rewards))
    