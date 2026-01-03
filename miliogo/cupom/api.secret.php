<?php
$id_usuario = null;

if (!isset($headers['secret-key'])) {
    http_response_code(401);
    echo json_encode(["erro" => "secret-key not found"]);
    exit;
} else {
    $secret_key = $headers['secret-key'];
    $secret_key = base64_decode($secret_key);
    $lines = explode("\n", $secret_key);
    if (count($lines) !== 2) {
        http_response_code(401);
        echo json_encode(["erro" => "invalid secret-key format"]);
        exit;
    }
    $username = trim($lines[0]);
    $password = trim($lines[1]);

    $auth_stmt = $conn->prepare("SELECT id FROM usuario WHERE nome = ? AND senha = ?");
    $auth_stmt->bind_param("ss", $username, $password);
    $auth_stmt->execute();
    $auth_stmt->bind_result($id_usuario);
    $auth_stmt->fetch();
    $auth_stmt->close();

    if (!$id_usuario) {
        http_response_code(401);
        echo json_encode(["erro" => "invalid credentials"]);
        exit;
    }
}
?>
