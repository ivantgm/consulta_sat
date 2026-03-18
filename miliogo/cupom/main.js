document.addEventListener(
  "DOMContentLoaded", 
  function() {
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

async function ler_config() {
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
    document.getElementById("email").value = data.email || "";
    document.getElementById("telefone").value = data.telefone || "";

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
    <input type="email" id="email" name="email" placeholder="Email" /><br>
    <label for="telefone">Telefone:</label><br>
    <input type="tel" id="telefone" name="telefone" placeholder="Telefone" />
  `;
  ler_config();
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
    <p>Agrupamento por mês:</p>
    <table id="tabela_agrupamento_por_mes" class="grid">
      <thead>
        <tr>
          <th>Mês/Ano</th>          
          <th>Valor</th>
          <th>Cupons</th>
        </tr>
      </thead>
      <tbody id="tabela_agrupamento_por_mes_body">
        <tr>  
          <td>03/2026</td>
          <td class="valor">123,45</td>
          <td class="valor">3</td>
        </tr>
        <tr>  
          <td>04/2026</td>
          <td class="valor">2,34</td>
          <td class="valor">4</td>
        </tr>        
      </tbody>
    </table>
  `;
  tabela_body = document.getElementById("tabela_agrupamento_por_mes_body");
  ler_agrupamento_por_mes(tabela_body);
}

async function ler_agrupamento_por_mes(tabela_body) {
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
    tabela_body.innerHTML = "";
    data.forEach(item => {
      const row = document.createElement("tr");
      const mesAnoCell = document.createElement("td");
      mesAnoCell.textContent = item.data;
      const valorCell = document.createElement("td");
      valorCell.textContent = format_currency(item.valor_total);
      valorCell.classList.add("valor");
      const cuponsCell = document.createElement("td");
      cuponsCell.textContent = item.qtde_cupons;
      cuponsCell.classList.add("valor");
      row.appendChild(mesAnoCell);
      row.appendChild(valorCell);
      row.appendChild(cuponsCell);
      tabela_body.appendChild(row);
    });
  } catch (error) {
    message.textContent = error.message;
    blinkMessage(message);
  }  
}

function format_currency(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}