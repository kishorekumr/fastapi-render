from typing import Optional

# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"message": "Hello from FastAPI!"}
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
# import requests
import uvicorn
from datetime import datetime, timedelta
# import pytz
# from pyotp import TOTP
# import pyotp
app = FastAPI()
import json
import hashlib
import hmac
import base64
import struct
import time

def generate_totp(totp_qr_code: str) -> str:
    try:
        key = base64.b32decode(totp_qr_code, casefold=True)
        time_step_bytes = struct.pack(">Q", int(time.time()) // 30)
        hmac_sha1 = hmac.new(key, time_step_bytes, hashlib.sha1).digest()
        offset = hmac_sha1[-1] & 0x0F
        otp = (int.from_bytes(hmac_sha1[offset:offset+4], 'big') & 0x7FFFFFFF) % 10**6
        totp = str(otp).zfill(6)
        return totp
    except Exception as e:
        print(f"Error in generating TOTP: {e}")
        return ""

def generate_totp_next(totp_qr_code: str) -> str:
    try:
        key = base64.b32decode(totp_qr_code, casefold=True)
        time_step_bytes = struct.pack(">Q", (int(time.time()) // 30) + 1)
        hmac_sha1 = hmac.new(key, time_step_bytes, hashlib.sha1).digest()
        offset = hmac_sha1[-1] & 0x0F
        otp = (int.from_bytes(hmac_sha1[offset:offset+4], 'big') & 0x7FFFFFFF) % 10**6
        totp = str(otp).zfill(6)
        return totp
    except Exception as e:
        print(f"Error in generating next TOTP: {e}")
        return ""


# url="https://api.investing.com/api/financialdata/historical/1195383?start-date=2023-10-12&end-date=2024-08-03&time-frame=Daily&add-missing-rows=false"
# url='https://api.investing.com/api/financialdata/historical/1195383?start-date=2024-08-02&end-date=2024-08-03&time-frame=Daily&add-missing-rows=false'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
#     'X-Requested-With': 'XMLHttpRequest',
#     'Referer': 'https://in.investing.com/',
#     'domain-id': 'in'}
# data = requests.get(url, headers=headers).json()
# print(data)
# # print(type(data)) # dict
# df=pd.DataFrame(data['data'])

import pandas as pd
######### Store in SQL token and ltp from websocket

from apscheduler.schedulers.background import BackgroundScheduler

symbol_to_token = None
df = pd.read_csv('/home/kishorekumar/fastapi/nse_token.csv')
symbol_to_token = dict(zip(df['Symbol'], df['Token']))
@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(read_csv_daily, 'cron', hour=8, minute=10)
    scheduler.start()

def read_csv_daily():
    global symbol_to_token
    try:
        # csv_data = pd.read_csv('/home/kishorekumar/fastapi/nse_token.csv')
        df = pd.read_csv('/home/kishorekumar/fastapi/nse_token.csv')
        symbol_to_token = dict(zip(df['Symbol'], df['Token']))
        print("CSV data loaded successfully.")
    except Exception as e:
        print(f"Failed to read CSV file: {e}")



@app.get("/")
def read_root():
    #token = symbol_to_token["TCS"]
    return {"message": f"Hello from FastAPI at {datetime.utcnow()}"}

@app.get("/totp/{text}", response_class=PlainTextResponse)
def get_text(text: str):
    # return str
    try:
        totp=generate_totp(text)
        totp = totp.zfill(6)
        # return int(totp)
        return  totp
    except:
        return "Error"

@app.get("/totp_next/{text}", response_class=PlainTextResponse)
def get_text_next(text: str):
    # return str
    try:
        totp=generate_totp_next(text)
        totp = totp.zfill(6)
        # return int(totp)
        return  totp
    except:
        return "Error"


@app.get("/nse_token/{text}", response_class=PlainTextResponse)
def get_nse_token(text: str):
    #global symbol_to_token
    try:
        token='11536'
        #token = symbol_to_token["TCS"]
        #token = symbol_to_token['3MINDIA']
        #print(token)
        # return int(totp)
        #send_message(5618402434, text)
        token = symbol_to_token[text]
        return  str(token)
    except:
        return "Error"


@app.get("/investing/{inv_id}/{end_date}")
def get_investing(inv_id: int,end_date:str):
    #global symbol_to_token
    try:

        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date_obj = end_date_obj - timedelta(days=1)

        # Format dates for URL
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        end_date_str = end_date_obj.strftime("%Y-%m-%d")

        # Construct URL
        url = f"https://api.investing.com/api/financialdata/historical/1195383?start-date={start_date_str}&end-date={end_date_str}&time-frame=Daily&add-missing-rows=false"
        # return url
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://in.investing.com/',
            'domain-id': 'in'
        }

        response = request.get(url, headers=headers)
        return response.text

        # if response.status_code == 200:
        #     data = response.json()
        #     df = pd.DataFrame(data['data'])

        #     # Ensure DataFrame is not empty
        #     if not df.empty:
        #         # Find the entry for the end_date
        #         df['rowDate'] = pd.to_datetime(df['rowDate'])
        #         end_date_entry = df[df['rowDate'] == end_date_obj]

        #         if not end_date_entry.empty:
        #             last_close = end_date_entry['last_close'].values[0]
        #             return {"inv_id": inv_id, "end_date": end_date_str, "last_close": last_close}
        #         else:
        #             return {"inv_id": inv_id, "end_date": end_date_str, "last_close": "No data available for the specified end_date"}
        #     else:
        #         return {"inv_id": inv_id, "end_date": end_date_str, "last_close": "No data available"}
        # else:
        #     raise HTTPException(status_code=response.status_code, detail="Request failed")

    except Exception as e:
        return {"error": str(e)}



