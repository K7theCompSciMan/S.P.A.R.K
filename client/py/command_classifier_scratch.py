import NeuralNetwork as Network
import json
import pandas as pd
import numpy as np
import string


data  = None
with open('client/py/nn_scratch_data.json', 'rb') as f:
    data = pd.read_json(f)

def postprocess(output):
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


max_len = 50


training_data = data[:400]
test_data = data[400:]
Network.Tokenizer.build_vocab(training_data['text'])

y_train = training_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
y_train = np.stack(y_train.to_numpy())
y_test = test_data['label'].apply(lambda x: [1, 0] if x == 'command' else [0, 1])
y_test = np.stack(y_test.to_numpy())

nn = Network.NeuralNetwork([
    Network.Layer.Dense(max_len, 64, Network.ActivationFunction.ReLU),
    Network.Layer.Dense(64, 2, Network.ActivationFunction.CombinedSoftmaxCrossEntropy)  
], y_train, Network.Optimizer.Adam(learning_rate = .005, rate_decay=1e-7)) 


nn.set_preprocess(lambda x: Network.Tokenizer.pad_sequence(Network.Tokenizer.encode(x.translate(str.maketrans('','',string.punctuation)).lower()), max_len))
nn.set_postprocess(postprocess)


x_train = training_data['text'].apply(nn.preprocess)
x_train = np.stack(x_train.to_numpy())

x_test = test_data['text'].apply(nn.preprocess)
x_test = np.stack(x_test.to_numpy())





nn.load('client/py/nn_scratch_model.json')


if __name__ == "__main__":
    # history = nn.train(x_train, y_train, epochs=10000, output_file='client/py/nn_scratch_model.json')
    # nn.validate(x_test, y_test)
    while True:
        text = input( "Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        print(nn.predict(nn.preprocess(text).reshape(1, max_len)))

