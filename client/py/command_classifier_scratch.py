import NeuralNetwork as Network
import json
import pandas as pd
import numpy as np
import string

class CommandClassifierSoftmax:
    def __init__(self, data_file, data_size):
        self.data_file = data_file
        self.data  = None
        with open(self.data_file, 'rb') as f:
            self.data = pd.read_json(f)
        
        self.max_len = 50
        self.training_data = self.data[:data_size]
        self.test_data = self.data[data_size:]
        Network.Tokenizer.build_vocab(self.training_data['text'])

        self.y_train = self.training_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
        self.y_train = np.stack(self.y_train.to_numpy())
        self.y_test = self.test_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
        self.y_test = np.stack(self.y_test.to_numpy())

        self.nn = Network.NeuralNetwork([
            Network.Layer.Dense(self.max_len, 64, Network.ActivationFunction.ReLU, Network.Regularizer.L1L2(8e-4, 8e-4)),
            Network.Layer.Dropout(0.15),
            Network.Layer.Dense(64, 2, Network.ActivationFunction.CombinedSoftmaxCategoricalCrossEntropy)  
        ], self.y_train, Network.Optimizer.Adam(learning_rate = .005, rate_decay=1e-7)) 


        self.nn.set_preprocess(lambda x: Network.Tokenizer.pad_sequence(Network.Tokenizer.encode(x.translate(str.maketrans('','',string.punctuation)).lower()), self.max_len))
        self.nn.set_postprocess(self.postprocess)


        self.x_train = self.training_data['text'].apply(self.nn.preprocess)
        self.x_train = np.stack(self.x_train.to_numpy())

        self.x_test = self.test_data['text'].apply(self.nn.preprocess)
        self.x_test = np.stack(self.x_test.to_numpy())

    def load_model(self, file):
        self.nn.load(file)
    
    def postprocess(self,output):
        indices = np.argmax(output, axis=1)
        result = ""
        if(indices[0] == 0):
            result ='command'
        else:
            result ='not_command'
        confidence = output[0][indices[0]]
        return {
            'result':result,
            'confidence': float(confidence),
        }
    
    def predict(self, text):
        padded = self.nn.preprocess(text)
        prediction = self.nn.predict(padded)
        return prediction
    
    def train(self, output_file):
        self.nn.train(self.x_train, self.y_train, epochs=10001, output_file=output_file)
        
    def validate(self):
        self.nn.set_targets(self.y_test)
        self.nn.validate(self.x_test, self.y_test)

class CommandClassifierBinary:
    def __init__(self, data_file, data_size):
        self.data_file = data_file
        self.data  = None
        with open(self.data_file, 'rb') as f:
            self.data = pd.read_json(f)
        
        self.max_len = 50
        self.training_data = self.data[:data_size]
        self.test_data = self.data[data_size:]
        Network.Tokenizer.build_vocab(self.training_data['text'])

        self.y_train = self.training_data['label'].apply(lambda x: [1] if x == 'command' else [0])
        self.y_train = np.stack(self.y_train.to_numpy())
        self.y_test = self.test_data['label'].apply(lambda x: [1] if x == 'command' else [0])
        self.y_test = np.stack(self.y_test.to_numpy())

        self.y_train = self.y_train.reshape(-1, 1)
        self.y_test = self.y_test.reshape(-1, 1)
        # print(self.y_train[:5])
        # print(self.training_data['text'][:5])
        self.nn = Network.NeuralNetwork([
            Network.Layer.Dense(self.max_len, 64, Network.ActivationFunction.ReLU, Network.Regularizer.L1L2(8e-4, 8e-4)),
            Network.Layer.Dropout(0.2),
            Network.Layer.Dense(64, 1, Network.ActivationFunction.Sigmoid)  
        ], self.y_train, Network.Optimizer.Adam(learning_rate = .005, rate_decay=1e-7), loss_function=Network.Loss.BinaryCrossEntropy) 


        self.nn.set_preprocess(lambda x: Network.Tokenizer.pad_sequence(Network.Tokenizer.encode(x.translate(str.maketrans('','',string.punctuation)).lower()), self.max_len))
        self.nn.set_postprocess(self.postprocess)


        self.x_train = self.training_data['text'].apply(self.nn.preprocess)
        self.x_train = np.stack(self.x_train.to_numpy())

        self.x_test = self.test_data['text'].apply(self.nn.preprocess)
        self.x_test = np.stack(self.x_test.to_numpy())

    def load_model(self, file):
        self.nn.load(file)
    
    def postprocess(self,output):
        result = ''
        confidence = 0
        if(output[0][0] > 0.5):
            result ='command'
            confidence = output[0][0]
        else:
            result ='not_command'
            confidence = 1- output[0][0]
        
        return {'result':result, 'confidence': float(confidence)}
    
    def predict(self, text):
        padded = self.nn.preprocess(text)
        prediction = self.nn.predict(padded)
        return prediction
    
    def train(self, output_file):
        self.nn.train(self.x_train, self.y_train, epochs=10001, output_file=output_file)
        
    def validate(self):
        self.nn.set_targets(self.y_test)
        self.nn.validate(self.x_test, self.y_test)



if __name__ == "__main__":
    # classifier = CommandClassifierSoftmax('client/py/command_dataset_direct_and_ai_questions.json', 4000)
    # classifier.load_model('client/py/nn_scratch_model_direct_and_ai_softmax.json')
    # classifier.train('client/py/nn_scratch_model_direct_and_ai_softmax.json')
    
    # classifier = CommandClassifierBinary('client/py/command_dataset_direct_and_ai_questions.json', 4000)
    # classifier.load_model('client/py/nn_scratch_model_direct_and_ai_binary.json')
    # classifier.train('client/py/nn_scratch_model_direct_and_ai_binary.json')
    
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        result = classifier.predict(text)
        print(result)