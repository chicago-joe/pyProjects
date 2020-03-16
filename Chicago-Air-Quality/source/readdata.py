import pandas as pd

def read_training_set(self):
    df = pd.read_csv(self, sep = ',', header = 0)
    df.columns = ['s02', 'car.count', 'wind.velocity', 'wind.direction', 'time.of.day',
                       'day.index', 'temperature.1', 'temperature.30']
    return df

def read_testing_set(self):
    df = pd.read_csv(self, sep = ',', header = 0)
    df.columns = ['car.count', 'wind.velocity', 'wind.direction', 'time.of.day',
                  'day.index', 'temperature.1', 'temperature.30']
    return df
