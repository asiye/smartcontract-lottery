from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    LinkToken,
    Contract,
    interface,
)
from web3 import Web3
from brownie.network.gas.strategies import LinearScalingStrategy

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
DECIMALS = 8
INITIAL_VALUE = 20e10
GAS_PRICE = 1e9

# BASE_FEE = 100000000000000000  # 0.1 link 100000000000000000
# GAS_PRICE_LINK = 1e9
BASE_FEE = 25e16
GAS_PRICE_LINK = 1e9


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["from_key"])


def get_gas_price():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return GAS_PRICE
    else:
        gas_strategy = LinearScalingStrategy("60 gwei", "70 gwei", 1.1)
        network.gas_price(gas_strategy)
        return gas_strategy


def deploy_mocks():
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    print("MockV3Aggregator deployed!")
    LinkToken.deploy({"from": account})
    print("LinkToken deployed!")
    VRFCoordinatorV2Mock.deploy(BASE_FEE, GAS_PRICE_LINK, {"from": account})
    print("VRFCoordinatorMock deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]  # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(contract_address, account: None, link_token: None, amount: 1e17):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    transaction = link_token.transfer(contract_address, amount, {"from": account})
    # link_contract = interface.LinkTokenInterface(link_token.address)
    # transaction = link_contract.transfer(contract_address, amount, {"from": account})
    transaction.wait(1)
    print("Fund contract!")
    return transaction
