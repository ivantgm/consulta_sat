<?php

require "api.php";

if(!isset($data["emitente"])) {
    http_response_code(400);
    echo json_encode(["erro" => "Emitente não informado"]);
    exit;
}

$emit = $data["emitente"];

if(empty($emit["cnpj"])) {
    http_response_code(400);
    echo json_encode(["erro" => "CNPJ do emitente não informado"]);
    exit;
}
if(empty($data["chave_acesso"])) {
    http_response_code(400);
    echo json_encode(["erro" => "Chave de acesso não informada"]);
    exit;
}
if(
    (!isset($data["itens"])) || 
    (!is_array($data["itens"])) || 
    (count($data["itens"]) == 0)
  ) {
    http_response_code(400);
    echo json_encode(["erro" => "Itens do cupom não informados"]);
    exit;
}
foreach ($data["itens"] as $item) {
    if(!is_array($item)) {
        http_response_code(400);
        echo json_encode(["erro" => "Item do cupom deve ser um objeto"]);
        exit;
    }
    if(
        empty($item["seq"]) || 
        empty($item["descricao"]) || 
        empty($item["qtde"]) || 
        empty($item["un"]) || 
        empty($item["valor_total"])
      ) {
        http_response_code(400);
        echo json_encode(["erro" => "Estrutura do item incompleta"]);
        exit;
    }
}

if(empty($data["valor_total"])) {
    http_response_code(400);
    echo json_encode(["erro" => "Valor total não informado"]);
    exit;
}

$check_stmt = $conn->prepare("SELECT COUNT(*), nome FROM emitente WHERE cnpj = ?");
$check_stmt->bind_param("s", $emit["cnpj"]);
$check_stmt->execute();
$check_stmt->bind_result($count, $emitente_nome);
$check_stmt->fetch();
$check_stmt->close();

if ($count == 0) {
    $stmt = $conn->prepare("
        INSERT INTO emitente (cnpj, ie, im, nome, fantasia, endereco, bairro, cep, municipio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");
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

$check_stmt = $conn->prepare("SELECT COUNT(*) FROM cupom WHERE chave_acesso = ? AND id_usuario = ?");
$check_stmt->bind_param("si", $data["chave_acesso"], $id_usuario);
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
    $valor_currency = number_format($data["valor_total"], 2, ',', '.');
    $mensagem = 
      "Cupom importado com sucesso!\n" .
      "R$ " . $valor_currency . 
      " de " . 
      $emitente_nome
    ;
    echo json_encode(
        [
            "status" => "OK",
            "mensagem" => $mensagem,
            "id_cupom" => $id_cupom
        ]
    );
} else {
    $stmt = $conn->prepare("SELECT id FROM cupom WHERE chave_acesso = ? AND id_usuario = ?");
    $stmt->bind_param("si", $data["chave_acesso"], $id_usuario);
    $stmt->execute();
    $stmt->bind_result($id_cupom);
    $stmt->fetch();
    $stmt->close();
    echo json_encode(
        [
            "status" => "OK",
            "mensagem" => "Cupom ja existe.",
            "id_cupom" => $id_cupom
        ]
    );
}
?>