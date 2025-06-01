from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import os
import json

SAVE_HTML = True
SAVE_JSON_RESULT = True

def consulta_sat(chave_acesso, aguardar_consulta_callback=None):
	if sys.platform == "linux":
		geckodriver_path = '/snap/bin/geckodriver' #To get the geckodriver path run `$ which geckodriver` in shell
		driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
		driver = webdriver.Firefox(service=driver_service)
	else:
		driver = webdriver.Firefox()

	driver.set_window_size(700, 700)
	driver.get('https://satsp.fazenda.sp.gov.br/COMSAT/Public/ConsultaPublica/ConsultaPublicaCfe.aspx')
	
	elem = driver.find_element(By.ID, "conteudo_txtChaveAcesso")
	elem.clear()
	elem.send_keys(chave_acesso)

	if aguardar_consulta_callback:
		aguardar_consulta_callback()
	else:
		input("Informe o captcha e pesquise, volte aqui e pressione enter para que eu processar o resultado.")

	if SAVE_HTML:	
		if not os.path.exists("./html"):
			os.makedirs("./html")
		with open(f"./html/{chave_acesso}.html", "w", encoding="utf-8") as file:
			file.write(driver.page_source)

	result = {		
		'data_hora_emissao': driver.find_element(By.ID, "conteudo_lblDataEmissao").text,
		'numero_cfe': driver.find_element(By.ID, "conteudo_lblNumeroCfe").text,
		'numero_serie_sat': driver.find_element(By.ID, "conteudo_lblSatNumeroSerie").text,		
		'chave_acesso': chave_acesso,
		'valor_total': driver.find_element(By.ID, "conteudo_lblTotal").text,
		'obs': driver.find_element(By.ID, "conteudo_lblObservacaoContribuinte").text,
		'total_tributos': driver.find_element(By.ID, "conteudo_lblTotal12741").text,
		'emitente': {
			'cnpj': driver.find_element(By.ID, "conteudo_lblCnpjEmitente").text,
			'ie': driver.find_element(By.ID, "conteudo_lblIeEmitente").text,
			'im': driver.find_element(By.ID, "conteudo_lblImEmintente").text,
			'nome': driver.find_element(By.ID, "conteudo_lblNomeEmitente").text,
			'fantasia': driver.find_element(By.ID, "conteudo_lblNomeFantasiaEmitente").text,
			'endereco': driver.find_element(By.ID, "conteudo_lblEnderecoEmintente").text,
			'bairro': driver.find_element(By.ID, "conteudo_lblBairroEmitente").text,
			'cep': driver.find_element(By.ID, "conteudo_lblCepEmitente").text,
			'municipio': driver.find_element(By.ID, "conteudo_lblMunicipioEmitente").text
		},
		'consumidor': {
			'cpf_consumidor': driver.find_element(By.ID, "conteudo_lblCpfConsumidor").text,
			'razao_social_consumidor': driver.find_element(By.ID, "conteudo_lblRazaoSocial").text,
		},
		'itens': []
	}

	tableItens = driver.find_element(By.ID, 'tableItens')
	linhas = tableItens.find_elements(By.TAG_NAME, 'tr')

	for linha in linhas:
		colunas = linha.find_elements(By.TAG_NAME, 'td')  
		valores = [coluna.text for coluna in colunas]
		if not valores or (valores[0] == ''):
			continue
		if (len(valores) == 2) and (valores[0] == 'Desconto:'):
			result["itens"][-1]['desconto'] = valores[1]
			continue
		item = {
			'seq': valores[0],
			'codigo': valores[1],
			'descricao': valores[2],
			'qtde': valores[3],
			'un': valores[4],
			'valor_unit': valores[5],
			'tributos': valores[6],
			'valor_total': valores[7],
			'desconto': None
		}
		result["itens"].append(item)
	
	driver.quit()

	if SAVE_JSON_RESULT:
		if not os.path.exists("./json"):
			os.makedirs("./json")
		with open(f"./json/{chave_acesso}.json", "w", encoding="utf-8") as file:
			json.dump(result, file)

	if __name__ == "__main__":
		print(result)
	else:
		return result

if __name__ == "__main__":
	chave_acesso = input("Digite a chave de acesso: ")
	consulta_sat(chave_acesso)