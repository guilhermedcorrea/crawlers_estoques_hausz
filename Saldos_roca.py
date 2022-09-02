from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.select import Select
import time
from webdriver_manager.chrome import ChromeDriverManager
import pyodbc
import operator
import re
from datetime import datetime
from sqlalchemy import text
from config import get_engine, LogEstoqueFornecedor
from functools import wraps
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, select, insert, text


def call_procedure_saldo_hausz_mapa(f):
    @wraps(f)
    def update_saldo(*args, **kwargs):
        print('saldoooo Calling decorated function',kwargs.get('sku'), kwargs.get('saldo'))
       
        try:
            print('Calling procedure update SALDO', kwargs)
            engine = get_engine()
            with engine.begin() as conn:

                exec = (text(
                    """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        kwargs.get('saldo'), kwargs.get('sku'), kwargs.get('idmarca'))))
                exec_produtos = conn.execute(exec)
                print(kwargs.get('sku'), kwargs.get('saldo'))

        except:
            print('erro')
        
 
        return f(*args, **kwargs)
    return update_saldo


@call_procedure_saldo_hausz_mapa
def insert_log_produtos_saldos(*args, **kwargs):
    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    """Recebe parametros de entrada e cadastra log saldo"""
    print('log saldo',kwargs,kwargs.get('sku'), kwargs.get('saldo'))
    engine = get_engine()
    with engine.begin() as conn:
        
        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('sku'), IdMarca=kwargs.get('IdMarca'),IdTipo=12,
            PrazoProducaoAlterado=kwargs.get('prazo'),ValorAnterio = kwargs.get('saldoanterior')
            ,PrazoProducaoAnterior=kwargs.get('prazoanterior'),DataAlteracao= data)
            )
        exec_produtos = conn.execute(stmt)




class Roca:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    def __init__(self):
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M')).split()[0]
        self.path='http://estoque.incepa.com.br/ConsultaEstoque/Detalhe/'
        self.lista_dicts = []


    def login(self):
        usuario = self.driver.find_element(By.XPATH,"//input[@id='Login']")
        usuario.send_keys('CLIENTE')

        senha = self.driver.find_element(By.XPATH,"//input[@id='Senha']")
        senha.send_keys('INCEPA')
        confirmar = self.driver.find_element(By.XPATH,"//input[@id='btnEntrar']").click()


    def index(self):
        self.driver.implicitly_wait(10)
        self.driver.get("http://estoque.incepa.com.br/")

        self.login()

    def call_procedure_hausz_mapa(self,*args, **kwargs):
        for arg in args:
            try:
                saldo = str(arg.get('Quantidade')).split()[0].replace(".","").replace(",",".")
                saldo = float(saldo)
            except:
                saldo = float(0)
            try:
                sku = str(arg.get('SKU'))
            except:
                pass
                
            try:
                idmarca = int(arg.get('IDMARCA'))
            except:
                pass

            try:
                engine = get_engine()
                with engine.begin() as conn:
                    exec = (text(
                        """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                            saldo, sku,idmarca)))
                    exec_produtos = conn.execute(exec)
                    print('Call procedure hausz mapa saldo ~~ >', saldo, sku, idmarca)
            except:
                print('erro')


    def extract_item(self, url_produto, ref, idmarca):
        produtos = {}
        self.driver.implicitly_wait(10)
        produtos['URLPRODUTO'] = url_produto
        produtos['DATA'] = self.dataatual
        produtos['IDMARCA'] =  idmarca
        produtos['SKU'] = ref
        
        try:
            nome_produto = self.driver.find_elements(By.XPATH,'//*[@id="descricaoItem"]')[0].text
            produtos['NomeProduto'] = nome_produto
        except:
            print("erro nome produto")
        try:
            ref_saldo = self.driver.find_elements(By.XPATH,'//*[@id="table-estoque"]/tbody/tr[1]/th')
            saldo_produto = self.driver.find_elements(By.XPATH,'//*[@id="table-estoque"]/tbody/tr[2]/td')
            cont = 0
            for saldo in ref_saldo:
                produtos[saldo.text] = saldo_produto[cont].text
                cont+=1
        except:
            print("erro infos")
        
        self.lista_dicts.append(produtos)
        try:
            saldoproduto  = str(produtos['Quantidade'].split(" ")[0].replace(",","."))
            saldoproduto = float(saldoproduto)
          
            #hausz.call_procedure_hausz_mapa(saldoproduto, ref, idmarca)
           
        except:
            pass
        self.call_procedure_hausz_mapa(produtos)
  

    def executa_pesquisa(self):
        hausz.select_produtos()
        self.driver.implicitly_wait(10)
        referencias = hausz.select_produtos()
        for referencia in referencias:
            url = self.path + str(referencia['SKU'])
            
            self.driver.get(url)
            
            self.extract_item(url,referencia['SKU'],referencia['IdMarca'])

            #quantidade, codigo, idmarca)


    def create_excel(self):
        data_roca = pd.DataFrame(self.lista_dicts)
        data_roca.to_excel("testegruporoca.xlsx")


roca = Roca()
roca.index()
roca.executa_pesquisa()
roca.create_excel()