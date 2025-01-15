from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, Dropout, GlobalMaxPooling1D, LSTM, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


class CommandClassifier:
    def __init__(self, max_words=20000, max_length=50, embedding_dim=100):
        self.max_words = max_words
        self.max_length = max_length
        self.embedding_dim = embedding_dim
        self.tokenizer = Tokenizer(num_words=max_words)
        self.model = None
        self.action_verbs = {
            'turn ', 'set ', 'play ', 'open ', 'close ', 'send ', 'call ', 'start ',
            'stop ', 'pause ', 'create ', 'delete ', 'show ', 'hide ', 'increase ',
            'decrease ', 'adjust ', 'schedule ', 'remind ', 'add ', 'remove ', 'find ',
            'search ', 'navigate ', 'go ', 'get ', 'fetch ', 'bring ', 'move ', 'change ',
            'launch ', 'run ', 'execute ', 'start ', 'restart ', 'stop ', 'pause ',
        }
        
    def preprocess_text(self, text):
        text = text.lower()
        
        text = text.replace('?', ' ? ')
        
        
        text = ''.join([char for char in text if char.isalnum() or char.isspace() or char == '?'])
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english')) - {'what', 'how', 'when', 'where', 'why', 'who'}
        tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(tokens)
        
    def build_model(self):
        model = Sequential([
            Embedding(self.max_words, self.embedding_dim, input_length=self.max_length),
            
            Bidirectional(LSTM(128, return_sequences=True)),
            Dropout(0.3),
            
            Bidirectional(LSTM(64, return_sequences=True)),
            Dropout(0.3),
            
            Conv1D(128, 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            Conv1D(256, 3, activation='relu', padding='same'),
            MaxPooling1D(2),
            
            GlobalMaxPooling1D(),
            Dense(256, activation='relu', kernel_regularizer=l2(0.01)),
            Dropout(0.5),
            Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
            Dropout(0.3),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        return model
    
    def train(self, data_path, epochs=50, batch_size=32):
        df = pd.read_csv(data_path)
        df = df.drop_duplicates()
        
        texts = df['Text'].apply(self.preprocess_text)
        labels = df['IsAction']
        
        self.tokenizer.fit_on_texts(texts)
        sequences = self.tokenizer.texts_to_sequences(texts)
        X = pad_sequences(sequences, maxlen=self.max_length)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        model_checkpoint = ModelCheckpoint(
            'best_model.keras',
            monitor='val_accuracy',
            save_best_only=True
        )
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, model_checkpoint]
        )
        
        return history
    
    def predict(self, text):
        processed_text = self.preprocess_text(text)
        sequence = self.tokenizer.texts_to_sequences([processed_text])
        padded = pad_sequences(sequence, maxlen=self.max_length)
        prediction = self.model.predict(padded)[0][0]
        
        is_likely_question = (('?' in text or 
                            any(text.lower().startswith(wh) 
                                for wh in ['what', 'why', 'where', 'when', 'how', 'who'])))
        is_likely_command = (any(verb in text.lower() for verb in self.action_verbs))
        
        threshold = 0.6 if not is_likely_question else 0.7
        
        if is_likely_question:
            prediction = prediction * 0.7  
        elif is_likely_command:
            prediction = prediction * 1.3  
        return {
            'is_action': bool(prediction > threshold),
            'confidence': float(prediction),
            'classification': 'Action/Command' if prediction > threshold else 'Not a Command',
            'likely_question_indicators': is_likely_question,
            'likely_command': is_likely_command
        }

def plot_training_history(history):
    metrics = ['accuracy', 'precision', 'recall']
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, metric in enumerate(metrics):
        axes[i].plot(history.history[metric], '-', label=f'Training {metric}')
        axes[i].plot(history.history[f'val_{metric}'], ':', label=f'Validation {metric}')
        axes[i].set_title(f'Training and Validation {metric.capitalize()}')
        axes[i].set_xlabel('Epoch')
        axes[i].set_ylabel(metric.capitalize())
        axes[i].legend()
    
    plt.tight_layout()
    plt.show()





if __name__ == "__main__":
    classifier = CommandClassifier()
    classifier.build_model()
    # history = classifier.train('actions.csv')
    # plot_training_history(history)
    
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        
        result = classifier.predict(text)
        print(f"\nClassification: {result['classification']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Likely Question Indicators: {result['likely_question_indicators']}")
        print(f"Likely Command: {result['likely_command']}")
        
        


