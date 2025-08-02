from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import json
from time import sleep
import re


# URL da página de consulta
url_nota_fiscal = 'http://nfe.sefaz.go.gov.br/nfeweb/sites/nfe/consulta-completa'
def scraper_function(chave_de_acesso: str):

    # Verifica se a chave já existe no arquivo
    notas_path = os.path.join('dados', 'notas.txt')
    if os.path.exists(notas_path):
        with open(notas_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    registro = json.loads(line)
                    if registro.get('chave_nota') == chave_de_acesso:
                        print(f"Nota fiscal {chave_de_acesso} já foi processada.")
                        return None
                except Exception:
                    continue

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url_nota_fiscal)

    campo_chave = driver.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/div[2]/form/div[1]/div/input')
    campo_chave.send_keys(chave_de_acesso)
    driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/button').click() 
    sleep(2)
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))  # ou use um seletor mais preciso se quiser
    )

    driver.switch_to.frame(iframe)
    produtos = []
    try:
        # Espera até que a tabela com os produtos apareça (máximo 15 segundos)
        tabela = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tabResult"))
        )
        forma_de_pagamento_elem = driver.find_element(
            By.XPATH,
            '//div[@id="linhaForma"]/following::div[@id="linhaTotal"][1]//label'
        )
        forma_de_pagamento = forma_de_pagamento_elem.text
        print(f"Forma de pagamento: {forma_de_pagamento}")
        
        li_info = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div[2]/div[2]/div[1]/div/ul/li')
        texto_completo = li_info.text
        match = re.search(r'Emissão: (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', texto_completo)
        data_hora_str = match.group(1) if match else "N/A"
        data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M:%S")

        # Pega todas as linhas da tabela
        rows = driver.find_elements(By.XPATH, '//table[@id="tabResult"]/tbody/tr')

        
        for row in rows:
            try:
                produto = row.find_element(By.CLASS_NAME, 'txtTit').text.strip()
                quantidade = row.find_element(By.CLASS_NAME, 'Rqtd').text.replace("Qtde.:", "").strip()
                unidade = row.find_element(By.CLASS_NAME, 'RUN').text.replace("UN:", "").strip()
                valor_unitario = row.find_element(By.CLASS_NAME, 'RvlUnit').text.replace("Vl. Unit.:", "").strip()
                
                produtos.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'unidade': unidade,
                    'valor_unitario': valor_unitario,
                    'total_da_venda': float(quantidade.replace(',','.')) * float(valor_unitario.replace(',','.')),
                    'forma_de_pagamento': forma_de_pagamento,
                    'data_hora': data_hora,
                    'chave_nota': chave_de_acesso
                })
            except Exception as e:
                print(f"[ERRO] Linha ignorada: {e}")

        # Exibe os dados extraídos
        # Salva os produtos extraídos no arquivo .txt (JSONL)
        if produtos:
            with open(notas_path, 'a', encoding='utf-8') as f:
                for produto in produtos:
                    print(f"Produto: {produto['produto']}")
                    f.write(json.dumps(produto, default=str, ensure_ascii=False) + '\n')
        
    except Exception as e:
        print(f"[ERRO GERAL] Tabela não encontrada ou erro no scraping: {e}")

    finally:
        driver.quit()
        return produtos