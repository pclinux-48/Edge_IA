<?php
include 'conexao.php';

// Função para converter voltagem em percentual (Substituindo a map do Arduino)
function calcularPercentual($voltagem) {
    if ($voltagem <= 0) return 0;
    $min = 3.3; // Bateria descarregada
    $max = 4.2; // Bateria cheia
    $percentual = (($voltagem - $min) / ($max - $min)) * 100;
    
    if ($percentual > 100) return 100;
    if ($percentual < 0) return 0;
    return (int)$percentual;
}
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Dashboard IoT - UFLA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <meta http-equiv="refresh" content="10"> 
</head>
<body class="bg-light">
    <div class="container mt-5">
        <h2 class="mb-4 text-center">Monitoramento de Incêndios (TinyML)</h2>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">Últimas Inferências da IA</div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Data/Hora</th>
                                    <th>Dispositivo</th>
                                    <th>Status</th>
                                    <th>Temp. Registrada</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php
                                $query = "SELECT * FROM leituras_tinyml WHERE tipo_leitura = 'IA' ORDER BY id DESC LIMIT 10";
                                $result = $conn->query($query);
                                
                                if ($result->num_rows > 0) {
                                    while($row = $result->fetch_assoc()) {
                                        $badge = ($row['classe_detectada'] == 'ALERTA') ? 'bg-danger' : 'bg-success';
                                        echo "<tr>
                                                <td>" . date('d/m H:i:s', strtotime($row['timestamp'])) . "</td>
                                                <td>{$row['device_id']}</td>
                                                <td><span class='badge {$badge}'>{$row['classe_detectada']}</span></td>
                                                <td>{$row['acuracia']}°C</td>
                                              </tr>";
                                    }
                                } else {
                                    echo "<tr><td colspan='4' class='text-center'>Nenhum dado recebido ainda.</td></tr>";
                                }
                                ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card shadow">
                    <div class="card-header bg-dark text-white">Nível da Bateria</div>
                    <div class="card-body text-center">
                        <?php
                        $sql_bat = "SELECT acuracia FROM leituras_tinyml WHERE tipo_leitura = 'BATTERY' ORDER BY id DESC LIMIT 1";
                        $res_bat = $conn->query($sql_bat);
                        $voltagem = 0;
                        
                        if ($res_bat->num_rows > 0) {
                            $row_bat = $res_bat->fetch_assoc();
                            $voltagem = $row_bat['acuracia'];
                        }
                        
                        $percentual = calcularPercentual($voltagem);
                        $cor_barra = ($percentual < 20) ? 'bg-danger' : 'bg-success';
                        ?>
                        
                        <h3 class="display-6"><?php echo number_format($voltagem, 2); ?>V</h3>
                        <p class="text-muted">Última leitura analógica</p>
                        
                        <div class="progress mt-3" style="height: 35px;">
                            <div class="progress-bar <?php echo $cor_barra; ?> progress-bar-striped progress-bar-animated" 
                                 role="progressbar" 
                                 style="width: <?php echo $percentual; ?>%">
                                 <?php echo $percentual; ?>%
                            </div>
                        </div>
                        <small class="d-block mt-2">Escala: 3.3V a 4.2V</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>