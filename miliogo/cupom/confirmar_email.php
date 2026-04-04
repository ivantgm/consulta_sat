<?php

require "api.php";
require "email.php";

if ($_SERVER["REQUEST_METHOD"] == "GET") {

    $sql = "
      SELECT email, email_confirmado, ts_email_confirmacao 
      FROM usuario 
      WHERE id = ?
    ";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id_usuario);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $email_confirmado = $row["email_confirmado"] ? true : false;
        if ($email_confirmado) {
            http_response_code(400);
            echo json_encode(["erro" => "email ja confirmado"]);
            exit;
        } else {

            if ($row["ts_email_confirmacao"] && (time() - strtotime($row["ts_email_confirmacao"])) < 3600) {
                http_response_code(400);
                echo json_encode([
                    "erro" => "email enviado recentemente, aguarde um pouco..."
                ]);
                exit;
            }

            $email = $row["email"];
            if ($email == "") {
                http_response_code(400);
                echo json_encode(["erro" => "email nao cadastrado"]);
                exit;
            }

            $token = bin2hex(random_bytes(32));
            $confirm_link = "https://miliogo.com/cupom/confirmar.php?t=" . urlencode($token);
            $subject = "Confirmação de Email - Miliogo";
            $body = "Clique no link abaixo para confirmar seu email:<br><a href='$confirm_link'>$confirm_link</a>";

            if (send_email($email, $subject, $body)) {
                $sql_update = "
                    UPDATE usuario 
                    SET email_confirmacao = ?, ts_email_confirmacao = NOW()
                    WHERE id = ?
                ";
                $stmt_update = $conn->prepare($sql_update);
                $stmt_update->bind_param("si", $token, $id_usuario);
                $stmt_update->execute();                
                echo json_encode(["sucesso" => "Email de confirmação enviado com sucesso"]);
            } else {
                http_response_code(500);
                echo json_encode(["erro" => "Falha ao enviar email de confirmação"]);
            }   

        }

    } else {
        http_response_code(404);
        echo json_encode(["erro" => "Configurações do usuário não encontradas"]);
    }
    $stmt->close();
    exit;
} else {
    http_response_code(400);
    echo json_encode(["erro" => "Metodo HTTP nao permitido"]);
    exit;
}
?>