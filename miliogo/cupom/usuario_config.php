<?php

require "api.php";

if (($_SERVER["REQUEST_METHOD"] == "POST") || 
    ($_SERVER["REQUEST_METHOD"] == "PUT")) {

    $email = $data["email"] ?? "";
    $telefone = $data["telefone"] ?? "";

    $sql = "UPDATE usuario SET email = ?, telefone = ? WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssi", $email, $telefone, $id_usuario);
    $stmt->execute();
    if ($stmt->affected_rows > 0) {
        echo json_encode([
            "sucesso" => "Configurações atualizadas com sucesso"
        ]);
    } else {
        echo json_encode([
            "sucesso" => "Nenhuma alteração feita nas configurações do usuário"
        ]);
    } 
    $stmt->close();

    exit;
} else if ($_SERVER["REQUEST_METHOD"] == "GET") {

    $email = $data["email"] ?? "";
    $telefone = $data["telefone"] ?? "";

    $sql = "SELECT email, telefone FROM usuario WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id_usuario);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        echo json_encode([
            "email" => $row["email"],
            "telefone" => $row["telefone"]
        ]);
    } else {
        http_response_code(404);
        echo json_encode(["erro" => "Configurações do usuário não encontradas"]);
    }
    $stmt->close();

    exit;
} else {
    http_response_code(400);
    echo json_encode(["erro" => "Metodo HTTP nao permitido"]);
    exit;
}




?>

