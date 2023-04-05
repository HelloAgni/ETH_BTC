import asyncio
import statistics
from datetime import datetime, timedelta
from binance import AsyncClient

SCRIPT_DURATION = 3600  # 60 minutes
CORRELATION = 0.6  # for example 0.6; Usual correlation ~ 0.98
SLEEP_1HOUR = 3600  # 60 minutes
SLEEP_1MINUTE = 60  # 1 minute
SLEEP_15SECONDS = 15


async def check_corel(eth, btc):
    """
    Analyzing the start_current_price.
    """
    corel = statistics.correlation(eth, btc)
    print('Correlation: ', corel)
    print('Own price movement')
    if corel <= CORRELATION:  # 0.6
        return True
    return False


async def start_current_price(client: AsyncClient):
    """
    Current price change since script launch.
    The script start price and the current price are used.
    """
    g = await client.get_symbol_ticker(symbol='ETHUSDT')
    start_price_eth = float(g.get("price"))
    print("start price:", start_price_eth)
    # start price: 1912.35
    bt = await client.get_symbol_ticker(symbol='BTCUSDT')
    start_price_bt = float(bt.get("price"))
    while True:
        g = await client.get_symbol_ticker(symbol='ETHUSDT')
        print(f'Ticker: {g.get("symbol")} current price: {float(g.get("price"))}')
        # Ticker: ETHUSDT current price: 1912.35

        curent_price_eth = float(g.get("price"))
        eth_start_end = [start_price_eth, curent_price_eth]
        print('list eth: ', eth_start_end)
        # list eth:  [1912.35, 1912.35]

        change_percent = round(((curent_price_eth - start_price_eth) / start_price_eth) * 100, 2)
        print("change percent since script launch:", change_percent)
        # change percent since script launch: -0.05

        bt = await client.get_symbol_ticker(symbol='BTCUSDT')
        print(f'Ticker: {bt.get("symbol")} current price: {float(bt.get("price"))}')
        # Ticker: BTCUSDT current price: 28498.0
        curent_price_bt = float(bt.get("price"))
        btc_start_end = [start_price_bt, curent_price_bt]
        print('list btc: ', btc_start_end)
        # list btc:  [28510.12, 28498.0]

        if change_percent <= -1 or change_percent >= 1:
            print(f'ETHUSD change percent is: {change_percent}')
            result = await check_corel(eth=eth_start_end, btc=btc_start_end)
            if result:
                print('Own price movement')
        await asyncio.sleep(SLEEP_15SECONDS)


async def percent_and_corel(eth, btc):
    """
    Analyzing the price change in percentages
    Analyzing the correlation.
    Usual correlation between ETHUSDT and BTCUSDT is around 0.98.
    """
    open_price = eth[0]
    close_price = eth[-1]
    change_percent = ((close_price - open_price) / open_price) * 100

    print('change percent:', change_percent)

    ss = statistics.correlation(eth, btc)
    print('current corel: ', ss)
    if change_percent <= -1 or change_percent >= 1:
        corel = statistics.correlation(btc, eth)
        print('Correlation: ', corel)
        print('Own price movement')
        if corel <= CORRELATION:  # 0.6
            return True
    return False


async def correlation_1hour(client: AsyncClient):
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
            'BTCUSDT',
            client.KLINE_INTERVAL_30MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        mini_maxi_btc = [float(elem) for elem in btc[0][2:4]]
        # print(mini_maxi_btc)
        # [28225.15, 28210.7]

        eth = await client.get_historical_klines(
            'ETHUSDT',
            client.KLINE_INTERVAL_30MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        mini_maxi_eth = [float(elem) for elem in eth[0][2:4]]
        # print(mini_maxi_eth)
        # [1914.24, 1911.1]
        
        result = await percent_and_corel(
            eth=mini_maxi_eth,
            btc=mini_maxi_btc
            )
        if result:
            print('price changed more than 1%')
     
        await asyncio.sleep(SLEEP_1HOUR)
        cur_serv_time = cur_serv_time + timedelta(hours=1)


async def corel_1m(client: AsyncClient):
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
            'BTCUSDT',
            client.KLINE_INTERVAL_1MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        open_close_btc = [float(elem) for elem in btc[0][1:5:3]]
        # BTC [28183.62, 28178.15]
        
        # open_close_btc = [elem for elem in btc]
        # BTC [[1680637920000, '28196.29000000', '28196.30000000', '28182.26000000', '28184.67000000', '41.65650000', 1680637979999, '1174152.52776840', 475, '20.67055000', '582597.87995640', '0']]

        eth = await client.get_historical_klines(
            'ETHUSDT',
            client.KLINE_INTERVAL_1MINUTE,
            start_str=cur_serv_time.strftime('%Y-%m-%d %H:%M:%S')
            )
        open_close_eth = [float(elem) for elem in eth[0][1:5:3]]
        
        result = await percent_and_corel(
            eth=open_close_eth,
            btc=open_close_btc
            )
        if result:
            print('SELF PRICE CHANGED')
     
        await asyncio.sleep(SLEEP_1MINUTE)
        cur_serv_time = cur_serv_time + timedelta(minutes=1)


async def main():
    client = await AsyncClient.create()

    task_infinity_price = asyncio.Task(start_current_price(client))
    # task_corel_1hour = asyncio.Task(correlation_1hour(client))
    # task_corel_1m = asyncio.Task(corel_1m(client))
    await asyncio.sleep(60)  # TIME SCRIPT

    await client.close_connection()
    task_infinity_price.cancel()

    # task_corel_1hour.cancel()    
    # task_corel_1m.cancel()

    # with suppress(asyncio.CancelledError):
    #     # await task  # await for task cancellation


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
