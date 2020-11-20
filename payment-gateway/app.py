import datetime
import logging
import os

import requests
from flask import Flask, render_template, request

from Checksum import generate_checksum, verify_checksum

logging.basicConfig(level=logging.DEBUG)

app = Flask(
    __name__,
    static_url_path="",
    static_folder="./static",
    template_folder="./templates",
)

MERCHANT_ID = os.getenv("MERCHANT_ID")
MERCHANT_KEY = os.getenv("MERCHANT_KEY")
WEBSITE_NAME = os.getenv("WEBSITE_NAME")
INDUSTRY_TYPE_ID = os.getenv("INDUSTRY_TYPE_ID")
BASE_URL = os.getenv("BASE_URL")
APP_URL = os.getenv("APP_URL")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "GET":
        return render_template("donationform.html")
    else:
        form_response = request.form.to_dict()
        transaction_data = {
            "MID": MERCHANT_ID,
            "WEBSITE": WEBSITE_NAME,
            "INDUSTRY_TYPE_ID": INDUSTRY_TYPE_ID,
            "ORDER_ID": str(datetime.datetime.now().timestamp()),
            "CUST_ID": "007",
            "TXN_AMOUNT": form_response.get("amount"),
            "CHANNEL_ID": "WEB",
            "MOBILE_NO": form_response.get("phone"),
            "EMAIL": form_response.get("email"),
            "CALLBACK_URL": f"{APP_URL}/callback",
        }

        # Generate checksum hash
        transaction_data["CHECKSUMHASH"] = generate_checksum(
            transaction_data, MERCHANT_KEY
        )

        logging.info(
            "Request params: {transaction_data}".format(
                transaction_data=transaction_data
            )
        )

        url = BASE_URL + "/theia/processTransaction"
        return render_template("payment.html", paytmParams=transaction_data, url=url)


@app.route("/callback", methods=["GET", "POST"])
def callback():
    # log the callback response payload returned:
    callback_response = request.form.to_dict()
    logging.info(
        "Callback response: {callback_response}".format(
            callback_response=callback_response
        )
    )

    # verify callback response checksum:
    checksum_verification_status = verify_checksum(
        callback_response, MERCHANT_KEY, callback_response.get("CHECKSUMHASH")
    )
    logging.info(
        "checksum_verification_status: {check_status}".format(
            check_status=checksum_verification_status
        )
    )

    # verify transaction status:
    transaction_verify_payload = {
        "MID": callback_response.get("MID"),
        "ORDERID": callback_response.get("ORDERID"),
        "CHECKSUMHASH": callback_response.get("CHECKSUMHASH"),
    }
    url = BASE_URL + "/order/status"
    verification_response = requests.post(url=url, json=transaction_verify_payload)
    logging.info(
        "Verification response: {verification_response}".format(
            verification_response=verification_response.json()
        )
    )
    verification_response = verification_response.json()
    if verification_response.get("RESPCODE") == "01":
        return render_template("paymentsuccess.html", home_url=APP_URL)
    else:
        return f"{verification_response.get('RESPMSG')}"
