<?php

header("Content-Type: application/json; charset=UTF-8");
ini_set('precision', 14);
ini_set('serialize_precision', -1);

require "my.php";

$id_usuario = null;
$headers = array_change_key_case(apache_request_headers());

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

$json = file_get_contents("php://input");
$data = json_decode($json, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["erro" => "JSON inválido"]);
    exit;
}

$ultimo_id = $data["ultimo_id"] ?? "";

if ($ultimo_id !== "") {
    $sql = "
        SELECT 
          c.*,
          e.cnpj AS cnpj_emitente,
          e.ie AS ie_emitente,
          e.im AS im_emitente,
          e.nome AS nome_emitente,
          e.fantasia AS fantasia_emitente,
          e.endereco AS endereco_emitente,
          e.bairro AS bairro_emitente,
          e.cep AS cep_emitente,
          e.municipio AS municipio_emitente
        FROM cupom c
        LEFT OUTER JOIN emitente e ON c.cnpj_emitente = e.cnpj
        WHERE (c.id > ?) AND (c.id_usuario = ?)
        ORDER BY c.id ASC
    ";
    $stmt = $conn->prepare($sql);    
    $stmt->bind_param("ii", $ultimo_id, $id_usuario);
    $stmt->execute();
    $result = $stmt->get_result();
    $arr = [];
    while ($row = $result->fetch_assoc()) {
        $itens = [];
        $itens_sql = "
          SELECT 
            seq, 
            codigo, 
            descricao, 
            qtde, 
            un, 
            valor_unit, 
            tributos,
            valor_total,
            desconto 
          FROM cupom_item 
          WHERE id_cupom = ?
        ";
        $itens_stmt = $conn->prepare($itens_sql);
        $itens_stmt->bind_param("i", $row["id"]);
        $itens_stmt->execute();
        $itens_result = $itens_stmt->get_result();

        while ($item_row = $itens_result->fetch_assoc()) {
            $itens[] = [
                "seq" => $item_row["seq"],
                "codigo" => $item_row["codigo"],
                "descricao" => $item_row["descricao"],
                "qtde" => $item_row["qtde"],
                "un" => $item_row["un"],
                "valor_unit" => floatval($item_row["valor_unit"]),
                "tributos" => floatval($item_row["tributos"]),
                "valor_total" => floatval($item_row["valor_total"]),
                "desconto" => floatval($item_row["desconto"])
            ];
        }
        $arr[] = [
            "id" => $row["id"],
            "chave_acesso" => $row["chave_acesso"],
            "url_consulta" => $row["url_consulta"],
            "numero_cfe" => $row["numero_cfe"],
            "numero_serie_sat" => $row["numero_serie_sat"],
            "data_hora_emissao" => $row["data_hora_emissao"],
            "valor_total" => $row["valor_total"],
            "total_tributos" => $row["total_tributos"],
            "obs_cupom" => $row["obs_cupom"],
            "obs_inf" => $row["obs_inf"],
            "consumidor" => [
                "cpf_consumidor" => $row["cpf_consumidor"],
                "razao_social_consumidor" => $row["razao_social_consumidor"]
            ],
            "emitente" => [
                "cnpj" => $row["cnpj_emitente"],
                "ie" => $row["ie_emitente"],
                "im" => $row["im_emitente"],
                "nome" => $row["nome_emitente"],
                "fantasia" => $row["fantasia_emitente"],
                "endereco" => $row["endereco_emitente"],
                "bairro" => $row["bairro_emitente"],
                "cep" => $row["cep_emitente"],
                "municipio" => $row["municipio_emitente"]
            ],
            "itens" => $itens
        ];
    }
    echo json_encode($arr);
    $stmt->close();
} else {
  echo json_encode([]);  
}
$conn->close();
?>

