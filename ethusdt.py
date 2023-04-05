import asyncio
import logging
import statistics
import sys
from datetime import datetime, timedelta

from binance import AsyncClient

TEST_SCRIPT_DURATION = 65  # 65 seconds
SCRIPT_DURATION = 3900  # 65 minutes
CORRELATION = 0.6  # for example 0.6; Usual correlation ~ 0.98
SLEEP_1HOUR = 3600  # 60 minutes
SLEEP_1MINUTE = 60  # 1 minute
SLEEP_15SECONDS = 15
ETH = 'ETHUSDT'
BTC = 'BTCUSDT'
PERIOD_HOUR = 'hour'
PERIOD_MINUTE = 'minute'
PERIOD_START = 'script_launch'
DETECTED = 'Price movement detected'

file_handler = logging.FileHandler(filename='info.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    format="%(levelname)-8s %(asctime)s %(message)s",
    level=logging.INFO,
    handlers=handlers,
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def check_corel(eth: list, btc: list, period=None):
    """
    Analyzing the corellation.
    """
    corel = round(statistics.correlation(eth, btc), 3)
    if corel <= CORRELATION:  # 0.6
        logging.warning(f'Analyzing {ETH} corellation is: '
                        f'{corel} for last {period}')
        return True
    return False


async def start_current_price(client: AsyncClient):
    """
    Current price change since script launch.
    The script start price and the current price are used.
    """
    g = await client.get_symbol_ticker(symbol=ETH)
    start_price_eth = float(g.get("price"))
    bt = await client.get_symbol_ticker(symbol=BTC)
    start_price_bt = float(bt.get("price"))
    while True:
        g = await client.get_symbol_ticker(symbol=ETH)
        curent_price_eth = float(g.get("price"))
        logging.info(f'Ticker: {g.get("symbol")} '
                     f'current price: {float(g.get("price"))}')
        eth_start_end = [start_price_eth, curent_price_eth]
        change_percent = round(
            ((curent_price_eth - start_price_eth) / start_price_eth) * 100, 3
            )
        bt = await client.get_symbol_ticker(symbol=BTC)
        curent_price_bt = float(bt.get("price"))
        btc_start_end = [start_price_bt, curent_price_bt]
        if change_percent <= -1 or change_percent >= 1:
            result = await check_corel(
                eth=eth_start_end,
                btc=btc_start_end,
                period=PERIOD_START
                )
            if result:
                logging.warning(DETECTED)
        await asyncio.sleep(SLEEP_15SECONDS)


async def percent_and_corel(eth: list, btc: list, period: str):
    """
    Analyzing the price change in percentages
    Analyzing the correlation.
    Usual correlation between ETHUSDT and BTCUSDT is around 0.98.
    """
    open_price = eth[0]
    close_price = eth[-1]
    change_percent = round(
        ((close_price - open_price) / open_price) * 100, 3
        )
    logging.info(f'Analyzing {ETH} change percent is: '
                 f'{change_percent} for last {period}')
    if change_percent <= -1 or change_percent >= 1:
        corel = statistics.correlation(btc, eth)
        if corel <= CORRELATION:  # 0.6
            # print(DETECTED)
            return True
    return False


async def analyzing_correlation_1hour(client: AsyncClient):
    """
    Analyzing the price change for the previous hour.
    Using the minimum and maximum values.
    """
    g = await client.get_server_time()
    cur_serv_time = (
        datetime.utcfromtimestamp(
            g.get('serverTime') / 1000) - timedelta(hours=1)
        )
    while True:
        btc = await client.get_historical_klines(
            symbol=BTC,
            interval=client.KLINE_INTERVAL_3MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        full_price_list_btc = [
            elem for inner in btc for elem in map(float, inner[1:5:3])]
        eth = await client.get_historical_klines(
            symbol=ETH,
            interval=client.KLINE_INTERVAL_3MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        full_price_list_eth = [
            elem for inner in eth for elem in map(float, inner[1:5:3])]
        result = await check_corel(
            eth=full_price_list_eth,
            btc=full_price_list_btc,
            period=PERIOD_HOUR
            )
        if result:
            logging.warning(DETECTED)
        await asyncio.sleep(SLEEP_1HOUR)
        cur_serv_time = cur_serv_time + timedelta(hours=1)


async def price_movement_change_1hour(client: AsyncClient):
    """
    Analyzing the price change for the previous hour.
    Using the minimum and maximum values.
    """
    g = await client.get_server_time()
    cur_serv_time = (
        datetime.utcfromtimestamp(
            g.get('serverTime') / 1000) - timedelta(hours=1)
        )
    while True:
        btc = await client.get_historical_klines(
            symbol=BTC,
            interval=client.KLINE_INTERVAL_1HOUR,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        mini_maxi_btc = [float(elem) for elem in btc[0][2:4]]
        eth = await client.get_historical_klines(
            symbol=ETH,
            interval=client.KLINE_INTERVAL_1HOUR,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        mini_maxi_eth = [float(elem) for elem in eth[0][2:4]]
        result = await percent_and_corel(
            eth=mini_maxi_eth,
            btc=mini_maxi_btc,
            period=PERIOD_HOUR
            )
        if result:
            logging.warning(DETECTED)
        await asyncio.sleep(SLEEP_1HOUR)
        cur_serv_time = cur_serv_time + timedelta(hours=1)


async def price_movement_change_1min(client: AsyncClient):
    """
    Analyzing the price change for the previous 1 minute.
    Using the open value and close value.
    """
    g = await client.get_server_time()
    cur_serv_time = (
        datetime.utcfromtimestamp(
            g.get('serverTime') / 1000) - timedelta(minutes=1)
        )
    while True:
        btc = await client.get_historical_klines(
            symbol=BTC,
            interval=client.KLINE_INTERVAL_1MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        open_close_btc = [float(elem) for elem in btc[0][1:5:3]]
        eth = await client.get_historical_klines(
            symbol=ETH,
            interval=client.KLINE_INTERVAL_1MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        open_close_eth = [float(elem) for elem in eth[0][1:5:3]]
        result = await percent_and_corel(
            eth=open_close_eth,
            btc=open_close_btc,
            period=PERIOD_MINUTE
            )
        if result:
            logging.warning(DETECTED)
        await asyncio.sleep(SLEEP_1MINUTE)
        cur_serv_time = cur_serv_time + timedelta(minutes=1)


async def main():
    client = await AsyncClient.create()

    task_infinity_price = asyncio.Task(start_current_price(client))
    task_corel_1hour = asyncio.Task(price_movement_change_1hour(client))
    task_corel_1m = asyncio.Task(price_movement_change_1min(client))
    task_full_analyz = asyncio.Task(analyzing_correlation_1hour(client))
    await asyncio.sleep(TEST_SCRIPT_DURATION)  # TIME SCRIPT

    await client.close_connection()

    task_full_analyz.cancel()
    task_infinity_price.cancel()
    task_corel_1hour.cancel()
    task_corel_1m.cancel()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    logging.info('---The End---\n')
