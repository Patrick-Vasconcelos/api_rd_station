from api import PutDeals

if __name__ == "__main__":
    PutDeals().put_data(nome_paciente='paciente teste api', telefone = '859996716012',data_nascimento_txt='1979-01-01', value_indicacao='Indicacao Teste Completa', data_indicacao='01/01/2023', value_sexo= 'Feminino')
