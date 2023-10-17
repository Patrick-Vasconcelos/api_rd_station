import requests
from abc import abstractmethod, ABC
import logging
import pandas as pd
import pyodbc
import pandas.io.sql as psql
from dotenv import load_dotenv
from os import getenv
from tqdm import tqdm
import time


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def import_query(path):
    with open(path, 'r') as open_file:
        return open_file.read() 
    

class Rd_api(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.base_endpoint = "https://crm.rdstation.com/api/v1"
    

    def _get_base_endpoint(self, **kwargs) -> str:
        self.base_endpoint = "https://crm.rdstation.com/api/v1"

        return self.base_endpoint

    @abstractmethod
    def _get_endpoint(self, **kwargs) -> str: 
        pass

    def get_token(self,**kwargs) -> str:
        with open('token.txt', 'r') as file:
            token = file.read()

        return token

class GetDeals(Rd_api):

    def __init__(self) -> None:
        super().__init__()

    
    
    def _get_endpoint(self) -> str:
        token = self.get_token()
        return f"{self.base_endpoint}/deals/?token={token}"

    
    def get_data(self, **kwargs) -> dict:
        endpoint = self._get_endpoint(**kwargs)
        logger.info(f"Getting data from endpoint: {endpoint}")
        
        headers = {
        "accept": "application/json"
        }

        response = requests.request("GET", endpoint, headers=headers)
        response = response.json()
        response = pd.json_normalize(response)
        print(response['deals'])

class PutDeals(Rd_api):
    def __init__(self) -> None:
        super().__init__()
    
    def _get_endpoint(self) -> str:
        token = self.get_token(self)
        endpoint = self._get_base_endpoint(self)
        print(token)
        return f"{endpoint}/deals/?token={token}"
    
    def put_data(self,nome_paciente, value_indicacao,data_indicacao, value_sexo, value_data_nascimento_txt, value_contato, value_quadro_clinico,
                    label_sexo : str = "64e63eac51f84c0018a09ac6", label_indicacao : str = "64e4c19a2c71dd000e03ead5",
                    label_data_indicacao : str = "64e4abda173a72001acc99ff", label_fase_lead : str = "64b13bb2ebfad3000d22bdfe" ,
                    label_data_nascimento : str = "6514767ee1a4fd0011ddb4ed", label_contato : str = "651476a6ff79ae002289cd94",
                    label_quadro_clinico : str = "64e4c23367bd0f000d23bdee" , **kwargs) -> None:
        
        endpoint = self._get_endpoint(self,**kwargs)
        
        self.value_data_nascimento_txt = value_data_nascimento_txt

        self.label_fase_lead = label_fase_lead
        self.label_indicacao = label_indicacao
        self.label_quadro_clinico = label_quadro_clinico
        self.value_quadro_clinico = value_quadro_clinico
        self.value_indicacao = value_indicacao
        self.label_data_indicacao = label_data_indicacao
        self.data_indicacao = data_indicacao
        self.nome_paciente = nome_paciente
        self.value_contato = value_contato
        self.value_sexo = value_sexo
        self.label_sexo = label_sexo

        
        

        payload = { "deal": {
        "deal_custom_fields": [
            {
                "custom_field_id": f"{label_indicacao}",
                "value": f"{value_indicacao}"
            },
            {
                "custom_field_id": f"{label_data_indicacao}",
                "value": f"{data_indicacao}"
            },
            {
                "custom_field_id": f"{label_sexo}",
                "value" : f"{value_sexo}"
            },
            {
                "custom_field_id": f"{label_data_nascimento}",
                "value" : f"{value_data_nascimento_txt}"
            },
            {
                "custom_field_id": f"{label_contato}",
                "value" : f"{value_contato}"
            },
            {
                "custom_field_id": f"{label_quadro_clinico}",
                "value" : f"{value_quadro_clinico}"
            }
        ],
        "deal_stage_id": f"{label_fase_lead}",
        "name": f"{nome_paciente}"
        }

        }
        
        headers = {
        "accept": "application/json",
        "content-type": "application/json"
        }

        response = requests.post(url=endpoint, json=payload, headers=headers)

        print(response.status_code)

    def get_list(self, **kwargs):
        nome = 'Ingestao_RD'
    
        env = load_dotenv(r'C:\Users\USER\.env.txt')

        usuario = getenv('usuario_DW')
        senha = getenv('senha_DW')

        conexao, cursor = Conexao_Banco.conecta_ao_banco(username=usuario,password=senha)

        consulta = Conexao_Banco.consulta_ao_banco(query=nome, conexao=conexao)

        conexao.close()

        return consulta
    
    def put_list(self, **kwargs):
        list_deals = self.get_list(self)

        with tqdm(list_deals.iterrows(),desc= "Ingestão RD STATION") as pbar:
            for i, deal in list_deals.iterrows():
                
                
                print(f" Incluindo paciente {deal['Paciente']}\n")
                self.put_data(self,nome_paciente=deal['Paciente'], value_indicacao= deal['Nome'],data_indicacao= deal['DataIndicacao'],
                                value_sexo=deal['Sexo'],value_data_nascimento_txt=deal['DataNascimento'],value_contato=deal['Contato'],value_quadro_clinico=deal['Indicacao']
                                )

                pbar.update(1)

                time.sleep(0.1)
        
        pbar.close()

class Conexao_Banco(Rd_api):
    
    def conecta_ao_banco(driver= 'ODBC Driver 17 for SQL Server', server= '192.168.10.63', database = 'SISAC', username=None,password=None,trusted_connection='no'):

        string_conexao = f"DRIVER={driver};SERVER={server};DATABASE={database};ENCRYPT=no;UID={username};PWD={password};TRUSTED_CONNECTION={trusted_connection}"
        
        conexao = pyodbc.connect(string_conexao)
        cursor = conexao.cursor()

        return conexao, cursor
    
    def consulta_ao_banco(query,conexao):

        query = import_query(f'querys/{query}.sql')

        df = psql.read_sql(query,conexao)

        return df

        list_deals = self.get_list(self)

        with tqdm(list_deals.iterrows(),desc= "Ingestão RD STATION") as pbar:
            for i, deal in list_deals.iterrows():
                
                Deal = PutDeals()
                print(f" Incluindo paciente {deal['Paciente']}\n")
                Deal.put_data(nome_paciente=deal['Paciente'], value_indicacao= deal['Nome'],data_indicacao= deal['DataIndicacao'],
                                value_sexo=deal['Sexo'],value_data_nascimento_txt=deal['DataNascimento'],value_contato=deal['Contato'],value_quadro_clinico=deal['Indicacao']
                                )

                pbar.update(1)

                time.sleep(0.1)
        
        pbar.close()