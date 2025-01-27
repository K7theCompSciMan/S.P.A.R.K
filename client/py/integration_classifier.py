from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, Dropout, GlobalMaxPooling1D, LSTM, Bidirectional, BatchNormalization
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from collections import Counter
from difflib import get_close_matches

class IntegrationClassifier:
    def __init__(self, max_words=10000, max_length=30, embedding_dim=200):
        self.max_words = max_words
        self.max_length = max_length
        self.embedding_dim = embedding_dim
        self.tokenizer = Tokenizer(num_words=max_words, oov_token='<OOV>')
        self.model = None
        
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        except:
            pass
        
        self.lemmatizer = WordNetLemmatizer()
        
        self.integration_indicators = {
            'media': {
                'actions': ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward'],
                'objects': {'song': 'music', 'video': 'film', 'playlist': 'music', 'track': 'music', 'album': 'music', 'movie': 'film', 'episode': 'film', 'audio': 'music', 'music': 'music', 'stream': 'film'},
                'platforms': ['spotify', 'youtube', 'netflix', 'pandora', 'apple music', 'amazon music', 'twitch'],
                'modifiers': ['next', 'previous', 'current', 'random', 'favorite', 'liked', 'recommended']
            },
            'management': {
                'actions': ['create', 'update', 'delete', 'assign', 'schedule', 'track', 'monitor', 'complete', 'start', 'finish'],
                'objects': {'task': 'management', 'project': 'management', 'milestone': 'management', 'deadline': 'management', 'meeting': 'management', 'event': 'management', 'reminder': 'management', 'notification': 'management', 'alert': ''},
                'attributes': ['priority', 'status', 'progress', 'due date', 'assigned to', 'category', 'label'],
                'platforms': ['asana', 'trello', 'jira', 'monday', 'basecamp', 'clickup', 'notion']
            },
            'communication': {
                'actions': ['send', 'receive', 'reply', 'forward', 'compose', 'call', 'message', 'chat', 'share', 'text', 'email', 'call'],
                'objects': {'email': 'communication', 'sms': 'communication', 'call': 'communication', 'chat': 'communication', 'message': 'communication', 'email': 'communication', 'text': 'communication', 'call': 'communication'},
                'platforms': ['slack', 'teams', 'zoom', 'discord', 'whatsapp', 'telegram', 'gmail', 'sms'],
                'modifiers': ['urgent', 'private', 'group', 'direct', 'team', 'channel']
            }
        }
        # self.command_patterns = {
        #     'actions': ['help', 'exit', 'quit', 'clear', 'show', 'list', 'version', 'about', 'info', 'run', 'launch', 'set', 'open', 'start'],
        #     'objects': ['screen', 'settings', 'preferences', 'profile', 'system', 'help'],
        #     'modifiers': ['all', 'system', 'user', 'admin']
        # }
    # def preprocess_text(self, text):
    #     text = text.lower().strip()
        
    #     tokens = word_tokenize(text)
        
    #     tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
    #     tokens = [token for token in tokens if token.isalnum()]
        
    #     return ' '.join(tokens)

    # def prepare_data(self, texts, labels):
    #     processed_texts = []
    #     for text in texts:
    #         processed_text = self.preprocess_text(text)
    #         processed_texts.append(processed_text)
        
    #     self.tokenizer.fit_on_texts(processed_texts)
        
    #     sequences = self.tokenizer.texts_to_sequences(processed_texts)
        
    #     padded_sequences = pad_sequences(sequences, maxlen=self.max_length, padding='post', truncating='post')
        
    #     return padded_sequences, labels
    
    # def build_model(self, num_classes):
    #     model = Sequential([
    #         Embedding(self.max_words, self.embedding_dim, input_length=self.max_length),
            
    #         Bidirectional(LSTM(128, return_sequences=True)),
    #         BatchNormalization(),
    #         Dropout(0.3),
            
    #         Conv1D(128, 3, activation='relu', padding='same'),
    #         BatchNormalization(),
            
    #         Bidirectional(LSTM(64)),
    #         BatchNormalization(),
    #         Dropout(0.3),
            
    #         Dense(256, activation='relu', kernel_regularizer=l2(0.01)),
    #         BatchNormalization(),
    #         Dropout(0.5),
    #         Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
    #         BatchNormalization(),
    #         Dropout(0.3),
    #         Dense(num_classes, activation='softmax')
    #     ])
        
    #     optimizer = Adam(learning_rate=0.001)
    #     model.compile(
    #         optimizer=optimizer,
    #         loss='categorical_crossentropy',
    #         metrics=['accuracy']
    #     )
        
    #     self.model = model
    #     return model
    
    # def generate_training_data_file(self, filename='training_data.json', samples_per_category=10000):
    #     training_data = []
        
    #     for integration_type, word_categories in self.integration_indicators.items():
    #         for _ in range(samples_per_category):
    #             if random.random() < 0.75:
    #                 platform = random.choice(word_categories['platforms'])
    #                 action = random.choice(word_categories['actions'])
    #                 obj = random.choice(word_categories['objects'])
                    
    #                 patterns = [
    #                     f"Hey spark, {action} {obj} on {platform}",
    #                     f"Hey spark, using {platform} {action} {obj}",
    #                     f"Hey spark, {platform} {action} {obj}",
    #                 ]
    #                 command = random.choice(patterns)
    #             else:
    #                 action = random.choice(word_categories['actions'])
    #                 obj = random.choice(word_categories['objects'])
    #                 command = f"{action} {obj}"

    #             if random.random() < 0.3 and 'modifiers' in word_categories:
    #                 modifier = random.choice(word_categories['modifiers'])
    #                 command = f"{modifier} {command}"

    #             training_data.append({
    #                 'text': command.lower(),
    #                 'label': integration_type
    #             })
        
    #     for _ in range(samples_per_category):
    #         action = random.choice(self.command_patterns['actions'])
    #         if random.random() < 0.5:
    #             obj = random.choice(self.command_patterns['objects'])
    #             command = f"{action} {obj}"
    #         else:
    #             command = action

    #         if random.random() < 0.3:
    #             modifier = random.choice(self.command_patterns['modifiers'])
    #             command = f"{command} {modifier}"

    #         training_data.append({
    #             'text': command.lower(),
    #             'label': 'command'
    #         })
        
    #     random.shuffle(training_data)
        
    #     with open(filename, 'w') as f:
    #         json.dump(training_data, f, indent=2)
        
    #     return filename

    # def load_training_data(self, filename='training_data.json'):
    #     with open(filename, 'r') as f:
    #         data = json.load(f)
        
    #     texts = [item['text'] for item in data]
    #     labels = [item['label'] for item in data]
        
    #     return texts, pd.get_dummies(labels).values

    # def train(self, data_file='training_data.json', epochs=50, batch_size=32, validation_split=0.2):
    #     texts, labels = self.load_training_data(data_file)
    #     X, y = self.prepare_data(texts, labels)
        
    #     label_indices = np.argmax(labels, axis=1)
    #     class_weights = compute_class_weight(
    #         class_weight='balanced',
    #         classes=np.unique(label_indices),
    #         y=label_indices
    #     )
    #     class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        
    #     X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split, random_state=42)
        
    #     callbacks = [
    #         EarlyStopping(
    #             monitor='val_accuracy',
    #             patience=5,
    #             restore_best_weights=True,
    #             min_delta=0.01
    #         ),
    #         ReduceLROnPlateau(
    #             monitor='val_loss',
    #             factor=0.5,
    #             patience=3,
    #             min_lr=0.00001
    #         ),
    #         ModelCheckpoint(
    #             'best_integration_model.keras',
    #             monitor='val_accuracy',
    #             save_best_only=True,
    #             mode='max'
    #         )
    #     ]
        
    #     history = self.model.fit(
    #         X_train, y_train,
    #         epochs=epochs,
    #         batch_size=batch_size,
    #         validation_data=(X_val, y_val),
    #         callbacks=callbacks,
    #         class_weight=class_weight_dict
    #     )
        
    #     return history
    
    # def predict(self, text):
    #     processed_text = self.preprocess_text(text)
        
    #     sequence = self.tokenizer.texts_to_sequences([processed_text])
    #     padded_sequence = pad_sequences(sequence, maxlen=self.max_length, padding='post', truncating='post')
        
    #     prediction = self.model.predict(padded_sequence, verbose=0)
        
    #     class_names = list(self.integration_indicators.keys()) + ['command']
        
    #     predicted_class = class_names[np.argmax(prediction)]
    #     confidence = float(np.max(prediction))
        
    #     return {
    #         'class': predicted_class,
    #         'confidence': confidence,
    #         'probabilities': {
    #             class_name: float(prob)
    #             for class_name, prob in zip(class_names, prediction[0])
    #         }
    #     }

    # def plot_training_history(self, history):
    #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
    #     ax1.plot(history.history['accuracy'], label='Training')
    #     ax1.plot(history.history['val_accuracy'], label='Validation')
    #     ax1.set_title('Model Accuracy')
    #     ax1.set_xlabel('Epoch')
    #     ax1.set_ylabel('Accuracy')
    #     ax1.legend()
        
    #     ax2.plot(history.history['loss'], label='Training')
    #     ax2.plot(history.history['val_loss'], label='Validation')
    #     ax2.set_title('Model Loss')
    #     ax2.set_xlabel('Epoch')
    #     ax2.set_ylabel('Loss')
    #     ax2.legend()
        
    #     plt.tight_layout()
    #     plt.show()
        
    def predict_algorithm(self, text):
        action = None
        modifier = None
        object = None
        integration_type = None
        platform = None
        for category in self.integration_indicators:
            for word in text.split(' '):
                print(self.integration_indicators[category]['actions'])
                action_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['actions'], n=1, cutoff=0.6)
                if action_matches:
                    action = action_matches[0]
                    print(f"got match for action {action}")
                    for word in text.split(' '):
                        modifier_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['modifiers'], n=1, cutoff=0.6)
                        if modifier_matches:
                            print(f"got match for modifier {modifier_matches[0]}")
                            modifier = modifier_matches[0]
                            break
                        else:
                            print(f"no modifier match for {word}")
                            modifier = None
                    for word in text.split(' '):
                        object_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['objects'].keys(), n=1, cutoff=0.6)
                        object = object_matches[0] if object_matches else None
                        if object_matches:
                            print(f"got match for object {object_matches[0]}")
                            integration_type = self.integration_indicators[category]['objects'][object_matches[0]]
                            break
                        else:
                            integration_type = category
                    for word in text.split(' '):
                        platform_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['platforms'], n=1, cutoff=0.6)
                        if platform_matches:
                            print(f"got match for platform {platform_matches[0]}")
                            platform = platform_matches[0]
                            return action, modifier, object, platform,integration_type
                        else:
                            print(f"no platform match for {word}")
                            platform = None
        return action, modifier, object, platform,integration_type

if __name__ == '__main__':
    classifier = IntegrationClassifier()
    # data_file = classifier.generate_training_data_file(samples_per_category=10000)
    # classifier.build_model(num_classes=4)
    # history = classifier.train(
    #     data_file=data_file,
    #     epochs=50,
    #     batch_size=64)
    # classifier.plot_training_history(history)
    
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        # result = classifier.predict(text)
        # print(result)
        result = classifier.predict_algorithm(text)
        print(result)        