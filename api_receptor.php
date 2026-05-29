<?php
include 'conexao.php';

// O ESP8266 enviará via POST
$id_dispositivo = $_POST['device_id'] ?? 'Nó_Desconhecido';
$status_ia      = $_POST['status']    ?? 'Indeterminado';
$valor_leitura  = $_POST['valor']     ?? 0;
$tipo           = $_POST['tipo']      ?? 'IA';

if (isset($_POST['device_id'])) {
    // Prepara a inserção para evitar problemas de segurança
    $sql = "INSERT INTO leituras_tinyml (device_id, classe_detectada, acuracia, tipo_leitura) 
            VALUES (?, ?, ?, ?)";
    
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssds", $id_dispositivo, $status_ia, $valor_leitura, $tipo);
    
    if ($stmt->execute()) {
        echo "DADO_RECEBIDO";
    } else {
        echo "ERRO_BANCO";
    }
    $stmt->close();
} else {
    echo "AGUARDANDO_POST";
}
?>