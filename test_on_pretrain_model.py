import numpy as np
import tensorflow as tf
import matplotlib as plt
from dataloader import *
from model import *
from util_sample import *

def run_epoch(session, initial_state, cost, X, y_, placeholder_x, placeholder_y):
	costs = 0.0
	batch_size = config['batch_size']
	N, coords, _ = X.shape
	state = session.run(initial_state)
	fetches = {
		"cost": cost,
	}
	for step in range(N/batch_size+1):
		batch_idx = np.random.choice(N, batch_size, replace=False)
		feed_dict = {}
		for i, (c, h) in enumerate(initial_state):
			feed_dict[c] = state[i][0]
			feed_dict[h] = state[i][1]
		feed_dict[placeholder_x] = X[batch_idx]
		feed_dict[placeholder_y] = y_[batch_idx]
		vals = session.run(fetches, feed_dict)
		cost = vals['cost']
		costs += cost

	return costs

directory = 'data/'
filename = 'all_data.csv'
#filename = 'seq_all.csv'

config = {}
if filename=='seq_all.csv':
	config['seq_len'] = 20
	config['batch_size'] = 64
	config['overlap_rate'] = 0.0
	config['lr_decay'] = 0.95
	config['mixtures'] = 3
	config['max_epoch'] = 10
	config['max_max_epoch'] = 20
else:
	config['seq_len'] = 40
	config['batch_size'] = 20
	config['overlap_rate'] = 0.8
	config['lr_decay'] = 0.98
	config['max_epoch'] = 60
	config['max_max_epoch'] = 100
config['learning_rate'] = 0.005
config['num_layers'] = 2
config['hidden_size'] = 64
config['lr_decay'] = 0.9
config['keep_prob'] = 1
config['max_grad_norm'] = 0.5
config['init_scale'] = 0.01

train_ratio = 0.8

def main(_):
	dl = DataLoad(directory, filename)

	dl.load_data(config['seq_len'], config['overlap_rate'], verbose = True)

	dl.split_train_test(train_ratio)

	data = dl.data
	X_train = np.transpose(data['X_train'], [0,2,1])
	y_train = np.transpose(data['y_train'], [0,2,1])
	X_test = np.transpose(data['X_test'], [0,2,1])
	y_test = np.transpose(data['y_test'], [0,2,1])

	N, coords, _ = X_train.shape
	N_test = X_test.shape[0]

	config['coords'] = coords


	with tf.Session() as session:

		saver = tf.train.import_meta_graph(directory+'my-model.meta')
		saver.restore(session, directory+'my-model')

		initial_state_c = tf.get_collection("initial_state_c")
		initial_state_h = tf.get_collection("initial_state_h")
		initial_state = []
		for i in range(len(initial_state_c)):
			initial_state.append((initial_state_c[i], initial_state_h[i]))
		test_cost = tf.get_collection("test_cost")[0]
		placeholder_x = tf.get_collection("x")[0]
		placeholder_y = tf.get_collection("y_")[0]
		test_outputs = tf.get_collection("test_outputs")

		for i in range(config['max_epoch']):
			
			test_perplexity = run_epoch(session, initial_state, test_cost, X_test, y_test, placeholder_x, placeholder_y)
			print "Epoch: %d test perplexity: %.3f"%(i+1, test_perplexity)

		sample(session, placeholder_x, test_outputs, config, X_train[5], sl_pre=config['seq_len']/2);

if __name__ == '__main__':
	tf.app.run(main=main)