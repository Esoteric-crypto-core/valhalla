from logger import logger
from valhalla import Account
from config import *
import csv
import json
import os
import aiofiles
import asyncio


async def set_info():
    file_empty = not os.path.exists(
        'files/data.csv') or os.path.getsize('files/data.csv') == 0

    async with aiofiles.open('files/data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "idx", "walletAddress", "points", "dailyPoints", "seasonalPoints", "referralPoints", "numReferrals"])

        await f.write(';'.join(writer.fieldnames) + '\n')

        try:
            with open('accounts.json', 'r') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        for account in data:
            row = {field: account.get(field, '')
                   for field in writer.fieldnames}
            await f.write(';'.join(map(str, row.values())) + '\n')

        with open('accounts.json', 'w') as file:
            json.dump([], file, indent=4)

    logger.info(f"Work done | Accounts info saved in data.csv")

    try:
        with open('files/bad_twitters.txt', 'r') as f:
            tw = [x for x in f.readlines() if x.strip()]
    except FileNotFoundError:
        tw = []
    except json.JSONDecodeError:
        tw = []
    except Exception as e:
        tw = []

    if len(tw) == 1:
        num_twitters = 'twitters token'
    else:
        num_twitters = 'twitters tokens'

    logger.info(f"Work done | {len(data)} accounts done | {
                len(tw)} bad {num_twitters}")


async def main():
    with open('files/proxy.txt', 'r') as file:
        proxies = [
            f"socks5://{x.strip()}" for x in file.readlines() if x.strip()]

    with open('files/referrals.txt', 'r') as file:
        referrals = [x.strip() for x in file.readlines() if x.strip()]

    with open('files/wallets.txt', 'r') as file:
        wallets = [x.strip() for x in file.readlines() if x.strip()]

    with open('files/twitters.txt', 'r') as file:
        twitters = [x.strip() for x in file.readlines() if x.strip()]

    if len(twitters) != len(proxies):
        logger.error(f"The number of Twitter accounts ({
            len(twitters)}) and proxies ({len(proxies)}) does not match")
        return

    tasks = []
    _referrals = []

    for i in range(len(twitters)):
        wallet = None
        referral = None
        if wallets:
            wallet = wallets.pop(0)

        if not referrals:
            if _referrals:
                referral = _referrals.pop(0)
                referrals.append(referral)
        else:
            referral = referrals.pop(0)
            _referrals.append(referral)

        account = Account(
            idx=i+1, proxy=proxies[i], twitter_auth_token=twitters[i], private_key=wallet, referrer_code=referral)

        tasks.append(account.account_process())

    await asyncio.gather(*tasks)
    await set_info()


if __name__ == '__main__':

    print("<--------------------------------------->")
    print(" |  https://t.me/esoteric_crypto_core  |")
    print(" |                                     |")
    print(" |              ESOTERIC               |")
    print(" |               CRYPTO                |")
    print(" |                CORE                 |")
    print(" |                                     |")
    print(" |  https://t.me/esoteric_crypto_core  |")
    print("<--------------------------------------->")

    try:
        asyncio.run(main())
    except Exception as e:
        with open('accounts.json', 'w') as file:
            json.dump([], file, indent=4)
        logger.error(f'The operation has been stopped | Error: {e}')

    with open('accounts.json', 'w') as file:
        json.dump([], file, indent=4)
