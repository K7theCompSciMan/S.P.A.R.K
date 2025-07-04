from command_classifier_nn import CommandClassifierSoftmax, CommandClassifierBinary

model_path = '/___'
data_path = '/___'

classifier_softmax = CommandClassifierSoftmax(data_path, 0)
classifier_binary = CommandClassifierBinary(data_path, 0)

classifier_softmax.load_model(model_path)
classifier_binary.load_model(model_path)

classifier_softmax.validate()
classifier_binary.validate()

