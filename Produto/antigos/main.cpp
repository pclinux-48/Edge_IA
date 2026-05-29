#include <Arduino.h>
#include "DHT.h"
#include <EloquentTinyML.h>
#include "model_data.h" // Sua IA convertida

// Configurações da IA
#define NUMBER_OF_INPUTS 2
#define NUMBER_OF_OUTPUTS 1
#define TENSOR_ARENA_SIZE 2*1024 // 2KB de RAM para a IA

Eloquent::TinyML::TfLite<NUMBER_OF_INPUTS, NUMBER_OF_OUTPUTS, TENSOR_ARENA_SIZE> ml;

// Configurações do Sensor
#define DHTPIN 4 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// INSIRA AQUI os valores que apareceram no final do seu treino no Python
float media_temp = 27.8591; // Exemplo: altere para o seu valor
float desvio_temp = 4.5005;  // Exemplo: altere para o seu valor
float media_umid = 49.0048; 
float desvio_umid = 11.4890;

void setup() {
    Serial.begin(115200);
    dht.begin();
    
    // Inicializa o modelo de IA
    if (!ml.begin(modelo_ia)) {
        Serial.println("Erro ao carregar modelo de IA!");
        while (true);
    }
    Serial.println("IA de Borda UFLA Carregada!");
}

void loop() {
    delay(2000);
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) return;

    // 1. NORMALIZAÇÃO (Essencial para a IA entender)
    float input[2] = {
        (h - media_umid) / desvio_umid,
        (t - media_temp) / desvio_temp
    };

    // 2. INFERÊNCIA (A IA decide)
    float predicao = ml.predict(input);

    // 3. AÇÃO BASEADA NA IA
    Serial.print("Leitura: "); Serial.print(t); Serial.print("C | ");
    Serial.print("Probabilidade de Alerta: "); Serial.println(predicao);

    if (predicao > 0.5) {
        Serial.println("!!! ANOMALIA DETECTADA PELA IA !!!");
        // Aqui você poderia acionar um buzzer ou LED
    }
}