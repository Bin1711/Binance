import torch
import torch.nn.functional as F

from models.actor_critic import ActorCritic
from env import Env

def test(args, shared_model, params):
    torch.manual_seed(args.seed)

    env = Env(params) #create environment here

    model = ActorCritic(params)

    model.eval()

    state = env.reset()
    state = torch.from_numpy(state)
    reward_sum = 0
    done = True
    
    episode_rewards = []
    episode_length = 0
    while True:
        episode_length += 1
        # Sync with the shared model
        if done:
            model.load_state_dict(shared_model.state_dict())

        with torch.no_grad():
            action, mu, var, value = model.act(state)
            
        action = F.softmax(action, dim = 0)
        #action = F.normalize(action, p = 1, dim = 0)

        state, reward, done = env.step(action.numpy())
        state = torch.from_numpy(state)
        done = done or episode_length >= args.max_episode_length
        reward_sum += reward
        episode_rewards.append(reward)
        if done:
            break
    return episode_rewards