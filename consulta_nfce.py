from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import sys
import os
import time
import json
import bs4
import re

SAVE_HTML = True
SAVE_JSON_RESULT = True
PROCESSA_DETALHES = True
USE_SELENIUM = False

def get_2nd_page_selenium(url: str) -> str:
    if sys.platform == "linux":
        geckodriver_path = '/snap/bin/geckodriver' #To get the geckodriver path run `$ which geckodriver` in shell
        driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
        driver = webdriver.Firefox(service=driver_service)
    else:
        driver = webdriver.Firefox()

    driver.set_window_size(700, 700)
    driver.get(url)

    time.sleep(1)

    btnVisualizarAbas = driver.find_element(By.NAME, "btnVisualizarAbas")
    btnVisualizarAbas.click()

    time.sleep(1)

    src = driver.page_source

    driver.quit()

    return src

def get_2nd_page_requests(url: str) -> str:
	UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

	headers1 = {
		'User-Agent': UserAgent
	}

	response1 = requests.get(url, headers=headers1)

	parse_html = bs4.BeautifulSoup(response1.text, features="html.parser")

	inputs = parse_html.find_all('input')
	data = {}
	for input_element in inputs:
		name = input_element.get('name')
		value = input_element.get('value', '')
		if name:
			if name == '__EVENTTARGET':
				value = 'btnVisualizarAbas'
			if name in ['__EVENTTARGET', '__EVENTARGUMENT', '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']:            
				data[name] = value        	

	url2 = 'https://www.nfce.fazenda.sp.gov.br/NFCeConsultaPublica/Paginas/ConsultaResponsiva/ConsultaResumidaRJFrame_v400.aspx'	

	headers2 = {
	    'Referer': url,
	    'User-Agent': UserAgent
	}	

	time.sleep(1)

	return requests.post(url2, cookies=response1.cookies, headers=headers2, data=data).text

def get_2nd_page(url: str) -> str:
    if USE_SELENIUM:
        return get_2nd_page_selenium(url)
    
    return get_2nd_page_requests(url)

def tirar_virgula(text: str) -> str:
	return " ".join(text.split()).replace('\n', '').replace('\u00a0', '')

def municipio(text: str) -> str:
	return " ".join(text[text.rfind('\n'):].split())

def consulta_nfce(url):
	result = dict()
	result["obs"] = ""
	result["emitente"] = dict()
	result["consumidor"] = dict()
	result["itens"] = list()

	# como a página tem dados resumidos,
	# precisamos pegar o endereço de redirecionamento do botão "Visualizar em abas"
	# nesse site, terá os dados completos

	html_src = get_2nd_page(url)
	html = bs4.BeautifulSoup(html_src, features="html.parser")

	tds = html.find("table").find_all("td")

	chave_acesso = re.sub(r'[^0-9]', '', tds[3].get_text())
	result["chave_acesso"] = chave_acesso
	result["url_consulta"] = url

	if SAVE_HTML:
		if not os.path.exists("./html"):
			os.makedirs("./html")
		with open(f"./html/{chave_acesso}.html", "w", encoding="utf-8") as file:
			file.write(html_src)

	fieldsets = html.find_all("fieldset")
	for fieldset in fieldsets:
		legend = fieldset.find("legend").get_text()
		spans = fieldset.find_all("span")

		match legend:
			case "Dados da NF-e":
				result["numero_cfe"]        = spans[2].get_text()
				result["numero_serie_sat"]  = spans[1].get_text()
				result["data_hora_emissao"] = spans[3].get_text().replace(' ', " - ")[:-6]
				result["valor_total"]       = spans[5].get_text()
			case "Dados do Emitente":
				result["emitente"]["cnpj"]      = spans[2].get_text()
				result["emitente"]["ie"]        = spans[10].get_text()
				result["emitente"]["im"]        = spans[11].get_text()
				result["emitente"]["nome"]      = spans[0].get_text()
				result["emitente"]["fantasia"]  = spans[1].get_text()
				result["emitente"]["endereco"]  = tirar_virgula(spans[3].get_text())
				result["emitente"]["bairro"]    = spans[4].get_text()
				result["emitente"]["cep"]       = spans[5].get_text()
				result["emitente"]["municipio"] = municipio(spans[6].get_text())
			case "Dados do Destinatário":
				result["consumidor"]["cpf_consumidor"]          = spans[1].get_text()
				result["consumidor"]["razao_social_consumidor"] = spans[0].get_text()
			case "Totais":
				result["total_tributos"] = spans[-1].get_text()
				try:
					float(result["total_tributos"][:].replace(',', '.'))
				except ValueError:
					result["total_tributos"] = "00,00"

	toggle_boxes = html.find_all("table", class_="toggle box")
	toggable_boxes = html.find_all("table", class_="toggable box")

	for i in range(len(toggable_boxes)):
		spans = toggle_boxes[i].find_all("span")

		if not spans[0].get_text().isdigit():
			break

		item = dict()

		item["seq"]         = spans[0].get_text()
		item["descricao"]   = spans[1].get_text()
		item["qtde"]        = spans[2].get_text()
		item["un"]          = spans[3].get_text()
		item["valor_total"] = spans[4].get_text()

		spans = toggable_boxes[i].find_all("span")

		item["codigo"]      = spans[0].get_text()
		item["desconto"]    = spans[9].get_text().replace('\n', '')
		if item["desconto"] == "":
			item["desconto"] = "00,00"	

		item["valor_unit"]  = spans[19].get_text()
		item["tributos"]    = spans[23].get_text()
		if item["tributos"] == '\n':
			item["tributos"] = "00,00"

		if PROCESSA_DETALHES:
			if spans[13].get_text() != "SEM GTIN":
				item["codigo"] = spans[13].get_text()

		result["itens"].append(item)

	if SAVE_JSON_RESULT:
		if not os.path.exists("./json"):
			os.makedirs("./json")
		with open(f"./json/{chave_acesso}.json", "w", encoding="utf-8") as file:
			json.dump(result, file)

	if __name__ == "__main__":
		print(json.dumps(result, indent=4))
	else:
		return result

if __name__ == "__main__":
	url = input("Informe o URL do cupom: ")
	consulta_nfce(url)