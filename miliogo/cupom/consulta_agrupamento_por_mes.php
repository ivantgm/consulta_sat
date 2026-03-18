<?php

require "api.php";

$data_inicio = $data["data_inicio"] ?? "00000000000000";
$data_fim = $data["data_fim"] ?? "99999999999999";

$sql = "
    select
        concat(
          substr(c.data_hora_emissao, 5, 2) , '/',
          substr(c.data_hora_emissao, 1, 4)
        ) as data,
        round(sum(c.valor_total), 2) as valor_total,
        count(c.id) as qtde_cupons,
        group_concat(c.id) as cupom_ids
    from cupom c
    where (c.data_hora_emissao between ? and ?)
      and (c.id_usuario = ?)
    group by substr(c.data_hora_emissao, 1, 6)
    order by substr(c.data_hora_emissao, 1, 6) desc
";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssi", $data_inicio, $data_fim, $id_usuario);
$stmt->execute();
$result = $stmt->get_result();
$arr = [];
while ($row = $result->fetch_assoc()) {
    $arr[] = [
        "data" => $row["data"],
        "valor_total" => floatval($row["valor_total"]),
        "qtde_cupons" => intval($row["qtde_cupons"]),
        "cupom_ids" => $row["cupom_ids"]
    ];
}
echo json_encode($arr);


$conn->close();

?>