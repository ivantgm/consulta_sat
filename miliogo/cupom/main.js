document.addEventListener(
  "DOMContentLoaded", 
  function() {
    google.charts.load('current', {'packages':['corechart']});

    main_panel = document.getElementById('main_panel');
    if(main_panel) {
      const secret = localStorage.getItem("secret");
      if(!secret) {
        layout_login(main_panel);

      } else {
        main_panel.secret = secret;
        main_panel.user = localStorage.getItem("user");        
        main_panel.user_id = localStorage.getItem("user_id");
        layout_app(main_panel);
      }
    } else {
      console.error("main_panel não encontrado");
    }
  }
);

function blinkMessage(message) {
  if (message.blinking) {
    return;
  }
  message.blinking = true;
  const blinkInterval = setInterval(() => {  
      message.style.visibility = 
        (message.style.visibility === "hidden" ? "visible" : "hidden");
    }, 
    500
  ); 
  setTimeout(() => { 
      clearInterval(blinkInterval); 
      message.style.visibility = "visible";
      message.blinking = false;
    }, 
    5000
  ); 
}

async function criar_usuario(user, password, message) {
  try {  
    const response = await fetch(
      "usuario.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(
          { 
            "nome": user, 
            "senha": password,
            "funcao": "criar"
          }
        )
      }      
    );
    const data = await response.json();
    if (!response.ok) {                      
      throw new Error(data.erro);
    }
    localStorage.setItem("secret", data.secret);
    localStorage.setItem("user_id", data.id);
    localStorage.setItem("user", user);
    layout_redirect(main_panel, "Usuário criado com sucesso!");
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }
}

async function trocar_senha(main_panel) {
  const senha_atual = document.getElementById("senha_atual").value;
  const nova_senha = document.getElementById("nova_senha").value;
  const confirmar_senha = document.getElementById("confirmar_senha").value;
  const message = document.getElementById("message_troca_senha");
  if (nova_senha !== confirmar_senha) {    
    message.textContent = "A nova senha e a confirmação não coincidem!";
    blinkMessage(message);
    return;
  }
  if (!senha_atual || !nova_senha) {
    message.textContent = "Preencha os campos de senha atual e nova senha!";
    blinkMessage(message);
    return;
  }
  if (senha_atual === nova_senha) {
    message.textContent = "A nova senha deve ser diferente da senha atual!";
    blinkMessage(message);
    return;
  }
  try {  
    const response = await fetch(
      "usuario.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(
          {
            "nome": main_panel.user,
            "senha": senha_atual,
            "nova_senha": nova_senha,
            "funcao": "mudar_senha"
          }
        )
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    } else {
      const data = await response.json();
      localStorage.setItem("secret", data.secret);
      main_panel.secret = data.secret;
    }    
    layout_redirect(main_panel, "Senha alterada com sucesso!");
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }  
}

async function salvar_config(main_panel) {
  const email = document.getElementById("email").value;
  const telefone = document.getElementById("telefone").value;
  try {  
    const response = await fetch(
      "usuario_config.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "secret-key": main_panel.secret
        },
        body: JSON.stringify(
          { 
            "email": email, 
            "telefone": telefone
          }
        )
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    }
    layout_redirect(main_panel, "Configurações salvas com sucesso!");
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }  
}

async function ler_config(main_panel) {
  try {  
    const response = await fetch(
      "usuario_config.php",
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "secret-key": main_panel.secret
        }
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    }
    const data = await response.json();
    edit_email = document.getElementById("email");
    edit_telefone = document.getElementById("telefone");
    btn_confirmar_email = document.getElementById("btn_confirmar_email");

    edit_email.value = data.email || "";
    edit_telefone.value = data.telefone || "";    

    if (data.email_confirmado) {
      btn_confirmar_email.disabled = true;
      edit_email.disabled = true;
    } else { 
      btn_confirmar_email.disabled = false; 
      edit_email.disabled = false;    
      btn_confirmar_email.addEventListener("click", async function() {
        btn_confirmar_email.disabled = true; 
        const response = await fetch(
          "confirmar_email.php",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              "secret-key": main_panel.secret
            }
          }      
        );
        if (!response.ok) {
          const data = await response.json();
          btn_confirmar_email.textContent = data.erro;
          throw new Error(data.erro);
        } else {          
          btn_confirmar_email.textContent = "EMail enviado, verifique sua caixa postal";
        }
      });
    }


  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }  
}

async function login(user, password, message) {
  try {  
    const response = await fetch(
      "usuario.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(
          { 
            "nome": user, 
            "senha": password,
            "funcao": "login"
          }
        )
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    }
    const data = await response.json();
    if (data.secret) {
      localStorage.setItem("secret", data.secret);
      localStorage.setItem("user_id", data.id);
      localStorage.setItem("user", user);
      layout_redirect(main_panel, "Login realizado com sucesso!");
    } 
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }
}

async function enviar_email_recuperacao(email, message_recuperacao) {
  try {  
    const response = await fetch(
      "usuario.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(
          { 
            "email": email, 
            "funcao": "recuperar_senha"
          }
        )
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    } else {
      const data = await response.json();
      layout_redirect(main_panel, "Enviamos um e-mail para você :-)");
    }
  } catch (error) {
    message_recuperacao.textContent = error.message;
    blinkMessage(message_recuperacao);
  }
}

function layout_novo_usuario(main_panel) {
  main_panel.innerHTML = `
    <p>Bem vindo!</p>
    <p>Informe seus dados e crie sua conta:</p>
    <input type="text" id="user" placeholder="Usuário" />
    <input type="password" id="password" placeholder="Senha" />
    <button id="btn_criar">Criar Conta</button>
    <div id="message" class="mensagem_erro"></div>
  `;
  const btn_criar = document.getElementById("btn_criar");
  btn_criar.addEventListener(
    "click", 
    async function() {
      const user = document.getElementById("user").value;
      const password = document.getElementById("password").value;
      const message = document.getElementById("message");
      
      if(user && password) {
        criar_usuario(user, password, message);
      } else {
        message.textContent = "Preencha ambos os campos!";
        blinkMessage(message);
      }
    }
  );
}

function layout_login(main_panel) {
  main_panel.innerHTML = `
    <p>Faça login:</p>
    <input type="text" id="user" placeholder="Usuário" />
    <input type="password" id="password" placeholder="Senha" />
    <button id="btn_login">Login</button>
    <div id="message" class="mensagem_erro"></div>
    <p>Não é cadastrado? Crie sua conta, é grátis:</p>
    <button id="btn_create_user">Criar novo usuário</button>
    <p>Esqueceu sua senha?</p>
    <div id="message_recuperacao" class="mensagem_erro"></div>
    <input type="email" id="email_recuperacao" placeholder="Email para recuperação de senha" />
    <button id="btn_recuperar_senha">Recuperar Senha</button>

  `;
  btn_login = document.getElementById("btn_login");
  btn_login.addEventListener(
    "click", 
    function() {
      const user = document.getElementById("user").value;
      const password = document.getElementById("password").value;
      const message = document.getElementById("message");

      if(user && password) {
        login(user, password, message);
      } else {
        message.textContent = "Preencha ambos os campos!";
        blinkMessage(message);
      }
    }
  );
  btn_create_user = document.getElementById("btn_create_user");
  btn_create_user.addEventListener(
    "click", 
    function() {
      layout_novo_usuario(main_panel);
    }
  );
  btn_recuperar_senha = document.getElementById("btn_recuperar_senha");
  btn_recuperar_senha.addEventListener(
    "click", 
    function() {
      const email = document.getElementById("email_recuperacao").value;
      const message_recuperacao = document.getElementById("message_recuperacao");
      if (!email) {
        message_recuperacao.textContent = "Preencha o campo de email!";
        blinkMessage(message_recuperacao);
        return;
      }
      enviar_email_recuperacao(email, message_recuperacao);
    }
  );
}

function layout_redirect(main_panel, message) {
  main_panel.innerHTML = `        
    <p>${message}</p>
    <p>Aguarde, redirecionando...</p>
  `;
  setTimeout(() => {
    location.reload();
  }, 3000);
}  

function layout_config(main_panel) {
  main_panel.innerHTML = `
    <p>Configurações do usuário</p>
    <button id="salvar">Salvar</button>
    <button id="cancelar">Cancelar</button>
    <p><div id="message" class="mensagem_erro"></div></p>
    <label for="email">Email:</label><br>
    <input type="email" id="email" name="email" placeholder="Email" />
    <button id="btn_confirmar_email" disabled>Confirmar Email</button>
    <br>
    <label for="telefone">Telefone:</label><br>
    <input type="tel" id="telefone" name="telefone" placeholder="Telefone" />
    <br>
    <div id="div_troca_senha" class="group_box">
      <p>Alterar Senha:</p>
      <p><div id="message_troca_senha" class="mensagem_erro"></div></p>
      <label for="senha_atual">Senha Atual:</label><br>
      <input type="password" id="senha_atual" name="senha_atual" placeholder="Senha Atual" /><br>
      <label for="nova_senha">Nova Senha:</label><br>
      <input type="password" id="nova_senha" name="nova_senha" placeholder="Nova Senha" /><br>
      <label for="confirmar_senha">Confirmar Nova Senha:</label><br>
      <input type="password" id="confirmar_senha" name="confirmar_senha" placeholder="Confirmar Nova Senha" /><br>
      <br>
      <button id="btn_troca_senha">Trocar Senha</button>      
    </div>
  `;
  ler_config(main_panel);
  cancelar = document.getElementById("cancelar");
  cancelar.addEventListener(
    "click", 
    function() {
      layout_app(main_panel);
    }
  );
  salvar = document.getElementById("salvar");
  salvar.addEventListener(
    "click", 
    function() {
      salvar_config(main_panel);
    }
  );
  btn_troca_senha = document.getElementById("btn_troca_senha");
  btn_troca_senha.addEventListener(
    "click",
    function() {
      trocar_senha(main_panel);
    }
  );
}

function layout_app(main_panel) {
  main_panel.innerHTML = `
    <button id="config">Configurações</button>
    <button id="logout">Sair do Usuário (${main_panel.user})</button>
    <div id="client_panel"></div>
  `;
  logout = document.getElementById("logout");
  logout.addEventListener(
    "click", 
    function() {
      localStorage.removeItem("secret");
      localStorage.removeItem("user_id");
      localStorage.removeItem("user");
      location.reload();
    }
  );
  config = document.getElementById("config");
  config.addEventListener(
    "click", 
    function() {
      layout_config(main_panel);
    }
  ); 
  client_panel = document.getElementById("client_panel");
  layout_agrupamento_por_mes(client_panel); 
} 

function layout_agrupamento_por_mes(client_panel) {
  client_panel.innerHTML = `
    <p id="client_panel_label">Agrupamento por mês:</p>
    <div id="div_agrupamento_por_mes">
      <button id="btn_grafico">Mostrar Gráfico</button>
      <table id="tabela_agrupamento_por_mes" class="grid">
        <thead>
          <tr>
            <th>Mês/Ano</th>          
            <th>Valor</th>
            <th>Cupons</th>
          </tr>
        </thead>
        <tbody id="tabela_agrupamento_por_mes_body"></tbody>
      </table>
      <div id="grafico" style="display: none;">
      </div>
    </div>
    <div id="div_cupons">
      <button id="btn_voltar_agrupamento_por_mes">Voltar</button>
      <button id="btn_grafico_pie">Mostrar Gráfico</button>
      <table id="tabela_cupons" class="grid">
        <thead>
          <tr>
            <th>Itens</th>
            <th>Valor</th>
            <th>Data, Hora</th>
            <th>Emitente</th>
            <th>Endereço</th>
          </tr>
        </thead>
        <tbody id="tabela_cupons_body"></tbody>
      </table>
      <div id="grafico_pie" style="display: none;">
      </div>
      <table id="tabela_produtos_agrupados" class="grid" style="display: none;">
        <thead>
          <tr>
            <th>Produto</th>
            <th>Valor</th>
            <th>Percentual</th>
          </tr>
        </thead>
        <tbody id="tabela_produtos_agrupados_body"></tbody>
      </table>
    </div>
  `;
  btn_voltar_agrupamento_por_mes = document.getElementById(
    "btn_voltar_agrupamento_por_mes"
  );
  btn_voltar_agrupamento_por_mes.addEventListener(
    "click",
    function() {
      layout_agrupamento_por_mes(client_panel);
    }
  );

  btn_grafico = document.getElementById("btn_grafico");
  btn_grafico.addEventListener(
    "click",
    function() {
      const grafico = document.getElementById("grafico");
      const tabela_agrupamento_por_mes = document.getElementById("tabela_agrupamento_por_mes");
      if (grafico.style.display === "none") {
        grafico.style.display = "";
        tabela_agrupamento_por_mes.style.display = "none";
        btn_grafico.textContent = "Mostrar Tabela";
      } else {
        grafico.style.display = "none";
        tabela_agrupamento_por_mes.style.display = "";
        btn_grafico.textContent = "Mostrar Gráfico";
      }
    }
  );

  btn_grafico_pie = document.getElementById("btn_grafico_pie");
  btn_grafico_pie.addEventListener(
    "click",
    function() {
      const grafico_pie = document.getElementById("grafico_pie");
      const tabela_cupons = document.getElementById("tabela_cupons");
      const tabela_produtos_agrupados = document.getElementById('tabela_produtos_agrupados');
      if (grafico_pie.style.display === "none") {
        grafico_pie.style.display = "";
        tabela_cupons.style.display = "none";
        tabela_produtos_agrupados.style.display = "";
        btn_grafico_pie.textContent = "Mostrar Tabela";
      } else {
        grafico_pie.style.display = "none";
        tabela_cupons.style.display = "";
        tabela_produtos_agrupados.style.display = "none";
        btn_grafico_pie.textContent = "Mostrar Gráfico";
      }
    }
  );

  client_panel.label = document.getElementById("client_panel_label");
  tabela_cupons = document.getElementById("tabela_cupons");
  div_cupons = document.getElementById("div_cupons");
  div_cupons.style.display = "none";
  tabela_cupons.div_cupons = div_cupons;
  tabela_agrupamento_por_mes = 
    document.getElementById("tabela_agrupamento_por_mes");
  div_agrupamento_por_mes = document.getElementById("div_agrupamento_por_mes");
  tabela_agrupamento_por_mes.div_agrupamento_por_mes = div_agrupamento_por_mes;
  ler_agrupamento_por_mes(client_panel, tabela_agrupamento_por_mes, tabela_cupons);
}

async function ler_agrupamento_por_mes(
  client_panel, tabela_agrupamento_por_mes, tabela_cupons) {
  try {  
    const response = await fetch(
      "consulta_agrupamento_por_mes.php",
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "secret-key": main_panel.secret
        }
      }      
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.erro);
    }
    
    const data = await response.json();

    //------------------------
    //------------------------
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
      const dataTable = new google.visualization.DataTable();
      dataTable.addColumn('string', 'Mês');
      dataTable.addColumn('number', 'Valor');
      dataTable.addColumn('number', 'Cupons');
      data.forEach(item => {
        dataTable.addRow(
          [
            map_meses_MM_SSS.get(parseInt(item.data.substring(0, 2), 10)),
            item.valor_total,
            item.qtde_cupons
          ]
        );
      });
      var options = {
        width: 600, 
        height: 300,
        backgroundColor: '#ffffff',        
        chartArea: {
          left: 0,
          top: 0,
          width: '100%',
          height: '85%'
        },                
        series: {
          0: { targetAxisIndex: 0 },
          1: { targetAxisIndex: 1 }
        },
        vAxes: {
          0: { 
            title: 'Valor', 
            viewWindow: { 
              min: 0 
            } 
          },
          1: { 
            title: 'Cupons', 
            viewWindow: { 
              min: 0 
            } 
          }
        },
        title: 'Valores por Mês'
      };
      const chart = new google.visualization.ColumnChart(document.getElementById('grafico'));
      chart.draw(dataTable, options);
    }
    //------------------------
    //------------------------      

    tabela_agrupamento_por_mes_body = tabela_agrupamento_por_mes.tBodies[0];
    tabela_agrupamento_por_mes_body.innerHTML = "";
    data.forEach(item => {
      const mes_ano = item.data;
      const valor_total = item.valor_total;
      const qtde_cupons = item.qtde_cupons;    
      const row = document.createElement("tr");
      const mesAnoCell = document.createElement("td");
      mesAnoCell.textContent = mes_ano;
      const valorCell = document.createElement("td");
      valorCell.textContent = format_currency(valor_total);
      valorCell.classList.add("valor");
      const cuponsCell = document.createElement("td");
      cuponsCell.textContent = qtde_cupons;
      cuponsCell.classList.add("valor");
      row.appendChild(mesAnoCell);
      row.appendChild(valorCell);
      row.appendChild(cuponsCell);
      row.cupom_ids = item.cupom_ids.split(",").map(Number);
      tabela_agrupamento_por_mes_body.appendChild(row);

      row.addEventListener(
        "click", 
        async function() {  
          client_panel.label.textContent = `Cupons de ${mesAnoCell.textContent}`;        
          tabela_agrupamento_por_mes.div_agrupamento_por_mes.style.display = "none";
          tabela_cupons.div_cupons.style.display = "";
          tabela_cupons_body = tabela_cupons.tBodies[0];
          tabela_cupons_body.innerHTML = "";
          const response = await fetch(
            "consulta_cupom.php",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "secret-key": main_panel.secret
              },
              body: JSON.stringify(
                { 
                  "in_ids": this.cupom_ids
                }
              )
            }      
          );
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.erro);
          }
          //-----------------------------
          // PieChart
          //-----------------------------             
          const array_produtos_valores = [];
          //-----------------------------             
          const data = await response.json(); 
          data.forEach(cupom => {
            const row = document.createElement("tr");
            row.cupom = cupom;
            const countCell = document.createElement("td");
            countCell.textContent = cupom.itens.length;
            countCell.classList.add("valor");
            
            const valorCell = document.createElement("td");
            valorCell.textContent = format_currency(cupom.valor_total);
            valorCell.classList.add("valor");

            const dataCell = document.createElement("td");
            dataCell.textContent = format_date_time(cupom.data_hora_emissao);

            const emitenteCell = document.createElement("td");
            emitenteCell.textContent = cupom.emitente.nome;

            const enderecoCell = document.createElement("td");
            enderecoCell.textContent = cupom.emitente.endereco;

            row.appendChild(countCell);
            row.appendChild(valorCell);
            row.appendChild(dataCell);
            row.appendChild(emitenteCell);
            row.appendChild(enderecoCell);
            tabela_cupons_body.appendChild(row);

            //------

            row.child_row = document.createElement("tr");
            const child_row_cell = document.createElement("td");
            child_row_cell.colSpan = 5;
            const itens_table = document.createElement("table");
            itens_table.classList.add("grid");
            const itens_table_head = document.createElement("thead");
            const head_row = document.createElement("tr");
            [
              "Seq", 
              "Código", 
              "Descrição", 
              "Qtde",
              "Un",
              "V. Unit", 
              "V. Total",
              "Desconto",
              "V. Líquido"
            ].forEach(text => {
              const th = document.createElement("th");
              th.textContent = text;
              head_row.appendChild(th);
            });
            itens_table_head.appendChild(head_row);
            itens_table.appendChild(itens_table_head);
            const itens_table_body = document.createElement("tbody");            
            cupom.itens.forEach(item => {

              //-----------------------------
              // PieChart
              //-----------------------------              
              array_produtos_valores.push({
                descricao: item.descricao,
                valor: ((item.valor_unit * item.qtde) - item.desconto)
              });
              //-----------------------------              

              const item_row = document.createElement("tr");
              const seqCell = document.createElement("td");
              seqCell.textContent = item.seq;
              const codigoCell = document.createElement("td");
              codigoCell.textContent = item.codigo;
              const descricaoCell = document.createElement("td");
              descricaoCell.textContent = item.descricao;
              const qtdeCell = document.createElement("td");
              qtdeCell.textContent = item.qtde;
              const unCell = document.createElement("td");
              unCell.textContent = item.un;
              
              const valorCell = document.createElement("td");              
              valorCell.textContent = format_currency(item.valor_unit);
              valorCell.classList.add("valor");

              const valorTotalCell = document.createElement("td");
              valorTotalCell.textContent = format_currency(item.valor_unit * item.qtde);
              valorTotalCell.classList.add("valor");

              const descontoCell = document.createElement("td");
              descontoCell.textContent = format_currency(item.desconto);
              descontoCell.classList.add("valor");

              const valorLiquidoCell = document.createElement("td");
              const valorLiquido = (item.valor_unit * item.qtde) - item.desconto;
              valorLiquidoCell.textContent = format_currency(valorLiquido);
              valorLiquidoCell.classList.add("valor");
              
              item_row.appendChild(seqCell);
              item_row.appendChild(codigoCell);
              item_row.appendChild(descricaoCell);
              item_row.appendChild(qtdeCell);
              item_row.appendChild(unCell);
              item_row.appendChild(valorCell);
              item_row.appendChild(valorTotalCell);
              item_row.appendChild(descontoCell);
              item_row.appendChild(valorLiquidoCell);
              itens_table_body.appendChild(item_row);
            });
            itens_table.appendChild(itens_table_body);
            child_row_cell.appendChild(itens_table);
            row.child_row.appendChild(child_row_cell);
            row.child_row.style.display = "none";
            tabela_cupons_body.appendChild(row.child_row);

            row.addEventListener(
              "click", 
              function() {
                if (this.child_row.style.display === "none") {
                  this.child_row.style.display = "";
                } else {
                  this.child_row.style.display = "none";
                } 
              }
            );
          });
          //-----------------------------
          // PieChart
          //-----------------------------
          const agrupado = 
            Object.groupBy(
              array_produtos_valores, 
              ({ descricao }) => descricao
            );
          const somado = 
            Object.entries(agrupado).map(([descricao, array_produtos_valores]) => ({
              descricao: descricao,
              valor: array_produtos_valores.reduce((sum, item) => sum + item.valor, 0)
            }));
          somado.sort(function(a, b) {
            const vA = a.valor;
            const vB = b.valor;
            if (vA > vB) { return -1; }
            if (vA < vB) { return 1;}
            return 0;
          }); 
          google.charts.setOnLoadCallback(drawChart);
          function drawChart() {
            const dataTable = new google.visualization.DataTable();
            dataTable.addColumn('string', 'Produto');
            dataTable.addColumn('number', 'Valor');
            somado.forEach(item => {
              dataTable.addRow(
                [
                  item.descricao,
                  item.valor
                ]
              );
            });
            var options = {
              title: 'Produtos por Valor',
              width: 600, 
              height: 370,
              backgroundColor: '#ffffff',
              chartArea: {
                left: 0,
                top: 0,
                width: '100%',
                height: '100%'
              },
              sliceVisibilityThreshold: .025 // menor que 2,5% agrupa em "Outros"
            };
            const chart = new google.visualization.PieChart(document.getElementById('grafico_pie'));
            chart.draw(dataTable, options);
          } 
          //-----------------------------.
          // Table
          //-----------------------------
          const table = document.getElementById('tabela_produtos_agrupados');
          const table_body = table.tBodies[0];
          table_body.innerHTML = "";
          
          soma_total = somado.reduce((sum, item) => sum + item.valor, 0);

          somado.forEach(item => {
            const row = document.createElement("tr");
            const descricaoCell = document.createElement("td");
            descricaoCell.textContent = item.descricao;
            const valorCell = document.createElement("td");
            valorCell.textContent = format_currency(item.valor);
            valorCell.classList.add("valor");

            const percCell = document.createElement("td");
            percCell.textContent = ((item.valor / soma_total) * 100).toFixed(2) + "%";
            percCell.classList.add("valor");

            row.appendChild(descricaoCell);
            row.appendChild(valorCell);
            row.appendChild(percCell);
            table_body.appendChild(row);
          });          
        }
      );
    });
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }  
}

function format_currency(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function format_date_time(dateString) {
  if (!/^\d{14}$/.test(dateString)) {
    return dateString;
  }
  const year = parseInt(dateString.substring(0, 4), 10);
  const month = parseInt(dateString.substring(4, 6), 10) - 1;
  const day = parseInt(dateString.substring(6, 8), 10);
  const hour = parseInt(dateString.substring(8, 10), 10);
  const minute = parseInt(dateString.substring(10, 12), 10);
  const second = parseInt(dateString.substring(12, 14), 10);
  const dateObject = new Date(year, month, day, hour, minute, second);  
  return dateObject.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}