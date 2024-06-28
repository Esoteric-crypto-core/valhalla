from session import BaseClient
from logger import logger
import aiohttp
import datetime
from aiohttp_socks import ProxyConnector
import asyncio
import sys
import random
import time
import json
from twitter import Twitter
from tools import *
from config import *
from web3 import Web3

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Account(BaseClient):

    def __init__(self, idx, proxy,  twitter_auth_token, private_key=None, referrer_code=None):
        super().__init__()
        self.idx = idx
        self.proxy = proxy
        self.referrer_code = referrer_code
        self.private_key = private_key
        self.twitter_auth_token = twitter_auth_token
        self.headers = self.website_headers.copy()
        self.bearer = None
        self.address = None
        self.account_info = {}

        w3 = Web3(Web3.HTTPProvider('wss://eth.drpc.org'))

        if self.private_key != None:
            self.account = w3.eth.account.from_key(self.private_key)
            self.address = self.account.address

    def get_conn(self):
        return ProxyConnector.from_url(self.proxy) if self.proxy else None

    async def request(self, method, url, resp_handler=get_value2, key=None, **kwargs):
        headers = self.headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        try:
            async with aiohttp.ClientSession(connector=self.get_conn()) as client:
                if method.lower() == 'post':

                    response = await client.post(url=url, headers=headers,  **kwargs)

                    return await resp_handler(response, key)
                if method.lower() == 'get':
                    response = await client.get(url=url, headers=headers, **kwargs)
                    return await resp_handler(response, key)
        except Exception as e:
            logger.error(f'{self.idx} | Request failed | Error: {e}')

    async def update_bearer(self, bearer):
        self.headers['authorization'] = f"Bearer {bearer}"

    async def sign_in(self):
        try:
            async def get_vercel_token(resp, key, **kwargs):
                if resp.status == 429:
                    print("Too many requests, try again later.")
                    # return None

                headers = resp.headers
                vercel_token = headers.get('X-Vercel-Challenge-Token')

                if vercel_token:
                    print("Vercel Token:", vercel_token)
                    return vercel_token
                else:
                    print("Vercel Token not found in the response headers.")
                    return None

            # vercel_token = await self.request(
                # 'GET', 'https://www.valhallafoundation.xyz/api/generateAuthToken', key='token', resp_handler=get_vercel_token)

            bearer = await self.request(
                'GET', 'https://www.valhallafoundation.xyz/api/generateAuthToken', key='token')

            # logger.info(f'{self.idx} | Bearer: {bearer}')

            if bearer == None:
                raise Exception('Failed to obtain bearer token')

            await self.update_bearer(bearer)
            link = await self.request(
                'POST', 'https://www.infinigods.com/api/auth/twitterV2/generateAuthUrl', key='url')

            if link == None:
                raise Exception('Failed to obtain auth link')

            # logger.info(f'{self.idx} | Auth link: {link}')

            twitter = Twitter(idx=self.idx, proxy=self.proxy,
                              twitter_auth_token=self.twitter_auth_token)
            logger.info(f"{self.idx} | Work on Twitter starts")
            await asyncio.sleep(3)
            cookies = await twitter.start()
            await asyncio.sleep(5)
            redirect_uri = await twitter.sign_in(url=link)

            async with aiohttp.ClientSession(connector=self.get_conn()) as client:

                headers = {
                    "sec-ch-ua": self.headers['sec-ch-ua'],
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": self.headers['user-agent'],
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "host": "www.valhallafoundation.xyz"
                }

                data = {
                    'o': redirect_uri,
                    'sv': '0.1.2',
                    'sdkn': '@vercel/analytics/react',
                    'sdkv': '1.2.2',
                    'ts': int(time.time()),
                    'r': 'https://twitter.com/',
                }

                await client.post(url='https://www.valhallafoundation.xyz/_vercel/insights/view', headers=headers, data=json.dumps(data))

                data = {'code': redirect_uri.split(
                    'code=')[1],
                    'referrerCode': self.referrer_code
                }
                token = await self.request(method='POST',
                                           url='https://www.infinigods.com/api/auth/twitterV2/connect', data=json.dumps(data), key='token')

                await self.update_bearer(token)

            return

        except Exception as e:
            # logger.error(f"Sign in failed | Error: {e}")
            raise Exception(f" Sign in failed | Error: {e}")

    async def account_process(self):
        try:
            logger.info(f"{self.idx} | Sign in")
            await self.sign_in()
            await self.get_account_info()

            logger.info(f"{self.idx} | The task process starts")
            if self.private_key != None:
                await self.connect_wallet()
            await self.task_process('daily')
            await self.task_process('seasonal')

            await self.set_account_info()
            await self.get_num_referrals()
            logger.info(f"{self.idx} | Account work is finished")

            try:
                with open('accounts.json', 'r') as file:
                    data = json.load(file)
                    if not isinstance(data, list):
                        raise ValueError(
                            "JSON file does not contain a list at the top level.")
            except FileNotFoundError:
                data = []
            except json.JSONDecodeError:
                data = []

            data.append(self.account_info)

            with open('accounts.json', 'w') as file:
                json.dump(data, file, indent=4)

            logger.info(f"{self.idx} | Statistics | Total points: {
                        self.account_info['points']} | Daily points: {self.account_info['dailyPoints']} | Seasonal points: {self.account_info['seasonalPoints']} | Referral points: {self.account_info['referralPoints']} | Num referrals: {self.account_info['numReferrals']}")

            return self.account_info
        except Exception as e:
            error_message = str(e)

            if error_message == ' Sign in failed | Error: not readable':
                with open('files/bad_twitters.txt', 'r') as f:
                    existing_tokens = [x.strip()
                                       for x in f.readlines() if x.strip()]

                if self.twitter_auth_token not in existing_tokens:
                    with open('files/bad_twitters.txt', 'a') as f:
                        f.write(f"{self.twitter_auth_token}\n")

            logger.error(f"{self.idx} | Account failed | {e}")

    async def task_process(self, tasks_id):
        if tasks_id == 'daily':
            tasks = self.dailyQuests.copy()
        if tasks_id == 'seasonal':
            tasks = self.seasonalQuests.copy()

        for _ in tasks:
            index = random.randint(0, len(tasks) - 1)
            task = tasks.pop(index)

            if int(task['quest']['endDate']) > int(time.time()) + 120:
                if task['completed'] == False:
                    await asyncio.sleep(random.randint(MIN_SLEEP_BETWEEN_TASKS, MAX_SLEEP_BETWEEN_TASKS))
                    data = {'questId': task['quest']
                            ["_id"], 'seasonId': self.seasonId, }
                    result = await self.request('POST', url='https://www.infinigods.com/api/mountOlympus/startQuest', key='Success', data=json.dumps(data))
                    if result == True:
                        logger.info(f"{self.idx} | Quest {
                                    task['quest']['title']} starts")

                        # await asyncio.sleep(120)

                        data = {'questId': task['quest']
                                ["_id"], 'seasonId': self.seasonId, }
                        result = await self.request('POST', url='https://www.infinigods.com/api/mountOlympus/claimQuest', key='Success', data=json.dumps(data))

                        await self.get_account_info()

                        if tasks_id == 'daily':
                            tasks = self.dailyQuests.copy()
                        if tasks_id == 'seasonal':
                            tasks = self.seasonalQuests.copy()

                        for check_task in tasks:
                            if check_task['quest']['_id'] == task['quest']["_id"]:
                                if check_task['completed'] == True:
                                    logger.success(f"{self.idx} | Quest {task['quest']['title']} complete | Claimed {
                                        task['quest']['points']} points")
                                logger.error(f"{self.idx} | Task {
                                    task['quest']['title']} claim failed")
                    logger.error(f"{self.idx} | Task {
                                 task['quest']['title']} start failed")
                logger.info(f"{self.idx} | Task {
                    task['quest']['title']} already completed")

    async def set_account_info(self):
        account_info = await self.get_account_info()

        self.account_info = {'idx': self.idx,
                             'walletAddress': self.address,
                             'twitter_token': self.twitter_auth_token,
                             'userId': account_info['socialPoints']['userId'],
                             'points': account_info['socialPoints']['points'],
                             'dailyPoints': account_info['socialPoints']['dailyPoints'],
                             'seasonalPoints': account_info['socialPoints']['seasonalPoints'],
                             'referralPoints': account_info['socialPoints']['referralPoints'],
                             }

    async def get_account_info(self):
        async with aiohttp.ClientSession(connector=self.get_conn()) as client:
            account_info = await client.post(url='https://www.infinigods.com/api/mountOlympus/getSocialPoints', headers=self.headers)

            account_info = await account_info.json()
            self.user_id = account_info['socialPoints']['userId']
            self.seasonId = account_info['socialPoints']['seasonId']

            self.dailyQuests = account_info['socialPoints']['dailyQuests']
            self.seasonalQuests = account_info['socialPoints']['seasonalQuests']

            return account_info

    async def connect_wallet(self):
        if self.private_key == None:
            return

        account_info = await self.get_account_info()

        if account_info["walletAddress"] != '':
            return

        now = datetime.datetime.now()

        issued_at = now.strftime("%B %d, %Y at %I:%M:%S %p")

        expires_at = (now + datetime.timedelta(minutes=1)
                      ).strftime("%B %d, %Y at %I:%M:%S %p")

        expires_at_utc = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        message = f"\nwww.valhallafoundation.xyz wants to connect your wallet with metamask walletId.\n\nDomain: www.valhallafoundation.xyz\nIssued At: {
            issued_at}\nExpires At: {expires_at}\nExpires At UTC: {expires_at_utc}\n"
        sign = await signature(message=message, private_key=self.private_key)
        data = {
            'walletAddress': self.address,
            'message': message,
            'signature': sign,
            "isDelegateWallet": False
        }

        response = await self.request(
            method='POST', url='https://www.infinigods.com/api/mountOlympus/connectWallet', data=json.dumps(data), key='success')

        if response == True:
            logger.success(f"{self.idx} | Connect wallet | Address: {
                self.address}")
            return

        logger.error(f"{self.idx} | Connect wallet failed | Address: {
            self.address}")

    async def get_num_referrals(self):
        num_referals = await self.request('POST', url='https://www.infinigods.com/api/mountOlympus/getNumReferrals', key='numReferrals')
        self.account_info['numReferrals'] = num_referals
