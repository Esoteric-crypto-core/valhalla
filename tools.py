from logger import logger
from web3 import Web3
from eth_account.messages import encode_defunct
w3 = Web3(Web3.HTTPProvider('wss://eth.drpc.org'))


async def get_value(resp, key, **kwargs):
    try:
        resp_json = resp.json()

        if key in resp_json:
            return resp_json[key]
        else:
            return None
    except Exception as e:
        raise Exception(f"Getting {key} failed | Error: {e}")


async def get_value2(resp, key, **kwargs):
    try:

        resp_json = await resp.json()
        if key in resp_json:
            return resp_json[key]
        else:
            return None
    except Exception as e:
        raise Exception(f"Getting {key} failed | Error: {e}")


async def get_auth_code_and_cookies(resp, **kwargs):
    try:
        cookies = resp.cookies
        cookie_dict = {}
        for key, morsel in cookies.items():
            if key == 'guest_id':
                cookie_dict = {
                    'guest_id': morsel.value,
                    'domain': morsel['domain'],
                    'path': morsel['path'],
                    'expires': morsel['expires'],
                    'secure': morsel['secure'],
                    # 'httponly': morsel['httponly'],
                    # 'samesite': morsel['samesite']
                }
        return cookie_dict
    except Exception as e:
        raise Exception(f"Getting cookies failed | Error: {e}")


async def signature(message, private_key):
    encoded_message = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(
        encoded_message, private_key=private_key)

    signature = signed_message.signature
    return signature.hex()
