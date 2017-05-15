#!/usr/bin/env python
# coding: utf-8

import argparse
import urllib, StringIO, zipfile 
import pandas as pd
import numpy as np


def grab_params(params):
    urlparams = urllib.urlencode(params)
    url = 'https://eco2mix.rte-france.com/curves/eco2mixDl?' + urlparams
    u = urllib.urlopen(url)
    s = StringIO.StringIO(u.read())
    z = zipfile.ZipFile(s)
    l = z.namelist()
    assert len(l) == 1
    f = z.open(l[0])

    if params['region'] is not 'France':
        df = pd.read_csv(f,sep='\t',encoding='cp1252',skiprows=1,header=None)

        # NOTE : patching the malformed NaN unnamed last column...
        assert len(df[df.columns[-1]].dropna()) == 0
        df = df[df.columns[:-1]]
        df.columns =[u'Périmètre', u'Nature', u'Date', u'Heures', u'Consommation', u'Thermique', u'Nucléaire', u'Eolien', u'Solaire', u'Hydraulique', u'Pompage', u'Bioénergies', u'Ech. physiques']

    else:
        df = pd.read_csv(f,sep='\t',encoding='cp1252')

    # NOTE : remove the disclaimer last line ...
    df = df[:-1]
    assert len(df) == 96
    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="date format YYYY-MM-DD", type=str)
    parser.add_argument("--output", help="csv output filepath",type=str)
    args = parser.parse_args()

    region = {
        'France':'France',
        'ACA':'Grand-Est',
        'ALP':'Nouvelle-Aquitaine',
        'ARA':'Auvergne-Rhônes-Alpes',
        'BFC':'Bourgogne-Franche-Comté',
        'BRE':'Bretagne',
        'CEN':'Centre-Val de Loire',
        'IDF':'Ile-de-France',
        'LRM':'Occitanie',
        'NPP':'Hauts-de-France',
        'NOR':'Normandie',
        'PLO':'Pays-de-Loire',
        'PAC':'PACA',
    }

    # french date format...
    datefr = args.date[-2:] + '/' + args.date[5:7] + '/' + args.date[:4]

    if args.output:
        output = args.output
    else:
        output = 'eco2mix-' + args.date + '.csv'

    # grab all regions...
    df = [grab_params({'region':k,'date':datefr}) for k in region.keys()]
    df = pd.concat(df)
    assert len(df) == 96*len(region.keys())

    # NOTE : patching malformed date...
    df['Date'] = [i if '-' in i else i[-4:]+'-'+i[3:5]+'-'+i[:2] for i in df['Date']]

    assert len(set(df.Date)) == 1

    # NOTE : remove - empty values by NaN
    df.replace(to_replace = '-', value = np.NaN, inplace=True)
    df.replace(to_replace = 'ND', value = np.NaN, inplace=True)

    df.to_csv(output,index = False, encoding = 'UTF8')
