import pandas as pd
import numpy as np
import tensorflow as tf
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Evita bugs de conversão no Mac M4
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# 1. CARREGAR DADOS SINTÉTICOS
# Agora lemos o arquivo unificado que geramos
data = pd.read_csv('dados_treinamento.csv')

# 2. PRÉ-PROCESSAMENTO
# Garantindo a ordem: 0 = Umidade, 1 = Temperatura
X = data[['umidade', 'temperatura']].values
y = data['label'].values

# Dividir em dados de treino (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalizar os dados (O segredo do sucesso no ESP8266)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 3. CRIAR A REDE NEURAL (Arquitetura TinyML)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, activation='relu', input_shape=(2,)), 
    tf.keras.layers.Dense(4, activation='relu'),                  
    tf.keras.layers.Dense(1, activation='sigmoid')                
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 4. TREINAR
print("\nIniciando treinamento da IA com dados sintéticos...")
model.fit(X_train, y_train, epochs=50, batch_size=8, validation_data=(X_test, y_test))

# 5. SALVAR O MODELO
model.save('modelo_ambiental.h5')
print("\nModelo salvo com sucesso!")

# 6. EXPORTAR PARÂMETROS PARA O ESP8266 (COPIE ESTES VALORES)
print("\n" + "="*40)
print("COPIE ESTES VALORES PARA O SEU MAIN.CPP")
print("="*40)
print(f"float media_umid = {scaler.mean_[0]:.4f};")
print(f"float media_temp = {scaler.mean_[1]:.4f};")
print(f"float desvio_umid = {scaler.scale_[0]:.4f};")
print(f"float desvio_temp = {scaler.scale_[1]:.4f};")
print("="*40)