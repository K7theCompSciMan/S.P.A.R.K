import numpy as np
import nnfs
from nnfs.datasets import spiral_data
import pickle
class ActivationFunction:
    class ReLU:
        @staticmethod
        def calculate(inputs):
            # print("performed ReLU")
            return np.maximum(0, inputs)

        @staticmethod
        def backward(inputs, dvalues):
            # print("performed ReLU backward")
            return dvalues * (inputs > 0)
    class Softmax:
        @staticmethod
        def calculate(inputs):
            # print("performed softmax")
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            return exp_values / np.sum(exp_values, axis=1, keepdims=True)
        @staticmethod
        def backward(outputs, dvalues):
            # print("performed softmax backward")
            dinputs = np.empty_like(dvalues)
            for index, (output, dvalue) in enumerate(zip(outputs, dvalues)):
                output = output.reshape(-1, 1)
                matrix = np.diagflat(output) - np.dot(output, output.T)
                dinputs[index] = np.dot(matrix, dvalue)
            return dinputs
    class CombinedSoftmaxCrossEntropy:
        @staticmethod
        def softmax(inputs):
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
            return probabilities
        
        @staticmethod
        def calculate(inputs, y_true):
            output = ActivationFunction.CombinedSoftmaxCrossEntropy.softmax(inputs)
            loss = ActivationFunction.CombinedSoftmaxCrossEntropy.loss(output, y_true)
            return output, loss
        
        @staticmethod
        def loss(probabilities, y_true):
            samples = len(probabilities)
            clipped = np.clip(probabilities, 1e-7, 1 - 1e-7)

            if len(y_true.shape) == 1:
                correct_confidences = clipped[range(samples), y_true]
            elif len(y_true.shape) == 2:
                correct_confidences = np.sum(clipped * y_true, axis=1)

            return np.mean(-np.log(correct_confidences))

        @staticmethod
        def backward(probabilities, y_true):
            samples = len(probabilities)
            if len(y_true.shape) == 2:
                y_true = np.argmax(y_true, axis=1)
            dinputs = probabilities.copy()
            dinputs[range(samples), y_true] -= 1
            return dinputs / samples
class Loss:
    class Empty:
        pass
    class CrossEntropy:

        @staticmethod
        def calculate(predicted, actual):
            samples = len(predicted)
            
            clipped_pred = np.clip(predicted, 1e-7, 1.0 - 1e-7)
            # sparse data
            if(len(actual.shape) == 1):
                confidences = clipped_pred[range(samples), actual]
            # one=hot data
            elif(len(actual.shape) == 2):
                confidences = np.sum(clipped_pred * actual, axis=1)
            
            return -np.log(confidences)
            
        @staticmethod
        def mean(predicted, actual):
            return np.mean(Loss.CrossEntropy.calculate(predicted, actual))
        
        @staticmethod
        def backward(prediction, actual):
            # print("performed CrossEntropy backward")
            samples = len(prediction)
            labels = len(prediction[0]) if len(actual.shape) == 2 else np.max(actual) + 1
            if len(actual.shape) == 1:
                actual = np.eye(labels)[actual]
            
            clipped_prediction = np.clip(prediction, 1e-7, 1.0 - 1e-7)
            dinputs = - actual / clipped_prediction
            return dinputs / samples
class Layer:
    class Dense:
        def __init__(self, input_size: int, output_size: int, activation_function: ActivationFunction):
            self.input_size = input_size
            self.output_size = output_size
            self.activation_function = activation_function
            self.weights = 0.01 * np.random.randn(input_size, output_size)
            self.biases = np.zeros((1, output_size))
        
        def set_inputs(self, inputs):
            self.inputs = inputs
        
        def forward(self, inputs):
            self.set_inputs(inputs)
            self.output = np.dot(inputs, self.weights) + self.biases
            # print("performed forward pass Dense")
            return self.output
        def forward_with_activation(self, inputs):
            self.pre_activation_output = self.forward(inputs)
            self.activation_output = self.activation_function.calculate(self.pre_activation_output)
            return self.activation_output
        
        def forward_with_combined_activation(self, inputs, targets):
            self.pre_activation_output = self.forward(inputs)
            self.activation_output, self.loss = self.activation_function.calculate(self.pre_activation_output, targets)
            return self.activation_output, self.loss
        
        def backward(self, dvalues):
            # print("dense backward")
            self.dweights = np.dot(self.inputs.T, dvalues)
            self.dbiases = np.sum(dvalues, axis=0, keepdims=True)
            self.dinputs = np.dot(dvalues, self.weights.T)
            return self.dinputs
        def backward_with_activation(self, dvalues):
            # print("dense backward with activation")
            activation_dvalues = self.activation_function.backward(self.pre_activation_output, dvalues)
            return self.backward(activation_dvalues)

        def set_params(self, params: (float, float)):
            self.weights = params['weights']
            self.biases = params['biases']
class Optimizer:
    class SGD:
        def __init__(self, learning_rate: float=1, rate_decay: float=0, min_rate: float=1e-3, momentum: float=None):
            self.learning_rate = learning_rate
            self.initial_learning_rate = learning_rate
            self.rate_decay = rate_decay
            self.iteration = 0
            self.min_rate = min_rate
            self.momentum = momentum
        def decay_learning_rate(self):
            if (self.learning_rate > self.min_rate):
                new_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
                if(new_rate < self.min_rate):
                    new_rate = self.min_rate
                self.learning_rate = new_rate
            self.iteration += 1
            return self.learning_rate
        
        def adjust_parameters(self, layer: Layer):
            self.learning_rate = self.decay_learning_rate()
            #momentum calculations
            
            if self.momentum:
                if not (hasattr(layer, 'momentum_weights')):
                    layer.weight_momentums = np.zeros_like(layer.weights)
                    layer.bias_momentums = np.zeros_like(layer.biases)
                
                weight_update = self.momentum * layer.weight_momentums - self.learning_rate * layer.dweights
                bias_update = self.momentum * layer.bias_momentums - self.learning_rate * layer.dbiases
                layer.weight_momentums = weight_update
                layer.bias_momentums = bias_update
                layer.weights += weight_update
                layer.biases += bias_update
            else:
                layer.weights -= self.learning_rate * layer.dweights
                layer.biases -= self.learning_rate * layer.dbiases
    class AdaGrad:
        def __init__(self, learning_rate: float=1, rate_decay: float=0, min_rate: float=0, epsilon: float=1e-7):
            self.learning_rate = learning_rate
            self.initial_learning_rate = learning_rate
            self.rate_decay = rate_decay
            self.iteration = 0
            self.min_rate = min_rate
            self.epsilon = epsilon
        def decay_learning_rate(self):
            if (self.learning_rate > self.min_rate):
                new_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
                if(new_rate < self.min_rate):
                    new_rate = self.min_rate
                self.learning_rate = new_rate
            self.iteration += 1
            return self.learning_rate
        
        def adjust_parameters(self, layer: Layer):
            self.learning_rate = self.decay_learning_rate()
            #adagrad calculations
            if not (hasattr(layer, 'weight_cache')):
                layer.weight_cache = np.zeros_like(layer.weights)
                layer.bias_cache = np.zeros_like(layer.biases)
            layer.weight_cache += layer.dweights **2
            layer.bias_cache += layer.dbiases **2
            
            layer.weights -= (self.learning_rate * layer.dweights) / (np.sqrt(layer.weight_cache) + self.epsilon)
            layer.biases  -= (self.learning_rate * layer.dbiases )/ (np.sqrt(layer.bias_cache) + self.epsilon)
    class RMSProp:
        def __init__(self, learning_rate: float=.001, rate_decay: float=0, min_rate: float=0, epsilon: float=1e-7, rho: float=0.9):
            self.learning_rate = learning_rate
            self.initial_learning_rate = learning_rate
            self.rate_decay = rate_decay
            self.iteration = 0
            self.min_rate = min_rate
            self.epsilon = epsilon
            self.rho = rho
        def decay_learning_rate(self):
            if(min_rate != 0):
                if (self.learning_rate > self.min_rate):
                    new_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
                    if(new_rate < self.min_rate):
                        new_rate = self.min_rate
                    self.learning_rate = new_rate
            else:
                self.learning_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
            self.iteration += 1
            return self.learning_rate
        def adjust_parameters(self, layer: Layer):
            
            if not (hasattr(layer, "weight_cache")):
                layer.weight_cache = np.zeros_like(layer.weights)
                layer.bias_cache = np.zeros_like(layer.biases)
            layer.weight_cache = self.rho * layer.weight_cache + (1 - self.rho) * layer.dweights ** 2
            layer.bias_cache = self.rho * layer.bias_cache + (1 - self.rho) * layer.dbiases ** 2
            layer.weights -= self.learning_rate * layer.dweights / (np.sqrt(layer.weight_cache) + self.epsilon)
            layer.biases -= self.learning_rate * layer.dbiases / (np.sqrt(layer.bias_cache) + self.epsilon)
    class Adam:
        def __init__(self, learning_rate: float=.001, rate_decay: float=0, min_rate: float=0, epsilon: float=1e-7, beta1: float=0.9, beta2: float=0.999):
            self.learning_rate = learning_rate
            self.initial_learning_rate = learning_rate
            self.rate_decay = rate_decay
            self.iteration = 0
            self.min_rate = min_rate
            self.epsilon = epsilon
            self.beta1 = beta1
            self.beta2 = beta2
        def decay_learning_rate(self):
            if(self.min_rate != 0):
                if (self.learning_rate > self.min_rate):
                    new_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
                    if(new_rate < self.min_rate):
                        new_rate = self.min_rate
                    self.learning_rate = new_rate
            else:
                self.learning_rate = self.initial_learning_rate / (1 + self.rate_decay * self.iteration)
            self.iteration += 1
            return self.learning_rate
        def adjust_parameters(self, layer: Layer):
            self.decay_learning_rate()
            if not (hasattr(layer, "weight_cache")):
                layer.weight_cache = np.zeros_like(layer.weights)
                layer.bias_cache = np.zeros_like(layer.biases)
                layer.weight_momentums = np.zeros_like(layer.weights)
                layer.bias_momentums = np.zeros_like(layer.biases)
            
            layer.weight_momentums = self.beta1 * layer.weight_momentums + (1-self.beta1) * layer.dweights
            layer.bias_momentums = self.beta1 * layer.bias_momentums + (1-self.beta1) * layer.dbiases
            
            normalized_weight_momentums = layer.weight_momentums / (1 - self.beta1**(self.iteration))
            normalized_bias_momentums = layer.bias_momentums / (1 - self.beta1**(self.iteration))
            
            layer.weight_cache = self.beta2 * layer.weight_cache + (1-self.beta2) * layer.dweights ** 2
            layer.bias_cache = self.beta2 * layer.bias_cache + (1-self.beta2) * layer.dbiases ** 2
            
            normalized_weight_cache = layer.weight_cache / (1 - self.beta2**(self.iteration))
            normalized_bias_cache = layer.bias_cache / (1 - self.beta2**(self.iteration))
            
            layer.weights -= self.learning_rate * normalized_weight_momentums / (np.sqrt(normalized_weight_cache) + self.epsilon)
            layer.biases -= self.learning_rate * normalized_bias_momentums / (np.sqrt(normalized_bias_cache) + self.epsilon)
class NeuralNetwork:
    def __init__(self, layers: list[Layer], targets, optimizer: Optimizer, loss_function=Loss.Empty):
        self.layers = layers
        self.output = None
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.targets = targets
        
        #model initialization
        self.model = {'accuracy': 0, 'loss': 99999, 'params': [{'weights': x.weights, 'biases': x.biases} for x in self.layers]}
        
    def forward(self, inputs):
        self.inputs = inputs
        self.output = inputs
        for layer in self.layers:
            layer.set_inputs(self.output)
            if(layer.activation_function is not None):
                if(layer.activation_function == ActivationFunction.CombinedSoftmaxCrossEntropy):
                    self.output, self.loss = layer.forward_with_combined_activation(self.output, self.targets)
                else:
                    self.output = layer.forward_with_activation(self.output)
            else:
                self.output = layer.forward(self.output)
        if(self.loss_function is not Loss.Empty):
            self.loss = self.calculate_loss(self.targets)
        return self.output
    
    def set_targets(self, targets):
        self.targets = targets

    def calculate_loss(self, targets):
        self.set_targets(targets)
        if(self.loss_function is not Loss.Empty):
            self.loss = self.loss_function.mean(self.output, targets)
        return self.loss
    
    def backward(self):
        if (self.loss_function is not Loss.Empty):
            dvalues = self.loss_function.backward(self.output, self.targets)
        else:
            dvalues = self.targets.copy()
        for index, layer in enumerate(reversed(self.layers)):
            if(layer.activation_function is not None):
                dvalues = layer.backward_with_activation(dvalues)  
            
    def adjust_parameters(self):
        for layer in self.layers:
            self.optimizer.adjust_parameters(layer)

    def get_accuracy(self):
        targets = self.targets.copy()
        predictions = np.argmax(self.output, axis=1)
        if(len(targets.shape) == 2):
            targets = np.argmax(self.targets, axis=1)
        return np.mean(predictions == targets)

    def get_params(self):
        return [{'weights': x.weights, 'biases': x.biases} for x in self.layers]  

    def load_model(self, model):
        self.model=model
        for index, layer in enumerate(self.layers):
            layer.set_params(model['params'][index])
        
        print("loaded model params")
    
    def load(self, file="client/py/training.json"):
        with open(file, 'rb') as f:
            self.model = pickle.load(f)
        print("loaded model")
        self.load_model(self.model)
    
    def train(self, inputs, targets, epochs: float, output_file="client/py/training.json"):
        best_accuracy = self.model['accuracy']
        best_params = self.model['params']
        best_loss = self.model['loss']
        print(best_accuracy, best_loss)
        for epoch in range(epochs):
            self.forward(inputs)
            accuracy = self.get_accuracy()
            loss = self.loss
            if((best_accuracy != None) and (best_loss != None) and accuracy > best_accuracy and loss < best_loss):
                best_accuracy = accuracy
                best_params = self.get_params()
                best_loss = loss
            if not epoch % 100 :
                print(f"epoch: {epoch}, accuracy: {accuracy}, loss: {loss}, learning rate: {self.optimizer.learning_rate}")
                # print(f"epoch: {epoch}, best accuracy: {best_accuracy}, best loss: {best_loss}, learning rate: {self.optimizer.learning_rate}")
            self.backward()
            self.adjust_parameters()
        self.model = {'accuracy': best_accuracy, 'loss': best_loss, 'params': best_params}
        print(f"Best Accuracy: {best_accuracy}, Best Loss: {best_loss}")
        save_model = input("save model? [y/n]").lower()
        if (save_model == "y" or save_model == "yes"):
            with open(output_file, 'wb') as f:
                pickle.dump(self.model, f, pickle.HIGHEST_PROTOCOL)
                print("saved model")
    
    def validate(self, inputs, targets):
        self.forward(inputs)
        
        print(f"validation accuracy: {self.get_accuracy()}, loss: {self.loss}")
    
    def predict(self, inputs):
        pass
class Tokenizer:
    def __init__(self ):
        self.vocab_size = 1024
        self.merges = {}
        
    def get_stats(self, tokens):
        counts = {}
        for pair in zip(tokens, tokens[1:]):
            counts[pair] = counts.get(pair, 0) + 1
        return counts
        
    def merge(self, tokens, pair, new_index):
        new_tokens = []
        i =0
        while (i<len(tokens)):
            if( i<len(tokens)-1 and tokens[i] == pair[0] and tokens[i+1] == pair[1]):
                new_tokens.append(new_index)
                i+=2
            else:
                new_tokens.append(tokens[i])
                i+=1
        return new_tokens
    
    def train(self, text, verbose=False):
        num_merges = self.vocab_size - 256
        tokens = list(text.encode('utf-8'))
        
        for i in range(num_merges):
            stats = self.get_stats(tokens)
            top_pair = max(stats, key=stats.get)
            index = 256+i
            if verbose:
                print(f"merging {top_pair} -> {index}")
            tokens = self.merge(tokens, top_pair, index)
            self.merges[top_pair] = index
        return self.merges
    
    def encode(self, text):
        tokens = list(text.encode('utf-8'))
        
    



    
X, y = spiral_data(samples=100, classes=3)
test_x, test_y = spiral_data(samples=100, classes=3)

nn = NeuralNetwork([
    Layer.Dense(2, 64, ActivationFunction.ReLU),
    Layer.Dense(64, 3, ActivationFunction.CombinedSoftmaxCrossEntropy)  
], y, Optimizer.Adam(learning_rate = .005, rate_decay=1e-7)) 

# nn.load()
# nn.train(X, y, 40001)
# nn.validate(test_x, test_y)

print(Tokenizer.Whitespace.tokenize("hello, world."))