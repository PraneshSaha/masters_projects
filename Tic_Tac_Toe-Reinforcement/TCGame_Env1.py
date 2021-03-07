from gym import spaces
import numpy as np
import random
from itertools import groupby
from itertools import product



class TicTacToe():

    def __init__(self):
        """initialise the board"""
        
        # initialise state as an array
        self.state = [np.nan for _ in range(9)]  # initialises the board position, can initialise to an array or matrix
        # all possible numbers
        self.all_possible_numbers = [i for i in range(1, len(self.state) + 1)] # , can initialise to an array or matrix

        self.reset()


    def is_winning(self, curr_state_list):
        """Takes state as an input and returns whether any row, column or diagonal has winning sum
        Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan]
        Output = False"""
        curr_state =  np.asarray(curr_state_list).reshape((3,3))
        sd1 = 0
        sd2 = 0     
        sum_list = []
        for i in range(3):
            sr = 0
            sc = 0                  
            for j in range(3):
                sr += curr_state[i,j]
                sc += curr_state[j,i]
                if i==j:
                    sd1 += curr_state[i,j]
                if i+j == 2:
                    sd2 += curr_state[i,j]
            sum_list.append(sr)
            sum_list.append(sc)
        sum_list.append(sd1)
        sum_list.append(sd2)
        if 15 in sum_list:
            return True
        else:
            return False
             

    def is_terminal(self, curr_state):
        # Terminal state could be winning state or when the board is filled up

        if self.is_winning(curr_state):
            return True, 'Win'

        elif len(self.allowed_positions(curr_state)) ==0:
            return True, 'Tie'

        else:
            return False, 'Resume'


    def allowed_positions(self, curr_state):
        """Takes state as an input and returns all indexes that are blank"""
        allowed_pos = []
        for i in range(len(curr_state)):
            if np.isnan(curr_state[i]):
                allowed_pos.append(i)
        return allowed_pos


    def allowed_values(self, curr_state):
        """Takes the current state as input and returns all possible (unused) values that can be placed on the board"""
        used_values = [val for val in curr_state if not np.isnan(val)]
        agent_values = [val for val in self.all_possible_numbers if val not in used_values and val % 2 !=0]
        env_values = [val for val in self.all_possible_numbers if val not in used_values and val % 2 ==0]
        return (agent_values, env_values)


    def action_space(self, curr_state):
        """Takes the current state as input and returns all possible actions, i.e, all combinations of allowed positions and allowed values"""
        agent_actions = product(self.allowed_positions(curr_state), self.allowed_values(curr_state)[0])
        env_actions = product(self.allowed_positions(curr_state), self.allowed_values(curr_state)[1])
        return (list(agent_actions), list(env_actions))



    def state_transition(self, curr_state, curr_action):
        """Takes current state and action and returns the board position just after agent's move.
        Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan], action- [7, 9] or [position, value]
        Output = [1, 2, 3, 4, nan, nan, nan, 9, nan]
        """
        pos = curr_action[0]
        next_state = []
        next_state.extend(curr_state)
        next_state[pos] = curr_action[1]
        return next_state        


    def step(self, curr_state, curr_action):
        """Takes current state and action and returns the next state, reward and whether the state is terminal. Hint: First, check the board position after
        agent's move, whether the game is won/loss/tied. Then incorporate environment's move and again check the board status.
        Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan], action- [7, 9] or [position, value]
        Output = ([1, 2, 3, 4, nan, nan, nan, 9, nan], -1, False)"""

        next_state = self.state_transition(curr_state, curr_action)
        game_pos_after,result_after = self.is_terminal(next_state)
        reward = -1
        if game_pos_after == False:
            _, env_actions = self.action_space(next_state)
            action_pick = np.random.randint(0,high=len(env_actions))
            action_env = env_actions[action_pick]
            next_state = self.state_transition(next_state, action_env)
            game_pos_env, result_env = self.is_terminal(next_state)
            if game_pos_env == False:
                return (next_state, reward, game_pos_env)
            elif game_pos_env == True and result_env=="Win":
                return (next_state, reward - 10, game_pos_env)
            else:
                return (self.state, reward , game_pos_env)
        else:
            if result_after == "Win":
                return (next_state, reward+10, game_pos_after)
            else:
                return (self.state, reward, game_pos_after)

                
        

    def reset(self):
        return self.state
