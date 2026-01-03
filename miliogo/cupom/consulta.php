<?php

require "api.headers.php";
require "my.php";
require "api.data.php";

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

