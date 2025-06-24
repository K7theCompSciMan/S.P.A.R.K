import NeuralNetwork as Network
import json
import pandas as pd
import numpy as np
import string

class CommandClassifier:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data  = None
        with open(self.data_file, 'rb') as f:
            self.data = pd.read_json(f)
        
        self.max_len = 50
        self.training_data = self.data[:400]
        self.test_data = self.data[400:]
        Network.Tokenizer.build_vocab(self.training_data['text'])

        self.y_train = self.training_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
        self.y_train = np.stack(self.y_train.to_numpy())
        self.y_test = self.test_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
        self.y_test = np.stack(self.y_test.to_numpy())

        self.nn = Network.NeuralNetwork([
            Network.Layer.Dense(self.max_len, 64, Network.ActivationFunction.ReLU, Network.Regularizer.L1L2(8e-4, 8e-4)),
            Network.Layer.Dropout(0.15),
            Network.Layer.Dense(64, 2, Network.ActivationFunction.CombinedSoftmaxCrossEntropy)  
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
        self.nn.train(self.x_train, self.y_train, epochs=1001, output_file=output_file)
        
    def validate(self):
        self.nn.set_targets(self.y_test)
        self.nn.validate(self.x_test, self.y_test)



if __name__ == "__main__":
    classifier = CommandClassifier('client/py/nn_scratch_data_dataset_claude.json')
    classifier.load_model('client/py/nn_scratch_model_dataset_claude.json')
    # classifier.train('client/py/nn_scratch_model_dataset_claude.json')
    classifier.validate()
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        result = classifier.predict(text)
        print(result)