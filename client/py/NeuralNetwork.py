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
        
    class CombinedSoftmaxCrossEntropy:
        @staticmethod
        def softmax(inputs):
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
            return probabilities
        
        @staticmethod
        def calculate(inputs, y_true):
            loss(softmax(inputs), y_true)
        
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
            if len(y_true.shape) == 1:
                y_true = np.eye(probabilities.shape[1])[y_true]
            return (probabilities - y_true) / samples
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
        self.activation_output = self.activation_function.calculate(self.pre_activation_output, targets)
        return self.activation_output
    
    def forward_with_combined_activation(self, inputs, targets):
        self.pre_activation_output = self.forward(inputs)
        self.activation_output = self.activation_function.calculate(self.pre_activation_output)
        return self.activation_output
    
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
class Optimizer:
    class SGD:
        def __init__(self, learning_rate: float):
            self.learning_rate = learning_rate
        def adjust_parameters(self, layer: Layer):
            # print("performing SGD adjust_parameters")
            layer.weights -= self.learning_rate * layer.dweights
            layer.biases -= self.learning_rate * layer.dbiases
class NeuralNetwork:
    def __init__(self, layers: list[Layer], optimizer: Optimizer):
        self.layers = layers
        self.output = None
        # self.loss_function = loss_function
        self.optimizer = optimizer
    def forward(self, inputs):
        self.inputs = inputs
        self.output = inputs
        for layer in self.layers:
            layer.set_inputs(self.output)
            if(layer.activation_function is not None):
                if(layer.activation_function == ActivationFunction.CombinedSoftmaxCrossEntropy):
                    self.output = layer.forward_with_combined_activation(self.output, self.targets)
                else:
                    self.output = layer.forward_with_activation(self.output)
            else:
                self.output = layer.forward(self.output)
        return self.output
    
    def set_targets(self, targets):
        self.targets = targets

    # def calculate_loss(self, targets):
    #     self.set_targets(targets)
    #     return self.loss_function.mean(self.output, targets)
    
    def backward(self):
        # dvalues = self.loss_function.backward(self.output, self.targets)
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


    
X, y = spiral_data(samples=100, classes=3)

nn = NeuralNetwork([
    Dense(2, 64, ActivationFunction.ReLU),
    Dense(64, 3, ActivationFunction.CombinedSoftmaxCrossEntropy)
], Optimizer.SGD(0.01))
nn.set_targets(y)


for epoch in range(1000):
    nn.forward(X)
    loss = nn.calculate_loss(y)
    accuracy = nn.get_accuracy()
    if not epoch % 100:
        print(f"epoch: {epoch}, accuracy: {accuracy}, loss: {loss}")
    nn.backward()
    nn.adjust_parameters()
