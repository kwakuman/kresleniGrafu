#!/usr/bin/python3
'''
kresleniGrafu.py - vytvoří grafy vývoje spotřeby z dat nasbíraných měřičem.
parametry úpravy dat a grafů se dají nastavit v souboru options.txt
'''

import datetime, csv, pandas, logging, matplotlib, pathlib, os

logging.basicConfig(filename='kresleniGrafu.log',
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

#soubor s moznostmi nastaveni parametru
optionsFile = 'options.txt'

#vytvoření podadresářů v aktuálním adresáři
subfolders = ('csv', 'grafy')
for folder in subfolders:
    pathlib.Path(folder).mkdir(exist_ok=True)

#nacteni parametru do slovniku
with open(optionsFile) as options:
    moznosti = dict([y.split(',') for y in [x.strip() for x in options.readlines()]])
for klic, hodnota in moznosti.items():
    if hodnota.isnumeric():
        moznosti[klic] = int(hodnota)

'''transformace dat z měřiče do data framu pandas
 a vytvoření csv souboru pro případnou ruční prácy s daty'''
def convert_data(rawDataFile):
    with open(rawDataFile, 'r') as file:
        data = file.readlines()

    data = [item.strip() for item in data]
    data = [item.split(' ') for item in data]

    #vyrad druhy prvek v podseznamu, pokud je prazdny (objevuje se u kladnych cisel)
    for item in data:
        if item[1] == '':
            del item[1]
    #spoj datum a cas do jednoho retezce
    for item in data:
        datum_a_cas = ' '.join([item[2], item[3]])
        item.append(datum_a_cas)

    #vymaz samostatne datum a samostatny cas
    for item in data:
        for i in range(3, 1, -1):
            item.pop(i)

    #oznaceni faze prevedeno na cislo, posun (A) o dve desetina mista
    for item in data:
        item[0] = int(item[0])
        if float(item[1]) < 0:
            logging.debug('{}'.format(item))
            item[1] = 0
        item[1] = round(float(item[1])*50, 3)

    with open('csv/dataTest.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for line in data:
            writer.writerow(line)

    return data # list of lists

if __name__ == '__main__':
    #convert_data(moznosti['jmenoVstupnihoSouboru'])

    dataFile = 'csv/dataTest.csv'
    meritkoSpotreby = moznosti['intervalLokalnichMaxim']
    meritkoGrafy = moznosti['intervalOsaX']

    #load data frame
    dataFrame = pandas.DataFrame(convert_data(moznosti['jmenoVstupnihoSouboru']), columns=['faze', 'proud (A)', 'datum_a_cas_str'])
    #dataFrame = pandas.read_csv(dataFile, names=['faze', 'spotreba', 'datum_a_cas_str'])


    #create datetime object from 'datum_a_cas_str'
    dataFrame['datum_a_cas'] = pandas.to_datetime([datetime for datetime in dataFrame['datum_a_cas_str']])
    dataFrame.drop('datum_a_cas_str', axis=1, inplace=True)

    vsechnyFaze = []
    for i in range(1,4):
        dataFrameFaze = dataFrame[dataFrame['faze'] == i]
        dataFrameFaze.reset_index(drop=True, inplace=True)

        groups = dataFrameFaze.groupby(pandas.cut(dataFrameFaze.index, range(0, len(dataFrameFaze), meritkoSpotreby)))
        LokalniMaxima = groups['proud (A)'].idxmax()
        seskupenaData = dataFrameFaze.loc[LokalniMaxima]
        csvFile = 'csv/faze{}Test.csv'.format(i)
        seskupenaData.to_csv(csvFile)
        seskupenaData.reset_index(drop=True, inplace=True)
        vsechnyFaze.append(seskupenaData)

    #nakresleni grafu pro jednotlivé fáze
    for poradi, faze in enumerate(vsechnyFaze, start=1):
        pocetIntervalu = (len(faze) // meritkoGrafy) + 1
        for i in range(0, pocetIntervalu):

            hodnotyProGraf = faze[i*meritkoGrafy:meritkoGrafy*(i+1)]
            hodnotyProGraf.set_index('datum_a_cas')['proud (A)'].plot()

            matplotlib.pyplot.title('{} - fáze {}'.format(os.path.splitext(moznosti['jmenoVstupnihoSouboru'])[0] ,poradi))
            matplotlib.pyplot.xlabel('Datum a čas')
            matplotlib.pyplot.ylabel('Proud (A)')
            matplotlib.pyplot.ylim(moznosti['osaYMin'], moznosti['osaYMax'])

            zacatekGrafu = hodnotyProGraf['datum_a_cas'].min().to_pydatetime()
            zacatekGrafu = zacatekGrafu.strftime('%d-%m')
            konecGrafu = hodnotyProGraf['datum_a_cas'].max().to_pydatetime()
            konecGrafu = konecGrafu.strftime('%d-%m')

            matplotlib.pyplot.savefig('grafy/{}_Faze{}_{}_{}_{}.png'.format(os.path.splitext(moznosti['jmenoVstupnihoSouboru'])[0],poradi, zacatekGrafu, konecGrafu, i))
            matplotlib.pyplot.clf()

    #nakresleni grafů pro všechny fáze dohromady
    for i in range(0, int(len(vsechnyFaze[0]) // meritkoGrafy) + 1):

        for poradi, faze in enumerate(vsechnyFaze, start=1):
            hodnotyProGraf = faze[i*meritkoGrafy:meritkoGrafy*(i+1)]
            hodnotyProGraf.set_index('datum_a_cas')['proud (A)'].plot(label='fáze {}'.format(poradi))

        zacatekGrafu = hodnotyProGraf['datum_a_cas'].min().to_pydatetime()
        zacatekGrafu = zacatekGrafu.strftime('%d-%m')
        konecGrafu = hodnotyProGraf['datum_a_cas'].max().to_pydatetime()
        konecGrafu = konecGrafu.strftime('%d-%m')

        matplotlib.pyplot.title('{} - všechny fáze'.format(os.path.splitext(moznosti['jmenoVstupnihoSouboru'])[0]))
        matplotlib.pyplot.xlabel('Datum a čas')
        matplotlib.pyplot.ylabel('Proud (A)')
        matplotlib.pyplot.ylim(moznosti['osaYMin'], moznosti['osaYMax'])
        matplotlib.pyplot.legend()

        matplotlib.pyplot.savefig('grafy/{}_všechny fáze{}_{}_{}_{}.png'.format(os.path.splitext(moznosti['jmenoVstupnihoSouboru'])[0],poradi, zacatekGrafu, konecGrafu, i))
        matplotlib.pyplot.clf()
