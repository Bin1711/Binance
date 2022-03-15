import numpy as np

class Env():
    def __init__(self, params):
        self.params = params
        
        self.data = params.data
        
        self.index = self.data[params.syms[0]].index
        
    def reset(self):
        self.curr_i = self.params.window - 1
        return self.get_state()
    
    def step(self, action):
        reward = self.get_reward(action)
        
        self.curr_i += 1
        
        states = self.get_state()
        
        done = True if self.curr_i >= len(self.index)-2 else False
        
        return states, reward, done
    
    def get_state(self):
        states = []
        start_ = self.index[self.curr_i - self.params.window + 1]
        end_ = self.index[self.curr_i]
        for i, sym in enumerate(self.params.syms):
            df = self.data[sym]
            df = df[start_:end_].values
            df = df/df.max(axis=0) #(df - df.mean(axis=0)) / df.std(axis=0)
            states.append(df)
            
        return np.array(states)
    
    def get_reward(self, action):
        returns = []
        curr_date = self.index[self.curr_i]
        next_date = self.index[self.curr_i + 1]
        for i, sym in enumerate(self.params.syms):
            df = self.data[sym]
            ret = df.loc[next_date, 'close'] / df.loc[curr_date, 'close'] - 1
            returns.append(ret)
            
        returns = np.dot(returns, action)
        return returns*(1 - self.params.fee) if returns >= 0 else returns*(1 + self.params.fee)