<?php
header('Content-Type: application/json');
// ... conexão com banco igual ao anterior ...

$external_id = $_GET['external_id'] ?? '';

// 1. Primeiro consulta no Mercado Pago o status atual
$ch = curl_init("https://api.mercadopago.com/v1/payments/search?external_reference=" . $external_id);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer " . $access_token]);
$res = json_decode(curl_exec($ch), true);
curl_close($ch);

$status_remoto = $res['results'][0]['status'] ?? 'pending';

if ($status_remoto == 'approved') {
    // Atualiza o teu banco de dados
    $conn->query("UPDATE tb_depositos_pix SET status = 'approved', data_pagamento = NOW() WHERE external_reference = '$external_id'");
    echo json_encode(["pago" => true]);
} else {
    echo json_encode(["pago" => false]);
}