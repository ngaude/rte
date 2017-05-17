#!/usr/bin/env python
# coding: utf-8

import argparse
import urllib, StringIO, zipfile 
import pandas as pd
import numpy as np
import tempfile
import os.path
from datetime import timedelta, date,datetime
import time
import sys

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def grab_eco2mix_realtime(date,region_code=None,ddir='./'):
    datefr = date[-2:] + '/' + date[5:7] + '/' + date[:4]
    params = {'date':datefr}
    if region_code is not None and region_code is not 'France':
        params['region'] = region_code 
    urlparams = urllib.urlencode(params)
    url = 'https://eco2mix.rte-france.com/curves/eco2mixDl?' + urlparams
    u = urllib.urlopen(url)
    s = StringIO.StringIO(u.read())
    z = zipfile.ZipFile(s)
    l = z.namelist()
    assert len(l) == 1
    fname = l[0]
    f = z.open(fname)
    c = f.read()
    # patching the malformed \t before EOL
    c = c.replace('\t\n','\n')
    lines = c.split('\n')
    # filtering malformed lines
    lines = [line for line in lines if len(line) > 0 and 'RTE ne pourra' not in line]
    c = '\n'.join(lines)
    fname = fname.split('\\')[-1].split('.')[0] + '.csv'
    with tempfile.NamedTemporaryFile() as tempf:
        tempf.write(c)
        tempf.flush()
        df = pd.read_csv(tempf.name,sep='\t',encoding='cp1252')
    # filter obvious NaN values...
    df.replace(to_replace = '-', value = np.NaN, inplace=True)
    df.replace(to_replace = 'ND', value = np.NaN, inplace=True)
    if u'Périmètre' in df.columns:
        df['region.code'] = [region2code[k] for k in df[u'Périmètre'].values]
    df.to_csv(os.path.join(ddir, fname),index = False, encoding = 'UTF8')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--startdate", help="start date YYYY-MM-DD, default is today", type=str,default='')
    parser.add_argument("--dir", help="csv output directory",type=str,default='./')
    args = parser.parse_args()

    now = datetime.now()
    end_date = date(now.year,now.month,now.day)

    if len(args.startdate)==0:
        start_date = end_date
    else:
        try:
            ymd = args.startdate.split('-')
            start_date = date(int(ymd[0]),int(ymd[1]),int(ymd[2]))
        except:
            parser.print_help()
            sys.exit(1)

    code2region = {
        'ACA':u'Grand-Est',
        'ALP':u'Nouvelle-Aquitaine',
        'ARA':u'Auvergne-Rhône-Alpes',
        'BFC':u'Bourgogne-Franche-Comté',
        'BRE':u'Bretagne',
        'CEN':u'Centre-Val de Loire',
        'IDF':u'Ile-de-France',
        'LRM':u'Occitanie',
        'NPP':u'Hauts-de-France',
        'NOR':u'Normandie',
        'PLO':u'Pays-de-la-Loire',
        'PAC':u'PACA',
        'France':u'France',
    }

    region2code = {v:k for k,v in code2region.iteritems()}

    for single_date in daterange(start_date, end_date):
        date = single_date.strftime("%Y-%m-%d")
        print 'grab eco2mix realtime csv at', date, 'to',args.dir
        codes = sorted(code2region.keys())
        for code in codes:
            grab_eco2mix_realtime(date,region_code=code,ddir=args.dir)

