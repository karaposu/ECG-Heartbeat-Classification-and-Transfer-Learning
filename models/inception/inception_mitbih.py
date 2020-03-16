import numpy as np
from numpy.random import seed
seed(1)
import tensorflow as tf
#from tensorflow import set_random_seed
tf.compat.v1.set_random_seed(2)


import pandas as pd
from keras.models import Sequential, load_model
from keras.layers import Dense, SimpleRNN, GRU
from keras.layers import Dropout
from keras.layers import LSTM
from keras.utils import np_utils
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.utils import class_weight
from sklearn.metrics import accuracy_score

print("TF VERSION")
print(tf.__version__)

df_train = pd.read_csv("./data/mitbih_train.csv", header=None)
df_train = df_train.sample(frac=1)
df_test = pd.read_csv("./data/mitbih_test.csv", header=None)

Y = np.array(df_train[187].values).astype(np.int8)
X = np.array(df_train[list(range(187))].values)[...,np.newaxis]

Y_test = np.array(df_test[187].values).astype(np.int8)
X_test = np.array(df_test[list(range(187))].values)[..., np.newaxis]

X = np.reshape(X, (len(X), 187, 1))

# weights = class_weight.compute_class_weight('balanced', np.unique(Y), Y)
# weights = dict(zip(list(range(5)), weights))

# print(weights)
Y = np_utils.to_categorical(Y)

print('Data shape: ', X.shape)
print('Y shape: ', Y.shape)


#Implement Inception Module
n_modules = 1
input_shape = (187,1)
input_layer = tf.keras.layers.Input(input_shape)

#1 channel input
L = input_layer
#Multichannel
L = tf.keras.layers.Conv1D(filters=32, kernel_size=10, strides=1, activation='relu', use_bias=False)(L)
L = tf.keras.layers.Conv1D(filters=32, kernel_size=10, strides=1, activation='relu', use_bias=False)(L)
L_skip = L

#Inception Module
for i in range(3) :
    L_max = tf.keras.layers.MaxPool1D(pool_size=3,strides=1,padding='same')(L)
    L_conv1 = tf.keras.layers.Conv1D(filters=32, kernel_size=1, strides=1, activation='relu',padding = 'same', use_bias=False)(L)

    L_conv10 = L_conv1 = tf.keras.layers.Conv1D(filters=32, kernel_size=10, strides=1, activation='relu',padding = 'same', use_bias=False)(L_conv1)
    L_conv20 =L_conv1 = tf.keras.layers.Conv1D(filters=32, kernel_size=20, strides=1, activation='relu',padding = 'same', use_bias=False)(L_conv1)
    L_conv40 =L_conv1 = tf.keras.layers.Conv1D(filters=32, kernel_size=40, strides=1, activation='relu',padding = 'same', use_bias=False)(L_conv1)

    L_max = L_conv1 = tf.keras.layers.Conv1D(filters=32, kernel_size=1, strides=1, activation='relu',padding = 'same', use_bias=False)(L_max)

    L = tf.keras.layers.Concatenate(axis=2)([L_conv10,L_conv20,L_conv40,L_max])
    L = tf.keras.layers.BatchNormalization()(L)
    L = tf.keras.activations.get('relu')(L)

#Add residual connection
L_residual = tf.keras.layers.Conv1D(filters=int(L.shape[-1]), kernel_size=1, strides=1, activation='relu', padding='same', use_bias=False)(L_skip)
L_residual = tf.keras.layers.BatchNormalization()(L_residual)
L = tf.keras.layers.Add()([L_residual, L])

gap_layer = tf.keras.layers.GlobalAveragePooling1D()(L)
output_layer = tf.keras.layers.Dense(units=5, activation='softmax')(gap_layer)
model = tf.keras.models.Model(inputs=input_layer,outputs=output_layer)

#model = get_model()
opt = tf.keras.optimizers.Adam(lr=0.001)

check = ModelCheckpoint('best_model_Inception_mitbih.h5', monitor='val_acc', save_best_only=True, mode='max', verbose=2)
early = EarlyStopping(monitor='val_acc', mode='max', patience=6, verbose=2)
reduce_lr = ReduceLROnPlateau(monitor='val_acc', factor=0.2, patience=3, verbose=2)

model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['acc'])
model.summary()
model.fit(X, Y, epochs=100, batch_size=64, callbacks=[check, early, reduce_lr],validation_split=0.1)

predictions = model.predict(X_test)
print(X_test.shape)
print(predictions.shape)
predictions = np.argmax(predictions, axis=-1)


acc = accuracy_score(predictions, Y_test)
print("Test accuracy score : %s "% acc)

