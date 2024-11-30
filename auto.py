from web3 import Web3
import json, os, sys, requests, time
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

with open('./abi.json') as f:
    abi = json.load(f)

with open('./erc20.json') as f_erc:
    abi_erc = json.load(f_erc)

with open('./pair.json') as f_pair:
    pair_abi = json.load(f_pair)

os.system('cls' if os.name == 'nt' else 'clear')
if not web3.is_connected():
    print("Failed to Connect to Base")
    sys.exit()
print(f"Starting Sniper\nEnhanced Version")
privatekey = os.getenv("PRIVATE_KEY")
address = web3.eth.account.from_key(privatekey).address
prices_min = web3.to_wei(int(input("Enter the minimum price: ")), 'ether')

contracts = web3.eth.contract(
    address='0xF66DeA7b3e897cD44A5a231c61B6B4423d613259',
    abi=abi
)

swapper = web3.eth.contract(
    address='0x08758354a72F2765FA8ba4CaC7c1dDdC88EDBdB6',
    abi=abi
)

def approve_tx(token_address_checksum):
    nonce = web3.eth.get_transaction_count(address)
    erc20 = web3.eth.contract(
        address=web3.to_checksum_address(token_address_checksum),
        abi=abi_erc
    )
    if erc20.functions.allowance(address, web3.to_checksum_address("0x08758354a72F2765FA8ba4CaC7c1dDdC88EDBdB6")).call() == 0:
        tx = {
        "to": web3.to_checksum_address(token_address_checksum),
        "gasPrice": int(web3.eth.gas_price *2),
        "nonce": nonce,
        "data": "0x095ea7b300000000000000000000000008758354a72f2765fa8ba4cac7c1dddc88edbdb6ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "chainId": 8453,
        "gas": 200000,
        }
        signed_txns = web3.eth.account.sign_transaction(tx, private_key=privatekey)
        tx_hash = w3.eth.send_raw_transaction(signed_txns.raw_transaction)
        print("Recipt Approve >> " + web3.to_hex(tx_hash) +"\nExecuted on block: " + str(web3.eth.get_block('latest')['number']))
        web3.eth.wait_for_transaction_receipt(tx_hash)
    else:
        print(f"Already Approved {token_address_checksum}")


def sell_tx(token_address_checksum):
    nonce = web3.eth.get_transaction_count(address)
    erc20 = web3.eth.contract(
        address=web3.to_checksum_address(token_address_checksum),
        abi=abi_erc
    )
    token_address = token_address_checksum.lower()
    balance = erc20.functions.balanceOf(address).call()
    tx = swapper.functions.mempoolSell(
        web3.to_checksum_address(token_address),
        balance
    ).build_transaction(
        {
            "from": web3.to_checksum_address(address),
            "gasPrice": int(web3.eth.gas_price * 2),
            "chainId": 8453,
            "gas": 400000,
            "nonce": nonce
        }
    )
    signed_txns = web3.eth.account.sign_transaction(tx, private_key=privatekey)
    tx_hash = w3.eth.send_raw_transaction(signed_txns.raw_transaction)
    print("Recipt Swap >> " + web3.to_hex(tx_hash) +"\nExecuted on block: " + str(web3.eth.get_block('latest')['number']))
    web3.eth.wait_for_transaction_receipt(tx_hash)

def all_tx(token_address_checksum, pair):
    contracts_pair = web3.eth.contract(
        address=web3.to_checksum_address(pair),
        abi=pair_abi
    )
    ahaaaa, lel = contracts_pair.functions.getReserves().call()
    erc20 = web3.eth.contract(
        address=web3.to_checksum_address(token_address_checksum),
        abi=abi_erc
    )
    balance = erc20.functions.balanceOf(address).call()
    prices = (lel / ahaaaa * balance)/100*95
    print("Estimated Price: "+ str(web3.from_wei(prices, 'ether')))
    if(prices <= prices_min ):
        approve_tx(token_address_checksum)
        sell_tx(token_address_checksum)

if __name__ == "__main__":
    apps = requests.get(f"https://deep-index.moralis.io/api/v2.2/{address}/erc20?chain=base",headers={"X-API-Key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImQyZTM0M2MwLWU5MTItNDllMi1iODg0LTRkNGUxNTIyNWQ3YSIsIm9yZ0lkIjoiNDE4NjgzIiwidXNlcklkIjoiNDMwNTY2IiwidHlwZUlkIjoiZGUwNjg5MDItMDc0ZS00OTE5LWFmY2MtODUyMGNjMDI1YTNlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MzI4ODc0OTYsImV4cCI6NDg4ODY0NzQ5Nn0.jG_6VaxKjKYGn9DvR09UWr4b_H38zgr3qnc05AYC2I8"}).json()
    for app in apps:
        if("fun" in app["name"]):
            print(app['token_address'])
            print(app['name'])
            print(app['symbol'])
            print(app['decimals'])
            print(app['balance'])
            try:
                all_tx(app['token_address'], contracts.functions.tokenInfo(web3.to_checksum_address(app['token_address'])).call()[2])
            except Exception as e:
                all_tx(app['token_address'], contracts.functions.tokenInfo(web3.to_checksum_address(app['token_address'])).call()[2])
            print("--------------------------------")
            
    #approve_tx("0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b")
    #all_tx("0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b", "0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b")