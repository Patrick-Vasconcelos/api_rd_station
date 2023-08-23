from api import Rd_api

if __name__ == "__main__":
    conexao = Rd_api()
    
    conexao.put_data(nome_paciente='Teste Larissa', value_indicacao= 'Teste Indicacao Larissa', data_indicacao= '23/08/2023')
    