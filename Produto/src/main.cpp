#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <EloquentTinyML.h>
#include "model_data.h"

// --- Configurações do seu Wi-Fi Residencial ---
const char* ssid = "";
const char* password = "";

// --- Endereço do seu Mac (IP na rede local) ---
const char* serverUrl = "http://192.168.0.24/edgeIA/api_receptor.php";

// --- Hardware ---
#define DHTPIN 4 // D2 no NodeMCU
#define DHTTYPE DHT11
#define BATTERY_PIN A0
DHT dht(DHTPIN, DHTTYPE);

// --- IA e Controle ---
Eloquent::TinyML::TfLite<2, 1, 2048> ml;
float ultima_temp = -100.0;
unsigned long last_battery = 0;

// Médias do seu treinamento UFLA
float media_temp = 27.8591; 
float desvio_temp = 4.5005;
float media_umid = 49.0048; 
float desvio_umid = 11.4890;

void enviarDados(String tipo, String status, float valor) {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;
        HTTPClient http;
        http.setTimeout(4000); // Aumentado um pouco para evitar timeouts em redes instáveis
        
        if (http.begin(client, serverUrl)) {
            http.addHeader("Content-Type", "application/x-www-form-urlencoded");
            
            // Valor com 2 casas decimais para precisão de bateria/IA
            String httpRequestData = "device_id=ESP8266_CASA&status=" + status + 
                                     "&valor=" + String(valor, 2) + "&tipo=" + tipo;
            
            Serial.printf("Enviando [%s]... ", tipo.c_str());
            int httpCode = http.POST(httpRequestData);
            
            if (httpCode > 0) {
                Serial.printf("[OK] Código: %d\n", httpCode);
            } else {
                Serial.printf("[ERRO] %s\n", http.errorToString(httpCode).c_str());
            }
            http.end();
        }
    }
}

void setup() {
    Serial.begin(115200);
    dht.begin();
    ml.begin(modelo_ia);

    WiFi.begin(ssid, password);
    Serial.print("Conectando ao Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500); Serial.print(".");
    }
    Serial.println("\nConectado! IP do ESP: " + WiFi.localIP().toString());
}

void loop() {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!isnan(h) && !isnan(t)) {
        // Envio por variação térmica (Histerese)
        if (abs(t - ultima_temp) >= 0.5) {
            float input[2] = {
                (h - media_umid) / desvio_umid, 
                (t - media_temp) / desvio_temp
            };
            
            float predicao = ml.predict(input);
            String status = (predicao > 0.5) ? "ALERTA" : "NORMAL";
            
            enviarDados("IA", status, t);
            ultima_temp = t;
        }
    }

    // Reporte de bateria a cada 1 minuto (60000 ms)
    if (millis() - last_battery >= 60000) {
        // Leitura analógica com correção do divisor de tensão (Fator 2.0)
        // 1023.0 é a resolução do ESP8266 e 3.3V é a tensão de referência do NodeMCU
        float v_pino = (analogRead(BATTERY_PIN) / 1023.0) * 3.1; 
        float v_bat = v_pino * 2.0;
        
        enviarDados("BATTERY", "NIVEL_BAT", v_bat);
        last_battery = millis();
        
        Serial.printf("Bateria: %.2fV (Pino: %.2fV)\n", v_bat, v_pino);
    }
    
    yield(); // Alimenta o Watchdog do ESP8266 para evitar resets
    delay(2000);
}