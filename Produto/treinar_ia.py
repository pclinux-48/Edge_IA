import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. CARREGAR DADOS
# Supondo que você tenha os dois arquivos. Vamos rotular: Normal = 0, Alerta = 1
df_normal = pd.read_csv('normal.csv')
df_normal['label'] = 0

df_alerta = pd.read_csv('alerta.csv')
df_alerta['label'] = 1

# Juntar tudo em um único dataset de treinamento
data = pd.concat([df_normal, df_alerta], ignore_index=True)

# 2. PRÉ-PROCESSAMENTO
X = data[['umidade', 'temperatura']].values
y = data['label'].values

# Dividir em dados de treino (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalizar os dados (Essencial para IA)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 3. CRIAR A REDE NEURAL (Arquitetura TinyML)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, activation='relu', input_shape=(2,)), # Camada de entrada + oculta
    tf.keras.layers.Dense(4, activation='relu'),                  # Camada oculta extra
    tf.keras.layers.Dense(1, activation='sigmoid')                # Saída (0 a 1)
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 4. TREINAR
print("\nIniciando treinamento da IA de Borda...")
model.fit(X_train, y_train, epochs=50, batch_size=4, validation_data=(X_test, y_test))

# 5. SALVAR O MODELO
model.save('modelo_ambiental.h5')
print("\nModelo salvo com sucesso como 'modelo_ambiental.h5'")

# Exportar as médias da normalização para usarmos no ESP8266 depois
print(f"Média: {scaler.mean_}")
print(f"Desvio: {scaler.scale_}")