import tensorflow as tf
import numpy as np
import h5py
from keras.utils import np_utils
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import load_model

import pandas as pd

import os 
import yaml 
path_csv = "./scores_mitbih.csv"

with open("paths.yaml",'r') as f :
    paths = yaml.load(f, Loader=yaml.FullLoader)

path_mitbih = os.path.join(paths["MITBIH"]["Data"], "mitbih_test.csv")

df_test = pd.read_csv(path_mitbih, header=None)
Y_test = np.array(df_test[187].values).astype(np.int8)
Y = Y_test
Y_test = np_utils.to_categorical(Y_test)

X_test = np.array(df_test[list(range(187))].values)[..., np.newaxis]
del df_test

names = list(paths["MITBIH"]["Models"].keys())
paths = list(paths["MITBIH"]["Models"].values())
print("NAMES ",names)
print(paths)
models = []
accs = []
d = dict()

for p in paths :
    models.append(load_model(filepath=p))

for i in range(len(models)):
    predictions = models[i].predict(X_test)
    predictions = np.argmax(predictions,axis=-1)
    d[names[i]] = accuracy_score(predictions, Y)
    #accs.append(accuracy_score(predictions, Y))

d = pd.DataFrame(d,index=["Accuracy"])
d.to_csv(path_csv)