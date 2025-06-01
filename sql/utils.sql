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