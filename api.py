import requests
from abc import abstractmethod, ABC
import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Rd_api(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.base_endpoint = "https://crm.rdstation.com/api/v1"
    
    
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
        token = self.get_token()
        return f"{self.base_endpoint}/deals/?token={token}"
    
    def put_data(self,nome_paciente,telefone,data_nascimento_txt , value_indicacao,data_indicacao, value_sexo,
                    label_sexo : str = "64e63eac51f84c0018a09ac6", label_indicacao : str = "64e4c19a2c71dd000e03ead5",
                    label_data_indicacao : str = "64e4abda173a72001acc99ff", label_fase_lead : str = "64b13bb2ebfad3000d22bdfe" , **kwargs) -> None:
        
        endpoint = self._get_endpoint(**kwargs)
        
        data_nascimento = datetime.strptime(data_nascimento_txt,('%Y-%m-%d'))
        dia = data_nascimento.day
        mes = data_nascimento.month
        ano = data_nascimento.year

        print (dia,mes,ano)

        self.label_indicacao = label_indicacao
        self.value_indicacao = value_indicacao
        self.label_data_indicacao = label_data_indicacao
        self.nome_paciente = nome_paciente
        self.telefone = telefone
        self.data_indicacao = data_indicacao
        self.value_sexo = value_sexo
        self.label_sexo = label_sexo
        self.label_fase_lead = label_fase_lead

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
            }
        ],
        "deal_stage_id": f"{label_fase_lead}",
        "name": f"{nome_paciente}"
        },
        "contacts": [
        {
            "birthday": {
                "day": dia,
                "month": mes,
                "year": ano
            },
            "phones": [
                {
                    "type": "cellphone",
                    "phone": f"{telefone}"
                }
            ]
        }
        ]


        }
        
        headers = {
        "accept": "application/json",
        "content-type": "application/json"
        }

        response = requests.post(url=endpoint, json=payload, headers=headers)

        print(response.status_code)