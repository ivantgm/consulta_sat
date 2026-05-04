<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Miliogo - Exclusão de conta ou dados">
    <link rel="stylesheet" type="text/css" href="style.css">
    <title>Exclusão de Conta ou Dados - Miliogo</title>    
</head>

<h1>Exclusão de Conta - Cupom Fiscal Miliogo</h1>
<p><strong>Desenvolvedor:</strong> miliogo.com</p>

<h2>Solicitar Exclusão</h2>

<p>Você pode:</p>
<ul>
  <li>Excluir sua conta permanentemente</li>
  <li>Excluir apenas seus cupons cadastrados por período</li>
</ul>

<h3>1. Escolha o tipo de exclusão</h3>

<select id="tipo">
  <option value="conta">Excluir conta completa</option>
  <option value="1">Excluir cupons de hoje</option>
  <option value="7">Excluir cupons desta semana</option>
  <option value="30">Excluir cupons deste mês</option>
  <option value="0">Excluir todos os cupons</option>
</select>

<h3>2. Confirme sua solicitação</h3>
<input type="text" id="usuario" placeholder="Seu usuário" />
<input type="password" id="senha" placeholder="Sua senha" />

<br><br> <button onclick="enviar()">Solicitar Exclusão</button>

<p id="status"></p>

<hr>

<h2>Como funciona</h2>
<ol>
  <li>Selecione o tipo de exclusão desejada</li>
  <li>Informe seu usuário e senha</li>
  <li>Clique em "Solicitar Exclusão"</li>
  <li>Você receberá confirmação por e-mail (se aplicável)</li>
</ol>

<h2>Dados excluídos</h2>
<ul>
  <li>Cupons fiscais cadastrados</li>
  <li>Dados de perfil (nome, e-mail)</li>
</ul>

<h2>Dados que podem ser mantidos</h2>
<ul>
  <li>Todos os dados serão excluídos permanentemente de modo irreversível</li>
</ul>

<h2>Período de retenção</h2>
<p>Os dados são prontamente excluídos após a solicitação de exclusão.</p>

<script>
async function enviar() {
  const tipo = document.getElementById("tipo").value;
  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;

  const response = await fetch("https://miliogo.com/cupom/usuario.php", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(
        { 
            funcao: "excluir", 
            nome: usuario, 
            senha: senha, 
            excluir_usuario: tipo === "conta",
            dias: tipo 
        }
    )});
    if (!response.ok) {
        const data = await response.json();
        document.getElementById("status").innerText = "Erro ao enviar solicitação: " + (data.erro || response.statusText);
    }  else {
        const data = await response.json();
        document.getElementById("status").innerText = data.sucesso || "Solicitação enviada com sucesso!";
        alert("Os dados foram excluídos com sucesso. Se você solicitou a exclusão da conta, ela foi removida permanentemente. Se você solicitou a exclusão de cupons, eles foram removidos conforme o período selecionado.");
    }

}
</script>

</body>
</html>
