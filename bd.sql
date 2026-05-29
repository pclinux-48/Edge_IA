CREATE DATABASE IF NOT EXISTS monitoramento_iot;
USE monitoramento_iot;

CREATE TABLE IF NOT EXISTS leituras_tinyml (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    classe_detectada VARCHAR(100) NOT NULL,
    acuracia FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);