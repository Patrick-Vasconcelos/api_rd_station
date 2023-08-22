import requests
from abc import abstractmethod, ABC
import logging
import pandas as pd

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
    
    def put_data(self,nome_paciente, value_indicacao,data_indicacao, label_indicacao = "64e4c19a2c71dd000e03ead5", label_data_indicacao = "64e4abda173a72001acc99ff", label_fase_lead = "64b13bb2ebfad3000d22bdfe" , **kwargs) -> None:
        
        endpoint = self._get_endpoint(**kwargs)


        
        payload = { "deal": {
        "deal_custom_fields": [
            {
                "custom_field_id": f"{self.label_indicacao}",
                "value": f"{self.value_indicacao}"
            },
            {
                "custom_field_id": f"{self.label_data_indicacao}",
                "value": f"{self.data_indicacao}"
            }
        ],
        "deal_stage_id": f"{self.label_fase_lead}",
        "name": f"{self.nome_paciente}"
        } }
        headers = {
        "accept": "application/json",
        "content-type": "application/json"
        }

        response = requests.post(url=endpoint, json=payload, headers=headers)

        print(response.text)