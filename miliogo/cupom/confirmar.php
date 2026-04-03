<?php
require "my.php";

if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $token = $_GET["t"] ?? "";
    if ($token == "") {
        http_response_code(400);
        exit;
    }
    $sql = "
      SELECT id, nome 
      FROM usuario 
      WHERE (email_confirmacao = ?)
        AND (email_confirmado IS NULL)
    ";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $token);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $id_usuario = $row["id"];
        $nome = $row["nome"];
        $sql_update = "UPDATE usuario SET email_confirmado = NOW() WHERE id = ?";
        $stmt_update = $conn->prepare($sql_update);
        $stmt_update->bind_param("i", $id_usuario);
        $stmt_update->execute();
        if ($stmt_update->affected_rows > 0) {
            echo "Email confirmado com sucesso!<br>Seja bem vindo $nome!";
        } else {
            http_response_code(500);
            echo "Falha ao confirmar email";
        }
    } else {
        http_response_code(400);
        echo "Token de confirmação inválido";
    }
    $stmt->close();
    exit;
} else {
    http_response_code(400);
    echo "Metodo HTTP nao permitido";
    exit;
}
?>