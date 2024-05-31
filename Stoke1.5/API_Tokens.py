import keyring
#DISCORD 
Bot_Token = keyring.get_password('Discord', 'bot')
stoke = 1058910316211208323
purplestoke = 403248917657157632
bugsServerId = 1053533258706595870


#ETHERSCAN
block_num = 0
ETH_VALUE = 10**18
BASE_URL = 'https://api.etherscan.io/api'
TESTNET_BASE_URL = "https://api-sepolia.etherscan.io/api"
ETHSCAN_API_KEY = keyring.get_password('Etherscan', 'api')

# EVENT FEES
ProfileFee = "3000000000000000"
eventEntryCost = "5000000000000000"
updateProfileFee = "3000000000000000" 

# bugs WALLETS
bugsAddr = "0xc3a414d4496dbd9013b5f44051291b09c97931d2"
bugsApexAddr = "0x69b6234f010625433fb0c3e1b9467e02600c5cdb"
bugsFinalsAddr = "0xc10ecb4abf1a0ec69c8c0d96527ea260eed7ba5c"
bugsXdefAddr = "0xd3fb39a1ba4602eff76d0e95f43a696eae2713f4"
