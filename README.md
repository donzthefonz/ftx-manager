# ftx-manager
A command line tool that helps manage capital across multiple FTX sub-accounts.

**Requirements**
 - Python


Very much a work in progress, there are options in the command line that you can choose but will not do anything.
If you select them, the script will just exit. I have not written any code for orders/trades yet so no risk of major malfunction.


**Working Features:**
  - View Balances (aggregates across multiple subaccounts and summarises them by USD/BTC value and collateral percentages.)
  - Track Liquidity (prints the USD value between bid and - 1% as well as ask + 1% of each asset.)
  - View Positions (across sub accounts)
  
**To-do List:**
  - Close All Positions by X% (capiture profits easily when you think we're over bought/sold.)
  - Rebalance Portfolio (give the script your desired % for each collateral and it will buy/sell to get their on each sub account.)
  - Scaled Order (for manual trading - scale into a position from price X to price Y with size Z.)
  
  
  
 **Run Instructions**
 
Fill in the configuration.yaml with your settings. Required fields are at least one main account with API credentials.
Create this from your main FTX account (not a sub account) if you want all features to work properly. Read-Only access should 
be fine for now though later I want to add the ability to rebalance portfolios (in which case read-only will not work).

1. Download the zip and extract it.
2. Open up command prompt and enter "cd C:\Users\localuser\Downloads\ftx-manager\" (replace folder location with your local path)
3. Create new virtual environment and activate it.
4. Run "pip install -r requirements.txt"
5. Run "python run.py" - if you have filled the configuration.yaml in properly it should run.

