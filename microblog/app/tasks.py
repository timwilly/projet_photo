import csv
import time
#from app import db
#from models import BusinessMontreal
from rq import get_current_job
from urllib.request import urlopen

def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')

def example2():
    print('TEST')
    
def import_data():
    print('BONJOUR!')
    try:
        import_data_to_csv("https://data.montreal.ca/dataset/c1d65779-d3cb"
                           "-44e8-af0a-b9f2c5f7766d/resource/28a4957d-732e"
                           "-48f9-8adb-0624867d9bb0/download/businesses.csv",
                           "business_montreal")
        #import_csv_to_database("business_montreal")
    except Exception as e:
        print(e)
        
def import_data_to_csv(link, write_file_name):
    url = urlopen("{}".format(link))
    string = url.read().decode('utf-8')
    try:
        file = open("app/static/data/{}.csv".format(write_file_name), "w")
    except Exception as e:
        print(e)
    file.write(string)
    file.close()
    
"""
def import_csv_to_database(read_file_name):
    with open("app/static/data/{}.csv".format(read_file_name), 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            business_montreal = BusinessMontreal(id=row[0], name=row[1],
                                                 address=row[2], city=row[3],
                                                 state=row[4], type=row[5],
                                                 statut=row[6], 
                                                 date_statut=row[7],
                                                 latitude=row[8],
                                                 longitude=row[9], x=row[10],
                                                 y=row[11])
            db.session.add(business_montreal)
        db.session.commit()
        return 'Data imported successfully'
"""