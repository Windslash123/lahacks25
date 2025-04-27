import pandas as pd
import numpy as np
import yfinance as yf

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from keras.callbacks import EarlyStopping
from keras.metrics import RootMeanSquaredError, MeanAbsoluteError

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit

import warnings
warnings.filterwarnings('ignore')

#Downloading of data from Yahoo Finance which will be used for model training
end = '2020-12-31'
start = '1999-01-02'

trainingData = yf.download('^GSPC', start=start, end=end)
trainingData.head()

#Downloading of data from Yahoo Finance which will be used for model testing
start = '2021-01-02'

testingData = yf.download('^GSPC', start=start)
testingData.head()

#Prediction will take place on Close price, therefore we must isolate Close.
trainprice = trainingData['Close']
trainData = trainprice.values

testprice = testingData['Close']
testData = testprice.values


plt.figure(figsize=(10,10))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().yaxis.set_major_locator(mdates.DayLocator(interval=200))

plt.plot(trainingData.index, trainingData['Close'], label='Train Data Actual Close')
plt.plot(testingData.index, testingData['Close'], label='Test Data Actual Close')
plt.xlabel('Date')
plt.ylabel('USD')
plt.legend()
plt.gcf().autofmt_xdate()
plt.show()

sc = MinMaxScaler(feature_range=(0,1))
trainDataScaled = sc.fit_transform(trainData.reshape(-1, 1))
testDataScaled = sc.fit_transform(testData.reshape(-1, 1))

n_steps = 20

xTrain, yTrain = [], []

for i in range(n_steps, len(trainDataScaled)):
    xTrain.append(trainDataScaled[i - n_steps:i, 0])
    yTrain.append(trainDataScaled[i, 0])

xTrain, yTrain = np.array(xTrain), np.array(yTrain)
xTrain = np.reshape(xTrain, (xTrain.shape[0], xTrain.shape[1], 1))
# LSTM Model

model = Sequential()

# Layer 1
model.add(LSTM(units=200, return_sequences=True, input_shape=(xTrain.shape[1], 1)))
model.add(Dropout(0.2))
# Layer 2
model.add(LSTM(units=200, return_sequences=True))
model.add(Dropout(0.2))
# Layer 3
model.add(LSTM(units=200, return_sequences=True))
model.add(Dropout(0.2))
# Layer 4
model.add(LSTM(units=200, return_sequences=False))
model.add(Dropout(0.2))
# Layer 5
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error', metrics=[RootMeanSquaredError(), MeanAbsoluteError()])
model.summary()

# Early stopping parameters to stop unnecessary training
earlyStopping = EarlyStopping(
    monitor='val_root_mean_squared_error',
    patience=15,
    mode='min',
    min_delta=0.000001
)

def plot_metric(history, metric):
    train_metrics = history.history[metric]
    val_metrics = history.history['val_'+metric]
    epochs = range(1, len(train_metrics) + 1)
    plt.plot(epochs, train_metrics)
    plt.plot(epochs, val_metrics)
    plt.title('Training and validation '+ metric)
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.legend(["train_"+metric, 'val_'+metric])
    plt.show()
#Evaluation of model to confirm if parameters set above are valid
eval = model.evaluate(xTrain, yTrain)

log = model.fit(
    xTrain,
    yTrain,
    epochs=100,
    batch_size=128,
    validation_split = 0.25,
    verbose=1,
    callbacks=[earlyStopping],
    shuffle=False)
plot_metric(log, 'root_mean_squared_error')

n_steps = 20

xTest = []
yTest = []

for i in range(n_steps, len(testDataScaled)):
    xTest.append(testDataScaled[i - n_steps:i, 0])
    yTest.append(testDataScaled[i, 0])

xTest, yTest = np.array(xTest), np.array(yTest)
xTest = np.reshape(xTest, (xTest.shape[0], xTest.shape[1], 1))
predictions = model.predict(xTest)  # Prediction on Data using trained model
output = sc.inverse_transform(predictions)
rmse = np.sqrt(mean_squared_error(predictions, yTest))  # Calculating of RMSE

eval = model.evaluate(xTest, yTest) #Calculating of additional metrics (Loss, RMSE, MAE)

df1 = pd.DataFrame(testingData['Close']).astype(float)
df1.columns = ['Close']
df1 = df1.iloc[:-20]
df1 = df1.reset_index(drop=False)

df2 = pd.DataFrame(output, columns = ['Pred Close']).astype(float)

df = df1.join(df2)
df = df.set_index('Date')
print(df)
#plotting of graphs - Full Overview

model.save('lstm_sp500_model.keras')

train = trainingData['Close']
real = df['Close']
pred = df['Pred Close']
plt.figure(figsize=(10,10))
plt.title('SP500 Actual vs Predicted (01/01/2020 - 01/01/2024)')
plt.xlabel('Date')
plt.ylabel('Close Price ($)')
plt.plot(train)
plt.plot(real)
plt.plot(pred)
plt.legend(['Actual Pre-Training', 'Actual Post-Training','LSTM Prediction'], loc='lower right')
plt.xticks()
plt.show()

#plotting of graphs - Full Overview
real = df['Close']
pred = df['Pred Close']
plt.figure(figsize=(10,10))
plt.title('SP500 Actual vs Predicted (01/01/2020 - 01/01/2024)')
plt.xlabel('Date')
plt.ylabel('Close Price ($)')
plt.plot(real)
plt.plot(pred)
plt.legend(['Actual Post-Training','LSTM Prediction'], loc='lower right')
plt.xticks()
plt.show()