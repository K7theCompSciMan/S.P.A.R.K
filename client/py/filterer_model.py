from keras.models import Sequential
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, Dropout, GlobalMaxPooling1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.regularizers import l2
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt

nltk.download('punkt')
nltk.download('stopwords')

max_words = 20000
max_length = 50


model = Sequential()
model.add(Embedding(max_words, 32, input_length=max_length))
model.add(MaxPooling1D(5))
model.add(Dropout(0.5))  # Dropout after pooling
model.add(Conv1D(32, 7, activation='relu'))
model.add(GlobalMaxPooling1D())
model.add(Dropout(0.5))  # Dropout before the dense layer
model.add(Dense(1, activation='sigmoid', kernel_regularizer=l2(0.01)))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

df = pd.read_csv('C:\\Users\\k7ran\\Code\\S.P.A.R.K\\client\\py\\actions.csv')
df = df.drop_duplicates()

def remove_stop_words(text):
    text = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    text = [word for word in text if word.isalpha() and not word in stop_words]
    return ' '.join(text)
    
x = df.apply(lambda row: row['Text'], axis=1)
y = df['IsAction']
print(x[:5])
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(x)
sequences = tokenizer.texts_to_sequences(x)
x = pad_sequences(sequences, maxlen=max_length)

hist = model.fit(x, y, validation_split=0.2, epochs=10, batch_size=32)
acc = hist.history['accuracy']
val = hist.history['val_accuracy']
epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, '-', label='Training accuracy')
plt.plot(epochs, val, ':', label='Validation accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()

while True:
    text = input("Enter text: ")
    if text == 'q':
        break
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=max_length)
    pred = model.predict(padded)
    print(pred[0][0])

