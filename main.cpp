#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <EloquentTinyML.h>
#include "model_data.h"

// --- Configurações do seu Wi-Fi Residencial ---
const char* ssid = "Casa";
const char* password = "abacate123";

// --- Endereço do seu Mac (IP na rede local) ---
// Use 'ipconfig getifaddr en0' no terminal do Mac para confirmar
const char* serverUrl = "http://localhost/edgeIA/api_receptor.php";

// --- Hardware ---
#define DHTPIN 4 // D2 no NodeMCU
#define DHTTYPE DHT11
#define BATTERY_PIN A0
DHT dht(DHTPIN, DHTTYPE);

// --- IA e Controle ---
Eloquent::TinyML::TfLite<2, 1, 2048> ml;
float ultima_temp = -100.0;
unsigned long last_battery = 0;

void enviarDados(String tipo, String status, float valor) {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;
        HTTPClient http;
        http.begin(client, serverUrl);
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");

        // Monta o corpo do POST
        String httpRequestData = "device_id=ESP8266_CASA&status=" + status + 
                                 "&valor=" + String(valor) + "&tipo=" + tipo;
        
        int httpCode = http.POST(httpRequestData);
        if (httpCode > 0) Serial.println("Resposta: " + http.getString());
        http.end();
    }
}

void setup() {
    Serial.begin(115200);
    dht.begin();
    ml.begin(modelo_ia);

    WiFi.begin(ssid, password);
    Serial.print("Conectando ao Wi-Fi da Casa");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500); Serial.print(".");
    }
    Serial.println("\nConectado! IP do ESP: " + WiFi.localIP().toString());
}

void loop() {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!isnan(h) && !isnan(t)) {
        // Só envia se a temperatura mudar 0.5°C
        if (abs(t - ultima_temp) >= 0.5) {
            // Normalização UFLA
            float input[2] = {(h - 49.0048) / 11.4890, (t - 27.8591) / 4.5005};
            float predicao = ml.predict(input);
            
            String status = (predicao > 0.5) ? "ALERTA" : "NORMAL";
            enviarDados("IA", status, t);
            ultima_temp = t;
        }
    }

    // Reporte de bateria a cada 1 minuto
    if (millis() - last_battery >= 60000) {
        float v_bat = (analogRead(BATTERY_PIN) / 1023.0) * 4.2; 
        enviarDados("BATTERY", "NIVEL_BAT", v_bat);
        last_battery = millis();
    }
    delay(2000);
}