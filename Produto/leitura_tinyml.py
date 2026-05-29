import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import linregress

# Configurar estilo
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'

# 1. Carregar os dados
df = pd.read_csv('leituras_tinyml.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_bat = df[(df['tipo_leitura'] == 'BATTERY') & (df['acuracia'] > 2.0)].copy()

# Filtrar EXCLUSIVAMENTE o dia 29 de Maio
mask_29 = (df_bat['timestamp'].dt.month == 5) & (df_bat['timestamp'].dt.day == 29)
df_bat_29 = df_bat[mask_29].sort_values('timestamp').copy()

# Calcular horas e Regressão Linear para o dia 29
df_bat_29['horas_passadas'] = (df_bat_29['timestamp'] - df_bat_29['timestamp'].min()).dt.total_seconds() / 3600.0
slope, intercept, r_value, p_value, std_err = linregress(df_bat_29['horas_passadas'], df_bat_29['acuracia'])
taxa_decaimento_mv_por_hora = slope * 1000

# 2. Dados da Simulação de Fogo
np.random.seed(42)
tempos_sim = pd.date_range(start='2026-05-30 10:00', periods=120, freq='2min')
temp_normal = np.random.normal(24.5, 0.5, 100)
temp_fogo = 24.5 + np.exp(np.linspace(0, 3.8, 20)) 
temp_simulada = np.concatenate([temp_normal, temp_fogo])
df_sim_fogo = pd.DataFrame({'timestamp': tempos_sim, 'temperatura': temp_simulada})

# 3. Criar os Gráficos
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# --- Gráfico 1: Decaimento (29/05) ---
ax1.plot(df_bat_29['timestamp'], df_bat_29['acuracia'], color='#1f77b4', marker='.', linestyle='', alpha=0.5, label='Leituras Reais (29/05)')
trendline = intercept + slope * df_bat_29['horas_passadas']
ax1.plot(df_bat_29['timestamp'], trendline, color='red', linewidth=2, label=f'Tendência ({abs(taxa_decaimento_mv_por_hora):.2f} mV/h)')
ax1.set_ylabel('Tensão (V)', fontsize=11)
ax1.set_title('Análise da Taxa de Decaimento da Bateria (Operação em 29/05)', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.legend()

# --- Gráfico 2: Simulação de Fogo ---
ax2.plot(df_sim_fogo['timestamp'], df_sim_fogo['temperatura'], color='#d62728', linewidth=2, label='Temperatura do Sensor')
ax2.axhline(y=45, color='orange', linestyle='--', linewidth=1.5, label='Limiar de Alerta (TinyML)')
ax2.axhline(y=60, color='darkred', linestyle='-.', linewidth=1.5, label='Limiar Crítico (Dijkstra)')
ax2.fill_between(df_sim_fogo['timestamp'], 45, 80, where=(df_sim_fogo['temperatura'] >= 45), color='red', alpha=0.1)

ax2.set_ylabel('Temperatura Simulada (°C)', fontsize=11)
ax2.set_xlabel('Tempo', fontsize=11)
ax2.set_title('Comportamento Teórico do Sistema frente a um Evento de Incêndio', fontsize=12, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.legend(loc='upper left')
ax2.set_ylim(20, 80)

# Salvar e concluir
plt.tight_layout()
plt.savefig('graficos_bateria_dia_29.png', dpi=300)