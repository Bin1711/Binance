import torch
import torch.nn.functional as F
import torch.optim as optim

from models.actor_critic import ActorCritic
from env import Env

from datetime import datetime

def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(),
                                   shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad


def train(rank, args, shared_model, params, counter, lock, optimizer=None):
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
    while datetime.now() < params.end_time and episode_length < args.max_episode_length:
        # Sync with the shared model
        model.load_state_dict(shared_model.state_dict())

        values = []
        log_probs = []
        rewards = []
        entropies = []

        for step in range(args.num_steps):
            episode_length += 1
            action, mu, var, value = model.act(state)
            
            log_prob = model.calc_logprob(mu, var, action)
            entropy = model.calc_entropy(mu, var, action)
            
            action = F.softmax(action)
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

        (policy_loss + args.value_loss_coef * value_loss).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

        ensure_shared_grads(model, shared_model)
        optimizer.step()