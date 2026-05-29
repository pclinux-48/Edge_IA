<?php
// Configurações do Banco
$host = "localhost"; $user = "root"; $pass = ""; $db = "monitoramento_iot";
try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8", $user, $pass);
} catch (PDOException $e) { die("Erro banco: " . $e->getMessage()); }

// Cria um socket UDP na porta 9999
$socket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
socket_bind($socket, '0.0.0.0', 9999);

echo "Micro-Broker UDP iniciado na porta 9999...\n";

while (true) {
    // Aguarda receber dados (bloqueante)
    socket_recvfrom($socket, $buf, 512, 0, $remote_ip, $remote_port);
    
    // Formato esperado do ESP32 (exemplo de string compacta separada por vírgula): 
    // "ESP32_01,Fogo_Florestal,0.945"
    echo "Recebido de $remote_ip: $buf\n";
    
    $dados = explode(',', trim($buf));
    if (count($dados) === 3) {
        $stmt = $pdo->prepare("INSERT INTO leituras_tinyml (device_id, classe_detectada, acuracia) VALUES (?, ?, ?)");
        $stmt->execute([$dados[0], $dados[1], (float)$dados[2]]);
    }
}