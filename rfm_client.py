#Para saber quem são os cientes mais valiosos com base no comportamento de compras, podendo oferecer mais promoções, descontos etc..
import pandas as pd
import matplotlib.pyplot as plt
# 1. Carregar os dados
df = pd.read_csv("dados_vendas.csv")

#Converter coluna de data
df['Data'] = pd.to_datetime(df['Data'])

# 2. Calcular RFM
data_referencia = df['Data'].max() + pd.Timedelta(days=1) #Define uma data de referência como 1 dia após a última venda. Isso serve para calcular "Recência".


rfm = df.groupby('Cliente').agg({
    'Data': lambda x: (data_referencia - x.max()).days, #Recencia: dias desde a ultima compra
    'Cliente': 'count', #Frequencia: Quantas compras o cliente fez(quantas vezes o cliente aparece na base)
    'Total_Venda': 'sum' #Monetário: Total gasto do cliente
}).rename(columns={
    'Data': 'Recencia',
    'Cliente': 'Frequencia',
    'Total_Venda': 'Valor'
}).reset_index()

# 3. Gerar scores RFM (1-5)
rfm['R'] = pd.qcut(rfm['Recencia'], 5, labels=[5,4,3,2,1]).astype(int) #Divide a coluna Recencia em 5 quintis, cliente com maior R tem 5 de quintis,menor tem 1
rfm['F'] = pd.qcut(rfm['Frequencia'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
rfm['M'] = pd.qcut(rfm['Valor'], 5, labels=[1,2,3,4,5]).astype(int)
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str) #Concatena as notas de R, F e M para formar um score como 555, 314, 211, etc.

# 4. Segmentação simples
def segmentar(rfm_score):
    if rfm_score == '555':
        return 'Cliente VIP'
    elif rfm_score[0] == '5':
        return 'Recente'
    elif rfm_score[2] == '5':
        return 'Gastador'
    elif rfm_score[1] == '5':
        return 'Frequente'
    else:
        return 'Regular'

rfm['Segmento'] = rfm['RFM_Score'].apply(segmentar)

# 5. Resultados
print("Top 10 clientes por valor:")
print(rfm.sort_values('Valor', ascending=False).head(10))

#Mostra os clientes que estao em cada categoria de segmentação
print("\nDistribuição de segmentos:")
print(rfm['Segmento'].value_counts())

# Ordenar por RFM Score decrescente (VIPs no topo)
clientes_ordenados = rfm.sort_values(by=['R', 'F', 'M'], ascending=False)
print(clientes_ordenados[['Cliente', 'RFM_Score', 'Segmento']].head(10))

# 7. Gráfico de pizza dos segmentos
segmentos = rfm['Segmento'].value_counts()
plt.figure(figsize=(8, 6))
plt.pie(segmentos, labels=segmentos.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribuição dos Segmentos de Clientes (RFM)')
plt.axis('equal')  # Deixa o gráfico circular
plt.tight_layout()

# Salvar a imagem
plt.savefig("assets/grafico_rfm.png")
plt.show()