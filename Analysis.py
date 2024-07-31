import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.neighbors import LocalOutlierFactor
from sklearn.pipeline import Pipeline

protocol_map = {'ssh':1, 'http':2, 'https':3, "rdp":4}

def convert_ip_address(ip):
    parts=[int(p) for p in ip.split('.')]
    return int(f'{parts[0]:03}{parts[1]:03}{parts[2]:03}{parts[3]:03}')

def convert_protocol(p):
    return protocol_map[p] if p in protocol_map else -1

def convert_datetime(d):
    dt = datetime.fromisoformat(d)
    return  dt.weekday()*24 + dt.hour

class RecordTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_new = []

        for record in X:
            src_address= convert_ip_address(record[0])
            dst_address= convert_ip_address(record[1])
            protocol = convert_protocol(record[2])
            dt = convert_datetime(record[3])
            X_new.append([src_address, dst_address, protocol, dt])
        return np.array(X_new)

num_samples=100000

def generate_samples():
     # Load data from CSV
    data = pd.read_csv('CleanData.csv')
     # Assuming the columns are named 'src_address' and 'dst_address'
    src_addresses = data['Source'].unique()
    dst_addresses = data['Destination'].unique()
    protocols = ['ssh', 'http','https','rdp']
    samples=[]
    for _ in range(num_samples):
        src_address = random.choice(src_addresses)
        dst_address = random.choice(dst_addresses)
        protocol = random.choice(protocols)
        dt = datetime(2023, 5, random.randint(1,5),
                      random.randint(8,16),random.randint(0,59), random.randint(0,59))
        dt = dt.isoformat()
        
        samples.append([src_address,dst_address,protocol,dt])
    
    return np.array(samples)


samples = generate_samples()

local_outlier_factor = LocalOutlierFactor(novelty=True)

pipeline = Pipeline([('record-transformer', RecordTransformer())])

data = pipeline.fit_transform(samples)

local_outlier_factor.fit(data)

new_samples = np.array([
            ['192.168.100.1','192.168.50.1','rdp', datetime(2023,5,3,20,0,0).isoformat()],
            ['192.168.100.2','192.168.50.1','rdp', datetime(2023,5,3,10,0,0).isoformat()],
            ['192.168.100.3','44.44.44.44','ssh', datetime(2023,5,4,12,30,45).isoformat()],
            ['192.168.100.4','192.168.80.1','https', datetime(2023,5,3,9,0,0).isoformat()],
        ])
new_data = pipeline.transform(new_samples)

predictions = local_outlier_factor.predict(new_data)

outliers = np.where(predictions < 0)[0]

outliers = [new_samples[idx] for idx in outliers]

for outlier in outliers:
    print(outlier)