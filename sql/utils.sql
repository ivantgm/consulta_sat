-----------------------------------------------------------
select
  codigo, 
  descricao, 
  count(codigo) as vezes, 
  sum(qtde) as qtde, 
  avg(valor_unit) as valor_medio_unit_bruto,
  sum(valor_total) as total_bruto, 
  sum(desconto) as valor_desconto,
  avg((valor_total-desconto)/qtde) as valor_medio_unit_liq, 
  sum(valor_total-desconto) as total_liq
from cupom_item
group by codigo
order by total_liq desc

-----------------------------------------------------------
select 
  e.nome,
  e.fantasia,
  c.data_hora_emissao,
  i.qtde,
  i.valor_unit,
  i.valor_total,
  i.desconto
from cupom_item i
left outer join cupom c on c.id = i.id_cupom
left outer join emitente e on e.cnpj = c.cnpj_emitente
where i.codigo = '560481'
-----------------------------------------------------------
select 
  codigo, 
  descricao, 
  count(codigo) as vezes, 
  sum(qtde) as qtde, 
  avg(valor_unit) as valor_medio_unit, 
  sum(valor_total) as total, 
  sum(desconto) as desconto
from cupom_item
group by codigo
order by total desc

-----------------------------------------------------------
select 
  codigo, 
  descricao, 
  count(codigo) as vezes, 
  sum(qtde) as qtde, 
  avg((valor_total-desconto)/qtde) as valor_medio_unit, 
  sum(valor_total-desconto) as total
from cupom_item
group by codigo
order by total desc

-----------------------------------------------------------
select 
  c.cnpj_emitente,
  e.nome,
  count(c.cnpj_emitente) as qtde_cupons,
  (
    select 
	  sum(i.valor_total - i.desconto) 
	from cupom_item i 
	left outer join cupom cc on cc.id = i.id_cupom
	where cc.cnpj_emitente = c.cnpj_emitente	  
  ) as total
from cupom c
left outer join emitente e on e.cnpj = c.cnpj_emitente
group by c.cnpj_emitente

-----------------------------------------------------------
select sum(valor_total) from cupom where cnpj_emitente='47.603.246/0001-11'

-----------------------------------------------------------
select sum(i.valor_total - i.desconto) 
from cupom c
left outer join cupom_item i on i.id_cupom = c.id
where c.cnpj_emitente='47.603.246/0001-11'

-----------------------------------------------------------
select 
  c.data_hora_emissao,   
  i.valor_unit-(i.desconto/i.qtde) as valor_unit,
  e.fantasia as estabelecimento,
  e.endereco as endereco
from cupom_item i
left outer join cupom c on c.id = i.id_cupom
left outer join emitente e on e.cnpj = c.cnpj_emitente
where i.codigo = '2332'
order by c.data_hora_emissao desc

-----------------------------------------------------------
-- obter o modelo do documento fiscal a partir da chave de acesso
-- posição 21 e 22 da chave de acesso
-----------------------------------------------------------
select substr(chave_acesso, 21, 2) modelo_59_65
from cupom