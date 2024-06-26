# -*- coding: utf-8 -*-
"""solarpv_foreca.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nb7zcJnMrPYbrI_gJLthwNYRmZudor_l

#Solar PV Output Prediction with Machine Learning
Built for 6th semester Minor Project <br>
Built by: Angshuman Talukdar <br>
Electrical Engineering, 2103004

Importing dependencies
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

"""Load dataset"""

df = pd.read_csv("/content/Solar Power Plant Data.csv")

"""Data Preprocessing"""

def preprocess_data(df):

  #dropping date-hour column as it is not necessary
  df = df.drop(columns=['Date-Hour(NMT)'])

  #normalize the data
  scaler = MinMaxScaler(feature_range=(0,1))
  scaled_data = scaler.fit_transform(df)

  return scaled_data, scaler

scaled_data, scaler = preprocess_data(df)

"""Define function to create dataset for LSTM"""

def create_dataset(data, time_steps=1):
  X, y = [], []
  for i in range(len(data) - time_steps):
    X.append(data[i:(i + time_steps), :])
    y.append(data[i + time_steps, -1]) # Assuming the last column is system production
  return np.array(X), np.array(y)

"""Create dataset with time steps"""

time_steps = 24 # Assuming we want to predict based on the past 24 hours
X, y = create_dataset(scaled_data, time_steps)

"""Split data into train and test sets"""

split_ratio = 0.8
split = int(split_ratio * len(X))

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

"""Define and train LSTM model"""

model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(LSTM(units=50))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

"""Plot training history"""

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend
plt.show

"""Make Predictions"""

train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

"""Inverse scaling for predictions"""

train_predict = scaler.inverse_transform(np.concatenate((X_train[:, -1, :-1], train_predict.reshape(-1,1)), axis=1))[:, -1]
test_predict = scaler.inverse_transform(np.concatenate((X_test[:, -1, :-1], test_predict.reshape(-1, 1)), axis=1))[:, -1]

"""Calculate RMSE"""

train_rmse = np.sqrt(mean_squared_error(df.iloc[time_steps:split+time_steps, -1], train_predict))
test_rmse = np.sqrt(mean_squared_error(df.iloc[split+time_steps:, -1], test_predict))
print("Train RMSE:", train_rmse)
print("Test RMSE", test_rmse)

"""Plotting actual vs predicted"""

plt.figure(figsize=(14, 7))
plt.plot(df.index[time_steps:split], df.iloc[time_steps:split, -1], label='Actual')
plt.plot(df.index[split+time_steps:], df.iloc[split+time_steps:, -1], label='Actual')
plt.plot(df.index[time_steps:split], train_predict[:df.index[time_steps:split].shape[0]], label='Train Predictions')
plt.plot(df.index[split+time_steps:], test_predict, label='Test Predicitons')
plt.title('Solar PV Output Prediction')
plt.xlabel('Date')
plt.ylabel('System Prediciton')
plt.legend()
plt.show()