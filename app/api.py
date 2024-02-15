import requests
import logging
import pandas as pd
import pyodbc
import pandas.io.sql as psql
from dotenv import load_dotenv
from os import getenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# configurando os loggers
db_logger = logging.getLogger("ingestao.db")
api_logger = logging.getLogger("ingestao.api")
file_handler = logging.FileHandler('ingestao.log')
console_handler = logging.StreamHandler()
db_logger.addHandler(file_handler)
db_logger.addHandler(console_handler)
api_logger.addHandler(file_handler)
api_logger.addHandler(console_handler)
logging.basicConfig(filename='ingestao.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#configurando o envio de email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = ''
SMTP_PASSWORD = ''
TO_EMAIL = 'patrickvasc@qorpo.com.br'
FROM_EMAIL = '89patrick89@gmail.com'

load_dotenv('/home/bi_qorpo/Documentos/.env.txt')

class ApiRd:

    def __init__(self) -> None:
       self.base_endpoint = "https://crm.rdstation.com/api/v1"
       self.token = getenv('token_rd')
       self.usuario = getenv('usuario_DW')
       self.senha = getenv('senha_DW')
       self.nome_query = 'Ingestao_RD'
       
    def import_query(self,path):
        with open(path, 'r') as open_file:
            query = open_file.read()
        return query   

    def envia_email_erro(self,mensagem):
        subject = "Erro na ingestão de dados"
        message = MIMEMultipart()
        message['From'] = FROM_EMAIL
        message['Subject'] = subject
        message['To'] = TO_EMAIL
        message.attach(MIMEText(mensagem, 'plain'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, message.as_string())
            server.quit()
        except Exception as e:
            api_logger.error(f"Erro ao enviar e-mail de erro: {str(e)}")

    def _get_endpoint(self) -> str:
        return f"{self.base_endpoint}/deals/?token={self.token}"
    
    def put_data(self,
                    nome_paciente,
                    value_indicacao,
                    data_indicacao,
                    value_sexo,
                    value_data_nascimento_txt,
                    value_contato,
                    value_quadro_clinico,
                    label_sexo : str = "64e63eac51f84c0018a09ac6",
                    label_indicacao : str = "64e4c19a2c71dd000e03ead5",
                    label_data_indicacao : str = "64e4abda173a72001acc99ff",
                    label_fase_lead : str = "64b13bb2ebfad3000d22bdfe" ,
                    label_data_nascimento : str = "6514767ee1a4fd0011ddb4ed",
                    label_contato : str = "651476a6ff79ae002289cd94",
                    label_quadro_clinico : str = "64e4c23367bd0f000d23bdee") -> None:
        
        endpoint = self._get_endpoint(self)
    
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

        try:
            api_logger.info("Tentando incluir os dados via api...")
            api_logger.info(f"Tentando incluir paciente {nome_paciente}")
            requests.post(url=endpoint, json=payload, headers=headers)
            api_logger.info("Sucesso em incluir os dados via api!")
        except Exception as e:
            api_logger.error(f"Erro ao incluir os dados via api : {str(e)}")

    def get_list(self):
        
        try:

            db_logger.info("Tentando conectar ao banco...")
            conexao = self.conecta_ao_banco(username=self.usuario,password=self.senha)
            db_logger.info("Sucesso ao conectar ao banco de dados!")

        except Exception as e:

            erro_msg = f"Erro ao conectar ao banco de dados : {str(e)}"
            db_logger.error(erro_msg)
            # self.envia_email_erro(mensagem=erro_msg)


        try:
            
            db_logger.info("Realizando consulta ao banco..")
            consulta = self.consulta_ao_banco(query=self.nome_query, conexao=conexao)
            db_logger.info("Sucesso ao fazer a consulta!")
        except Exception as e:
            db_logger.error(f"Erro ao realizar a consulta no banco : {str(e)}")

        try:
            conexao.close()
        except Exception as e:
            db_logger.error(f"erro ao fechar a conexao")

        try:
            return consulta
        except Exception as e:
            db_logger.error(f"erro ao retornar a consulta")
            return []         
    
    def put_list(self):
        db_logger.info("buscando lista de paciente...")

        list_deals = self.get_list()
        if list_deals.empty:
            db_logger.info(f"Lista de pacientes vazia!")
        else:
            db_logger.info(f"lista com {len(list_deals)} pacientes")

            for index,deal in list_deals.iterrows():
                self.put_data(self,nome_paciente = deal['Paciente'],
                                   value_indicacao= deal['Nome'],
                                   data_indicacao= deal['DataIndicacao'],
                                   value_sexo=deal['Sexo'],
                                   value_data_nascimento_txt=deal['DataNascimento'],
                                   value_contato=deal['Contato'],
                                   value_quadro_clinico=deal['Indicacao']
                                )
    
    def conecta_ao_banco(driver= 'ODBC Driver 17 for SQL Server', server= '192.168.10.63', database = 'SISAC', username=None,password=None,trusted_connection='no'):

        string_conexao = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};ENCRYPT=no;UID={username};PWD={password};TRUSTED_CONNECTION={trusted_connection}"
        
        conexao = pyodbc.connect(string_conexao)

        return conexao
    
    def consulta_ao_banco(self,query,conexao):

        str_query = self.import_query(f'/home/bi_qorpo/Documentos/projetos/api_rd_station/app/querys/{query}.sql')
        df = psql.read_sql(str_query,conexao)

        return df
    
    def get_data(self) -> dict:
        endpoint = self._get_endpoint()
        api_logger.info(f"Getting data from endpoint: {endpoint}")
        
        headers = {
        "accept": "application/json"
        }

        response = requests.request("GET", endpoint, headers=headers)
        response = response.json()
        response = pd.json_normalize(response)
        print(response['deals'])