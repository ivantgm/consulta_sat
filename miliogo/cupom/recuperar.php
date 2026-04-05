<?php
require "my.php";

if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $token = $_GET["t"] ?? "";
    if ($token == "") {
        http_response_code(400);
        exit;
    }
    $sql = "
      SELECT id, nome 
      FROM usuario 
      WHERE (recuperacao_senha = ?)
    ";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $token);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $id_usuario = $row["id"];
        $nome = $row["nome"];
        ?>
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="Miliogo - Recuperação de senha">
            <link rel="stylesheet" type="text/css" href="style.css">
            <title>Recuperação de Senha - Miliogo</title>    
        </head>
        <body>
            <h1>Recuperação de senha</h1>
            <p>Olá <?php echo htmlspecialchars($nome); ?>, informe sua nova senha:</p>
            <form method="POST" action="recuperar.php">
                <input type="hidden" name="id_usuario" value="<?php echo $id_usuario; ?>">
                <input type="hidden" name="token" value="<?php echo $token; ?>">
                <input type="password" name="nova_senha" placeholder="Nova senha" required>
                <input type="password" name="confirma_senha" placeholder="Confirmar senha" required>
                <button type="submit">Mudar senha</button>
            </form>
        </body>
        </html>
        <?php
        
    } else {
        http_response_code(400);
        echo "Token de recuperação inválido";
    }
    $stmt->close();
    exit;

} else if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $id_usuario = $_POST["id_usuario"] ?? "";
    $token = $_POST["token"] ?? "";
    $nova_senha = $_POST["nova_senha"] ?? "";
    $confirma_senha = $_POST["confirma_senha"] ?? "";
    
    if ($id_usuario == "" || $token == "" || $nova_senha == "" || $confirma_senha == "") {
        http_response_code(400);
        exit;
    }
    
    if ($nova_senha !== $confirma_senha) {
        http_response_code(400);
        echo "Confirmação de senha não corresponde";
        exit;
    }    
    
    $sql = "
      SELECT id 
      FROM usuario 
      WHERE (id = ? AND recuperacao_senha = ?)
    ";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("is", $id_usuario, $token);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($row = $result->fetch_assoc()) {
        
        $nova_senha_hash = md5(HASH_SECRET . $nova_senha);
        $sql_update = "
          UPDATE usuario 
          SET senha = ?, recuperacao_senha = NULL 
          WHERE id = ?
        ";
        $stmt_update = $conn->prepare($sql_update);
        $stmt_update->bind_param("si", $nova_senha_hash, $id_usuario);
        if ($stmt_update->execute()) {
            ?>
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="description" content="Miliogo - Recuperação de senha">
                <link rel="stylesheet" type="text/css" href="style.css">
                <title>Senha Redefinida - Miliogo</title>    
            </head>
            <body>
                <h1>Senha Redefinida</h1>
                <p>Sua senha foi redefinida com sucesso!</p>
                <a href="index.php ">Voltar e fazer login</a>
            </body>
            </html>
            <?php               
        } else {
            http_response_code(500);
            echo "Erro ao atualizar a senha";
        }
        $stmt_update->close();
        
    } else {
        http_response_code(400);
        echo "Token de recuperação inválido para este usuário";
    }
    
    $stmt->close();
    exit;
} else {
    http_response_code(400);
    echo "Metodo HTTP nao permitido";
    exit;
}
?>