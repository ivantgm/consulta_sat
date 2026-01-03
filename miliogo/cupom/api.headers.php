<?php
header("Content-Type: application/json; charset=UTF-8");
ini_set('precision', 14);
ini_set('serialize_precision', -1);
$headers = array_change_key_case(apache_request_headers());
?>
