import pandas as pd
import numpy as np

# Configurar semente para resultados reproduzíveis
np.random.seed(42)
n_amostras = 500

# --- GERAR DADOS NORMAIS (CLIMA AMBIENTE) ---
temp_normal = np.random.normal(23.5, 0.8, n_amostras)      # Média 23.5°C
umid_normal = np.random.normal(60.0, 3.0, n_amostras)      # Média 60%
label_normal = np.zeros(n_amostras)

# --- GERAR DADOS DE ALERTA (ANOMALIA) ---
temp_alerta = np.random.normal(32.0, 1.5, n_amostras)      # Média 32°C (seu alvo de 33)
umid_alerta = np.random.normal(38.0, 4.0, n_amostras)      # Umidade cai quando esquenta
label_alerta = np.ones(n_amostras)

# Criar DataFrames
df_normal = pd.DataFrame({'umidade': umid_normal, 'temperatura': temp_normal, 'label': label_normal})
df_alerta = pd.DataFrame({'umidade': umid_alerta, 'temperatura': temp_alerta, 'label': label_alerta})

# Unificar e embaralhar
dataset = pd.concat([df_normal, df_alerta], ignore_index=True)
dataset = dataset.sample(frac=1).reset_index(drop=True)

# Salvar CSV
dataset.to_csv('dados_treinamento.csv', index=False)

print("Sucesso! Arquivo 'dados_treinamento.csv' gerado com 1000 amostras.")
print("\nExemplo dos dados (Primeiras 5 linhas):")
print(dataset.head())