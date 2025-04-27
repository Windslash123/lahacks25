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
import sendgrid
from sendgrid.helpers.mail import Mail
import os
import json
import smtplib
from email.mime.text import MIMEText

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
    model = load_model('lahacks_backend/lstm_sp500_model.keras')
    sc = joblib.load('lahacks_backend/scaler.save')
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

    prompt = (
        "You are a financial assistant. Given this user's transaction history, point out specific places and categories where they "
        "are spending excessively, specify the regularity of this spending, suggest compromises to reduce it, and recommend a reasonable "
        "monthly savings amount. Return ONLY a JSON object with two fields: "
        "'summary' (the analysis as a string) and 'suggested_savings' (a number, float or int). "
        "Do not add any greeting or closing text. Do not wrap it in markdown or code blocks."
        "\n\nTransaction History:\n" + str(transaction_history)
    )

    genai_api_key = os.getenv('GENAI_API_KEY')
    genai.configure(api_key=genai_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    response_text = response.text

    # Try to safely parse it as JSON
    try:
        response_json = json.loads(response_text)
        print(response_json)
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse AI output as JSON", "details": str(e), "raw_response": response_text}), 500

    return jsonify(response_json)


def parse_user_data(responses):
    for entry in responses:
        user_data.append({'date': entry['date'], 'category': entry['personal_finance_category'], 'name': entry['name'], 'amount': entry['amount']})

from flask import request  # Make sure you have this imported

from flask import request, jsonify
from twilio.rest import Client

@app.route('/api/send_email/', methods=['POST'])
def send_email_route():
    data = request.form
    to_email = data.get('user_email')
    user_goals = data.get('user_goals')
    ai_summary = data.get('ai_summary')

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = 'fiscora2614@gmail.com'
    from_password = 'wrafgzeurkqbxjll'  # Use your Gmail App Password!

    # subject = 'Your Financial Goals'
    # body = f"Thanks for submitting your goals! Here’s what you wrote:\n\n{user_goals}"

    prompt = (
    "You are a friendly financial coach.\n\n"
    "Given two pieces of information:\n"
    "- A financial spending analysis for the user (called 'financial_analysis')\n"
    "- A personal finance goal from the user (called 'user_goal')\n\n"
    "Your task:\n"
    "- Read the 'financial_analysis' to understand the user's current spending habits.\n"
    "- Read the 'user_goal' to understand what the user personally wants to improve.\n"
    "- Write an encouraging, positive, and empathetic message:\n"
    "  - Directly acknowledge the user's personal goal.\n"
    "  - Incorporate advice or motivation based on the financial analysis.\n"
    "  - Be supportive, not judgmental. Make the user feel optimistic about improving.\n"
    "  - Use warm, uplifting language. Keep it between 3–6 sentences.\n\n"
    "**Input:**\n"
    f"financial_analysis = {ai_summary}\n\n"
    f"user_goal = {user_goals}\n\n"
    "**Output:**\n"
    "Only return the motivational message as plain text. No formatting, no labels, no code block."
)

    genai_api_key = os.getenv('GENAI_API_KEY')
    genai.configure(api_key=genai_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    subject = 'Your Personalized Financial Coaching!'
    body = (
        f"Hello!\n\n"
        f"Thank you for sharing your financial goals with us.\n\n"
        f"{response_text}\n\n"
        f"Keep going — you've got this!\n\n"
        f"- Your Fiscora Team"
    )

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

    return 'Email sent successfully!'


if __name__ == '__main__':
    app.run(debug=True, port=5001)
