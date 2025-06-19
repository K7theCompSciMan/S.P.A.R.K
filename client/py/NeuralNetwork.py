import numpy as np
import nnfs
from nnfs.datasets import spiral_data
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
        self.set_inputs(inputs)
        self.output = np.dot(inputs, self.weights) + self.biases
        # print("performed forward pass Dense")
        return self.output
    def forward_with_activation(self, inputs):
        self.pre_activation_output = self.forward(inputs)
        self.activation_output = self.activation_function.calculate(self.forward(inputs))
        return self.activation_output

    def adjust_parameters(self):
        self.weights -= 0.01 * self.dweights
        self.biases -= 0.01 * self.dbiases
    
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


class NeuralNetwork:
    def __init__(self, layers: list[Layer], loss_function: Loss):
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
    
    def set_targets(self, targets):
        self.targets = targets

    def calculate_loss(self, targets):
        self.set_targets(targets)
        return self.loss_function.mean(self.output, targets)
    
    def backward(self):
        dvalues = self.loss_function.backward(self.output, self.targets)
        for index, layer in enumerate(reversed(self.layers)):
            if(layer.activation_function is not None):
                dvalues = layer.backward_with_activation(dvalues)  
            
    def adjust_parameters(self):
        for layer in self.layers:
            layer.adjust_parameters()

    def get_accuracy(self):
        targets = self.targets.copy()
        predictions = np.argmax(self.output, axis=1)
        if(len(targets.shape) == 2):
            targets = np.argmax(self.targets, axis=1)
        return np.mean(predictions == targets)
    
X, y = spiral_data(samples=100, classes=3)

nn = NeuralNetwork([
    Dense(2, 3, ActivationFunction.ReLU),
    Dense(3, 3, ActivationFunction.Softmax)
], Loss.CrossEntropy)
nn.set_targets(y)
nn.forward(X)
print(nn.get_accuracy())

nn.backward()
nn.adjust_parameters()

nn.forward(X)
print(nn.get_accuracy())

for i in range(1000):    
    nn.forward(X)
    print(nn.get_accuracy())
    nn.backward()
    nn.adjust_parameters()
