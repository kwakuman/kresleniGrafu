#!/usr/bin/python3

'''
detailniGraf.py vykresli podrobny graf spotreby v rozmezi dat dle zadani uzivatele
'''

import pandas
import matplotlib
import os
from kresleniGrafu import convert_data

# load options dictionary from options file
optionsFile = 'options.txt'
with open(optionsFile) as options:
    moznosti = dict([y.split(',') for y in [x.strip() for x in options.readlines()]])
for klic, hodnota in moznosti.items():
    if hodnota.isnumeric():
        moznosti[klic] = int(hodnota)

sourceDataFile = moznosti['jmenoVstupnihoSouboru']

optionsFile = 'detailOptions.txt'
with open(optionsFile) as options:
    moznosti = dict([y.split(',') for y in [x.strip() for x in options.readlines()]])
for klic, hodnota in moznosti.items():
    if hodnota.isnumeric():
        moznosti[klic] = int(hodnota)

datumStart = moznosti['datumStart']
datumStop = moznosti['datumStop']


dataFrame = pandas.DataFrame(convert_data(sourceDataFile), columns=[
                             'faze', 'proud (A)', 'datum_a_cas_str'])
dataFrame['datum_a_cas'] = pandas.to_datetime(
    [datetime for datetime in dataFrame['datum_a_cas_str']])
dataFrame.drop('datum_a_cas_str', axis=1, inplace=True)

mask = (dataFrame['datum_a_cas'] > datumStart) & (dataFrame['datum_a_cas'] <= datumStop)
dataFrame = dataFrame.loc[mask]


def kresliGraf(df):
    vsechnyFaze = []
    meritkoSpotreby = moznosti['intervalLokalnichMaxim']
    meritkoGrafy = moznosti['intervalOsaX']

    for i in range(1, 4):
        dataFrameFaze = df[df['faze'] == i]
        dataFrameFaze.reset_index(drop=True, inplace=True)

        groups = dataFrameFaze.groupby(pandas.cut(
            dataFrameFaze.index, range(0, len(dataFrameFaze), meritkoSpotreby)))
        LokalniMaxima = groups['proud (A)'].idxmax()
        seskupenaData = dataFrameFaze.loc[LokalniMaxima]
        #csvFile = 'csv/faze{}Test.csv'.format(i)
        # seskupenaData.to_csv(csvFile)
        seskupenaData.reset_index(drop=True, inplace=True)
        vsechnyFaze.append(seskupenaData)

    # nakresleni grafu pro jednotlivé fáze
    for poradi, faze in enumerate(vsechnyFaze, start=1):
        pocetIntervalu = (len(faze) // meritkoGrafy) + 1
        for i in range(0, pocetIntervalu):

            hodnotyProGraf = faze[i*meritkoGrafy:meritkoGrafy*(i+1)]

            if not hodnotyProGraf.empty:
                hodnotyProGraf.set_index('datum_a_cas')['proud (A)'].plot()
                matplotlib.pyplot.title(
                    f'detail {os.path.splitext(sourceDataFile)[0]} - fáze {poradi}')
                matplotlib.pyplot.xlabel('Datum a čas')
                matplotlib.pyplot.ylabel('Proud (A)')
                matplotlib.pyplot.ylim(moznosti['osaYMin'], moznosti['osaYMax'])

                zacatekGrafu = hodnotyProGraf['datum_a_cas'].min().to_pydatetime()
                zacatekGrafu = zacatekGrafu.strftime('%d-%m')
                konecGrafu = hodnotyProGraf['datum_a_cas'].max().to_pydatetime()
                konecGrafu = konecGrafu.strftime('%d-%m')

                matplotlib.pyplot.savefig('grafy/detail_{}_Faze{}_{}_{}_{}.png'.format(
                    os.path.splitext(sourceDataFile)[0], poradi, zacatekGrafu, konecGrafu, i))
                matplotlib.pyplot.clf()

    # nakresleni grafů pro všechny fáze dohromady
    for i in range(0, int(len(vsechnyFaze[0]) // meritkoGrafy) + 1):
        pocetIntervalu = (len(vsechnyFaze[0]) // meritkoGrafy) + 1
        for poradi, faze in enumerate(vsechnyFaze, start=1):

            hodnotyProGraf = faze[i*meritkoGrafy:meritkoGrafy*(i+1)]
            hodnotyProGraf.set_index('datum_a_cas')['proud (A)'].plot(
                label='fáze {}'.format(poradi))

        if not hodnotyProGraf.empty:
            zacatekGrafu = hodnotyProGraf['datum_a_cas'].min().to_pydatetime()
            zacatekGrafu = zacatekGrafu.strftime('%d-%m')
            konecGrafu = hodnotyProGraf['datum_a_cas'].max().to_pydatetime()
            konecGrafu = konecGrafu.strftime('%d-%m')

            matplotlib.pyplot.title(f'detail {os.path.splitext(sourceDataFile)[0]} - všechny fáze')
            matplotlib.pyplot.xlabel('Datum a čas')
            matplotlib.pyplot.ylabel('Proud (A)')
            matplotlib.pyplot.ylim(moznosti['osaYMin'], moznosti['osaYMax'])
            matplotlib.pyplot.legend()

            matplotlib.pyplot.savefig('grafy/detail_{}_všechny fáze{}_{}_{}_{}.png'.format(
                os.path.splitext(sourceDataFile)[0], poradi, zacatekGrafu, konecGrafu, i))
            matplotlib.pyplot.clf()


kresliGraf(dataFrame)
