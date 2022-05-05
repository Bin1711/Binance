import time
from datetime import datetime

import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

from models.actor_critic import ActorCritic
from env import Env

import dill

def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(),
                                   shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad


def _train(rank, args, shared_model, params, counter, lock, optimizer=None):
    torch.manual_seed(args.seed + rank)

    env = Env(params) #declare environment here
    
    model = ActorCritic(params)

    if optimizer is None:
        optimizer = optim.Adam(shared_model.parameters(), lr=args.lr)

    model.train()

    state = env.reset()
    state = torch.from_numpy(state)
    done = True

    episode_length = 0
    last_episode_rewards = []
    All_losses = []
    cnt = 0
    while cnt <= args.epoch and datetime.now() < params.end_time:
        # Sync with the shared model
        cnt += 1
        model.load_state_dict(shared_model.state_dict())

        values = []
        log_probs = []
        rewards = []
        entropies = []

        for step in range(1+np.random.randint(args.num_steps)):
            episode_length += 1
            action, mu, var, value = model.act(state)
            
            log_prob = model.calc_logprob(mu, var, action)
            entropy = model.calc_entropy(mu, var, action)
            
            action = F.softmax(action, dim = 0)
            #action = F.normalize(action, p = 1, dim = 0)
            action = action.detach()

            state, reward, done = env.step(action.numpy())
            done = done or episode_length >= args.max_episode_length

            with lock:
                counter.value += 1

            if done:
                episode_length = 0
                state = env.reset()

            state = torch.from_numpy(state)
            
            values.append(value)
            log_probs.append(log_prob)
            entropies.append(entropy)
            rewards.append(reward)
            
            if done:
                break
            
        last_episode_rewards = rewards
        R = torch.zeros(1, 1)
        if not done:
            mu, var, value = model(state)
            R = value.detach()
        
        values.append(R)
        policy_loss = 0
        value_loss = 0
        gae = torch.zeros(1, 1)
        for i in reversed(range(len(rewards))):
            R = args.gamma * R + rewards[i]
            advantage = R - values[i]
            value_loss = value_loss + 0.5 * advantage.pow(2)

            # Generalized Advantage Estimation
            delta_t = rewards[i] + args.gamma * values[i + 1] - values[i]
            gae = gae * args.gamma * args.gae_lambda + delta_t

            policy_loss = policy_loss - log_probs[i] * gae.detach() - args.entropy_coef * entropies[i]
            
        
        optimizer.zero_grad()
        total_loss = policy_loss + args.value_loss_coef * value_loss
        All_losses.append(total_loss)
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

        ensure_shared_grads(model, shared_model)
        optimizer.step()
    return rank, torch.cat(All_losses).detach().numpy(), last_episode_rewards

def _test(rank, args, shared_model, params, counter, lock, optimizer, sleep = True):
    torch.manual_seed(args.seed + rank)

    env = Env(params) #create environment here

    model = ActorCritic(params)

    model.eval()

    state = env.reset()
    state = torch.from_numpy(state)
    reward_sum = 0
    done = True
    All_rewards = []
    episode_rewards = []
    last_episode_rewards = []
    start_time = time.time()

    episode_length = 0
    
    while datetime.now() < params.end_time:
        episode_length += 1
        # Sync with the shared model
        if done:
            model.load_state_dict(shared_model.state_dict())

        with torch.no_grad():
            action, mu, var, value = model.act(state)
            
        action = F.softmax(action, dim = 0)
        #action = F.normalize(action, p = 1, dim = 0)

        state, reward, done = env.step(action.numpy())
        done = done or episode_length >= args.max_episode_length
        reward_sum += reward
        episode_rewards.append(reward)
        if done:
            print("Time {}, num steps {}, FPS {:.0f}, episode reward {}, episode length {}".format(
                time.strftime("%Hh %Mm %Ss",
                              time.gmtime(time.time() - start_time)),
                counter.value, counter.value / (time.time() - start_time),
                reward_sum, episode_length))
            
            All_rewards.append(reward_sum)
            last_episode_rewards = episode_rewards
            
            reward_sum = 0
            episode_rewards = []
            episode_length = 0
            state = env.reset()
            with open('alpha/shared_model.pkl', 'wb') as f:
                dill.dump(shared_model, f)
            if sleep: time.sleep(60 * 30)

        state = torch.from_numpy(state)
    return rank, All_rewards, last_episode_rewards


def train_and_test(rank, args, shared_model, params, counter, lock, optimizer):
    if rank == 0:
        return _test(rank, args, shared_model, params, counter, lock, optimizer)
    else:
        return _train(rank, args, shared_model, params, counter, lock, optimizer)