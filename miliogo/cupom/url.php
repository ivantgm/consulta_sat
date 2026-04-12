<?php

require "api.php";

if(!isset($data["url"])) {
    http_response_code(400);
    echo json_encode(["erro" => "URL não informada"]);
    exit;
}

$url = $data["url"];

$sql = "INSERT INTO url (url, id_usuario) VALUES (?, ?)";

$stmt = $conn->prepare($sql);
$stmt->bind_param("si", $url, $id_usuario);
$stmt->execute();
$last_id = $stmt->insert_id;
$stmt->close();

if(!str_starts_with($url, "https://")) {
    $erro = "URL inválida";
    $detalhes = "A URL deve começar com 'https://'";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

if(!str_contains($url, "fazenda.sp.gov.br")) {
    $erro = "URL inválida";
    $detalhes = "A URL deve conter 'fazenda.sp.gov.br'";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

$query_string = parse_url($url, PHP_URL_QUERY);

parse_str($query_string, $query_params);

$p = $query_params["p"];
$chave_acesso = "";

if(preg_match('/\b\d{44}\b/', $p, $matches)) {
    $chave_acesso = $matches[0];
} else {
    $erro = "URL inválida";
    $detalhes = "Não foi possível extrair a chave de acesso da URL";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

if(!str_starts_with($chave_acesso, "35")) {
    $erro = "Chave de acesso inválida";
    $detalhes = "Apenas chaves do estado de São Paulo (35) podem ser processadas";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

if(!validar_chave_acesso($chave_acesso)) {    
    $erro = "Chave de acesso inválida";
    $detalhes = "A chave de acesso não passou na validação de dígito verificador";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

$check_stmt = $conn->prepare(
    "
     SELECT COUNT(*) 
     FROM cupom 
     WHERE chave_acesso = ? 
       AND id_usuario = ?
    "
);
$check_stmt->bind_param("si", $chave_acesso, $id_usuario);
$check_stmt->execute();
$check_stmt->bind_result($count);
$check_stmt->fetch();
$check_stmt->close();

if ($count > 0) {
    $erro = "Chave de acesso já cadastrada";
    $detalhes = "A chave de acesso informada já está cadastrada";
    save_erro($conn, $last_id, $erro, $detalhes);
    http_response_code(400);
    echo json_encode(
        [
            "erro" => $erro,
            "detalhes" => $detalhes
        ]
    );
    exit;
}

http_response_code(200);
echo json_encode(
    [
        "sucesso" => true,
        "detalhes" => "A URL pode ser processada"
    ]
);

function validar_chave_acesso($chave) {
    $chave = preg_replace('/\D/', '', $chave);
    if (strlen($chave) != 44) {
        return false;
    }
    $chave43 = substr($chave, 0, 43);
    $dv = (int)substr($chave, 43, 1);
    $calculado = calcular_dv_chave_acesso($chave43);
    return $calculado === $dv;
}

function calcular_dv_chave_acesso($chave43) {
    $multiplicadores = [2, 3, 4, 5, 6, 7, 8, 9];
    $soma = 0;
    $index = 0;
    for ($i = 42; $i >= 0; $i--) {
        $soma += (int)$chave43[$i] * $multiplicadores[$index];
        $index++;
        if ($index > 7) {
            $index = 0;
        }
    }
    $resto = $soma % 11;
    $dv = 11 - $resto;
    if ($dv >= 10) {
        return 0;
    }
    return $dv;
}

function save_erro($conn, $last_id, $erro, $detalhes) {
    $sql = "UPDATE url SET erro = ?, detalhes = ? WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssi", $erro, $detalhes, $last_id);
    $stmt->execute();
}

?>