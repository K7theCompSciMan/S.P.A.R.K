import numpy as np
import nnfs
from nnfs.datasets import spiral_data
class ActivationFunction:
    class ReLU:
        @staticmethod
        def calculate(inputs):
            print("performed ReLU")
            return np.maximum(0, inputs)

        @staticmethod
        def backward(inputs, dvalues):
            print("performed ReLU backward")
            return np.multiply(dvalues, calculate(inputs))
    class Softmax:
        @staticmethod
        def calculate(inputs):
            print("performed softmax")
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            return exp_values / np.sum(exp_values, axis=1, keepdims=True)
        @staticmethod
        def backward(inputs, dvalues):
            print("performed softmax backward")
            pass
class Loss:
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
            
            losses = -np.log(confidences)
            return np.mean(losses)
        @staticmethod
        def backward(predicted, actual):
            print("performed CrossEntropy backward")
            return - np.divide(predicted, actual)
class Layer:
    def __init__(self, input_size: int, output_size: int, activation_function: ActivationFunction):
        self.input_size = input_size
        self.output_size = output_size
        self.activation_function = activation_function
    def forward(self, inputs):
        pass
    def backward(self, ):
        pass

class Dense(Layer):
    def __init__(self, input_size: int, output_size: int, activation_function: ActivationFunction):
        super().__init__(input_size, output_size, activation_function)
        self.weights = 0.01 * np.random.randn(input_size, output_size)
        self.biases = np.zeros((1, output_size))
    
    def set_inputs(self, inputs):
        self.inputs = inputs
    
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases
        print("performed forward pass Dense")
        return self.output
    def forward_with_activation(self, inputs):
        self.output = self.activation_function.calculate(self.forward(inputs))
        return self.output
    def backward(self, dvalues):
        self.dweights = np.dot(dvalues, self.inputs.T)
        self.dbiases = np.sum(dvalues, axis=0, keepdims=True)
        return self.dweights, self.dbiases
    def backward_with_activation(self, dvalues):
        activation_dvalues = self.activation_function.backward(self.forward(self.inputs), dvalues)


class NeuralNetwork:
    def __init__(self, layers: list(Layer), loss_function: Loss):
        self.layers = layers
        self.output = None
        self.loss_function = loss_function
    def forward(self, inputs):
        self.inputs = inputs
        self.output = inputs
        for layer in self.layers:
            layer.set_inputs(self.output)
            if(layer.activation_function is not None):
                self.output = layer.forward_with_activation(self.output)
            else:
                self.output = layer.forward(self.output)
        return self.output

    def calculate_loss(self, targets):
        return self.loss_function.calculate(self.output, targets)
    
    def backward(self, targets):
        dloss = self.loss_function.backward(self.output, targets)
        for layer in reversed(self.layers):
            if(layer.activation_function is not None):
                dloss = layer.backward_with_activation(dloss)
        
X, y = spiral_data(samples=100, classes=3)
layer1 = Dense(2, 3, ActivationFunction.ReLU)
layer2 = Dense(3, 3, ActivationFunction.Softmax)
layer1.forward_with_activation(X) 
layer2.forward_with_activation(layer1.output)
print(layer2.output[:5])
print(Loss.CrossEntropy.calculate(layer2.output, y))