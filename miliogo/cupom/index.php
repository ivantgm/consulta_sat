<?php
require "my.php";
$termo = isset($_GET['q']) ? trim($_GET['q']) : "";
$resultados = [];

if ($termo !== "") {
    $sql = "
        SELECT 
            i.descricao AS produto, 
            i.valor_unit-i.desconto AS valor, 
            i.desconto AS desconto,
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
        LIMIT 25
    ";
    $stmt = $conn->prepare($sql);
    $like = "%" . $termo . "%";
    $stmt->bind_param("s", $like);
    $stmt->execute();
    $result = $stmt->get_result();
    while ($row = $result->fetch_assoc()) {
        $resultados[] = $row;
    }
    $stmt->close();
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Cupom fiscal eletrônico Miliogo">
    <link rel="stylesheet" type="text/css" href="style.css">
    <title>Cupom Fiscal Eletrônico Miliogo</title>    
</head>
<body>
    <header>
        <h1>Cupom Fiscal Eletrônico Miliogo</h1>
        <nav>
            <ul>
                <li><a href="index.php">Home</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section>
            <form method="get" action="">
                <label for="q">Nome do produto:</label>
                <input type="text" id="q" name="q" value="<?= htmlspecialchars($termo) ?>">
                <button type="submit">Buscar</button>
            </form>

            <?php if ($termo !== ""): ?>

                <?php if (count($resultados) > 0): ?>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <tr>
                            <th>Produto</th>
                            <th>Valor Pago</th>
                            <th>Desconto</th>
                            <th>Data</th>
                            <th>Emitente</th>
                        </tr>
                        <?php foreach ($resultados as $r): ?>
                            <tr>
                                <td>
                                    <a href="?<?= htmlspecialchars(http_build_query(['q' => $r['produto']])) ?>">
                                        <?= htmlspecialchars($r['produto']) ?>
                                    </a>
                                </td>
                                <td class="valor"><?= number_format($r['valor'], 2, ',', '.') ?></td>
                                <td class="valor"><?= number_format($r['desconto'], 2, ',', '.') ?></td>
                                <td><?= htmlspecialchars($r['data']) ?></td>
                                <td><?= htmlspecialchars($r['emitente']) ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                <?php else: ?>
                    <p>Nenhum produto encontrado.</p>
                <?php endif; ?>
            <?php endif; ?>

        </section>
    </main>
    <footer>
        <p>&copy; <?php echo date("Y"); ?> Miliogo. All rights reserved.</p>
    </footer>
</body>
</html>