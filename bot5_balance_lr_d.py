import pygame
import os
import time
import random
import numpy as np
from vertical_shooter5 import sGame 
import pickle
import matplotlib.pyplot as plt


    

def run(episodes, is_training=True , render=False):
#def run(episodes, is_training=True):
    game = sGame()
    
    LOW = game.player.get_width() + 20 
    HIGH = game.WIDTH - game.player.get_width() + 20
    
    low = game.player.get_width()
    high = game.WIDTH
    high_y = game.HEIGHT 

    # Divide player , enemies and bullets position into segments
    
    player_space = np.linspace(LOW, HIGH, 60)
    
    danger_space = np.linspace(0,1000,60)    
    
    # enemy_x_space = np.linspace(0, high , 100)
    # enemy_y_space = np.linspace(0, high_y,100)
    danger_ahead_space = 2
    danger_left_space = 2
    danger_right_space = 2
    
    action_space = [0,1,2,3]
   
    
    
    
     
     
    
    if(is_training):
        # Initialize Q-table
        q_table = np.zeros((len(player_space), len(danger_space) ,danger_ahead_space, danger_left_space, danger_right_space , len(game.action_space))) # init a 50x{50}x4 array
        
        
    else:
        f = open('vertical_shooter5_balance_lr_d.pkl', 'rb')
        q = pickle.load(f)
        f.close()
    
    # Q-learning parameters
    LEARNING_RATE = 0.5
    DISCOUNT = 0.5
     # Exploration-exploitation parameters    
    epsilon = 0.99
    epsilon_decay_value =  1/episodes #epsilon decay rate
 
    rewards_per_episode = np.zeros(episodes)
    episode = 1
    max_score = 0
    max_reward = 0
    duration = 2 * 60
    j = 0
    
    
    
    
    
    for i in range(episodes):
        
        # Starting state
        player_state ,danger_state,danger_left_state, danger_ahead_state, danger_right_state  = game.reset()
        
        
        
        
        
        #take the value of state and push it to the appropriate place in space
        state_p = np.digitize(player_state, player_space)
        state_d= np.digitize(danger_state, danger_space)
        state_d_a = int(danger_ahead_state)
        state_d_l = int(danger_left_state)
        state_d_r = int(danger_right_state)
        
        # print(state_p)
        
        
        
        
        terminated = False          # True when game is over

        rewards=0
        start_time = time.time()

        while(not terminated and rewards>-1000):
            if is_training and np.random.random() < epsilon :
                # Explore: choose a random action
                
                action = np.random.choice(game.action_space)
                #print(action)
                
                
            else:
                # Choose the best action based on the Q-table
                action = np.argmax(q_table[state_p, state_d, state_d_l, state_d_a, state_d_r, :])
                #print(action)
            
            new_player_state, new_danger_state,new_danger_left_state, new_danger_ahead_state, new_danger_right_state, reward, new_max_score, levels, terminated = game.play_step(action)    
                
            
            
            new_state_p = np.digitize(new_player_state, player_space) 
            new_state_d = np.digitize(new_danger_state, danger_space)
            new_state_d_a =int(new_danger_ahead_state)
            new_state_d_l = int(new_danger_left_state)
            new_state_d_r = int(new_danger_right_state)
            # print(new_state_p)
           
            
            
            if is_training:
                if np.any(q_table[new_state_p, new_state_d,new_state_d_l,new_state_d_a,new_state_d_r, :]):
                    max_q_value = np.max(q_table[new_state_p, new_state_d,new_state_d_l,new_state_d_a,new_state_d_r, :])
                else:
                    max_q_value = 1  

                q_table[state_p, state_d, state_d_l,state_d_a,state_d_r, action] = q_table[state_p, state_d, state_d_l,state_d_a,state_d_r, action] + LEARNING_RATE * (
                    reward + DISCOUNT*max_q_value - q_table[state_p, state_d, state_d_l,state_d_a,state_d_r, action])
                #print(q_table[state_p, state_e_x, state_e_y, action])    
            
            
            state_p = new_state_p
            state_d = new_state_d
            state_d_l = new_state_d_l
            state_d_a = new_state_d_a
            state_d_r =  new_state_d_r
            

            rewards += reward
            max_score = new_max_score
            max_levels = levels 
            
            
            
            if  time.time() - start_time > duration:
                break
        
        print(f'{episode} episode is done.')
        episode = episode + 1
        print(f'MAXSCORE per episode =  {max_score}')
        print(f'Level = {max_levels}')
        epsilon = max(epsilon - epsilon_decay_value, 0)    
        rewards_per_episode[i] = rewards
        print(f'Rewards per episode = {rewards_per_episode[i]}')
        if max_reward < rewards_per_episode[i]:
            max_reward =  rewards_per_episode[i] 
            j=episode
        
    print(f'Max Reward is {max_reward} in episode {j}')    
    mean_reward = np.mean(rewards_per_episode)
    print(f'mean reward = {mean_reward}')    

        
        
        
    
    
        
    
    # Save Q table to file
    if is_training:
        f = open('vertical_shooter5_balance_lr_d.pkl','wb')
        pickle.dump(q_table, f)
        f.close()
    
    plt.plot(range(1, len(rewards_per_episode) + 1), rewards_per_episode, marker='o')
    plt.title('Reward vs Episode')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.grid(True)
    
    # mean_rewards = np.zeros(episodes)
    # for t in range(episodes):
    #     mean_rewards[t] = np.mean(rewards_per_episode[max(0, t-100):(t+1)])
    
    if is_training:
        plt.savefig(f'vertical_shooter5_balance_lr_d.png')
    else:
        plt.savefig(f'vertical_shooter5_balance_test.png')        

if __name__ == '__main__':
    run(300, is_training= False, render= True)
    #run(5000, is_training=True, render=False)

