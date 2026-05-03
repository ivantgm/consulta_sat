<?php

require "api.nu.php";
require "email.php";

$nome = $data["nome"] ?? "";
$senha = $data["senha"] ?? "";
$funcao = $data["funcao"] ?? "";

if ($funcao == "") {
    http_response_code(400);
    echo json_encode(["erro" => "Funcao e obrigatoria"]);
    exit;
}

$senha = md5(HASH_SECRET . $senha);

if ($funcao == "login") {

    if ($nome == "" || $senha == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Nome e senha sao obrigatorios"]);
        exit;
    }

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
    if ($nome == "" || $senha == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Nome e senha sao obrigatorios"]);
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

        $sql_email = "SELECT email FROM usuario WHERE nome = ?";
        $stmt_email = $conn->prepare($sql_email);
        $stmt_email->bind_param("s", $nome);
        $stmt_email->execute();
        $result_email = $stmt_email->get_result();
        if ($row_email = $result_email->fetch_assoc()) {
            $email_usuario = $row_email["email"];
        } else {
            $email_usuario = null;
        }
        $stmt_email->close();

        if ($email_usuario) {
            send_email(
                $email_usuario, 
                "Senha Alterada", 
                "Olá, " . $nome . "!<br><br>" . 
                "Sua senha foi alterada com sucesso.<br><br>" . 
                "Sua nova senha é: " . $nova_senha . "<br><br>" 
            );
        }

    } else {
        http_response_code(401);
        echo json_encode(["erro" => "Nome ou senha invalidos"]);
    }
    $stmt->close();
} else if ($funcao == "criar") {

    if ($nome == "" || $senha == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Nome e senha sao obrigatorios"]);
        exit;
    }

    $sql = "SELECT id FROM usuario WHERE nome = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $nome);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        http_response_code(409);
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

} else if ($funcao == "recuperar_senha") {
    $email = $data["email"] ?? "";
    if ($email == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Email e obrigatorio"]);
        exit;
    }
    $sql = "SELECT id, nome FROM usuario WHERE email = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {

        $token = bin2hex(random_bytes(32));

        $sql_update = "UPDATE usuario SET recuperacao_senha = ? WHERE id = ?";
        $stmt_update = $conn->prepare($sql_update);
        $stmt_update->bind_param("si", $token, $row["id"]);
        $stmt_update->execute();        

        $recuperar_link = "https://miliogo.com/cupom/recuperar.php?t=" . urlencode($token);
        $body = "Clique no link abaixo para recuperar sua senha:<br><a href='$recuperar_link'>$recuperar_link</a>";
        send_email(
            $email, 
            "Recuperação de Senha", 
            "Olá, " . $row["nome"] . "!<br><br>" . 
            "Recebemos uma solicitação para recuperar sua senha.<br><br>" .
            $body .
            "<br><br>Se você não solicitou a recuperação de senha, por favor ignore este email."
        );

        echo json_encode(["sucesso" => "Email de recuperação enviado com sucesso"]);
    } else {
        http_response_code(404);
        echo json_encode(["erro" => "Email nao encontrado"]);
    }
    $stmt->close();

} else if ($funcao == "excluir") {
    if ($nome == "" || $senha == "") {
        http_response_code(400);
        echo json_encode(["erro" => "Nome e senha sao obrigatorios"]);
        exit;
    }
    $sql = "SELECT id FROM usuario WHERE nome = ? AND senha = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ss", $nome, $senha);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $id_usuario = $row["id"];
    } else {
        http_response_code(401);
        echo json_encode(["erro" => "Nome ou senha invalidos"]);
        exit;
    }
    $stmt->close();

    $excluir_usuario = $data["excluir_usuario"] === true;     
    $dias = intval($data["dias"]) ?? 0;

    $sql = "DELETE i FROM cupom_item i JOIN cupom c ON i.id_cupom = c.id WHERE c.id_usuario = ?";
    if ($dias) {        
        $sql .= " AND STR_TO_DATE(c.data_hora_emissao, '%Y%m%d%H%i%s') >= DATE_SUB(NOW(), INTERVAL $dias DAY)";
    }
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id_usuario);
    $stmt->execute();
    $stmt->close();       

    $sql = "DELETE FROM cupom WHERE id_usuario = ?";
    if ($dias) {        
        $sql .= " AND STR_TO_DATE(data_hora_emissao, '%Y%m%d%H%i%s') >= DATE_SUB(NOW(), INTERVAL $dias DAY)";
    }
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id_usuario);
    $stmt->execute();
    $stmt->close(); 

    if ($excluir_usuario) {
        $sql = "DELETE FROM usuario WHERE id = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("i", $id_usuario);
        $stmt->execute();
        $stmt->close();
    }

    echo json_encode(["sucesso" => "Dados excluidos com sucesso"]);
    
} else {
    http_response_code(400);
    echo json_encode(["erro" => "funcao invalida"]);
}


$conn->close();
?>