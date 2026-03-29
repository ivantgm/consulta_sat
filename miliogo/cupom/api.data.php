<?php
$body_str = file_get_contents("php://input");
$data = json_decode($body_str, true);

if (!$data) {
    if ($_SERVER["REQUEST_METHOD"] != "GET") {
        http_response_code(400);
        echo json_encode(["erro" => "invalid input JSON"]);
        exit;
    }
}

function is_integer_array($array) {
    if (!is_array($array)) {
        return false;
    }
    foreach ($array as $value) {
        if (!is_int($value)) {
            return false;
        }
    }
    return true;
}
?>