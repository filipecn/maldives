#!/usr/bin/py

B3MarketType = {'010': 'VISTA', '012': 'EXERCICIO DE OPCOES DE COMPRA', '013': 'EXERCICIO DE OPCOES DE VENDA', '017': 'LEILAO', '020': 'FRACIONARIO', '030': 'TERMO', '050': 'FUTURO COM RETENCAO DE GANHO', '060': 'FUTURO COM MOVIMENTACAO CONTÍNUA', '070': 'OPCOES DE COMPRA', '080': 'OPCOES DE VENDA'}
class B3Register:
    def __init__(self, string):
        #B3 register structure
        self.attributes = {}
        self.attributes["type"] = string[0:2]
        self.attributes["date"] = '-'.join([string[6:8], string[8:10], string[2:6]])
        self.attributes["bdiCode"] = string[10:12]
        self.attributes["negotiationCode"] = string[12:24].strip()
        self.attributes["marketType"] = B3MarketType[string[24:27]]
        self.attributes["name"] = string[27:39]
        self.attributes["specification"] = string[39:49]
        self.attributes["termMarketDue"] = string[49:52]
        self.attributes["currency"] = string[52:56]
        self.attributes["openPrice"] = float(string[56:69])
        self.attributes["maxPrice"] = float(string[69:82])
        self.attributes["minPrice"] = float(string[82:95])
        self.attributes["medPrice"] = float(string[95:108])
        self.attributes["closePrice"] = float(string[108:121])
        self.attributes["bestBuyOffer"] = float(string[121:134])
        self.attributes["bestSellOffer"] = float(string[134:147])
        self.attributes["negotiationVolume"] = int(string[147:152])
        self.attributes["titleNegotiationCount"] = int(string[152:170])
        self.attributes["titleNegotiationVolume"] = int(string[170:188])
        self.attributes["preexe"] = int(string[188:201])
        self.attributes["indopc"] = string[201:202]
        self.attributes["datven"] = string[202:210]
        self.attributes["quoteFactor"] = string[210:217]
        self.attributes["ptoexe"] = string[217:230]
        self.attributes["codisi"] = string[230:242]
        self.attributes["dismes"] = string[242:245]

