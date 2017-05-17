# RTE Prévision de la consommation électrique
https://www.datascience.net/fr/challenge/32/details

Dear datascience.net fellows, you will find here a simple import automation of realtime eco2mix files.
Have a good challenge.

For example to update your eco2mix file with today realtime data :
```
python grab_eco2mix.py
```
This will create a bunch of eCO2mix_RTE_<region>_YYYY-mm_dd.csv files in your local directory

Even better to grab all days from 2017-04-01 till now simply do :
```
python grab_eco2mix.py
```

Complete usage commandline is :
```
python grab_eco2mix.py --help
usage: grab_eco2mix.py [-h] [--startdate STARTDATE] [--dir DIR]

optional arguments:
  -h, --help            show this help message and exit
  --startdate STARTDATE
                        start date YYYY-MM-DD, default is today
  --dir DIR             csv output directory
```

