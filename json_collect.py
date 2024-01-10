import urllib.request, json 
import pandas as pd

def coletar():
    # coleta dados api
    with urllib.request.urlopen("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativaMercadoMensais?$top=1000&$orderby=Data%20desc&$format=json&$select=Indicador,Data,DataReferencia,Media,Mediana,Minimo,Maximo,numeroRespondentes") as url:
        monthly_data = json.loads(url.read().decode())

    with urllib.request.urlopen("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoSelic?$top=100&$orderby=Data%20desc&$format=json&$select=*") as url:
        selic_data = json.loads(url.read().decode())

    with urllib.request.urlopen("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoTrimestrais?$top=100&$orderby=Data%20desc&$format=json&$select=Indicador,Data,DataReferencia,Media,Mediana,Minimo,Maximo,numeroRespondentes") as url:
        quarterly_data = json.loads(url.read().decode())

    with urllib.request.urlopen("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoInflacao12Meses?$top=100&$orderby=Data%20desc&$format=json&$select=Indicador,Data,Suavizada,Media,Mediana,Minimo,Maximo,numeroRespondentes") as url:
        twelve_months_data = json.loads(url.read().decode())

    with urllib.request.urlopen("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais?$top=1000&$orderby=Data%20desc&$format=json&$select=Indicador,IndicadorDetalhe,Data,DataReferencia,Media,Mediana,Minimo,Maximo,numeroRespondentes") as url:
        annual_data = json.loads(url.read().decode())

    # transforma json para df
    monthly_data_df = pd.DataFrame.from_dict(
        monthly_data['value'], orient='columns')
    monthly_data_df.to_csv('./output/monthly_data_df.csv')

    selic_data_df = pd.DataFrame.from_dict(
        selic_data['value'], orient='columns')
    selic_data_df.to_csv('./output/selic_data_df.csv')

    quarterly_data_df = pd.DataFrame.from_dict(
        quarterly_data['value'], orient='columns')
    quarterly_data_df.to_csv('./output/quarterly_data_df.csv')


    twelve_months_data_df = pd.DataFrame.from_dict(
        twelve_months_data['value'], orient='columns')
    twelve_months_data_df.to_csv('./output/twelve_months_data_df.csv')


    annual_data_df = pd.DataFrame.from_dict(
        annual_data['value'], orient='columns')
    annual_data_df.to_csv('./output/annual_data_df.csv')

    print("json_collect executed")



