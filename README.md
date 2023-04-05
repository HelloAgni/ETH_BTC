# ETH_BTC

**Script** that determines the own price movement of the **ETHUSDT** futures,  
excluding from them the movements caused by the influence of the **BTCUSDT** price  

***How to start***  
```bash
git clone <project>
cd <project>
python -m venv venv
# Windows
. venv/scripts/activate 
# Linux
. venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python ethusdt.py 
#info.log
```
Set the script duration if needed
```bash
TEST_SCRIPT_DURATION = 65  # 65 seconds
SCRIPT_DURATION = 3900  # 65 minutes
...
async def main():
    ...
    await asyncio.sleep(TEST_SCRIPT_DURATION)  # TIME SCRIPT
    ...
```
Example output
```bash
INFO     2023-04-05 14:04:31 Analyzing ETHUSDT change percent is: -0.049 for last hour
WARNING  2023-04-05 14:04:31 Analyzing ETHUSDT corellation is: 0.099 for last hour
WARNING  2023-04-05 14:04:31 Price movement detected
```