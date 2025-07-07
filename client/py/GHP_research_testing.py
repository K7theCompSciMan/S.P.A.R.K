from command_classifier_nn import CommandClassifierSoftmax, CommandClassifierBinary

# model_path = 'nn_scratch_model_dataset_claude.json'
validation_data_path = 'validation_data.json'
data_path = 'nn_scratch_data_mixed_updated.json'

classifier_softmax = CommandClassifierSoftmax(data_path, 3000)
classifier_binary = CommandClassifierBinary(data_path, 3000)

classifier_softmax.load_model('classifier_models/softmax_mixed_updated.json')
classifier_binary.load_model('classifier_models/binary_mixed_updated.json')

# classifier_softmax.train('classifier_models/softmax_mixed_updated.json', epochs=101)
# classifier_softmax.plot_history()
# classifier_binary.train('classifier_models/binary_mixed_updated.json', epochs=101)
# classifier_binary.plot_history()

#direct and ai is not good (doesn't work for binary)
#tone adjusted is not bad (doesn't get hibernate and sleep very well)
#large varied is not very good (does't get hibernate and sleep, or open chrome etc.. overfitted)
#device specific is pretty good (defaults to command, but get's questions p well)
#mixed updated is best  (defaults to command, but more generalized for questions so rlly good)
    # some false postives for questions, but overall not bad
    # implement safe case when processing commands & add to logs
classifier_softmax.validate()
classifier_binary.validate()

while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        result = classifier_softmax.predict(text)
        print("softmax: result: " + result['result'] + f" | confidence: {result['confidence']:.5f}")
        result = classifier_binary.predict(text)
        print("binary: result: " + result['result'] + f" | confidence: {result['confidence']:.5f}")