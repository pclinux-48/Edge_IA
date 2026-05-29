<?php
// Configurações do Banco de Dados
$host = "localhost";
$user = "root";
$pass = "";
$db   = "monitoramento_iot";

// Define que o retorno será JSON
header("Content-Type: application/json");

// Libera apenas requisições POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["status" => "erro", "mensagem" => "Metodo nao permitido. Use POST."]);
    exit;
}

// Captura o corpo da requisição (payload JSON)
$json_dados = file_get_contents("php://input");
$dados = json_decode($json_dados, true);

// Validação básica dos dados recebidos do ESP32
if (!isset($dados['device_id']) || !isset($dados['classe']) || !isset($dados['precisao'])) {
    http_response_code(400);
    echo json_encode(["status" => "erro", "mensagem" => "Dados incompletos."]);
    exit;
}

// Conexão com o banco usando PDO
try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Prepara a query para evitar SQL Injection
    $stmt = $pdo->prepare("INSERT INTO leituras_tinyml (device_id, classe_detectada, acuracia) VALUES (:device_id, :classe, :precisao)");
    
    $stmt->bindParam(':device_id', $dados['device_id']);
    $stmt->bindParam(':classe', $dados['classe']);
    $stmt->bindParam(':precisao', $dados['precisao']);

    $stmt->execute();

    http_response_code(201);
    echo json_encode(["status" => "sucesso", "mensagem" => "Dados salvos com sucesso."]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(["status" => "erro", "mensagem" => "Erro no banco de dados: " . $e->getMessage()]);
}
?>