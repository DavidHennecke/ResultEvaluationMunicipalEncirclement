# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:47:42 2023

@author: David Hennecke
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Pfade
nrwPath = r"Testdaten/dvg1_EPSG25832_Shape/dvg1bld_nw_32632.shp"
nrwGemPath = r"Testdaten/dvg1_EPSG25832_Shape/dvg1gem_nw_32632.shp"
clusterPath = r"Testdaten/cluster_32632.shp"
stockPathAktiv= r"Testdaten/Windbetrieb_Standorte_32632.shp"
stockPathAktivGen = r"Testdaten/Windbetrieb_WindGen_Standorte_32632.shp"
stockPathAktivStill = r"Testdaten/Anlagen_Aktiv_Still.shp"
stockPathAktivStillGen = r"Testdaten/Anlagen_Aktiv_Still_WindGen.shp"

#Daten laden
nrwGpd = gpd.read_file(nrwPath)
nrwGemGpd = gpd.read_file(nrwGemPath)
cluster = gpd.read_file(clusterPath)
stockAktiv = gpd.read_file(stockPathAktiv)
stockAktivGen = gpd.read_file(stockPathAktivGen)
stockAktivStill = gpd.read_file(stockPathAktivStill)
stockAktivStillGen = gpd.read_file(stockPathAktivStillGen)

def initData(allowedPath, restrictedPath, forbiddenPath):
    allowedGpd = gpd.read_file(allowedPath)
    restrictedGpd = gpd.read_file(restrictedPath)
    forbiddenGpd = gpd.read_file(forbiddenPath)
    
    #Daten verschneiden
    allowedGpd = allowedGpd.overlay(restrictedGpd, how='difference')
    allowedGpd = allowedGpd.overlay(forbiddenGpd, how='difference')
    allowedGpd = allowedGpd.overlay(nrwGpd, how='intersection')
    allowedGemGpd = allowedGpd.overlay(nrwGemGpd, how='intersection')
    d = {'GN': allowedGemGpd.GN_2, 'allowed': allowedGemGpd.geometry.area/1000000}
    allowedGpdResults = pd.DataFrame(data=d)
    
    restrictedGpd = restrictedGpd.overlay(forbiddenGpd, how='difference')
    restrictedGpd = restrictedGpd.overlay(nrwGpd, how='intersection')
    restrictedGemGpd = restrictedGpd.overlay(nrwGemGpd, how='intersection')
    d = {'GN': restrictedGemGpd.GN_2, 'restricted': restrictedGemGpd.geometry.area/1000000}
    restrictedGpdResults = pd.DataFrame(data=d)
    
    forbiddenGpd = forbiddenGpd.overlay(nrwGpd, how='intersection')
    forbiddenGemGpd = forbiddenGpd.overlay(nrwGemGpd, how='intersection')
    d = {'GN': forbiddenGemGpd.GN_2, 'forbidden': forbiddenGemGpd.geometry.area/1000000}
    forbiddenGpdResults = pd.DataFrame(data=d)

    return allowedGpdResults, restrictedGpdResults, forbiddenGpdResults

#Ergebnisse zusammentragen
def getResults(allowedGpdResults, restrictedGpdResults, forbiddenGpdResults):
    d = {'GN': nrwGemGpd.GN, 'Area_NRW':nrwGemGpd.geometry.area.sum()/1000000, 'Area_Gem': nrwGemGpd.geometry.area/1000000}
    res = pd.DataFrame(data=d)
    res = res.set_index('GN').join(allowedGpdResults.set_index('GN'))
    res = res.join(restrictedGpdResults.set_index('GN'))
    res = res.join(forbiddenGpdResults.set_index('GN'))
    return res

# Statistische Auswertung
def statEv (res):
    res['allowedPercentage'] = res.allowed / res.Area_Gem * 100
    res['allowedGesamt'] = res.allowed.sum()
    res['restrictedPercentage'] = res.restricted / res.Area_Gem * 100
    res['restrictedGesamt'] = res.restricted.sum()
    res['forbiddenPercentage'] = res.forbidden / res.Area_Gem * 100
    res['forbiddenGesamt'] = res.forbidden.sum()
    dataSzenario = {'Mean': res.allowed.mean(), 'Min': res.allowed.min(),'Max': res.allowed.max(),'Quartile25': res.allowedPercentage.quantile(0.25), 'MedianPercent': res.allowedPercentage.median(),  'Quartile75': res.allowedPercentage.quantile(0.75), 'StdPercent': res.allowedPercentage.std(), 'Varaince': res.allowedPercentage.var(), 'Kurtosis': res.allowedPercentage.kurt(), 'SkewPercent': res.allowedPercentage.skew()}
    serSzenario = pd.Series(data=dataSzenario)

    return res, serSzenario

#AKTIV_STILL


allowedPath = r"Ergebnisse/Aktiv_Still/allowedAreas.shp"
restrictedPath = r"Ergebnisse/Aktiv_Still/restrictedAreas.shp"
forbiddenPath = r"Ergebnisse/Aktiv_Still/forbiddenAreas.shp"

# Statistische Auswertung
allowedGpdResults, restrictedGpdResults, forbiddenGpdResults = initData(allowedPath, restrictedPath, forbiddenPath)
resultsAktivStill = getResults(allowedGpdResults, restrictedGpdResults, forbiddenGpdResults)
resultsAktivStill, serAktivStill = statEv(resultsAktivStill)

#Export
resultsAktivStill.to_csv('Ergebnisse/resultsGemAktivStill.csv')

#Histogramm
plt.figure(figsize=(8, 6))
#sns.violinplot(y=data.allowedPercentage, cut=0, inner='quartile')
ax = sns.histplot( x=resultsAktivStill.forbiddenPercentage, kde=True)
ax.lines[0].set_color('crimson')
plt.title(' Aktive und stillgelegte WKA', pad=20)
plt.ylabel('Häufigkeit')
plt.xlabel('Prozentualer Anteil der Verbotsfläche an der Gemeindefläche')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Ergebnisse/perc_forbidden_AktivStill.svg', dpi=300)
plt.show()



#AKTIV_STILL_GEN

#Pfade

allowedPath = r"Ergebnisse/Aktiv_Still_Gen/allowedAreas.shp"
restrictedPath = r"Ergebnisse/Aktiv_Still_Gen/restrictedAreas.shp"
forbiddenPath = r"Ergebnisse/Aktiv_Still_Gen/forbiddenAreas.shp"

#Daten laden
allowedGpd = gpd.read_file(allowedPath)
restrictedGpd = gpd.read_file(restrictedPath)
forbiddenGpd = gpd.read_file(forbiddenPath)

# Statistische Auswertung
allowedGpdResults, restrictedGpdResults, forbiddenGpdResults = initData(allowedPath, restrictedPath, forbiddenPath)
resultsAktivStillGen = getResults(allowedGpdResults, restrictedGpdResults, forbiddenGpdResults)
resultsAktivStillGen, serAktivStillGen = statEv(resultsAktivStill)

#Export
resultsAktivStillGen.to_csv('Ergebnisse/resultsGemAktivStillGen.csv')

#Histogramm
plt.figure(figsize=(8, 6))
#sns.violinplot(y=data.allowedPercentage, cut=0, inner='quartile')
ax = sns.histplot( x=resultsAktivStillGen.forbiddenPercentage, kde=True)
ax.lines[0].set_color('crimson')
plt.title(' Aktive, stillgelegte und in der Genehmigungsphase befindlichen WKA', pad=20)
plt.ylabel('Häufigkeit')
plt.xlabel('Prozentualer Anteil der Verbotsfläche an der Gemeindefläche')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Ergebnisse/perc_forbidden_AktivStillGen.svg', dpi=300)
plt.show()



#AKTIV

#Pfade
allowedPath = r"Ergebnisse/Aktiv/allowedAreas.shp"
restrictedPath = r"Ergebnisse/Aktiv/restrictedAreas.shp"
forbiddenPath = r"Ergebnisse/Aktiv/forbiddenAreas.shp"

#Daten laden
allowedGpd = gpd.read_file(allowedPath)
restrictedGpd = gpd.read_file(restrictedPath)
forbiddenGpd = gpd.read_file(forbiddenPath)


# Statistische Auswertung
allowedGpdResults, restrictedGpdResults, forbiddenGpdResults = initData(allowedPath, restrictedPath, forbiddenPath)
resultsAktiv = getResults(allowedGpdResults, restrictedGpdResults, forbiddenGpdResults)
resultsAktiv, serAktiv = statEv(resultsAktiv)
#Export
resultsAktiv.to_csv('Ergebnisse/resultsGemAktiv.csv')

#Histogramm
plt.figure(figsize=(8, 6))
#sns.violinplot(y=data.allowedPercentage, cut=0, inner='quartile')
ax = sns.histplot( x=resultsAktiv.forbiddenPercentage, kde=True)
ax.lines[0].set_color('crimson')
plt.title(' Aktive WKA', pad=20)
plt.ylabel('Häufigkeit')
plt.xlabel('Prozentualer Anteil der Verbotsfläche an der Gemeindefläche')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Ergebnisse/perc_forbidden_Aktiv.svg', dpi=300)
plt.show()



#AKTIV_GEN

#Pfade
allowedPath = r"Ergebnisse/Aktiv_Still_Gen/allowedAreas.shp"
restrictedPath = r"Ergebnisse/Aktiv_Gen/restrictedAreas.shp"
forbiddenPath = r"Ergebnisse/Aktiv_Gen/forbiddenAreas.shp"

#Daten laden
allowedGpd = gpd.read_file(allowedPath)
restrictedGpd = gpd.read_file(restrictedPath)
forbiddenGpd = gpd.read_file(forbiddenPath)

# Statistische Auswertung
allowedGpdResults, restrictedGpdResults, forbiddenGpdResults = initData(allowedPath, restrictedPath, forbiddenPath)
resultsAktivGen = getResults(allowedGpdResults, restrictedGpdResults, forbiddenGpdResults)
resultsAktivGen, serAktivGen = statEv(resultsAktivGen)

#Export
resultsAktivGen.to_csv('Ergebnisse/resultsGemAktivGen.csv')

#Histogramm
plt.figure(figsize=(8, 6))
#sns.violinplot(y=data.allowedPercentage, cut=0, inner='quartile')
ax = sns.histplot( x=resultsAktivGen.forbiddenPercentage, kde=True)
ax.lines[0].set_color('crimson')
plt.title(' Aktive und in der Genehmigungsphase befindlichen WKA', pad=20)
plt.ylabel('Häufigkeit')
plt.xlabel('Prozentualer Anteil der Verbotsfläche an der Gemeindefläche')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Ergebnisse/perc_forbidden_AktivGen.svg', dpi=300)
plt.show()


#GESAMT
resultsGem = pd.DataFrame()
resultsGem["Aktiv"] = serAktiv
resultsGem["AktivGen"] = serAktivGen
resultsGem["AktivStill"] = serAktivStill
resultsGem["AktivStillGen"] = serAktivStillGen

    
gemCluster = cluster.overlay(nrwGemGpd, how='intersection')
gemStockAktiv = stockAktiv.overlay(nrwGemGpd, how='intersection')
gemStockAktivGen = stockAktivGen.overlay(nrwGemGpd, how='intersection')
gemStockAktivStill = stockAktivStill.overlay(nrwGemGpd, how='intersection')
gemStockAktivStillGen = stockAktivStillGen.overlay(nrwGemGpd, how='intersection')
gemCluster = gemCluster.groupby(['GN']).size().reset_index(name='count')
gemStockAktiv = gemStockAktiv.groupby(['GN']).size().reset_index(name='count')
gemStockAktivGen = gemStockAktivGen.groupby(['GN']).size().reset_index(name='count')
gemStockAktivStill = gemStockAktivStill.groupby(['GN']).size().reset_index(name='count')
gemStockAktivStillGen = gemStockAktivStillGen.groupby(['GN']).size().reset_index(name='count')
d = {'GN': gemCluster.GN, 'clusterNum': gemCluster['count'], 'wkaNumAktiv': gemStockAktiv['count'], 'wkaNumAktivGen': gemStockAktivGen['count'], 'wkaNumAktivStill': gemStockAktivStill['count'], 'wkaNumAktivStillGen': gemStockAktivStillGen['count']}
stockClusterGpdResults = pd.DataFrame(data=d)

#Export
resultsGem.to_csv('Ergebnisse/resultsGemGeneral.csv')

with pd.ExcelWriter('Ergebnisse/resultsGem.xlsx') as writer:  
    resultsGem.to_excel(writer, sheet_name='General')
    resultsAktiv.to_excel(writer, sheet_name='Aktiv')
    resultsAktivGen.to_excel(writer, sheet_name='AktivGen')
    resultsAktivStill.to_excel(writer, sheet_name='AktivStill')
    resultsAktivStillGen.to_excel(writer, sheet_name='AktivStillGen')
    stockClusterGpdResults.to_excel(writer, sheet_name='Stock Cluster Count')


#datenGesamt = {'Szenario':,'allowedMin':,'allowedMax':,'allowedMedian':,'restrictedMin':,'restrictedMax':,'restrictedMedian':,'forbiddenMin':,'forbiddenMax':,'forbiddenMedian':}