import streamlit as st
import folium
from streamlit_folium import folium_static
import networkx as nx

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Esp32 Mesh - Dijkstra", layout="wide")
st.title("🌲 Sistema Tático de Monitoramento (Esp32 TinyML + Dijkstra)")
st.markdown("Simulação de Redes em Malha na área florestal delimitada (Polígono UFLA).")

# --- 1. Definição dos Nós Sensores ---
nodes_data = {
    0: {"coords": [-21.2295, -44.9735], "name": "Esp32 Gateway (Borda Noroeste)"},
    1: {"coords": [-21.2295, -44.9705], "name": "Esp32 Nó 1 (Borda Nordeste)"},
    2: {"coords": [-21.2315, -44.9735], "name": "Esp32 Nó 2 (Centro-Oeste)"},
    3: {"coords": [-21.2315, -44.9705], "name": "Esp32 Nó 3 (Centro)"},
    4: {"coords": [-21.2315, -44.9675], "name": "Esp32 Nó 4 (Centro-Leste)"},
    5: {"coords": [-21.2335, -44.9735], "name": "Esp32 Nó 5 (Sul-Oeste)"},
    6: {"coords": [-21.2335, -44.9705], "name": "Esp32 Nó 6 (Sul-Centro)"},
    7: {"coords": [-21.2335, -44.9675], "name": "Esp32 Nó 7 (Sul-Leste)"},
    8: {"coords": [-21.2355, -44.9705], "name": "Esp32 Nó 8 (Extremo Sul)"},
    9: {"coords": [-21.2355, -44.9675], "name": "Esp32 Nó 9 (Extremo Sudeste)"}
}

G = nx.Graph()
for node_id, info in nodes_data.items():
    G.add_node(node_id, pos=info["coords"], name=info["name"])

edges = [
    (0, 1), (0, 2), 
    (1, 3), (2, 3), (2, 5),
    (3, 4), (3, 6), (4, 7), 
    (5, 6), (6, 7), (6, 8),
    (7, 9), (8, 9)
]
for u, v in edges:
    G.add_edge(u, v, weight=1)

# --- 2. Painel de Controle Inteligente ---
st.sidebar.header("🔥 Controle de Incidentes")

fire_nodes = st.sidebar.multiselect(
    "Focos de Incêndio (Selecione os Nós):", 
    options=list(range(1, 10)),
    format_func=lambda x: f"Esp32 Nó {x}"
)

mode = st.sidebar.radio(
    "Objetivo da Missão Tática:",
    options=["Rota de Evasão (Civis)", "Rota de Incursão (Bombeiros)"]
)

st.sidebar.markdown("---")

# Dinâmica de Origem e Destino baseada na Missão
if mode == "Rota de Evasão (Civis)":
    start_node = st.sidebar.selectbox("Onde os civis estão?", options=list(range(1, 10)), index=8)
    end_node = 0  # Gateway é a fuga
    st.sidebar.info(f"📍 Destino Automático: {nodes_data[end_node]['name']}")
else:
    start_node = 0  # Bombeiros saem da Base
    st.sidebar.info(f"📍 Origem Automática: {nodes_data[start_node]['name']}")
    
    if fire_nodes:
        end_node = fire_nodes[0] # Vai direto para o foco principal de incêndio
        st.sidebar.warning(f"🚨 Destino de Combate: {nodes_data[end_node]['name']}")
    else:
        end_node = st.sidebar.selectbox("Destino da patrulha:", options=list(range(1, 10)), index=8)

# --- 3. Dijkstra com Pesos Condicionais ---
for f_node in fire_nodes:
    # Se a missão for dos bombeiros, não aplica peso proibitivo no destino final para permitir a chegada
    if mode == "Rota de Incursão (Bombeiros)" and f_node == end_node:
        continue 
    for neighbor in list(G.neighbors(f_node)):
        G[f_node][neighbor]['weight'] = 999

shortest_path = []
try:
    path_length = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
    
    if path_length >= 999:
         st.error("🚨 ÁREA ISOLADA! Não há caminhos seguros devido à propagação das chamas.")
    else:
         shortest_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
         st.success(f"✅ ROTA CALCULADA: {' ➔ '.join([str(n) for n in shortest_path])}")
except nx.NetworkXNoPath:
    st.error("🚨 Nenhuma rota física disponível.")

# --- 4. Renderização Cartográfica ---
m = folium.Map(location=[-21.2325, -44.9705], zoom_start=16, tiles="OpenStreetMap")

for u, v in G.edges():
    coord_u = nodes_data[u]["coords"]
    coord_v = nodes_data[v]["coords"]
    if u in fire_nodes or v in fire_nodes:
        folium.PolyLine([coord_u, coord_v], color="red", weight=3, dash_array="6, 6").add_to(m)
    else:
        folium.PolyLine([coord_u, coord_v], color="green", weight=1.5, opacity=0.6).add_to(m)

if len(shortest_path) > 1:
    path_coords = [nodes_data[node]["coords"] for node in shortest_path]
    route_color = "blue" if mode == "Rota de Evasão (Civis)" else "darkorange"
    folium.PolyLine(path_coords, color=route_color, weight=6, opacity=0.9).add_to(m)

for node_id, info in nodes_data.items():
    if node_id == start_node and mode == "Rota de Evasão (Civis)":
        color, icon = "blue", "user"
    elif node_id == 0:
        color, icon = "green", "home"
    elif node_id in fire_nodes:
        color, icon = "red", "fire"
    elif node_id == end_node:
        color, icon = "darkorange" if mode != "Rota de Evasão (Civis)" else "blue", "flag"
    else:
        color, icon = "cadetblue", "leaf"
        
    folium.Marker(
        location=info["coords"],
        popup=info["name"],
        icon=folium.Icon(color=color, icon=icon)
    ).add_to(m)

folium_static(m, width=1050, height=650)