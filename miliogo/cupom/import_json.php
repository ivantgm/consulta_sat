<?php

header("Content-Type: application/json; charset=UTF-8");

include "my.php";

$json = file_get_contents("php://input");
$data = json_decode($json, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["erro" => "JSON inválido"]);
    exit;
}

$id_usuario = null;
$headers = array_change_key_case(apache_request_headers());

if (!isset($headers['secret-key'])) {
    http_response_code(402);
    echo json_encode(["erro" => "secret-key not found"]);
    exit;
} else {
    $secret_key = $headers['secret-key'];
    $secret_key = base64_decode($secret_key);
    $lines = explode("\n", $secret_key);
    if (count($lines) !== 2) {
        http_response_code(403);
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
        http_response_code(404);
        echo json_encode(["erro" => "invalid credentials"]);
        exit;
    }
}

$check_stmt = $conn->prepare("SELECT COUNT(*) FROM emitente WHERE cnpj = ?");
$check_stmt->bind_param("s", $data["emitente"]["cnpj"]);
$check_stmt->execute();
$check_stmt->bind_result($count);
$check_stmt->fetch();
$check_stmt->close();

if ($count == 0) {
    $stmt = $conn->prepare("
        INSERT INTO emitente (cnpj, ie, im, nome, fantasia, endereco, bairro, cep, municipio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");

    $emit = $data["emitente"];
    $stmt->bind_param(
        "sssssssss",
        $emit["cnpj"],
        $emit["ie"],
        $emit["im"],
        $emit["nome"],
        $emit["fantasia"],
        $emit["endereco"],
        $emit["bairro"],
        $emit["cep"],
        $emit["municipio"]
    );
    $stmt->execute();
    $stmt->close();
}

$check_stmt = $conn->prepare("SELECT COUNT(*) FROM cupom WHERE chave_acesso = ?");
$check_stmt->bind_param("s", $data["chave_acesso"]);
$check_stmt->execute();
$check_stmt->bind_result($count);
$check_stmt->fetch();
$check_stmt->close();
if ($count == 0) {
    $stmt = $conn->prepare("
        INSERT INTO cupom 
            (
                chave_acesso, 
                cnpj_emitente,
                numero_cfe, 
                numero_serie_sat, 
                data_hora_emissao, 
                valor_total, 
                total_tributos, 
                obs_cupom,
                id_usuario,
                url_consulta
            )
        VALUES 
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
    ");

    $stmt->bind_param(
        "sssssddsis",
        $data["chave_acesso"],
        $data["emitente"]["cnpj"],
        $data["numero_cfe"],
        $data["numero_serie_sat"],
        $data["data_hora_emissao"],
        $data["valor_total"],
        $data["total_tributos"],
        $data["obs"],
        $id_usuario,
        $data["url_consulta"]
    );

    if (!$stmt->execute()) {
        http_response_code(500);
        echo json_encode(["erro" => "Erro ao inserir cupom: " . $stmt->error]);
        exit;
    }

    $id_cupom = $stmt->insert_id;
    $stmt->close();

    // --- Grava itens
    $stmt = $conn->prepare("
        INSERT INTO cupom_item
            (
                id_cupom, 
                seq, 
                descricao, 
                qtde, 
                un, 
                valor_total, 
                codigo, 
                desconto, 
                valor_unit, 
                tributos
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");

    foreach ($data["itens"] as $item) {
        $stmt->bind_param(
            "iisdsdsddd",
            $id_cupom,
            $item["seq"],
            $item["descricao"],
            $item["qtde"],
            $item["un"],
            $item["valor_total"],
            $item["codigo"],
            $item["desconto"],
            $item["valor_unit"],
            $item["tributos"]
        );
        $stmt->execute();
    }

    $stmt->close();
    $conn->close();
}

echo json_encode(
    [
        "status" => "OK",
        "mensagem" => "Cupom importado com sucesso!",
        "id_cupom" => $id_cupom
    ]
);
?>
