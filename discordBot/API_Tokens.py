import keyring


# METAMASK
bugsAddr = "0x5e8a3bf9404fc7adb819e4386807b8ba015e8e72"
bugsApexAddr = "0x80dbcbf7c1935b39a63301c06f8fd46f0e6f18c6"
bugsXDefAddr = "0x80dbcbf7c1935b39a63301c06f8fd46f0e6f18c6"

# bugs FEES
ProfileFee = "5000000000000000"
print(len(ProfileFee))
eventEntryCost = "5000000000000000"
updateProfileFee = "3000000000000000"


# INFURA
infuraApiKey = keyring.get_password("infura", "bugs")
infuraUrl = f"https://mainnet.infura.io/v3/{infuraApiKey}"

# Discord
service_name = "Discord"
username = "API_TOKEN"
Bot_Token = keyring.get_password(service_name, username)
STOKE_SALT = keyring.get_password("botPassword", "Stoke")
stoke = 1058910316211208323
purpleStoke = 403248917657157632

# ETHERSCAN MATERIALS
block_num = 0
ETH_VALUE = 10**18
BASE_URL = "https://api.etherscan.io/api"
system = "ETHERSCAN"
usernameETH = "API_TOKEN"
ETHSCAN_API_KEY = keyring.get_password(system, usernameETH)
