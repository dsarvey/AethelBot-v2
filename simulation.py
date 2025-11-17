# simulation.py
#
# Contains the core "untethered" simulation loop that runs
# as a background task.

import asyncio
import random
import datetime

# Import our global state and manager
from state import bot_state, manager

async def bot_trading_loop():
    """The main background task for the bot."""
    global bot_state
    print("Bot trading loop 'bot_trading_loop' started.")
    
    while bot_state["is_deployed"]:
        try:
            # 1. Simulate portfolio drift
            if bot_state["equity"] > 0:
                drift = random.uniform(-0.0005, 0.0007)
                bot_state["equity"] *= (1 + drift)
                bot_state["pnl"] = bot_state["equity"] - bot_state["total_external_funding"]

            # 2. Create the portfolio update message
            portfolio_msg = {
                "type": "PORTFOLIO_UPDATE",
                "payload": {
                    "equity": bot_state["equity"],
                    "pnl": bot_state["pnl"],
                    "totalExternalFunding": bot_state["total_external_funding"],
                    "reinvestedProfit": bot_state["reinvested_profit"],
                    "initialFunding": bot_state["initial_funding"],
                    "uninvestedCash": bot_state["equity"] * 0.1, # Simulating 10% cash
                    "allocations": [
                        {
                            "class": "Stocks", "value": bot_state["equity"] * 0.5, "percent": 50,
                            "positions": [{"symbol": "CSCO", "units": 100, "value": bot_state["equity"] * 0.5}]
                        },
                        {
                            "class": "Crypto", "value": bot_state["equity"] * 0.4, "percent": 40,
                            "positions": [{"symbol": "BTC/USD", "units": 3, "value": bot_state["equity"] * 0.4}]
                        }
                    ]
                }
            }
            # 3. Broadcast the update to all connected clients
            await manager.broadcast_json(portfolio_msg)

            # 4. Simulate a random log entry
            if random.random() < 0.1:
                log_msg = {
                    "type": "LOG_ENTRY",
                    "payload": {
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "level": "BUY",
                        "message": f"[SIMULATED BUY] Executed market buy of +{random.randint(1, 5)} units of PLTR."
                    }
                }
                await manager.broadcast_json(log_msg)

            # 5. Sleep for 1 second
            await asyncio.sleep(1)

        except Exception as e:
            print(f"Error in bot loop: {e}")

    print("Bot trading loop 'bot_trading_loop' stopped.")
