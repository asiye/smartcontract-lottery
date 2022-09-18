from brownie import Lottery, network, config
from scripts.helpful_scripts import (
    FORKED_LOCAL_ENVIRONMENTS,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    get_gas_price,
    fund_with_link,
)
import time


def deploy_lottery():
    account = get_account()
    active_network = network.show_active()
    network_config = config["networks"][active_network]

    eth_usd_price_feed = get_contract("eth_usd_price_feed").address
    vrf_coordinator = get_contract("vrf_coordinator").address
    link_token = get_contract("link_token").address

    lottery = Lottery.deploy(
        eth_usd_price_feed,
        vrf_coordinator,
        link_token,
        network_config.get("keyhash"),
        network_config.get("callback_gas_limit"),
        network_config.get("request_confirmations"),
        {
            "from": account,
        },
        publish_source=network_config.get("verify", False),
    )
    print(f"Deployed lottery is : {lottery.address}")

    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_tx = lottery.startLottery({"from": account})
    start_tx.wait(1)
    print("The lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee({"from": account}) + 100000
    transaction = lottery.enter({"from": account, "value": value})
    transaction.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    transaction = fund_with_link(lottery.address, None, None, 1e17)
    transaction.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
