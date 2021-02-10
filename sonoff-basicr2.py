#!/usr/bin/env python3

import time
import json
import requests
import sys

from base64 import b64encode, b64decode
from urllib import request
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes

from flask import Flask

DEVICE_HOST = '10.100.7.101' # MAC Address D8:F1:5B:B2:74:A5
DEVICE_ID = '1000bb772d'
DEVICE_KEY = '1edc4fd4-2a9e-411a-b9e5-43bb9adcf4e2'

app = Flask(__name__)

def pad(data_to_pad: bytes, block_size: int):
    padding_len = block_size - len(data_to_pad) % block_size
    padding = bytes([padding_len]) * padding_len
    return data_to_pad + padding

def encrypt(payload: dict, devicekey: str):
    devicekey = devicekey.encode('utf-8')

    hash_ = MD5.new()
    hash_.update(devicekey)
    key = hash_.digest()

    iv = get_random_bytes(16)
    plaintext = json.dumps(payload['data']).encode('utf-8')

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded)

    payload['encrypt'] = True
    payload['iv'] = b64encode(iv).decode('utf-8')
    payload['data'] = b64encode(ciphertext).decode('utf-8')

    return payload
    
def send(url: str, data: dict):
    sequence = str(int(time.time() * 1000))
    payload = {
        'sequence': sequence,
        'deviceid': DEVICE_ID,
        'selfApikey': '123',
        'data': data
    }
    
    print(url)
    print(payload)
    
    epayload = encrypt(payload, DEVICE_KEY)
    resp = requests.post(url, json=epayload, headers={'Connection': 'close'}, timeout=5)
    
    print(resp.json())

@app.route('/switch/on')    
def switch_on():
    url = f"http://{DEVICE_HOST}:8081/zeroconf/switch"
    data = { 'switch' : 'on' }
    send(url, data)
    return web()
   
@app.route('/switch/off')       
def switch_off():
    url = f"http://{DEVICE_HOST}:8081/zeroconf/switch"
    data = { 'switch' : 'off' }
    send(url, data)
    return web()
    
def wifi(ssid: str, password: str):
    url = f"http://{DEVICE_HOST}:8081/zeroconf/wifi"
    data =  { 'ssid': ssid, 'password': password }
    send(url, data)
    
@app.route('/')       
def web():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
            html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
            body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}
            .button {display: block;width: 80px;background-color: #1abc9c;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}
            .button-on {background-color: #1abc9c;}
            .button-on:active {background-color: #16a085;}
            .button-off {background-color: #34495e;}
            .button-off:active {background-color: #2c3e50;}
            p {font-size: 14px;color: #888;margin-bottom: 10px;}
        </style>
    </head>
    <body>
    <h1>SONOFF BASICR2</h1>
    <p><a class="button button-on" href="/switch/on">ON</a></p>
    <p><a class="button button-off" href="/switch/off">OFF</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Usage:')
        print('python3 sonoff-basicr2.py switch on|off')
        print('python3 sonoff-basicr2.py wifi SSID PASSWORD')
        print('python3 sonoff-basicr2.py web')
        exit(0)
        
    command = sys.argv[1]
    
    if command == 'switch' and len(sys.argv) == 3 and sys.argv[2] == 'on':
        switch_on()
    elif command == 'switch' and len(sys.argv) == 3 and sys.argv[2] == 'off':
        switch_off()
    elif command == 'wifi' and len(sys.argv) == 4:
        wifi(sys.argv[2], sys.argv[3])
    elif command == 'web' and len(sys.argv) == 2: 
        app.run(host= '0.0.0.0')
    else:
        print('Invalid arguments')
        exit(1)
    
