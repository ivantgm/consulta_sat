<?php

require "api.headers.php";
require "my.php";
require "api.data.php";

$nome = $data["nome"] ?? "";
$senha = $data["senha"] ?? "";
$funcao = $data["funcao"] ?? "";

if ($nome == "" || $senha == "" || $funcao == "") {
    http_response_code(400);
    echo json_encode(["erro" => "Nome, senha e funcao sao obrigatorios"]);
    exit;
}

$senha = md5(HASH_SECRET . $senha);

if ($funcao == "login") {
    $sql = "SELECT id, nome, senha FROM usuario WHERE nome = ? AND senha = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ss", $nome, $senha);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        echo json_encode([
            "sucesso" => "Login realizado com sucesso",
            "id" => $row["id"],
            "secret" => base64_encode($row["nome"] . "\n" . $row["senha"])
        ]);
    } else {
        http_response_code(401);
        echo json_encode(["erro" => "Nome ou senha invalidos"]);
    }
    $stmt->close();
} else if ($funcao == "mudar_senha") {
    $nova_senha = $data["nova_senha"] ?? "";
    if ($nova_senha == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Nova senha e obrigatoria"]);
        exit;
    }
    $nova_senha_hashed = md5(HASH_SECRET . $nova_senha);
    $sql = "UPDATE usuario SET senha = ? WHERE nome = ? AND senha = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("sss", $nova_senha_hashed, $nome, $senha);
    $stmt->execute();
    if ($stmt->affected_rows > 0) {
        echo json_encode([
            "sucesso" => "Senha alterada com sucesso",
            "secret" => base64_encode($nome . "\n" . $nova_senha_hashed)
        ]);
    } else {
        http_response_code(401);
        echo json_encode(["erro" => "Nome ou senha invalidos"]);
    }
    $stmt->close();
} else if ($funcao == "criar") {

    $sql = "SELECT id FROM usuario WHERE nome = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $nome);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        http_response_code(400);
        echo json_encode(["erro" => "Nome de usuario ja existe"]);
        $stmt->close();
        $conn->close();
        exit;
    }
    $stmt->close();

    $sql = "INSERT INTO usuario (nome, senha, ip) VALUES (?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("sss", $nome, $senha, $_SERVER['REMOTE_ADDR']);
    if ($stmt->execute()) {
        echo json_encode([
            "sucesso" => "Usuario criado com sucesso",
            "secret" => base64_encode($nome . "\n" . $senha)
        ]);
    } else {
        http_response_code(400);
        echo json_encode(["erro" => "Erro ao criar usuario"]);
    }
    $stmt->close();
} else {
    http_response_code(400);
    echo json_encode(["erro" => "funcao invalida"]);
}


$conn->close();
?>

