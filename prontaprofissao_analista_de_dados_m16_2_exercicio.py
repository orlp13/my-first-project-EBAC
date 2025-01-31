# -*- coding: utf-8 -*-
"""prontaProfissao Analista de dados M16 2 Exercicio.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nXwMfWeRuEshyS5U551CgsdBKyogJ_j2

<img src="https://raw.githubusercontent.com/andre-marcos-perez/ebac-course-utils/main/media/logo/newebac_logo_black_half.png" alt="ebac-logo">

---

# **Módulo** | Análise de Dados: Análise Exploratória de Dados de Logística II
Caderno de **Exercícios**<br>
Professor [André Perez](https://www.linkedin.com/in/andremarcosperez/)

---

# **Tópicos**

<ol type="1">
  <li>Manipulação;</li>
  <li>Visualização;</li>
  <li>Storytelling.</li>
</ol>

---

# **Exercícios**

Este *notebook* deve servir como um guia para **você continuar** a construção da sua própria análise exploratória de dados. Fique a vontate para copiar os códigos da aula mas busque explorar os dados ao máximo. Por fim, publique seu *notebook* no [Kaggle](https://www.kaggle.com/).

---

# **Análise Exploratória de Dados de Logística**

## 1\. Contexto

Escreva uma breve descrição do problema.

## 2\. Pacotes e bibliotecas
"""

# importe todas as suas bibliotecas aqui, siga os padrões do PEP8:

import json
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopandas
import matplotlib.pyplot as plt
import seaborn as sns

"""## 3\. Exploração de dados"""

# faça o código de exploração de dados:
!wget -q "https://raw.githubusercontent.com/andre-marcos-perez/ebac-course-utils/main/dataset/deliveries.json" -O deliveries.json
# - coleta de dados;
with open('deliveries.json', mode='r', encoding='utf8') as file:
  data = json.load(file)
# - wrangling da estrutura;
df = pd.DataFrame(data)
df.head()

"""## 4\. Manipulação"""

# normalize coluna origin
hub_origin_df = pd.json_normalize(df["origin"])
hub_origin_df.head()

#juncao no dataframe principal a  nova coluna origin
df = pd.merge(left=df, right=hub_origin_df, how='inner', left_index=True, right_index=True)
df.head()

#separando coluna origin en dois novas colunas
df = df.drop("origin", axis=1)
df = df[["name", "region", "lng", "lat", "vehicle_capacity", "deliveries"]]
df.head()

#trocando o nome das novas colunas
df.rename(columns={"lng": "hub_lng", "lat": "hub_lat"}, inplace=True)
df.head()

# coluna deliveries
deliveries_exploded_df = df[["deliveries"]].explode("deliveries")
deliveries_exploded_df.head()

#separando coluna deliveries
deliveries_normalized_df = pd.concat([
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["size"])).rename(columns={"deliveries": "delivery_size"}),
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["point"]["lng"])).rename(columns={"deliveries": "delivery_lng"}),
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record["point"]["lat"])).rename(columns={"deliveries": "delivery_lat"}),
  pd.DataFrame(deliveries_exploded_df["deliveries"].apply(lambda record: record.get("id", None))).rename(columns={"deliveries": "vehicle_id"})
  ], axis=1)
deliveries_normalized_df

len(deliveries_exploded_df)

len(df)

df = df.drop("deliveries", axis=1)
df = pd.merge(left=df, right=deliveries_normalized_df, how='right', left_index=True, right_index=True)
df.head()

df.shape

df.columns

df.index

df.info()

df.isna().any()

hub_df = df[["region", "hub_lng", "hub_lat"]]
hub_df = hub_df.drop_duplicates().sort_values(by="region").reset_index(drop=True)
hub_df.head()

geolocator = Nominatim(user_agent="ebac_geocoder")
location = geolocator.reverse("-15.657013854445248, -47.802664728268745")

print(json.dumps(location.raw, indent=2, ensure_ascii=False))

from geopy.extra.rate_limiter import RateLimiter

geocoder = RateLimiter(geolocator.reverse, min_delay_seconds=1)

hub_df["coordinates"] = hub_df["hub_lat"].astype(str)  + ", " + hub_df["hub_lng"].astype(str)
hub_df["geodata"] = hub_df["coordinates"].apply(geocoder)
hub_df.head()

hub_geodata_df = pd.json_normalize(hub_df["geodata"].apply(lambda data: data.raw))
hub_geodata_df.head()

hub_geodata_df.columns

geodata_df = hub_geodata_df[["address.town", "address.suburb", "address.city"]]
geodata_df.rename(columns={"address.town": "town", "address.suburb": "suburb", "address.city": "city"}, inplace=True)

geodata_df["city"] = np.where(geodata_df["city"].notna(), geodata_df["city"], geodata_df["town"])
geodata_df["suburb"] = np.where(geodata_df["suburb"].notna(), geodata_df["suburb"], geodata_df["city"])
geodata_df = geodata_df.drop("town", axis=1)
geodata_df.head()

geodata_df.isna().any()

hub_df = pd.merge(left=hub_df, right=geodata_df, left_index=True, right_index=True)
hub_df = hub_df[["region", "city", "suburb"]]
hub_df.head()

# Perform the merge
df = pd.merge(left=df, right=hub_df, how='inner', left_on="region", right_on="region")
df = df[["name", "region", "hub_lng", "hub_lat", "city", "suburb", "vehicle_capacity", "vehicle_id", "delivery_size", "delivery_lng", "delivery_lat"]]


df.head()

"""## 5\. Visualização"""

# faça o código de visualização de dados:
!wget -q "https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bc100/go_df/versao2016/shapefile/bc100_go_df_shp.zip" -O distrito-federal.zip
!unzip -q distrito-federal.zip -d ./maps
!cp ./maps/LIM_Unidade_Federacao_A.shp ./distrito-federal.shp
!cp ./maps/LIM_Unidade_Federacao_A.shx ./distrito-federal.shx

mapa = geopandas.read_file("distrito-federal.shp")
mapa = mapa.loc[[0]]
mapa.head()

hub_df = df[["region", "hub_lng", "hub_lat"]].drop_duplicates().reset_index(drop=True)
geo_hub_df = geopandas.GeoDataFrame(hub_df, geometry=geopandas.points_from_xy(hub_df["hub_lng"], hub_df["hub_lat"]))
geo_hub_df.head()

geo_deliveries_df = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["delivery_lng"], df["delivery_lat"]))
geo_deliveries_df.head()

# cria o plot vazio
fig, ax = plt.subplots(figsize = (50/2.54, 50/2.54))

# plot mapa do distrito federal
mapa.plot(ax=ax, alpha=0.4, color="lightgrey")

# plot das entregas
geo_deliveries_df.query("region == 'df-0'").plot(ax=ax, markersize=1, color="red", label="df-0")
geo_deliveries_df.query("region == 'df-1'").plot(ax=ax, markersize=1, color="blue", label="df-1")
geo_deliveries_df.query("region == 'df-2'").plot(ax=ax, markersize=1, color="seagreen", label="df-2")

# plot dos hubs
geo_hub_df.plot(ax=ax, markersize=30, marker="x", color="black", label="hub")

# plot da legenda
plt.title("Entregas no Distrito Federal por Região", fontdict={"fontsize": 16})
lgnd = plt.legend(prop={"size": 15})
for handle in lgnd.legendHandles:
    handle.set_sizes([50])

"""- **Insights**:

1. As **entregas** estão corretamente alocadas aos seus respectivos **hubs**;
1. Os **hubs** das regiões 0 e 2 fazem **entregas** em locais distantes do centro e entre si, o que pode gerar um tempo e preço de entrega maior.
"""

data = pd.DataFrame(df[['region', 'vehicle_capacity']].value_counts(normalize=True)).reset_index()
data.rename(columns={0: "region_percent"}, inplace=True)
data.head()

with sns.axes_style('whitegrid'):
  grafico = sns.barplot(data=data, x="region", y="proportion", errorbar=None, palette="pastel")
  grafico.set(title='Proporção de entregas por região', xlabel='Região', ylabel='Proporção');

"""- **Insights**:

1. A distribuição das **entregas** está muito concentrada nos **hubs** das regiões 1 e 2, mas pouco no da região 0. Contudo a capacidade dos veículos é mesma para todos os **hubs**, logo os **veículos** poderiam ser deslocados para as regiões de maior tráfego.
"""