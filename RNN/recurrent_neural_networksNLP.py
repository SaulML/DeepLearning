import glob
import os
import numpy as np
import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English

from random import shuffle, sample
import datetime

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, SimpleRNN

#start time
starttime = datetime.datetime.now()
print(starttime)

nlp = spacy.load('en_core_web_md') #load pre-trained model


tokenizer = Tokenizer(nlp.vocab) #generate tokenizer

traindata = '/home/saul/deeplearning/aclImdb/train'

def pre_process_data(filepath):
	positive_path = os.path.join(filepath, 'pos')
	negative_path = os.path.join(filepath, 'neg')
	pos_label = 1
	neg_label = 0
	dataset = []
	
	for filename in glob.glob(os.path.join(positive_path, '*.txt')):
		with open(filename, 'r') as f:
			dataset.append((pos_label, f.read()))
	
	for filename in glob.glob(os.path.join(negative_path, '*.txt')):
		with open(filename, 'r') as f:
			dataset.append((neg_label, f.read()))
	
	dataset = sample(dataset, 100) #number of samples to be used
	shuffle(dataset)
	return dataset
	
def tokenize_and_vectorized(dataset):
	
	vectorized_data = []
	
	
	for sample in dataset:
		tokens = tokenizer.tokenize(sample[1]) #tokize sentences 
		sample_vecs = []
		
		#print(sample[1])
		print(tokens)
		
		for token in tokens:
			try:
				sample_vecs.append(word_vectors[token])
			except KeyError:
				pass
		
		vectorized_data.append(sample_vecs)
	
	return vectorized_data

def tok_vec(dataset):
	vectorized_data = []
	#print('Size of the Dataset :', len(dataset))
	for sample in dataset:
		#print(sample[1])
		tokens = tokenizer(sample[1])
		#print(tokens)
		sample_vecs = []
		
		for token in tokens:
			
			try:
				sample_vecs.append(nlp(str(token)).vector)
				#print('A token :', token, 'Its vector :', len(nlp(str(token)).vector))
			except KeyError:
				pass
		vectorized_data.append(sample_vecs)
		#print('Sample :', sample)
		#print('Vectorised Data :', vectorized_data)
	#doc = nlp(str(dataset[1]))
	#print(doc)
	#print(dataset[1][1])
	return vectorized_data
	
def collect_expected(dataset):
	
	expected = []
	for sample in dataset:
		expected.append(sample[0])
	return expected
	
def rnnmodel(dataset, vectorised_data, expected):
	
	print('Size of the Dataset :', len(dataset))
	
	maxlen = 400 #400 tokens per example
	maxlen = 50 #400 tokens per example
	batch_size = 32
	embedding_dims = 300 # word vectors are 300 elements long
	embedding_dims = 300 # word vectors are 300 elements long
	epochs = 2
	num_neurons = 50
	
	print("Start of the rnn !!!!! ")
	
	split_point =  int(len(vectorised_data) * .8)
	
	print("End of Split !!!!! ")
	
	x_train = vectorised_data[:split_point]
	print("Shape ", np.shape(x_train))
	print(len(x_train))
	#print(len(x_train[1]))
	print(sum(len(x) for x in x_train))
	#print('Size of the Training Dataset :', len(x_train))
	y_train = expected[:split_point]
	
	#print("X train before padding ", x_train)
	
	#print("End of Train!!!
	
	x_test = vectorised_data[split_point:]
	y_test = expected[split_point:]
	
	print("Start of pad_trunc !!!!! ")
	x_train = pad_trunc(x_train, maxlen)
	#print("X train after padding ", x_train)
	x_test = pad_trunc(x_test, maxlen)
	
	print("End of pad_trunc !!!!! ")
	
	print('Maxlen ', maxlen)
	print('Embedding dims ', embedding_dims)
	
	x_train= np.reshape(x_train, (len(x_train), maxlen, embedding_dims))
	y_train = np.array(y_train)
	print("End of Training Reshape !!!!! ")
	
	x_test = np.reshape(x_test, (len(x_test), maxlen, embedding_dims)) # sample, time steps, number of features
	y_test = np.array(y_test)
	
	print("Start of the Model !!!!! ")
	model = Sequential()
	
	model.add(SimpleRNN(num_neurons, return_sequences = True, input_shape=(maxlen, embedding_dims)))
	model.add(Dropout(.2))
	model.add(Flatten())
	model.add(Dense(1, activation='sigmoid'))
	
	model.compile('rmsprop', 'binary_crossentropy', metrics = ['accuracy'])
	print(model.summary())
	
	print("The RNN model is ", model)
	
	fitmodel(model, x_train, y_train, x_test, y_test, batch_size, epochs)

def fitmodel(model, x_train, y_train, x_test, y_test, batch_size, epochs):
	
	#print('X Train ', x_train.shape)
	#print(' Y Train ', y_train.shape)
	
	#print('X Test ', x_test.shape)
	#print('Y Test ', y_test.shape)
	
	model.fit(x_train, y_train, 
			  batch_size = batch_size,
			  epochs =epochs,
			  validation_data=(x_test, y_test))
	
	#model.fit(np.array(x_train), np.array(y_train), 
			  #batch_size = batch_size,
			  #epochs =epochs,
			  #validation_data=(np.array(x_test), np.array(y_test)))
	
	model_structure = model.to_json()
	with open("simplernn_model.json", "w") as json_file:
		json_file.write(model_structure)
	
	#model.save_weights("rnn_weights.h5)
	
	#print(fittedmodel)
	

def pad_trunc (data, maxlen):
	
	new_data = []
	zero_vector = []
	
	for _ in range(len(data[0][0])):
		zero_vector.append(0.0)
		
	for sample in data:
		if len(sample) > maxlen:
			temp =sample[:maxlen]
		elif len(sample) < maxlen:
			temp = sample
			additional_elems = maxlen - len(sample)
			for _ in range(additional_elems):
				temp.append(temp)
		else:
			temp = sample
		new_data.append(temp)
	
	return new_data
			
			
	
	
if __name__ == '__main__':
	print ("Start !!!")
	
	dataset = pre_process_data(traindata)
	endtime = datetime.datetime.now()
	
	print('Data prepocessing took :', starttime - endtime)
	vectorised_data = tok_vec(dataset)
	endtime = datetime.datetime.now()
	print('Vectorisation took :', starttime - endtime)
	
	expected = collect_expected(dataset)
	endtime = datetime.datetime.now()
	print('Collection took :', endtime - starttime)
	
	rnnmodel(dataset, vectorised_data, expected)	
	
	endtime = datetime.datetime.now()
	print('RNN Model Run:', endtime - starttime)

	#end time
	endtime = datetime.datetime.now()
	
	print("Duration of Execution : ", endtime - starttime)
	
	#print('Dataset ', dataset)
	#vectorized_data = tokenize_and_vectorized(dataset)
