# edgeIA

Projeto de monitoramento ambiental com TinyML na borda, backend em PHP, persistencia em MySQL e uma interface em Streamlit para simulacao tática. O objetivo do sistema e ler temperatura/umidade em um ESP8266, executar uma inferencia local para classificar a leitura como `NORMAL` ou `ALERTA`, enviar os dados ao servidor, exibi-los em um dashboard web e apoiar a tomada de decisao com rotas de combate e fuga para um provavel incendio.

## Visao Geral

O repositorio contem tres blocos principais:

1. Aplicacao web na raiz do projeto:
   - recebe dados do dispositivo via HTTP;
   - oferece um micro-broker UDP alternativo;
   - salva leituras no MySQL;
   - mostra as ultimas inferencias e o nivel de bateria em uma pagina PHP.

2. Aplicacao analitica em Python/Streamlit na raiz:
   - renderiza um mapa interativo com `folium`;
   - modela uma rede em malha com `networkx`;
   - permite selecionar focos de incendio;
   - calcula rotas de fuga para civis e rotas de incursao para bombeiros com Dijkstra.

3. Projeto embarcado e pipeline de IA em `Produto/`:
   - gera dados sinteticos e/ou usa CSVs reais;
   - treina uma rede neural pequena em Python/TensorFlow;
   - converte o modelo para TensorFlow Lite e depois para `model_data.h`;
   - embarca o modelo no firmware do ESP8266 via PlatformIO.

## Arquitetura

```text
Sensor DHT11 + bateria
        |
        v
ESP8266 / NodeMCU
  - le umidade e temperatura
  - normaliza os dados
  - roda inferencia TinyML
  - envia HTTP POST para api_receptor.php
  - opcionalmente poderia enviar via UDP
        |
        v
Backend PHP
  - api_receptor.php / api.php / udp_broker.php
        |
        v
MySQL
  - tabela leituras_tinyml
        |
        v
Dashboard index.php
        
Camada de apoio tatico
  - app.py (Streamlit + Folium + Dijkstra)
```

## Estrutura Do Repositorio

```text
edgeIA/
|-- api.php
|-- api_receptor.php
|-- app.py
|-- bd.sql
|-- conexao.php
|-- index.php
|-- main.cpp
|-- requirements.txt
|-- udp_broker.php
`-- Produto/
    |-- platformio.ini
    |-- src/
    |   |-- main.cpp
    |   `-- model_data.h
    |-- antigos/
    |   |-- main.cpp
    |   `-- model_data_antigo.h
    |-- gerar_dados.py
    |-- treinar_ia.py
    |-- treinar_ia2.py
    |-- converter_tflite.py
    |-- dataset.py
    |-- normal.csv
    |-- alerta.csv
    |-- dados_treinamento.csv
    `-- modelo_ambiental.h5
```

## Aplicacao Web

### `conexao.php`

Arquivo simples de conexao com MySQL via `mysqli`. Define:

- host `localhost`;
- usuario `root`;
- senha vazia;
- banco `monitoramento_iot`;
- charset `utf8`.

Esse arquivo e incluido por `index.php` e `api_receptor.php`.

### `index.php`

E o dashboard principal do sistema. O arquivo:

- atualiza automaticamente a cada 10 segundos;
- busca as 10 ultimas leituras onde `tipo_leitura = 'IA'`;
- mostra `device_id`, classe detectada e o valor salvo em `acuracia`;
- interpreta a leitura de bateria procurando `tipo_leitura = 'BATTERY'`;
- converte a voltagem em percentual com a funcao `calcularPercentual()`.

Observacao importante: no dashboard, o campo `acuracia` esta sendo usado como temperatura exibida para leituras de IA e como voltagem para leituras de bateria. Na pratica, ele funciona como um campo numerico generico da leitura.

### `api_receptor.php`

Endpoint principal usado pelo firmware atual do ESP8266. Recebe `POST` com os campos:

- `device_id`
- `status`
- `valor`
- `tipo`

Em seguida grava na tabela `leituras_tinyml` com `prepared statement`.

Fluxo esperado:

```text
ESP8266 -> HTTP POST -> api_receptor.php -> INSERT no MySQL
```

### `api.php`

Endpoint alternativo em JSON. Ele:

- aceita apenas requisicoes `POST`;
- le o corpo JSON com `php://input`;
- valida `device_id`, `classe` e `precisao`;
- grava os dados usando `PDO`;
- responde em JSON.

Esse arquivo parece ter sido feito para uma versao anterior ou alternativa da integracao, porque o firmware atual aponta para `api_receptor.php`, nao para `api.php`.

### `udp_broker.php`

Micro-broker UDP executado em loop infinito na porta `9999`. Ele:

- abre um socket UDP;
- recebe mensagens no formato `device_id,classe,valor`;
- persiste os dados no MySQL usando `PDO`.

Esse componente oferece uma alternativa a comunicacao HTTP, mas nao e o caminho usado pelo `Produto/src/main.cpp`.

### `bd.sql`

Cria o banco `monitoramento_iot` e a tabela `leituras_tinyml` com:

- `id`
- `device_id`
- `classe_detectada`
- `acuracia`
- `timestamp`

## Aplicacao Tatica Em Streamlit

### `app.py`

O arquivo `app.py` adiciona uma camada de simulacao e apoio operacional ao projeto. Em vez de apenas mostrar leituras, ele representa uma malha de nos ESP32 sobre uma area florestal e calcula rotas com base em focos de incendio informados pelo usuario.

O aplicativo usa:

- `streamlit` para a interface;
- `folium` para o mapa;
- `streamlit_folium` para embutir o mapa no dashboard;
- `networkx` para modelar o grafo e executar o algoritmo de Dijkstra.

### Como a simulacao funciona

O codigo define:

- 10 nos com coordenadas geograficas aproximadas;
- um grafo nao direcionado com conexoes entre os nos;
- pesos padrao `1` para arestas seguras;
- penalizacao de peso `999` em arestas ligadas a nos em chamas.

Com isso, o aplicativo calcula a menor rota viavel em dois modos:

1. `Rota de Evasao (Civis)`
   - o usuario informa onde os civis estao;
   - o destino e automaticamente o no `0`, tratado como gateway e ponto de fuga;
   - nos afetados pelo incendio passam a ser evitados.

2. `Rota de Incursao (Bombeiros)`
   - a origem e automaticamente o no `0`;
   - o destino principal passa a ser o primeiro foco de incendio selecionado;
   - o algoritmo evita demais areas criticas, mas permite chegar ao foco principal do combate.

### Saidas visuais do mapa

O mapa renderizado em `folium` mostra:

- arestas verdes para caminhos normais;
- arestas vermelhas tracejadas para regioes impactadas pelo incendio;
- rota azul para evasao de civis;
- rota laranja escura para incursao dos bombeiros;
- marcadores coloridos para origem, destino, gateway e focos de incendio.

Se nao houver rota segura, a interface informa que a area esta isolada ou que nao existe caminho fisico disponivel.

## Firmware Embarcado

### `Produto/platformio.ini`

Define o ambiente PlatformIO:

- plataforma `espressif8266`;
- placa `nodemcuv2`;
- framework `arduino`;
- bibliotecas `DHT`, `Adafruit Unified Sensor` e `EloquentTinyML`.

### `Produto/src/main.cpp`

E o firmware principal do projeto. O fluxo dele e:

1. conecta ao Wi-Fi;
2. inicializa o sensor DHT11;
3. carrega o modelo TinyML embarcado em `model_data.h`;
4. le umidade e temperatura;
5. normaliza os dados com medias e desvios fixos no codigo;
6. executa `ml.predict(input)`;
7. converte a saida em `NORMAL` ou `ALERTA`;
8. envia o resultado via HTTP para `api_receptor.php`;
9. a cada 60 segundos, mede a bateria na entrada analogica e envia uma leitura do tipo `BATTERY`.

Detalhes relevantes:

- o endpoint do servidor esta em `serverUrl`;
- `ultima_temp` implementa uma histerese simples para evitar envio excessivo;
- `yield()` ajuda a evitar reset do watchdog do ESP8266;
- o campo enviado em `valor` representa temperatura para inferencia e voltagem para bateria.

### `main.cpp` na raiz

Existe um `main.cpp` adicional na raiz do repositorio com logica muito parecida com `Produto/src/main.cpp`. Pela estrutura do projeto, ele parece ser uma copia, versao de teste ou backup fora do fluxo principal do PlatformIO. O alvo mais consistente para compilacao e o arquivo dentro de `Produto/src/`.

### `Produto/antigos/main.cpp`

Versao anterior do firmware. Nessa variante:

- a inferencia ocorre localmente;
- os resultados sao impressos na serial;
- nao ha envio HTTP;
- o foco parece ser apenas validar o comportamento do modelo na borda.

## Pipeline De IA

### `Produto/gerar_dados.py`

Gera um dataset sintetico com 1000 amostras:

- 500 leituras `normal`;
- 500 leituras `alerta`;
- colunas `umidade`, `temperatura` e `label`.

Salva o resultado em `dados_treinamento.csv`.

### `Produto/treinar_ia.py`

Treina um modelo usando dois CSVs separados:

- `normal.csv`
- `alerta.csv`

Etapas do script:

1. carrega os CSVs e cria os labels;
2. separa treino e teste;
3. normaliza com `StandardScaler`;
4. cria uma rede densa pequena:
   - camada com 8 neuronios ReLU;
   - camada com 4 neuronios ReLU;
   - saida sigmoide com 1 neuronio;
5. treina por 50 epocas;
6. salva em `modelo_ambiental.h5`;
7. imprime medias e desvios para serem copiados ao firmware.

### `Produto/treinar_ia2.py`

Script muito parecido com o anterior, mas usando `dados_treinamento.csv` gerado de forma sintetica. O nome do arquivo sugere um typo em `treinar`.

Esse script:

- desativa GPU/Metal com `CUDA_VISIBLE_DEVICES=-1`;
- treina a mesma arquitetura;
- salva `modelo_ambiental.h5`;
- imprime os parametros de normalizacao no formato pronto para colar no `main.cpp`.

### `Produto/converter_tflite.py`

Converte `modelo_ambiental.h5` para TensorFlow Lite e gera um header C:

- carrega o modelo Keras;
- cria uma `concrete function`;
- converte para TFLite com otimizacao padrao;
- grava o binario como array C em `model_data.h`.

Esse arquivo e o elo entre o treinamento em Python e a execucao do modelo no microcontrolador.

### `Produto/dataset.py`

Script auxiliar para captura de dados via serial. Ele:

- abre uma porta serial fixa;
- le linhas no formato CSV vindas do dispositivo;
- salva em `dados_sensores.csv`.

Serve como apoio para montar datasets reais a partir do hardware.

## Fluxo Completo Do Sistema

### Fluxo principal atualmente implementado

1. O DHT11 mede umidade e temperatura.
2. O ESP8266 normaliza os dados.
3. O modelo TinyML classifica a leitura.
4. O firmware envia um `POST` para `api_receptor.php`.
5. O PHP grava a leitura no MySQL.
6. `index.php` consulta a base e renderiza o dashboard.

### Fluxo de apoio a decisao

1. O operador abre `app.py` via Streamlit.
2. Seleciona um ou mais focos de incendio.
3. Escolhe entre missao de evasao de civis ou incursao de bombeiros.
4. O grafo recebe pesos proibitivos nas areas em risco.
5. O algoritmo de Dijkstra calcula a melhor rota disponivel.
6. O mapa exibe visualmente o trajeto recomendado para fuga ou combate.

### Fluxo de treinamento e deploy do modelo

1. Gerar dados com `gerar_dados.py` ou usar `normal.csv` e `alerta.csv`.
2. Treinar com `treinar_ia.py` ou `treinar_ia2.py`.
3. Salvar `modelo_ambiental.h5`.
4. Converter com `converter_tflite.py`.
5. Copiar/usar `model_data.h` no firmware.
6. Ajustar medias e desvios no `main.cpp`.
7. Compilar e gravar o firmware com PlatformIO.

## Como Executar

### 1. Banco de dados

Importe `bd.sql` no MySQL/MariaDB do XAMPP.

### 2. Backend PHP

Coloque o projeto dentro de `htdocs` do XAMPP e garanta que o Apache e o MySQL estejam ativos.

Arquivos principais:

- dashboard: `http://localhost/edgeIA/index.php`
- endpoint HTTP: `http://localhost/edgeIA/api_receptor.php`

### 3. Interface Streamlit

Instale as dependencias Python e inicie o aplicativo:

```bash
pip install -r requirements.txt
streamlit run app.py
```

A interface abre no navegador local do Streamlit e permite simular os caminhos de combate e de fuga em funcao dos focos de incendio selecionados.

### 4. Firmware

No `Produto/src/main.cpp`, ajuste:

- `ssid`
- `password`
- `serverUrl`

Depois compile e envie com PlatformIO dentro de `Produto/`.

### 5. Treinamento do modelo

Exemplo de sequencia:

```bash
cd Produto
python3 gerar_dados.py
python3 treinar_ia2.py
python3 converter_tflite.py
```

Depois confirme se `model_data.h` e os valores de media/desvio foram refletidos no firmware.

## Observacoes Tecnicas

- `bd.sql` nao cria a coluna `tipo_leitura`, mas `index.php` e `api_receptor.php` dependem dela. Para o dashboard atual funcionar corretamente, a tabela precisa dessa coluna.
- O campo `acuracia` hoje esta sobrecarregado: guarda temperatura em leituras de IA e voltagem em leituras de bateria.
- `app.py` hoje funciona como simulador tatico independente: ele nao consulta diretamente o banco nem consome automaticamente as leituras do ESP8266.
- Existem duas rotas de ingestao HTTP (`api.php` e `api_receptor.php`) e uma rota UDP (`udp_broker.php`). O fluxo ativo no firmware principal aponta para `api_receptor.php`.
- Existem arquivos de ambiente virtual dentro de `Produto/venv` e `Produto/venv_tcc`. Eles sao dependencias locais e nao fazem parte da logica principal do sistema.
- O firmware contem configuracoes locais de rede e servidor hardcoded. Em um ambiente mais robusto, isso poderia ser externalizado.

## Sugestao De Evolucao

Se este projeto continuar evoluindo, os proximos ajustes naturais seriam:

- alinhar o schema do banco com o uso atual da aplicacao;
- separar semanticamente temperatura, confianca e voltagem em colunas distintas;
- integrar `app.py` com as leituras reais do backend para acionar rotas a partir de alertas detectados;
- consolidar os endpoints em uma unica API;
- remover arquivos duplicados ou antigos da raiz para deixar o fluxo principal mais claro;
- adicionar um README especifico em `Produto/` se a parte embarcada crescer.
