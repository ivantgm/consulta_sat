from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import os
import time
import json

SAVE_HTML = True
SAVE_JSON_RESULT = True

def consulta_nfce(url):
    if sys.platform == "linux":
        geckodriver_path = '/snap/bin/geckodriver'  # To get the geckodriver path run `$ which geckodriver` in shell
        driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
        driver = webdriver.Firefox(service=driver_service)
    else:
        driver = webdriver.Firefox()
    driver.set_window_size(700, 700)
    driver.get(url)    
    time.sleep(1)
    driver.execute_script("document.getElementById(\"btnVisualizarAbas\").scrollIntoView();")
    btnVisualizarAbas = driver.find_element(By.ID, "btnVisualizarAbas")    
    btnVisualizarAbas.click()
    time.sleep(1)

    chave_acesso = url.split("p=")[1].split("|")[0] 

    if SAVE_HTML:
        if not os.path.exists("./html"):
            os.makedirs("./html")          
        with open(f"./html/{chave_acesso}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    tabProdServ = driver.find_element(By.ID, "__tab_Conteudo_pnlNFe_tabProdServ")        
    tabProdServ.click()

    itens = []
    div_prod = driver.find_element(By.ID, "Prod")
    tables = div_prod.find_elements(By.TAG_NAME, "table")
    seq = None
    codigo = None
    descricao = None
    qtde = None
    un = None
    valor_unit = None
    tributos = None
    valor_total = None
    desconto = None 
    lista_unica_seq = []
    for table in tables:
        if table.get_attribute("class") == "toggle box":
            table.click()

            tds = table.find_elements(By.TAG_NAME, "td")
            for td in tds:
                if td.get_attribute("class") == "fixo-prod-serv-numero":
                    seq = td.text
                elif td.get_attribute("class") == "fixo-prod-serv-descricao":
                    descricao = td.text
                elif td.get_attribute("class") == "fixo-prod-serv-qtd":
                    qtde = td.text
                elif td.get_attribute("class") == "fixo-prod-serv-uc":
                    un = td.text
                elif td.get_attribute("class") == "fixo-prod-serv-vb":
                    valor_total = td.text

        if table.get_attribute("class") == "toggable box":
            trs = table.find_elements(By.TAG_NAME, "tr")
            for tr in trs:
                tds = tr.find_elements(By.TAG_NAME, "td")
                for td in tds:
                    label = td.find_elements(By.TAG_NAME, "label")
                    span = td.find_elements(By.TAG_NAME, "span")
                    if label and span:
                        if label[0].text == "Código do Produto":
                            codigo = span[0].text
                        if label[0].text == "Código EAN Comercial":
                            if span[0].text != "SEM GTIN":
                                codigo = span[0].text
                        if label[0].text == "Valor do Desconto":
                            desconto = span[0].text
                        if label[0].text == "Valor unitário de comercialização":
                            valor_unit = span[0].text
                        if label[0].text == "Valor Aproximado dos Tributos":
                            tributos = span[0].text

                    if (not codigo is None) and \
                       (not desconto is None) and \
                       (not valor_unit is None) and \
                       (not tributos is None):
                        break

                if (not codigo is None) and \
                   (not desconto is None) and \
                   (not valor_unit is None) and \
                   (not tributos is None):
                    break                    

        if (not seq is None) and (not desconto is None):
            if seq not in lista_unica_seq:
                lista_unica_seq.append(seq)
                item = {
                    'seq': seq,
                    'codigo': codigo,
                    'descricao': descricao,
                    'qtde': qtde,
                    'un': un,
                    'valor_unit': valor_unit,
                    'tributos': tributos,
                    'valor_total': valor_total,
                    'desconto': desconto
                }
                itens.append(item)
                seq = None
                codigo = None
                descricao = None
                qtde = None
                un = None
                valor_unit = None
                tributos = None
                valor_total = None
                desconto = None                 

    if SAVE_JSON_RESULT:
        if not os.path.exists("./json"):
            os.makedirs("./json")
        with open(f"./json/{chave_acesso}.json", "w", encoding="utf-8") as file:
            json.dump(itens, file)


    driver.quit()



if __name__ == "__main__":
	consulta_nfce("https://www.nfce.fazenda.sp.gov.br/NFCeConsultaPublica/Paginas/ConsultaQRCode.aspx?p=35250747603246000111652050000008391006364420|2|1|1|17db75e8b67a2be913c6d980e8aed1509c79c155")