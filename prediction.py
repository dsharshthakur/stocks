import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# loading the model
def load_model():
    model = tf.keras.models.load_model("trainedmodel.h5")
    return model


# require transformation
scaler = MinMaxScaler(feature_range=(0, 1))


def transformdata(stockdata, column="Close", window_size=100):

    data = stockdata
    x = data[column]

    x_scaled = scaler.fit_transform(x.values.reshape(-1, 1))
    all_input_windows = []

    for i in range(len(x) - window_size):
        window = x_scaled[i: i + window_size, 0]

        all_input_windows.append(window)

    input_window = np.array(all_input_windows)

    return input_window


def PastPrediction(dataframe):
    x_input = transformdata(stockdata=dataframe)
    model = load_model()

    y_predicted = model.predict(x_input)

    y_predicted_unscaled = scaler.inverse_transform(y_predicted)

    return y_predicted_unscaled


def PastDataFrame(stockdata, column="Close"):
    predicted_values = PastPrediction(dataframe=stockdata)

    pastdf = stockdata[["Date", column]][100:]
    pastdf.rename(columns={column: "Actual"}, inplace=True, )
    pastdf["Predictions"] = predicted_values

    return pastdf


def Forecast(dataframe, future_days=0, column="Close"):
    model = load_model()
    window_size = 100

    # scaling
    past_x = dataframe[column]

    past_x_scaled = scaler.transform(past_x.values.reshape(-1, 1))

    past_100_days_x = past_x_scaled[-window_size:]  # array having last 100 days x values (price) , we kept it 100 because training was also done based on the window size of  100 days.
    past_100_days_x = past_100_days_x.reshape(1, -1)

    x_updated = past_100_days_x.tolist()[0]  # list having past 100 days x values ,this list will keep on updating / moving

    all_predicted_y = []
    day = 0
    while day <= future_days:
        if len(x_updated) > window_size:
            new_x = x_updated[day:]  # shift the window for next 100 days

            new_x_array = np.array(new_x)
            new_x_array = new_x_array.reshape(1, -1)
            new_x_array = new_x_array.reshape(1, window_size, 1)

            # prediction
            predicted_y = model.predict(new_x_array, verbose=False)

            all_predicted_y.extend(predicted_y.tolist()[0])  # add  the predicted value in y_predicted
            x_updated.extend(
                predicted_y.tolist()[0])  # also , add the predicted value in x_updated to store the new input value

            day = day + 1

        else:
            past_100_days_x = past_100_days_x.reshape(1, window_size, 1)

            predicted_y = model.predict(past_100_days_x, verbose=False)

            x_updated.extend(predicted_y.tolist()[0])
            all_predicted_y.extend(predicted_y.tolist()[0])
            day = day + 1

    # unscaling
    y_unscaled = scaler.inverse_transform(np.array(all_predicted_y).reshape(1, -1))
    y_unscaled = y_unscaled.tolist()[0]
    return y_unscaled


def ForecastDataFrame(predicted_values, future_days=0):

    start_from = pd.to_datetime('today').date() #todays(current) date


    if start_from.weekday() == 5: #check if its a saturday
        start_from = pd.to_datetime('today').date() + pd.Timedelta(days=2) #add 2 days and return the date ,i.e (monday)
    elif start_from.weekday() == 6: #check if its a sunday
        start_from = pd.to_datetime('today').date() + pd.Timedelta(days=1) #add 1 days and return the date ,i.e (monday)
    else:
        pass

    #if user want prediction of "n" next days

    if future_days > 0 :
        end = pd.to_datetime(start_from) +pd.offsets.BDay(future_days)
        #if user want prediction for the same (current) day then end day will be same as start date
    else:
        end = start_from

    #furure dataframe
    df = pd.DataFrame()
    df["Date"] = pd.bdate_range(start=start_from, end = end)

    df["Predictions"] = predicted_values
    
    if start_from == pd.to_datetime("today").date(): #if the start date is same as  current date
        return df[1:] #show from nex today . i.e dont the current day price
    else: #if its not the current date
        df.index = [i for i in range(1 , len(df) + 1)]
        return df[:-1] #dont show the last a value

