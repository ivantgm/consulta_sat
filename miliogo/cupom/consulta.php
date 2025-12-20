<?php

header("Content-Type: application/json; charset=UTF-8");

ini_set('precision', 14);
ini_set('serialize_precision', -1);

require "my.php";

$json = file_get_contents("php://input");
$data = json_decode($json, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["erro" => "JSON inválido"]);
    exit;
}

$nome = $data["nome"] ?? "";
$codigo = $data["codigo"] ?? "";

if ($codigo !== "") {
    $sql = "
        SELECT 
            i.codigo AS codigo,
            i.descricao AS nome, 
            i.un AS un,
            round(i.valor_unit-(i.desconto/i.qtde), 2) AS valor, 
            round(i.desconto/i.qtde, 2) AS desconto,
            CONCAT(
            SUBSTRING(c.data_hora_emissao, 7, 2), '/', 
            SUBSTRING(c.data_hora_emissao, 5, 2), '/', 
            SUBSTRING(c.data_hora_emissao, 1, 4)
            ) AS data,
            e.nome AS emitente
        FROM cupom_item i
        JOIN cupom c ON c.id = i.id_cupom
        LEFT JOIN emitente e ON e.cnpj = c.cnpj_emitente
        WHERE i.codigo = ?        
        GROUP BY i.descricao, i.valor_unit, i.desconto, c.data_hora_emissao, e.nome
        ORDER BY c.data_hora_emissao DESC
    ";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $codigo);
    $stmt->execute();
    $result = $stmt->get_result();
    $arr = [];
    while ($row = $result->fetch_assoc()) {
        $arr[] = [
            "codigo" => $row["codigo"],
            "nome" => $row["nome"],
            "un" => $row["un"],
            "valor" => $row["valor"],
            "desconto" => $row["desconto"],
            "data" => $row["data"],
            "emitente" => $row["emitente"]
        ];
    }
    echo json_encode($arr);
    $stmt->close();
    $conn->close();
    exit;
} else if ($nome !== "") {
    $sql = "
        SELECT 
            i.codigo AS codigo,
            i.descricao AS nome, 
            i.un AS un,
            round(i.valor_unit-(i.desconto/i.qtde), 2) AS valor, 
            round(i.desconto/i.qtde, 2) AS desconto,
            CONCAT(
            SUBSTRING(c.data_hora_emissao, 7, 2), '/', 
            SUBSTRING(c.data_hora_emissao, 5, 2), '/', 
            SUBSTRING(c.data_hora_emissao, 1, 4)
            ) AS data,
            e.nome AS emitente
        FROM cupom_item i
        JOIN cupom c ON c.id = i.id_cupom
        LEFT JOIN emitente e ON e.cnpj = c.cnpj_emitente
        WHERE i.descricao LIKE ?        
        GROUP BY i.descricao, i.valor_unit, i.desconto, c.data_hora_emissao, e.nome
        ORDER BY c.data_hora_emissao DESC
    ";
    $stmt = $conn->prepare($sql);
    $like = "%" . $nome . "%";
    $stmt->bind_param("s", $like);
    $stmt->execute();
    $result = $stmt->get_result();
    $arr = [];
    while ($row = $result->fetch_assoc()) {
        $arr[] = [
            "codigo" => $row["codigo"],
            "nome" => $row["nome"],
            "un" => $row["un"],
            "valor" => $row["valor"],
            "desconto" => $row["desconto"],
            "data" => $row["data"],
            "emitente" => $row["emitente"]
        ];
    }
    echo json_encode($arr);
    $stmt->close();
} else {
  echo json_encode([]);  
}
$conn->close();
?>

