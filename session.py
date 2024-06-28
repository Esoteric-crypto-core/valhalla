from user_agent import *


class BaseClient:

    def __init__(self):
        chrome_version_details, windows_nt_version, arch, bitness = get_random()

        self.website_headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            "origin": "https://www.valhallafoundation.xyz",
            "priority": "u=1, i",
            "referer": "https://www.valhallafoundation.xyz/",
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            "sec-fetch-site": "cross-site",
            "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": f"Mozilla/5.0 (Windows NT {windows_nt_version}; Win64; {arch}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version_details['full_version']} Safari/537.36",
            "sec-ch-ua": f'"Google Chrome";v="{chrome_version_details["major_version"]}", "Not:A Brand";v="99", "Chromium";v="{chrome_version_details["major_version"]}"',
        }
