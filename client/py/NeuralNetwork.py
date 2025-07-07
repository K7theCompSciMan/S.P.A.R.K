import numpy as np
import nnfs
from nnfs.datasets import spiral_data
import pickle, matplotlib.pyplot as plt
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
    class CombinedSoftmaxCategoricalCrossEntropy:
        @staticmethod
        def softmax(inputs):
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
            return probabilities
        
        @staticmethod
        def calculate(inputs, y_true):
            output = ActivationFunction.CombinedSoftmaxCategoricalCrossEntropy.softmax(inputs)
            loss = ActivationFunction.CombinedSoftmaxCategoricalCrossEntropy.loss(output, y_true)
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
        
    class Sigmoid:
        @staticmethod
        def calculate(inputs):
            # print("performed sigmoid forward")
            return 1.0 / (1 + np.exp(-inputs))
        
        @staticmethod
        def backward(outputs, dvalues):
            # print("performed sigmoid backward")
            return dvalues * outputs * (1 - outputs)
        
class Loss:
    class Empty:
        pass
    class CategoricalCrossEntropy:

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
            return np.mean(Loss.CategoricalCrossEntropy.calculate(predicted, actual))
        
        @staticmethod
        def backward(prediction, actual):
            # print("performed CategoricalCrossEntropy backward")
            samples = len(prediction)
            labels = len(prediction[0]) if len(actual.shape) == 2 else np.max(actual) + 1
            if len(actual.shape) == 1:
                actual = np.eye(labels)[actual]
            
            clipped_prediction = np.clip(prediction, 1e-7, 1.0 - 1e-7)
            dinputs = - actual / clipped_prediction
            return dinputs / samples
    class BinaryCrossEntropy:
        @staticmethod
        def calculate(predicted, actual):
            # print("performed BinaryCrossEntropy forward")
            clipped_prediction = np.clip(predicted, 1e-7, 1.0 - 1e-7)
            return (-(actual * np.log(clipped_prediction) + (1 - actual) * np.log(1 - clipped_prediction)))
        
        @staticmethod
        def mean(predicted, actual):
            return np.mean(Loss.BinaryCrossEntropy.calculate(predicted, actual))
        
        @staticmethod
        def backward(predicted, actual):
            # print("performed BinaryCrossEntropy backward")
            
            samples = len(predicted)
            outputs = len(predicted[0])
            
            clipped_prediction = np.clip(predicted, 1e-7, 1.0 - 1e-7)
            dinputs = - (actual / clipped_prediction - (1 - actual) / (1 - clipped_prediction)) / outputs
            return dinputs / samples
        
        
class Regularizer:
    class Empty:
        pass
    class L1:
        def __init__(self, weight_regularizer: float, bias_regularizer: float):
            self.weight_regularizer = weight_regularizer
            self.bias_regularizer = bias_regularizer
        def calculate_weights(self, layer):
            return self.weight_regularizer * np.sum(np.abs(layer.weights))
        def calculate_biases(self, layer):
            return self.bias_regularizer * np.sum(np.abs(layer.biases))
        def calculate(self, layer):
            return self.calculate_weights(layer) + self.calculate_biases(layer)

        def backward(self, layer):
            dL1 = np.ones_like(layer.weights)
            dL1[layer.weights < 0] = -1 
            layer.dweights += self.weight_regularizer * dL1 
            dL1 = np.ones_like(layer.biases)
            dL1[layer.biases < 0] = -1 
            layer.dbiases += self.bias_regularizer * dL1 
    
    class L2:
        def __init__(self, weight_regularizer: float, bias_regularizer: float):
            self.weight_regularizer = weight_regularizer
            self.bias_regularizer = bias_regularizer
        def calculate_weights(self, layer):
            return self.weight_regularizer * np.sum((layer.weights**2))
        def calculate_biases(self, layer):
            return self.bias_regularizer * np.sum((layer.biases**2))
        def calculate(self, layer):
            return self.calculate_weights(layer) + self.calculate_biases(layer)

        def backward(self, layer):
            layer.dweights += 2 * self.weight_regularizer * layer.weights
            layer.dbiases += 2 * self.bias_regularizer * layer.biases
    class L1L2:
        def __init__(self, weight_regularizer: float, bias_regularizer: float):
            self.weight_regularizer = weight_regularizer
            self.bias_regularizer = bias_regularizer
            self.l1 = Regularizer.L1(weight_regularizer, bias_regularizer)
            self.l2 = Regularizer.L2(weight_regularizer, bias_regularizer)
        def calculate_weights(self,layer):
            return self.l1.calculate_weights(layer) + self.l2.calculate_weights(layer)
        def calculate_biases(self,layer):
            return self.l1.calculate_biases(layer) + self.l2.calculate_biases(layer)
        def calculate(self, layer):
            return self.l1.calculate(layer) + self.l2.calculate(layer)
        def backward(self, layer):
            self.l1.backward(layer)
            self.l2.backward(layer)
class Layer:
    class Dropout:
        def __init__(self, dropout_rate: float):
            self.rate = 1-dropout_rate
            self.weights = None
            self.biases = None
        
        def forward(self, inputs):
            self.binary_mask = np.random.binomial(1, self.rate, inputs.shape) / (self.rate)

            return inputs * self.binary_mask
        
        def set_inputs(self, inputs):
            self.inputs = inputs
        
        def backward(self, dvalues):
            return dvalues *self.binary_mask
            
    class Dense:
        def __init__(self, input_size: int, output_size: int, activation_function: ActivationFunction, regularizer: Regularizer=Regularizer.Empty):
            self.input_size = input_size
            self.output_size = output_size
            self.activation_function = activation_function
            self.weights = 0.01 * np.random.randn(input_size, output_size)
            self.biases = np.zeros((1, output_size))
            self.regularizer = regularizer
        
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
            if (self.regularizer is not Regularizer.Empty):
                self.regularizer.backward(self)
            
            self.dinputs = np.dot(dvalues, self.weights.T)
            return self.dinputs
        def backward_with_activation(self, dvalues):
            # print("dense backward with activation")
            activation_dvalues = self.activation_function.backward(self.activation_output, dvalues)
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
            # print("adjusted parameters")
class NeuralNetwork:
    def __init__(self, layers: list[Layer], targets, optimizer: Optimizer, regularizer: Regularizer=Regularizer.Empty, loss_function=Loss.Empty):
        self.layers = layers
        self.output = None
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.targets = targets
        self.regularizer = regularizer
        #model initialization
        self.model = {'accuracy': 0, 'loss': 99999, 'params': [{'weights': x.weights, 'biases': x.biases} for x in self.layers]}
        
    def forward(self, inputs):
        self.inputs = inputs
        self.output = inputs
        for layer in self.layers:
            layer.set_inputs(self.output)
            if(hasattr(layer, 'activation_function')):
                if(layer.activation_function == ActivationFunction.CombinedSoftmaxCategoricalCrossEntropy):
                    self.output, self.loss = layer.forward_with_combined_activation(self.output, self.targets)
                else:
                    self.output = layer.forward_with_activation(self.output)
            else:
                self.output = layer.forward(self.output)
        if(self.loss_function is not Loss.Empty):
            self.loss = self.calculate_loss(self.targets)
        for layer in self.layers:
            if(hasattr(layer, 'regularizer') and layer.regularizer is not Regularizer.Empty):
                self.loss += layer.regularizer.calculate(layer)
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
            if(hasattr(layer, 'activation_function')):
                dvalues = layer.backward_with_activation(dvalues)  
            else:
                dvalues = layer.backward(dvalues)
            
    def adjust_parameters(self):
        for layer in self.layers:
            if (type(layer) is not Layer.Dropout):
                self.optimizer.adjust_parameters(layer)

    def get_accuracy(self):
        if (self.loss_function is Loss.BinaryCrossEntropy):
            return self.get_accuracy_binary()
        targets = self.targets.copy()
        predictions = np.argmax(self.output, axis=1)
        if(len(targets.shape) == 2):
            targets = np.argmax(self.targets, axis=1)
        return np.mean(predictions == targets)

    def get_accuracy_binary(self):
        targets = self.targets.copy()
        predictions = (self.output > 0.5) * 1
        return np.mean(predictions == targets)

    def get_params(self):
        return [{'weights': x.weights, 'biases': x.biases} for x in self.layers]  

    def load_model(self, model):
        self.model=model
        for index, layer in enumerate(self.layers):
            if(hasattr(layer, 'set_params')):
                layer.set_params(model['params'][index])
        
        print("loaded model params")
    
    def load(self, file="client/py/nn_scratch_data.json"):
        with open(file, 'rb') as f:
            self.model = pickle.load(f)
        print("loaded model")
        self.load_model(self.model)
    
    def train(self, inputs, targets, epochs: float, output_file="client/py/nn_scratch_data.json"):
        best_accuracy = self.model['accuracy']
        best_params = self.model['params']
        best_loss = self.model['loss']
        self.history = {'epoch': [], 'accuracy': [], 'loss': []}
        print(best_accuracy, best_loss)
        for epoch in range(epochs):
            self.forward(inputs)
            accuracy = self.get_accuracy()
            loss = self.loss
            if((best_accuracy != None) and (best_loss != None) and accuracy >= best_accuracy and loss <= best_loss):
                best_accuracy = accuracy
                best_params = self.get_params()
                best_loss = loss
            if not epoch % 100 :
                print(f"epoch: {epoch}, accuracy: {accuracy:.3f}, loss: {loss:.3f}, learning rate: {self.optimizer.learning_rate}")
                # print(f"epoch: {epoch}, best accuracy: {best_accuracy}, best loss: {best_loss}, learning rate: {self.optimizer.learning_rate}")
            self.history['epoch'].append(epoch)
            self.history['accuracy'].append(accuracy)
            self.history['loss'].append(loss)
            self.backward()
            self.adjust_parameters()
        self.model = {'accuracy': best_accuracy, 'loss': best_loss, 'params': best_params}
        print(f"Best Accuracy: {best_accuracy}, Best Loss: {best_loss}")
        save_model = input("save model? [y/n]").lower()
        if (save_model == "y" or save_model == "yes"):
            with open(output_file, 'wb') as f:
                pickle.dump(self.model, f, pickle.HIGHEST_PROTOCOL)
                print("saved model")
    
    def plot_history(self):
        plt.plot(self.history['epoch'], self.history['accuracy'])
        plt.plot(self.history['epoch'], self.history['loss'])
        plt.show()
    
    def validate(self, inputs, targets):
        self.set_targets(targets)
        self.forward(inputs)
        
        print(f"validation accuracy: {self.get_accuracy()}, loss: {self.loss}")
        
    def predict(self, inputs):
        self.inputs = inputs
        self.output = inputs
        for layer in self.layers:
            layer.set_inputs(self.output)
            if(hasattr(layer, 'activation_function')):
                if(layer.activation_function == ActivationFunction.CombinedSoftmaxCategoricalCrossEntropy):
                    self.output, self.loss = layer.forward_with_combined_activation(self.output, self.targets)
                else:
                    self.output = layer.forward_with_activation(self.output)
            else:
                if (type(layer) is not Layer.Dropout):
                    self.output = layer.forward(self.output)
        if(self.loss_function is not Loss.Empty):
            self.loss = self.calculate_loss(self.targets)
        for layer in self.layers:
            if(hasattr(layer, 'regularizer') and layer.regularizer is not Regularizer.Empty):
                self.loss += layer.regularizer.calculate(layer)
        return self.postprocess(self.output)
    
    def set_preprocess(self, preprocess):
        self.preprocess = preprocess
    
    def set_postprocess(self, postprocess):
        self.postprocess = postprocess
class Tokenizer:
    char_to_index = {}
    index_to_char = {}

    @staticmethod
    def build_vocab(texts):
        chars = sorted(set("".join(texts)))
        Tokenizer.char_to_index = {c: i+1 for i, c in enumerate(chars)} 
        Tokenizer.index_to_char = {i+1: c for i, c in enumerate(chars)}

    @staticmethod
    def encode(text: str):
        return [Tokenizer.char_to_index.get(c, 0) for c in text]

    @staticmethod
    def decode(indices: list):
        return ''.join(Tokenizer.index_to_char.get(i, '?') for i in indices)
    
    @staticmethod
    def pad_sequence(seq, max_len):
        return np.array(seq + [0]*(max_len - len(seq)))[:max_len]
    

    
if __name__ == "__main__":    
    X, y = spiral_data(samples=100, classes=2)
    test_x, test_y = spiral_data(samples=100, classes=2)
    y = y.reshape(-1, 1)
    test_y = test_y.reshape(-1, 1)
    nn = NeuralNetwork([
        Layer.Dense(2, 64, ActivationFunction.ReLU, regularizer=Regularizer.L2(5e-6, 5e-6)),
        Layer.Dense(64, 1, ActivationFunction.Sigmoid)  
    ], y, Optimizer.Adam(learning_rate = 0.001, rate_decay=5e-9, min_rate=1e-5), loss_function=Loss.BinaryCrossEntropy)
    nn.train(X, y, epochs=10000)