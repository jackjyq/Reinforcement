import gym
import tensorflow as tf
import numpy as np
import random

# General Parameters
# -- DO NOT MODIFY --
ENV_NAME = 'CartPole-v0'
EPISODE = 100  # Episode limitation
STEP = 200  # Step limitation in an episode
TEST = 10  # The number of tests to run every TEST_FREQUENCY episodes
TEST_FREQUENCY = 100  # Num episodes to run before visualizing test accuracy

# TODO: HyperParameters
GAMMA = 0.9 # discount factor
INITIAL_EPSILON =  0.9# starting value of epsilon
FINAL_EPSILON =  20# final value of epsilon
EPSILON_DECAY_STEPS =  0.5# decay period

# Create environment
# -- DO NOT MODIFY --
env = gym.make(ENV_NAME)
epsilon = INITIAL_EPSILON
STATE_DIM = env.observation_space.shape[0]  # 4
ACTION_DIM = env.action_space.n # 2
# For Neural Network
HIDDEN_LAYER_DIM = 100
REPLAY_SIZE = 10000
BATCH_SIZE = 64

# Placeholders
# -- DO NOT MODIFY --
# state_in: shape=(?, 4)
#       takes the current state of the environment, which is 
#       represented in our case as a sequence of reals.
# action_in: shape=(?, 2)
#       accepts a one-hot action input. It should be used to "mask"
#       the q-values output tensor and return a q-value for that action.
# target_in: shape=(?,)
#       is the Q-value we want to move the network towards producing.
#       Note that this target value is not fixed - this is one of the
#       components that seperates RL from other forms of machine learning.
state_in = tf.placeholder("float", [None, STATE_DIM])
action_in = tf.placeholder("float", [None, ACTION_DIM])
target_in = tf.placeholder("float", [None])

# TODO: Define Network Graph

# input layer
w1 = tf.get_variable('w1', shape=[STATE_DIM, HIDDEN_LAYER_DIM],)
b1 = tf.get_variable('b1', shape=[1, HIDDEN_LAYER_DIM],\
        initializer=tf.constant_initializer(0.0))
output_1 = tf.tanh(tf.matmul(state_in, w1) + b1)    # shape=(?, 100)

# hidden layer
w2 = tf.get_variable('w2', shape=[HIDDEN_LAYER_DIM, HIDDEN_LAYER_DIM],)
b2 = tf.get_variable('b2', shape=[1, HIDDEN_LAYER_DIM],\
        initializer=tf.constant_initializer(0.0))
output_2 = tf.tanh(tf.matmul(output_1, w2) + b2) # (?, 100)

# output layer
w3 = tf.get_variable('w3', shape=[HIDDEN_LAYER_DIM, ACTION_DIM],)
b3 = tf.get_variable('b3', shape=[1, ACTION_DIM],\
        initializer=tf.constant_initializer(0.0))
output_3 = tf.matmul(output_2, w3) + b3 # (?, 2)

# TODO: Network outputs
# q_values: Tensor containing Q-values for all available actions i.e.
#       if the action space is 8 this will be a rank-1 tensor of length 8
# q_action: This should be a rank-1 tensor containing 1 element.
#       This value should be the q-value for the action set in the
#       action_in placeholder
# Loss/Optimizer Definition You can define any loss function you feel is
#       appropriate. Hint: should be a function of target_in and
#       q_action. You should also make careful choice of the optimizer
#       to use. 
q_values = output_3
q_action = tf.reduce_sum(tf.multiply(q_values, action_in),\
        reduction_indices=1)

# TODO: Loss/Optimizer Definition
loss = tf.reduce_sum(tf.square(target_in - q_action))
optimizer = tf.train.AdamOptimizer().minimize(loss)
session = tf.InteractiveSession()
session.run(tf.global_variables_initializer())


########################################################################



# -- DO NOT MODIFY ---
def explore(state, epsilon):
    """
    Exploration function: given a state and an epsilon value,
    and assuming the network has already been defined, decide which action to
    take using e-greedy exploration based on the current q-value estimates.
    """
    # print(state)
    # print(state.shape)
    Q_estimates = q_values.eval(feed_dict={
        state_in: state.reshape(1, STATE_DIM)
    })
    if random.random() <= epsilon:
        action = random.randint(0, ACTION_DIM - 1)
    else:
        action = np.argmax(Q_estimates)
    one_hot_action = np.zeros(ACTION_DIM)
    one_hot_action[action] = 1
    # print("one_hot_action:", one_hot_action)
    # print("action:", action)
    return action, one_hot_action


# Main learning loop
print("\n###################### Start Learning ######################")
replay_buffer = []
for episode in range(EPISODE):
    print("Episode:", episode)
    # initialize task
    state = env.reset()
    # Update epsilon once per episode
    epsilon -= epsilon / EPSILON_DECAY_STEPS

    # Move through env according to e-greedy policy
    for step in range(STEP):
        
        action, one_hot_action = explore(state, epsilon)
        next_state, reward, done, _ = env.step(action)
        env.render()

        nextstate_q_values = q_values.eval(feed_dict={
            state_in: next_state.reshape(1, STATE_DIM)
        })

        # TODO: Calculate the target q-value.
        # hint1: Bellman
        # hint2: consider if the episode has terminated
        
        # one_hot_action = np.zeros(ACTION_DIM)
        # one_hot_action[action] = 1

        # append to buffer
        replay_buffer.append([state, one_hot_action, reward, next_state, done])

        # Ensure replay_buffer doesn't grow larger than REPLAY_SIZE
        if len(replay_buffer) > REPLAY_SIZE:
                replay_buffer.pop(0)

        # state = next_state

        # perform a training step if the replay_buffer has a batch worth of samples
        if (len(replay_buffer) > BATCH_SIZE):
                        
                minibatch = random.sample(replay_buffer, BATCH_SIZE)

                state_batch = [data[0] for data in minibatch]
                action_batch = [data[1] for data in minibatch]
                reward_batch = [data[2] for data in minibatch]
                next_state_batch = [data[3] for data in minibatch]

                # state_batch = np.asarray(state_batch)
                # next_state_batch = np.asarray(next_state_batch).reshape(\
                #         BATCH_SIZE, STATE_DIM)
                # print("state_batch:", state_batch[0].reshape(4))
                # print("next_state_batch:", next_state_batch.shape)

                target_batch = []
                Q_value_batch = q_values.eval(feed_dict={
                        state_in: next_state_batch
                })
                for i in range(0, 64):
                        sample_is_done = minibatch[i][4]
                        if sample_is_done:
                                target_batch.append(reward_batch[i])
                        else:
                                # TO IMPLEMENT: set the target_val to the correct Q value update
                                target_val = reward_batch[i] + GAMMA * np.max(Q_value_batch[i])
                                target_batch.append(target_val)	
                # print("target_batch:", target_batch)

                # Do one training step
                # with Session() as sess:
        
        
                session.run([optimizer], feed_dict={
                    target_in: target_batch,
                    action_in: action_batch,
                    state_in: state_batch
                })

        # Update
        state = next_state
        if done:
            break


print("\n###################### Start Testing ######################")
# Test and view sample runs - can disable render to save time
# -- DO NOT MODIFY --
if (episode % TEST_FREQUENCY == 0 and episode != 0):
    total_reward = 0
    for i in range(TEST):
        state = env.reset()
        for j in range(STEP):
            env.render()
            action = np.argmax(q_values.eval(feed_dict={
                state_in: state
            }))
            state, reward, done, _ = env.step(action)
            total_reward += reward
            if done:
                break
    ave_reward = total_reward / TEST
    print('episode:', episode, 'epsilon:', epsilon, 'Evaluation '
                                                    'Average Reward:', ave_reward)

session.close()
env.close()
