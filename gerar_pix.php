<?php
header('Content-Type: application/json');

// Configurações do Banco de Dados
$host = "host";
$user = "user";
$pass = "pass";
$db   = "db";

$conn = new mysqli($host, $user, $pass, $db);

// Token do Mercado Pago (Mantenha em segurança!)
$access_token = "SEU_ACCESS_TOKEN_AQUI";

// Recebe o valor do Python
$valor = $_POST['valor'] ?? 0;
$external_id = uniqid("slot_"); // Gera um ID único para esta transação

if ($valor <= 0) {
    echo json_encode(["error" => "Valor inválido"]);
    exit;
}

// Corpo da requisição para o Mercado Pago
$data = [
    "transaction_amount" => (float)$valor,
    "description" => "Deposito Slot Machine",
    "payment_method_id" => "pix",
    "external_reference" => $external_id,
    "payer" => [
        "email" => "pagador@exemplo.com", // Pode ser estático ou vir do jogo
        "first_name" => "Jogador",
        "last_name" => "Slot"
    ]
];

$ch = curl_init("https://api.mercadopago.com/v1/payments");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "Authorization: Bearer " . $access_token,
    "X-Idempotency-Key: " . $external_id
]);

$response = json_decode(curl_exec($ch), true);
curl_close($ch);

if (isset($response['point_of_interaction'])) {
    $payment_id = $response['id'];
    $copy_paste = $response['point_of_interaction']['transaction_data']['qr_code'];
    
    // Salva no banco de dados como pendente
    $stmt = $conn->prepare("INSERT INTO tb_depositos_pix (external_reference, payment_id_mp, valor) VALUES (?, ?, ?)");
    $stmt->bind_param("ssd", $external_id, $payment_id, $valor);
    $stmt->execute();

    echo json_encode([
        "status" => "success",
        "pix_code" => $copy_paste,
        "external_id" => $external_id
    ]);
} else {
    echo json_encode(["status" => "error", "msg" => "Falha ao gerar Pix"]);
}