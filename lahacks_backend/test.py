from keras.models import load_model
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import joblib
from PIL import Image
from google.cloud import vision

def get_current_sp500_price():
    sp500 = yf.Ticker("^GSPC")
    intraday_data = sp500.history(period="1d", interval="1m")

    if not intraday_data.empty:
        return intraday_data['Close'].iloc[-1]
    else:
        # fallback: download last close
        sp500_data = yf.download('^GSPC', period='1d')
        return sp500_data['Close'].iloc[-1]

def get_line_graph_data(start_money):
    model = load_model('lstm_sp500_model.keras')
    sc = joblib.load('scaler.save')
    sp500_data = yf.download('^GSPC', period='60d')  # '60d' = last 60 days
    current_price = get_current_sp500_price()
    num_shares = start_money / current_price

    close_prices = sp500_data['Close']
    last_20_days = close_prices[-20:]

    last_20_days = np.reshape(last_20_days, (1, last_20_days.shape[0], 1))

    future_predictions = []

    n_future_days = 20  # Predict next 30 days

    for _ in range(n_future_days):
        pred_price_scaled = model.predict(last_20_days)

        # Store the prediction
        future_predictions.append(pred_price_scaled[0, 0])

        # Update the last_20_days sequence
        last_20_days = np.concatenate([last_20_days[:, 1:, :], np.expand_dims(pred_price_scaled, axis=1)], axis=1)

    # Inverse transform back to real prices
    future_predictions_real = sc.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    shares = []
    for price in future_predictions_real:
        shares.append(price[0]*num_shares)
    print(shares)


def get_line_graph_data_monthly_investment(start_money):
    model = load_model('lstm_sp500_model.keras')
    sc = joblib.load('scaler.save')

    sp500_data = yf.download('^GSPC', period='60d')
    current_price = get_current_sp500_price()

    close_prices = sp500_data['Close']
    last_20_days = np.reshape(close_prices[-20:], (1, 20, 1))

    future_predictions = []
    n_future_days = 100  # Predict 1 year

    for _ in range(n_future_days):
        pred_price_scaled = model.predict(last_20_days)
        future_predictions.append(pred_price_scaled[0, 0])
        last_20_days = np.concatenate([last_20_days[:, 1:, :], np.expand_dims(pred_price_scaled, axis=1)], axis=1)

    future_predictions_real = sc.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Monthly investing logic
    total_shares = 0
    portfolio_values = []

    for day in range(n_future_days):
        predicted_price = future_predictions_real[day][0]

        if day % 30 == 0:  # Invest every 30 days
            num_new_shares = start_money / predicted_price
            total_shares += num_new_shares

        portfolio_value = total_shares * predicted_price
        portfolio_values.append(portfolio_value)

    return portfolio_values

def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print("Texts:")

    for text in texts:
        print(f'\n"{text.description}"')

        vertices = [
            f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        ]

        print("bounds: {}".format(",".join(vertices)))

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )



if __name__ == "__main__":
    detect_text('/Users/jisharajala/Desktop/Screenshot 2025-04-26 at 4.12.50 PM.png')

