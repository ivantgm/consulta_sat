<?php
$body_str = file_get_contents("php://input");
$data = json_decode($body_str, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["erro" => "invalid input JSON"]);
    exit;
}
?>
