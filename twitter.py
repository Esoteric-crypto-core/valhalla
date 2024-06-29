import asyncio
import aiohttp
from logger import logger
from user_agent import *
from config import *
from tools import *
from aiohttp_socks import ProxyConnector


class Twitter:
    def __init__(self, idx, proxy, twitter_auth_token):
        chrome_version_details, windows_nt_version, arch, bitness = get_random()
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            # 'content-type': 'application/json',
            # 'origin': 'https://mobile.twitter.com',
            # 'referer': 'https://mobile.twitter.com/',
            'sec-ch-ua':  f'"Google Chrome";v="{chrome_version_details["major_version"]}", "Not:A Brand";v="99", "Chromium";v="{chrome_version_details["major_version"]}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
            'x-csrf-token': '',
            "user-agent": f"Mozilla/5.0 (Windows NT {windows_nt_version}; Win64; {arch}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version_details['full_version']} Safari/537.36",
        }

        self.idx = idx
        self.twitter_auth_token = twitter_auth_token
        self.cookies = {
            'auth_token': self.twitter_auth_token,
            'ct0': '',
        }
        self.proxy = proxy

    async def start(self):
        ct0, guest_id, cookies = await self._get_ct0()
        logger.info(f"{self.idx} | ct0 was received: {ct0}")
        logger.info(f"{self.idx} | guest id was received: {guest_id}")
        if ct0 == None:
            raise Exception
        self.cookies.update({'guest_id': guest_id})
        self.cookies.update({'ct0': ct0})
        self.headers.update({'x-csrf-token': ct0})

        return cookies

    def get_conn(self):
        return ProxyConnector.from_url(self.proxy) if self.proxy else None

    async def request(self, method, url, resp_handler=get_value, key=None, **kwargs):
        headers = self.headers.copy()
        cookies = self.cookies.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        if 'cookies' in kwargs:
            cookies.update(kwargs.pop('headers'))

        try:
            async with aiohttp.ClientSession(connector=self.get_conn()) as client:
                if method.lower() == 'post':
                    async with client.post(url=url, headers=headers, cookies=cookies, **kwargs) as resp:
                        return await resp_handler(resp, key)
                    # response = await client.post(url=url)
                    # return await resp_handler(response, key)
                if method.lower() == 'get':
                    async with client.get(url=url, headers=headers, cookies=cookies, **kwargs) as resp:
                        return await resp_handler(resp, key)
                    # response = await client.get(url=url)
                    # return await resp_handler(response, key)
        except Exception as e:
            with open('files/bad_twitters.txt', 'a') as f:
                if self.twitter_auth_token not in [x.strip() for x in f.readlines() if x.strip()]:
                    f.write(f"{self.twitter_auth_token}\n")
            # logger.error(f'Request failed | Error: {e}')
            raise Exception(f'{self.idx} | Request failed | Error: {e}')

    async def _get_ct0(self):
        try:
            kwargs = {'ssl': False} if DISABLE_SSL else {}

            async with aiohttp.ClientSession(connector=self.get_conn(),
                                             headers=self.headers, cookies=self.cookies) as sess:
                async with sess.get('https://twitter.com/i/api/1.1/dm/user_updates.json?', **kwargs) as resp:
                    new_csrf = resp.cookies.get("ct0")
                    guest_id = resp.cookies.get("guest_id")
                    if guest_id is None:
                        raise Exception(f'{self.idx} | Empty guest_id')
                    if new_csrf is None:
                        raise Exception(f'{self.idx} | Empty new csrf')
                    new_csrf = new_csrf.value
                    guest_id = guest_id.value

                    cookies = await get_auth_code_and_cookies(resp)

                    return new_csrf, guest_id, cookies
        except Exception as e:
            with open('files/bad_twitters.txt', 'a') as f:
                if self.twitter_auth_token not in [x.strip() for x in f.readlines() if x.strip()]:
                    f.write(f"{self.twitter_auth_token}\n")
            reason = 'Your account has been locked\n' if 'Your account has been locked' in str(
                e) else ''
            raise Exception(f'{self.idx} | Failed to ct0 for twitter: {
                            reason}{str(e)}')

    async def sign_in(self, url):
        try:
            state = url.split('state=')[1].split('&')[0]
            params = {
                # 'SktNU1VXZ0tQc0N2U3hST2lKcms6MTpjaQ',
                'client_id': url.split('client_id=')[1].split('&')[0],
                'code_challenge': url.split('code_challenge=')[1].split('&')[0],
                'code_challenge_method': url.split('code_challenge_method=')[1],
                'redirect_uri': 'https://www.valhallafoundation.xyz/auth/callback/twitter',
                'response_type': url.split('response_type=')[1].split('&')[0],
                'scope': url.split('scope=')[1].split('&')[0].replace('%20', ' '),
                'state': state,
            }
            auth_code = await self.request(
                method='GET', url='https://twitter.com/i/api/2/oauth2/authorize', params=params, key='auth_code', resp_handler=get_value2, headers={'Referer': url, 'Priority': 'u=1, i'})
            # logger.info(f"{self.idx} | auth_code: {auth_code}")

            if auth_code == None:
                with open('files/bad_twitters.txt', 'a') as f:
                    if self.twitter_auth_token not in [x.strip() for x in f.readlines() if x.strip()]:
                        f.write(f"{self.twitter_auth_token}\n")

                raise Exception(
                    f"{self.idx} | Getting auth code failed | Error: auth_code = {auth_code}")

            await asyncio.sleep(5)
            redirect_uri = await self.request(method='POST', url="https://twitter.com/i/api/2/oauth2/authorize", headers={'Referer': url}, resp_handler=get_value2,
                                              json={"approval": "true", "code": auth_code}, key='redirect_uri')
            # logger.info(f"{self.idx} | redirect_uri: {redirect_uri}")

            if redirect_uri == None:
                with open('files/bad_twitters.txt', 'a') as f:
                    if self.twitter_auth_token not in [x.strip() for x in f.readlines() if x.strip()]:
                        f.write(f"{self.twitter_auth_token}\n")

                raise Exception(
                    f"{self.idx} | Getting auth code failed | Error: redirect_uri = {redirect_uri}")

            return redirect_uri

        except Exception as e:
            with open('files/bad_twitters.txt', 'a') as f:
                if self.twitter_auth_token not in [x.strip() for x in f.readlines() if x.strip()]:
                    f.write(f"{self.twitter_auth_token}\n")
            # logger.error(f"Sign in failed | Error: {e}")
            raise Exception(f"{self.idx} | Sign in failed | Error: {e}")
