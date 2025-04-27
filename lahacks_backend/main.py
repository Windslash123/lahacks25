import plaid
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from flask import Flask, request, jsonify, render_template
from keras.models import load_model
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import joblib
import google.generativeai as genai
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

user_data = []

load_dotenv()  

client_id = os.getenv('PLAID_CLIENT_ID')
secret = os.getenv('PLAID_SECRET')

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Global variable to store access token (for demo)
access_token = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    request_data = LinkTokenCreateRequest(
        user={"client_user_id": "unique-user-id"},  # You should make this unique per user!
        client_name="Plaid Demo App",
        products=[Products('transactions')],
        country_codes=[CountryCode('US')],
        language="en",
    )
    response = client.link_token_create(request_data)
    print(response)
    return jsonify(response.to_dict())  # <-- FIX: response.link_token not response['link_token']

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    global access_token
    public_token = request.json['public_token']
    request_data = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request_data)
    access_token = response.access_token  # <-- FIX: response.access_token not response['access_token']
    return jsonify({'status': 'access token stored'})

@app.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    if access_token is None:
        return jsonify({'error': 'Access token not set yet'}), 400

    all_transactions = []
    cursor = None
    has_more = True

    while has_more:
        if cursor:
            request_data = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )
        else:
            request_data = TransactionsSyncRequest(
                access_token=access_token
            )

        response = client.transactions_sync(request_data)
        all_transactions += response.added  # <-- FIX: response.added not response['added']
        has_more = response.has_more
        cursor = response.next_cursor

    parse_user_data(response.added)
    print(user_data)
    return jsonify({'transactions': [txn.to_dict() for txn in all_transactions]})


def get_current_sp500_price():
    sp500 = yf.Ticker("^GSPC")
    intraday_data = sp500.history(period="1d", interval="1m")

    if not intraday_data.empty:
        return intraday_data['Close'].iloc[-1]
    else:
        # fallback: download last close
        sp500_data = yf.download('^GSPC', period='1d')
        return sp500_data['Close'].iloc[-1]


@app.route('/api/get_predictions/<start_money>', methods=['GET'])
def get_line_graph_data(start_money):
    print("HI", start_money)
    model = load_model('/Users/arshiaaravinthan/Documents/GitHub/LAHacks/lahacks_backend/lstm_sp500_model.keras')
    sc = joblib.load('/Users/arshiaaravinthan/Documents/GitHub/LAHacks/lahacks_backend/scaler.save')
    sp500_data = yf.download('^GSPC', period='60d')  # '60d' = last 60 days
    current_price = get_current_sp500_price()

    print(start_money, current_price)
    print(type(start_money))
    num_shares = int(start_money) / current_price

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

    shares = [start_money]
    for price in future_predictions_real:
        shares.append(float(price[0]*num_shares))
    return jsonify(shares)

@app.route('/api/get_ai_summary/', methods=['POST'])
def ask_gemini():
    transaction_history = request.json['transaction_history']


    prompt = ("You are a financial assistant. Given this user's transaction history point out specific places, categories they"
         " are spending excessively regardless of not needing to and specify the regularity of this spending." 
         " Suggest a compromise to reduce their spending. Analyze their spending and suggest a reasonable amount"
          " to reduce their monthly spending, if any, and invest that amount instead."
          "Bbe straight forward, (no fluff) but structured and pretty (dont add too many empty lines), "
          "don't suggest further conversation. Ignore accounts where category confidence level is low. Exclude the expenses from those facets."
          "Delete the fluff in the beginning including the Hello, get straight to a point but be in-depth. Return a tuple with the first entry being"
          "your response and the second being the amount of money you suggest to save")

    genai_api_key = os.getenv('GENAI_API_KEY')
    genai.configure(api_key=genai_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        prompt + "\n\nTransaction History:\n" + str(transaction_history)
    )

    print ("HELLO", response.text)

    return jsonify({'summary': response.text})

def parse_user_data(responses):
    for entry in responses:
        user_data.append({'date': entry['date'], 'category': entry['personal_finance_category'], 'name': entry['name'], 'amount': entry['amount']})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
