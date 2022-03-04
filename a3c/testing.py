import time
from collections import deque

import torch
import torch.nn.functional as F

from models.actor_critic import ActorCritic
from env import Env

from datetime import datetime

def test(rank, args, shared_model, params, counter, lock, optimizer):
    torch.manual_seed(args.seed + rank)

    env = Env(params) #create environment here

    model = ActorCritic(params)

    model.eval()

    state = env.reset()
    state = torch.from_numpy(state)
    reward_sum = 0
    done = True
    R = []
    start_time = time.time()

    # a quick hack to prevent the agent from stucking
    actions = deque(maxlen=100)
    episode_length = 0
    while datetime.now() < params.end_time:
        time.sleep(60)
        episode_length += 1
        # Sync with the shared model
        if done:
            model.load_state_dict(shared_model.state_dict())

        with torch.no_grad():
            action, mu, var, value = model.act(state)
            
        action = F.softmax(action)

        state, reward, done = env.step(action.numpy())
        done = done or episode_length >= args.max_episode_length
        reward_sum += reward

        if done:
            print("Time {}, num steps {}, FPS {:.0f}, episode reward {}, episode length {}".format(
                time.strftime("%Hh %Mm %Ss",
                              time.gmtime(time.time() - start_time)),
                counter.value, counter.value / (time.time() - start_time),
                reward_sum, episode_length))
            reward_sum = 0
            episode_length = 0
            actions.clear()
            state = env.reset()
            R.append(reward_sum)

        state = torch.from_numpy(state)
    return R