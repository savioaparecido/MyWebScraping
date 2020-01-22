"""
Criado por Sávio Aparecido
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


class getB3:
    """
    Classe para obter dados de FII de renda variável no site da B3
    """
    def __init__(self, fii, diretorio, num_coluna, tipoTabela):
        """
        :param fii: código da FII
        :param diretorio: caminho para salvar arquivo
        :param num_coluna: número de colunas na tabela; geralmente é 12 ou 15
        :param tipoTabela: tblResMensal ou tblResDiario
        """

        self.fii = fii.upper()
        self.num_coluna = num_coluna
        self.tipoTabela = tipoTabela
        if self.tipoTabela == 'tblResMensal':
            self.data = 'Mês'
        else:
            self.data = 'Dia'
        self.diretorio = diretorio
        self.url = 'http://bvmf.bmfbovespa.com.br/SIG/FormConsultaMercVista.asp?strTipoResumo=RES_MERC_VISTA&strSocEmissora=' + self.fii + '&strDtReferencia=12/2019&strIdioma=P&intCodNivel=2&intCodCtrl=160#'

    def getTable(self):
        """
        Web Scraping das tabelas mensais ou diárias da B3
        :return: dados coletados sem limpeza
        """

        #solicitando resposta
        answer = requests.get(self.url)

        #solicitando conteúdo HTML
        answer = answer.content

        #coletando HTML
        scraping = BeautifulSoup(answer, features='html.parser')

        self.data = []

        #coletando os dados da planilha
        for scr in scraping.find_all('table', {'name':self.tipoTabela}):
            for i in scr.find_all('table', {'width':'100%', 'border':'0', 'cellpadding':'3',
                                                      'cellspacing':'1', 'bgcolor':'#C0C0C0'}):

                stop = 0
                stringsTitle = str(i).split('>')

                for j in range(len(stringsTitle)):
                    if self.data in stringsTitle[j]:
                        count = j


                for k in range(count, len(stringsTitle)):
                        if '</td' in stringsTitle[k]:
                            self.data.append(stringsTitle[k])
                        if r'\table' in stringsTitle[k]:
                            break
                stop += 1

                if stop != 0:
                    break

        return self.data

    def processingInformation(self):
        """
        Limpeza dos dados
        :return: Dicionário com dados limpos
        """

        data = self.getTable()
        limp = []
        for i in range(len(data)):
            limp.append(self.data[i][:-4])
        cab = limp[0:self.num_coluna]

        numLine = int(len(limp)/self.num_coluna)

        lin = np.asarray(limp[self.num_coluna:])

        lin = lin.reshape(numLine-1, self.num_coluna)

        dicData = {}
        for k in range(len(cab)):
            dicData[cab[k]] = lin[:, k]


        return dicData

    def table(self):
        """
        Tabelas com dados limpos, salvas no diretório escolhido
        :return: csv's no diretório escolhido
        """

        dicData = self.processingInformation()

        dataFrame = pd.DataFrame(dicData)

        dataFrame.to_csv(self.diretorio + '\\' + self.fii + '.csv')