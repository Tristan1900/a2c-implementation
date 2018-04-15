import sys
import argparse
import numpy as np
import keras
import random
import gym


class Imitation():
    def __init__(self, model_config_path, expert_weights_path):
        # Load the expert model.
        with open(model_config_path, 'r') as f:
            self.expert = keras.models.model_from_json(f.read())
        self.expert.load_weights(expert_weights_path)
        self.expert.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        # Initialize the cloned model (to be trained).
        with open(model_config_path, 'r') as f:
            self.model = keras.models.model_from_json(f.read())
        # TODO: Define any training operations and optimizers here, initialize
        #       your variables, or alternatively compile your model here.
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    def run_expert(self, env, render=False):
        # Generates an episode by running the expert policy on the given env.
        return Imitation.generate_episode(self.expert, env, render)

    def run_model(self, env, render=False):
        # Generates an episode by running the cloned policy on the given env.
        return Imitation.generate_episode(self.model, env, render)

    @staticmethod
    def generate_episode(model, env, render=False):
        # Generates an episode by running the given model on the given env.
        # Returns:
        # - a list of states, indexed by time step
        # - a list of actions, indexed by time step
        # - a list of rewards, indexed by time step
        # TODO: Implement this method.
        states = []
        actions = []
        rewards = []
        state = env.reset()
        while True:
            states.append(state)
            action = model.predict(np.reshape(state, (1,8)))
            action = np.argmax(action)
            tmp = [0,0,0,0]
            tmp[action] = 1
            actions.append(tmp)

            state, reward, done, _ = env.step(action)
            rewards.append(reward)
            if done:
                break

        return np.array(states), np.array(actions), rewards
    
    def train(self, env, num_episodes=100, num_epochs=50, render=False):
        # Trains the model on training data generated by the expert policy.
        # Args:
        # - env: The environment to run the expert policy on. 
        # - num_episodes: # episodes to be generated by the expert.
        # - num_epochs: # epochs to train on the data generated by the expert.
        # - render: Whether to render the environment.
        # Returns the final loss and accuracy.
        # TODO: Implement this method. It may be helpful to call the class
        #       method run_expert() to generate training data.
        train_state = []
        train_action = []
        for i in range(num_episodes):
            s, a, r = self.run_expert(env)
            train_state.extend(s)
            train_action.extend(a)
        loss, acc = self.model.fit(np.reshape(train_state, (-1,8)),np.reshape(train_action, (-1,4)),epochs=num_epochs)
        return loss, acc

    def test(self, env, episode):
        reward_final = 0
        for i in range(episode):
            state = env.reset()
            res = 0
            while True:
                action = self.model.predict(np.reshape(state, (1,8)))
                action = np.argmax(action)
                state, reward, done, _ = env.step(action)
                res += reward
                if done:
                    reward_final += reward
                    break
        reward_avg = np.mean(reward_final)
        std = np.std(reward_final)

        print("Test reward is {}".format(reward_avg))
        print("Test std is {}".format(std))
        return




def parse_arguments():
    # Command-line flags are defined here.
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-config-path', dest='model_config_path',
                        type=str, default='LunarLander-v2-config.json',
                        help="Path to the model config file.")
    parser.add_argument('--expert-weights-path', dest='expert_weights_path',
                        type=str, default='LunarLander-v2-weights.h5',
                        help="Path to the expert weights file.")

    # https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    parser_group = parser.add_mutually_exclusive_group(required=False)
    parser_group.add_argument('--render', dest='render',
                              action='store_true',
                              help="Whether to render the environment.")
    parser_group.add_argument('--no-render', dest='render',
                              action='store_false',
                              help="Whether to render the environment.")
    parser.set_defaults(render=False)

    return parser.parse_args()


def main(args):
    # Parse command-line arguments.
    args = parse_arguments()
    model_config_path = args.model_config_path
    expert_weights_path = args.expert_weights_path
    render = args.render
    
    # Create the environment.
    env = gym.make('LunarLander-v2')
    
    # TODO: Train cloned models using imitation learning, and record their
    #       performance.
    imi = Imitation(model_config_path, expert_weights_path)
    imi.train(env)
    imi.test(env, 50)


if __name__ == '__main__':
  main(sys.argv)