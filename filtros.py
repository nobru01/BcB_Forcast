import pandas as pd
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly
import numpy as np

pd.options.display.float_format = '{:,.2f}'.format

atualiza_dados=input('Atualiza dados importando da API?(y/n)')
if atualiza_dados.lower()=='y':
    print('Inicializado Rotina json_collect.py.')
    from json_collect import coletar
    coletar()

# Relações datas das reuniões inseridas manualmente quando não tem previsão
df_selic_data=pd.read_csv('./input/selic_datas.csv', index_col='Reuniao')
# Dados baixados pelo .json
df_selic=pd.read_csv('./output/selic_data_df.csv', index_col='Reuniao')
df_selic=df_selic.drop(columns=['Unnamed: 0','Indicador'])
df_selic['Data']=pd.to_datetime(df_selic['Data']).dt.date

df_selic['data_reuniao']=''
for i in range(len(df_selic)):
    try:
        busca_data=df_selic_data.loc[df_selic.index[i],'data_reuniao']
        busca_data=datetime.datetime.strptime(busca_data,'%Y-%m-%d').date()
        df_selic.loc[df_selic.index[i],'data_reuniao']=busca_data
    except:
        #### será definida um expectativa para a data.
        # busca_data=df_selic_data.loc[df_selic.index[i],'data_reuniao']
        # df_selic.loc[df_selic.index[i],'data_reuniao']=busca_data
        continue

# df_selic['data_reuniao']=df_selic.apply(lambda x: datetime.datetime.strptime(x.data_reuniao,'%Y-%m-%d').date(),axis=1)
# df_selic=df_selic[df_selic['data_reuniao']!='']
df_selic=df_selic.sort_values(by=['Data','data_reuniao','baseCalculo'],ascending=[False,True,False])


'''Base de cálculo para as estatísticas
 baseada no prazo de validade das expectativas
 informadas pelas instituições informantes:
  - 0: uso das expectativas mais recentes informadas
   pelas instituições participantes a partir do
   30º dia anterior à data de cálculo das estatísticas 
  - 1: uso das expectativas mais recentes informadas
   pelas instituições participantes a partir do
    4º dia útil anterior à data de cálculo das estatísticas'''
# Gráfico iterativo utilizando o plotly
fig=px.line(df_selic,x='data_reuniao',y='Mediana', color='Data')
# Gerando arquivo com o resultado
plotly.offline.plot(fig, show_link = True, filename=f'./output/SELIC_forcast.html', auto_open=False)

# Informada à partir do 4º dia útil anterior à data de cálculo da expectativa.
df_selic = df_selic[df_selic['baseCalculo']==1]
# Expectativa mais atual
df_selic_ultima = df_selic[df_selic['Data']==df_selic['Data'].max()].copy()
# df_selic_ultima['mediana_mensal']=df_selic_ultima.apply(lambda x: (1+(x.Mediana/100))**(1/12)-1,axis=1)

# %%
# Insere coluna com números de dias no período (entre duas datas)
df_selic_ultima.loc[df_selic_ultima.index[0],'periodo']=(df_selic_ultima.loc[df_selic_ultima.index[0],'data_reuniao']-datetime.datetime.today().date()).days
# Define número índice de ref. 100 na data de hoje.
selic_atual=''
while type(selic_atual)!=float:
    try:
        selic_atual=float(input('Qual é a SELIC atual?(\d\d.d\d\)'))
    except:
        continue

# Cria num_indice inicial atribuindo 100 para a data de hoje
## Pode acontecer de demora para atualização do json do bc, gerando o primeiro período negativo, mas não tem problema
df_selic_ultima.loc[df_selic_ultima.index[0],'num_indice']=100*(1+selic_atual/100)**(df_selic_ultima.loc[df_selic_ultima.index[0],'periodo']/365)

# num_indice_f=num_indice_i*(1+taxa)**(periodo)
for i in range(1,len(df_selic_ultima)):

    #### Se der erro de tipos de srt com datatime é pq precisa inserir datas de reunião no input ###

    df_selic_ultima.loc[df_selic_ultima.index[i],'periodo']=(df_selic_ultima.loc[df_selic_ultima.index[i],'data_reuniao']-df_selic_ultima.loc[df_selic_ultima.index[i-1],'data_reuniao']).days
    df_selic_ultima.loc[df_selic_ultima.index[i],'num_indice']=df_selic_ultima.loc[df_selic_ultima.index[i-1],'num_indice']*(1+df_selic_ultima.loc[df_selic_ultima.index[i-1],'Mediana']/100)**(df_selic_ultima.loc[df_selic_ultima.index[i],'periodo']/365)

df_selic_ultima.to_csv('./output/selic_ultima_expectativa.csv',float_format='%.2f')

#### Função que calcula a SELIC do período entre data atual e data final
def calc_selic_periodo(df,data_f):
    # DF é um dataframe que contenha a culuna com num_indice
    
    # Utiliza a taxa digitada real vigente
    if data_f<=df.loc[df.index[0],'data_reuniao']:
        n_dias=(data_f-datetime.datetime.today().date()).days
        return 100*(1+selic_atual/100)**(n_dias/365)
    
    # Utiliza o número índice anterior + variação dos dias dentro do período
    else:
        df2=df[df['data_reuniao']<=data_f]
        n_indice=df2.loc[df2.index[-1],'num_indice']
        taxa=df2.loc[df2.index[-1],'Mediana']
        n_dias=(data_f-df2.loc[df2.index[-1],'data_reuniao']).days
        return n_indice*(1+taxa/100)**(n_dias/365)

df_monthly=pd.read_csv('./output/monthly_data_df.csv')
df_monthly=df_monthly.drop(columns=['Unnamed: 0'])
df_monthly['Data']=pd.to_datetime(df_monthly['Data']).dt.date
df_monthly['DataReferencia']=pd.to_datetime(df_monthly['DataReferencia'], format='%m/%Y').dt.date
delta = relativedelta(months=1)
delta_d = timedelta(days=1)
df_monthly['DataReferencia']=df_monthly['DataReferencia'].apply(lambda x: x+delta-delta_d)

df_monthly=df_monthly.sort_values(by=['Data','DataReferencia','numeroRespondentes'],ascending=[False,True,False])

fig=px.line(df_monthly[df_monthly['Indicador']=='IPCA'],x='DataReferencia',y='Mediana', color='Data')
plotly.offline.plot(fig, show_link=True, filename=f'./output/IPCA_forcast.html', auto_open=False)

# Gráfico iterativo utilizando o plotly
fig=px.line(df_monthly[df_monthly['Indicador']=='IGP-M'],x='DataReferencia',y='Mediana', color='Data')
# Gerando arquivo com o resultado
plotly.offline.plot(fig, show_link = True,filename=f'./output/IGPM_forcast.html', auto_open=False)

# Gráfico iterativo utilizando o plotly
fig=px.line(df_monthly[df_monthly['Indicador']=='Câmbio'],x='DataReferencia',y='Mediana', color='Data')
# Gerando arquivo com o resultado
plotly.offline.plot(fig, show_link = True,filename=f'./output/cambio_forcast.html', auto_open=False)
# fig.show()

# Gráfico iterativo utilizando o plotly
fig=px.line(df_monthly[df_monthly['Indicador']=='Taxa de desocupação'],x='DataReferencia',y='Mediana', color='Data')
# Gerando arquivo com o resultado
plotly.offline.plot(fig, show_link = True,filename=f'./output/tx_desocupacao_forcast.html', auto_open=False)
# fig.show()

# Expectativa mais atual para IPCA
df_ipca=df_monthly[df_monthly['Indicador']=='IPCA'].copy()
data_previsao=df_ipca['Data'].max()
df_ipca_ultima=df_ipca[df_ipca['Data']==data_previsao].copy()

# Selecione apenas colunas numéricas antes de calcular a média
df_ipca_ultima_numeric = df_ipca_ultima.select_dtypes(include=[np.number]).copy()
df_ipca_ultima_numeric['DataReferencia'] = df_ipca_ultima['DataReferencia']
df_ipca_ultima = df_ipca_ultima_numeric.groupby('DataReferencia', as_index=True).mean(numeric_only=True)

df_ipca_ultima['cumsum_mediana'] = df_ipca_ultima['Mediana'].cumsum()
#cumsum()-> soma acumulada de uma lista ou array termo a termo
#groupby -> delimita em grupos separados para análise
# df['Adjusted Quantity'] = df.groupby('ação_ref')['Adjusted Quantity'].cumsum()

# %%
# Insere coluna com números de dias no período (entre duas datas)

df_ipca_ultima.loc[df_ipca_ultima.index[0],'periodo']=(df_ipca_ultima.index[0]-datetime.datetime.today().date()).days

# Define número índice de ref. 100 na data de hoje.
df_ipca_ultima.loc[df_ipca_ultima.index[0],'num_indice']=100*(1+df_ipca_ultima.loc[df_ipca_ultima.index[0],'Mediana']/100)**(df_ipca_ultima.loc[df_ipca_ultima.index[0],'periodo']/30)

for i in range(1,len(df_ipca_ultima)):
    df_ipca_ultima.loc[df_ipca_ultima.index[i],'periodo']=(df_ipca_ultima.index[i]-df_ipca_ultima.index[i-1]).days
    df_ipca_ultima.loc[df_ipca_ultima.index[i],'num_indice']=df_ipca_ultima.loc[df_ipca_ultima.index[i-1],'num_indice']*(1+df_ipca_ultima.loc[df_ipca_ultima.index[i],'Mediana']/100)**(df_ipca_ultima.loc[df_ipca_ultima.index[i],'periodo']/30)

df_ipca_ultima.to_csv('./output/ipca_ultima_expectativa.csv',float_format='%.4f')

def calc_ipca_periodo(df,data_f):
    # DF é um dataframe que contenha a coluna com num_indice
    
    # Utiliza a taxa digitada real vigente
    if data_f<=df.index[0]:
        n_dias=(data_f-datetime.datetime.today().date()).days
        return 100*(1+df.loc[df.index[0],'Mediana']/100)**(n_dias/30)
    
    # Não calcula num_indice para o último termo, pois já está tabelado. 
    elif data_f==df.index[-1]:
        return df.loc[df.index[-1],'num_indice']

    # Utiliza o número índice anterior + variação dos dias dentro do período
    else:
        # Último número índice
        df_anterior=df[df.index<=data_f]
        # print(df_anterior)
        n_indice=df_anterior.loc[df_anterior.index[-1],'num_indice']
        prox_mes = df.index[len(df_anterior)]
        taxa=df.loc[prox_mes,'Mediana']    
        n_dias=(data_f-df_anterior.index[-1]).days
        return n_indice*(1+taxa/100)**(n_dias/30)

# Relação de datas até o mínimo entre os dataframes, para evitar erros
lista_datas_todos_dias=pd.date_range(start=datetime.datetime.today().date(),end=min(df_selic_ultima['data_reuniao'].max(),df_ipca_ultima.index.max()))
df_juros_real=pd.DataFrame(index=lista_datas_todos_dias,columns=['num_indice_selic','num_indice_ipca'],dtype='float64')

for i in range(len(df_juros_real)):
    df_juros_real.loc[df_juros_real.index[i],'num_indice_selic']=calc_selic_periodo(df_selic_ultima,df_juros_real.index[i].date())
    df_juros_real.loc[df_juros_real.index[i],'num_indice_ipca']=calc_ipca_periodo(df_ipca_ultima,df_juros_real.index[i].date())

# %%
df_ipca_ultima

# %%
# Não utilizada
def area(tipo,date):
    #tipo={selic,ipca}
    area=0
    df=df_juros_real[df_juros_real.index<=date]
    if (tipo=='selic' or tipo=='ipca'):
        for i in range(0,len(df)):
            area=area+1*df.loc[df.index[i],f'num_indice_{tipo}']
                
        return area
    else:
        print('Erro na escolha do tipo (selic ou ipca)')
    return 0

# %%
# df_juros_real['area_selic']=0
# for i in range(0,len(df_juros_real)):
#     # print(area('selic',df_juros_real.index[i]))
#     df_juros_real.loc[df_juros_real.index[i], 'area_selic']=area('selic',df_juros_real.index[i])
#     df_juros_real.loc[df_juros_real.index[i], 'area_ipca']=area('ipca',df_juros_real.index[i])
# df_juros_real

# %%
df_juros_real['dif_num_indice']=df_juros_real.apply(lambda x: x.num_indice_selic-x.num_indice_ipca+100,axis=1)
# df_juros_real['dif_area']=df_juros_real.apply(lambda x: x.area_selic-x.area_ipca,axis=1)
# df_juros_real['dif_area_por_dia']=df_juros_real.apply(lambda x: x.dif_area/(x.index-))
df_juros_real.to_csv('./output/num_indice_selic_ipca_diferenca.csv',float_format='%.2f')
df_juros_real


# %%
# Gráfico iterativo utilizando o plotly
fig=px.line(df_juros_real,x=df_juros_real.index,y=['num_indice_selic','num_indice_ipca','dif_num_indice'])
# Gerando arquivo com o resultado
# plotly.offline.plot(fig, show_link = True,filename=f'./output/IPCA_forcast.html')
# fig.show()

# %%
from time import strptime
from pyxirr import xirr
# calculo da IRR
def cal_irr(x,date,tipo):                #DF refer^rencia e a data de análise

    if date==x.index[0]:
        return (0,0,0,0)
    
    dates=[x.index[0],date]
    
    # tipo pode assumir ('selic' ou 'pre')
    if tipo=='selic':
        amounts=[-x.loc[x.index[0],'dif_num_indice'],x.loc[date,'dif_num_indice']]
    elif tipo=='pre_1':
        amounts=[-x.loc[x.index[0],'dif_num_indice_pre_1'],x.loc[date,'dif_num_indice_pre_1']]
    elif tipo=='pre_2':
        amounts=[-x.loc[x.index[0],'dif_num_indice_pre_2'],x.loc[date,'dif_num_indice_pre_2']]
            
    else:
        print('Erro de tipo diferente de "selic" ou "pre"') 
    # date=datetime.datetime.strptime(date,'%Y-%m-%d').date()
    # x=x[x.index==x.index[0] | x.index.date()==date]
    # dates=x.index
    # amounts=x['dif_num_indice']
    t_aa=xirr(dates, amounts)
    t_am=(1+t_aa)**(1/12)-1
    # print('TII a.a.(%): ',t_aa*100)
    # print('TII a.m.(%): ',t_am*100)
    # print('Soma dos valores: ',-x['Valor'].sum())
    # print(dates)
    # print(amounts)
    return (t_aa*100,t_am*100,dates,amounts)


# %%
for i in range(0,len(df_juros_real)):
    df_juros_real.loc[df_juros_real.index[i],'juros_real_acum_from_now']=cal_irr(df_juros_real,df_juros_real.index[i],'selic')[0]
    df_juros_real.loc[df_juros_real.index[i],'juros_real_am']=cal_irr(df_juros_real,df_juros_real.index[i],'selic')[1]

df_juros_real.head(30)

# %%
for i in range(0,len(df_juros_real)):
    # Primeiro dia do mês
    inicio_mes=df_juros_real.index[i]-timedelta(df_juros_real.index[i].day-1)
    if inicio_mes<=df_juros_real.index[0]:
        inicio_mes=df_juros_real.index[0]
    # print(f'Início do mês: {inicio_mes} - até: {df_juros_real.index[i]}')
    # Slice do DF do primeiro dia do mês até o dia da análise
    try:
        df_juros_real_i=df_juros_real[df_juros_real.index>=inicio_mes]
        df_juros_real_i=df_juros_real_i[df_juros_real_i.index<=df_juros_real.index[i]]
        # print(df_juros_real_i)
        df_juros_real.loc[df_juros_real.index[i],'juros_real_mesal']=cal_irr(df_juros_real_i,df_juros_real.index[i],'selic')[0]
    except:
        continue
df_juros_real.head(30)

# %%
def calc_pre_periodo(data_f,taxa_pre):
    n_dias=(data_f-datetime.datetime.today().date()).days
    return 100*(1+taxa_pre/100)**(n_dias/365)

# %%
calc_pre_periodo(datetime.datetime(2022,10,29).date(),12)

# %%
# Gera num_indice_taxa_pre-fixa
taxa_pre_1=14.74
taxa_pre_2=15.33
for i in range(0,len(df_juros_real)):
    df_juros_real.loc[df_juros_real.index[i],f'num_indice_pre_1']=calc_pre_periodo(df_juros_real.index[i].date(),taxa_pre_1)
    df_juros_real.loc[df_juros_real.index[i],f'num_indice_pre_2']=calc_pre_periodo(df_juros_real.index[i].date(),taxa_pre_2)

df_juros_real


# %%
# Agora que tenho num_indice_pre -> realizando os cálculos análogamente ao num_indice_selic
df_juros_real['dif_num_indice_pre_1']=df_juros_real.apply(lambda x: x.num_indice_pre_1-x.num_indice_ipca+100,axis=1)
df_juros_real['dif_num_indice_pre_2']=df_juros_real.apply(lambda x: x.num_indice_pre_2-x.num_indice_ipca+100,axis=1)


for i in range(0,len(df_juros_real)):
    df_juros_real.loc[df_juros_real.index[i],f'juros_real_acum_from_now_pre_{taxa_pre_1}%']=cal_irr(df_juros_real,df_juros_real.index[i],'pre_1')[0]
    df_juros_real.loc[df_juros_real.index[i],f'juros_real_acum_from_now_pre_{taxa_pre_2}%']=cal_irr(df_juros_real,df_juros_real.index[i],'pre_2')[0]

df_juros_real

# %%
# Gráfico iterativo utilizando o plotly
fig=px.line(df_juros_real,x=df_juros_real.index,y=['juros_real_acum_from_now','juros_real_mesal',f'juros_real_acum_from_now_pre_{taxa_pre_1}%',f'juros_real_acum_from_now_pre_{taxa_pre_2}%'])
# Gerando arquivo com o resultado
plotly.offline.plot(fig, show_link = True,filename=f'./output/Juros_real_forcast.html', auto_open=False)
# fig.show()

