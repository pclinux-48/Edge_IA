<?php
$host = "localhost";
$user = "root";     // Padrão do XAMPP
$pass = "";         // Padrão do XAMPP (vazio)
$db   = "monitoramento_iot";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Falha na conexão: " . $conn->connect_error);
}

// Garante que caracteres especiais e acentos funcionem
$conn->set_charset("utf8");
?>