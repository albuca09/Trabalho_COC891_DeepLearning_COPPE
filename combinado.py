# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pyHfJxHYKH-RnueETeZxTAVTBrQttpyF
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import librosa
import librosa.display
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate, BatchNormalization, PReLU, Softmax
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical

# Diretórios de entrada
input_1_dir = "/Users/luisguedes/Desktop/PAPERS A SEREM UTILIZADOS/BANCO DE DADOS/Espectrogramas"
input_2_dir = "/Users/luisguedes/Desktop/PAPERS A SEREM UTILIZADOS/BANCO DE DADOS/espectrogramas - VGGRESNET"

# Função para carregar espectrogramas
def load_spectrograms(data_dir):
    spectrograms = []
    labels = []

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.png'):  # Presume-se que os espectrogramas são salvos como .png
                file_path = os.path.join(root, file)
                spectrogram = plt.imread(file_path)
                spectrograms.append(spectrogram)

                # Extrair rótulo do nome do arquivo (supondo que o rótulo esteja no nome do arquivo)
                label = file.split('_')[0]  # Ajuste conforme a convenção de nomes
                labels.append(label)

    return np.array(spectrograms), np.array(labels)

# Carregar dados
X1, y1 = load_spectrograms(input_1_dir)
X2, y2 = load_spectrograms(input_2_dir)

# Verificar se os dados carregados têm os mesmos rótulos
assert np.array_equal(y1, y2), "Os rótulos das duas entradas devem ser os mesmos"

# Conversão dos rótulos para categóricos
y = to_categorical(y1)

# Dividir em conjunto de treino e teste
X1_train, X1_test, X2_train, X2_test, y_train, y_test = train_test_split(X1, X2, y, test_size=0.2, random_state=42)

# Definindo as dimensões de entrada
input_shape = X1_train.shape[1:]  # Assume que os dados têm a forma (n_amostras, altura, largura, canais)

# Construindo o modelo Fusion RNN
input_1 = Input(shape=input_shape, name='Input_1')
input_2 = Input(shape=input_shape, name='Input_2')

# LSTM para a primeira entrada
x1 = LSTM(64, return_sequences=True)(input_1)
x1 = LSTM(64)(x1)

# LSTM para a segunda entrada
x2 = LSTM(64, return_sequences=True)(input_2)
x2 = LSTM(64)(x2)

# Concatenar as saídas das duas LSTM
x = Concatenate()([x1, x2])

# Camadas fully connected com BatchNormalization e PReLU
x = Dense(512)(x)
x = BatchNormalization()(x)
x = PReLU()(x)

x = Dense(256)(x)
x = BatchNormalization()(x)
x = PReLU()(x)

x = Dense(128)(x)
x = BatchNormalization()(x)
x = PReLU()(x)

x = Dense(3)(x)
x = BatchNormalization()(x)
x = PReLU()(x)

# Camada de saída
output = Softmax()(x)

# Compilando o modelo
model = Model(inputs=[input_1, input_2], outputs=output)
model.compile(optimizer=Adam(learning_rate=1e-4), loss='categorical_crossentropy', metrics=['accuracy'])

# Resumo do modelo
model.summary()

# Treinamento do modelo
history = model.fit([X1_train, X2_train], y_train, validation_data=([X1_test, X2_test], y_test), epochs=50, batch_size=32)

# Avaliação do modelo
test_loss, test_accuracy = model.evaluate([X1_test, X2_test], y_test)
print(f'Test Loss: {test_loss}, Test Accuracy: {test_accuracy}')

# Plotar a curva de aprendizado
plt.plot(history.history['accuracy'], label='Acurácia de Treino')
plt.plot(history.history['val_accuracy'], label='Acurácia de Validação')
plt.title('Acurácia durante o Treinamento')
plt.xlabel('Época')
plt.ylabel('Acurácia')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Perda de Treino')
plt.plot(history.history['val_loss'], label='Perda de Validação')
plt.title('Perda durante o Treinamento')
plt.xlabel('Época')
plt.ylabel('Perda')
plt.legend()
plt.show()