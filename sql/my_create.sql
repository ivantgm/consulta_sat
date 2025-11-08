DROP TABLE IF EXISTS emitente;
DROP TABLE IF EXISTS cupom;
DROP TABLE IF EXISTS cupom_item;
DROP TABLE IF EXISTS usuario;

CREATE TABLE IF NOT EXISTS emitente (
    cnpj varchar(25),
    ie varchar(25),
    im varchar(25),
    nome varchar(255),
    fantasia varchar(255),
    endereco varchar(255),
    bairro varchar(255),
    cep varchar(10),
    municipio varchar(255),
    UNIQUE KEY `idx_cnpj` (`cnpj`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS cupom (
    id int(10) not null AUTO_INCREMENT,
    id_usuario int(10),
    data_hora_emissao varchar(25),
    numero_cfe varchar(25),
    numero_serie_sat varchar(25),
    chave_acesso varchar(44),
    url_consulta TEXT,
    valor_total DOUBLE,
    total_tributos DOUBLE,
    obs_cupom TEXT,
    obs_inf TEXT,
    cnpj_emitente varchar(25),
    cpf_consumidor varchar(25),
    razao_social_consumidor varchar(255),
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_chave_acesso` (`chave_acesso`),
    KEY `idx_cupom_data_hora_emissao` (`data_hora_emissao`),
    KEY `idx_cupom_cnpj_emitente` (`cnpj_emitente`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS cupom_item (
    id int(10) not null AUTO_INCREMENT,
    id_cupom int(10),
    seq int(10),
    codigo varchar(25),
    descricao varchar(255),
    qtde DOUBLE,
    un varchar(25),
    valor_unit DOUBLE,
    tributos DOUBLE,
    valor_total DOUBLE,
    desconto DOUBLE,
    PRIMARY KEY (`id`),
    KEY `idx_cupom_item_id_cupom` (`id_cupom`),
    KEY `idx_cupom_item_codigo` (`codigo`),
    KEY `idx_cupom_item_descricao` (`descricao`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS usuario (
    id int(10) not null AUTO_INCREMENT,
    nome varchar(255),
    senha varchar(255),
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_nome` (`nome`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

insert into usuario (nome, senha) values ('nome_usuario', md5('senha_usuario'));
