from command_classifier_nn import CommandClassifierSoftmax, CommandClassifierBinary

# model_path = 'nn_scratch_model_dataset_claude.json'
validation_data_path = 'validation_data.json'
data_path = 'nn_scratch_data_direct_and_ai.json'

classifier_softmax = CommandClassifierSoftmax(data_path, 4000)
classifier_binary = CommandClassifierBinary(data_path, 4000)

# classifier_softmax.load_model('nn_scratch_data_adjusted_tone.json')
# classifier_binary.load_model('nn_scratch_data_adjusted_tone.json')

classifier_softmax.train('classifier_models/softmax_direct_and_ai.json', epochs=5001)
classifier_binary.train('classifier_models/binary_direct_and_ai.json', epochs=5001)

#direct and ai is not good (doesn't work for binary)
#tone adjusted is not bad (doesn't get hibernate and sleep very well)
#

classifier_softmax.validate()
classifier_binary.validate()

while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        result = classifier_softmax.predict(text)
        print(result)
        result = classifier_binary.predict(text)
        print(result)