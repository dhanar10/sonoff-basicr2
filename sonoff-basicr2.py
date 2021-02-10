#!/usr/bin/env python3

import time
import json
import requests
import sys

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes

DEVICE_HOST = '10.100.7.101' # MAC Address D8:F1:5B:B2:74:A5
DEVICE_ID = '1000bb772d'
DEVICE_KEY = '1edc4fd4-2a9e-411a-b9e5-43bb9adcf4e2'

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

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Usage:')
        print('python3 sonoff-basicr2.py switch on|off')
        print('python3 sonoff-basicr2.py wifi SSID PASSWORD')
        exit(0)
        
    command = sys.argv[1]
    
    if command == 'switch' and (sys.argv[2] == 'on' or sys.argv[2] == 'off'):
        data = { 'switch' : sys.argv[2] }
    elif command == 'wifi' and len(sys.argv) == 4:
        data = { 'ssid': sys.argv[2], 'password': sys.argv[3] }
    else:
        print('Invalid arguments')
        exit(1)

    sequence = str(int(time.time() * 1000))

    payload = {
        'sequence': sequence,
        'deviceid': DEVICE_ID,
        'selfApikey': '123',
        'data': data
    }
    
    url = f"http://{DEVICE_HOST}:8081/zeroconf/{command}"
    
    print(url)
    print(payload)
    
    epayload = encrypt(payload, DEVICE_KEY)
    
    resp = requests.post(url, json=epayload, headers={'Connection': 'close'}, timeout=5)
    
    print(resp.json())
    
