# Valhalla

This repository contains a bot to automate various tasks on the Valhalla project website. The tasks include wallet binding, daily and seasonal quests, claiming points, collecting account statistics, and registering referrals.

# Important Notes:

- The project website is currently under development. Future changes to the website may require updates to this tool.
  
- The points claim process on the website is somewhat buggy. Errors during the claim process can be ignored as points will be reflected in the final account statistics.
 
- Not all tasks might be completed in a single run. It is advisable to rerun the tool on the same accounts.
  
- Task names might include unreadable characters for some consoles, causing logging errors. These can also be ignored as they do not affect the tool's functionality.
  

## Features
- Binds wallet
- Completes daily quests
- Completes seasonal quests
- Claims points
- Collects account statistics
- Registers referrals


# Setup Guide
Clone the Repository
```
git clone https://github.com/yourusername/valhalla-automation-tool.git
cd valhalla-automation-tool
```
Set Up Virtual Environment
```
python -m venv venv
source venv/Scripts/activate  # For Windows
source venv/bin/activate      # For Unix-based systems
```
Install Dependencies
```
pip install -r requirements.txt
```

## Configure Proxy

- Add your proxies to `files/proxy.txt` in the format: `login:pass@ip:port`

- Ensure proxies support `SOCKS5` protocol and have a suitable geolocation (European recommended).
- 
## Configure Twitter Tokens

- Add your Twitter tokens to `files/twitters.txt`
- 
## Configure Wallets (Optional)

- Add your private wallets to `files/wallets.txt`
 
## Configure Referrals (Optional)

- Add your referral codes (Twitter usernames without @) to `files/referrals.txt`
  
- Run the bot
```
python main.py
```

## Output

Successful account results will be saved in `data.csv`
Twitter tokens that failed to process will be saved in `bad_twitters.txt`

# Proxy Recommendation
For reliable proxies, consider using Proxy-Seller. Resident proxies with European geolocation are recommended.

# Donate
TRC-20: `TARuBWXr5yJHyhS9ZZF4RyqbUXQVWXQaUq` ERC-20: `0xB333b6e713d5879109ceb884cc50a6b946D72C1D`
