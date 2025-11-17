# routes.py
#
# Defines all API endpoints (routes) for the application.
# This file handles all HTTP and WebSocket requests.

import asyncio
import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Import our modular components
from schemas import DeployBody, CapitalInjectBody, TsoQuery
from state import manager, bot_state
from agent import agent_executor
from simulation import bot_trading_loop

# Create an API router
router = APIRouter()

# --- 1. REST API Endpoints (Command & Control) ---

@router.post("/v1/strategy/deploy")
async def deploy_strategy(body: DeployBody):
    global bot_state
    if not bot_state["is_deployed"]:
        bot_state["is_deployed"] = True
        bot_state["initial_funding"] = body.initialFunding
        bot_state["total_external_funding"] = body.initialFunding + body.additionalCapital
        bot_state["equity"] = bot_state["total_external_funding"]
        
        # Start the background task
        bot_state["bot_task"] = asyncio.create_task(bot_trading_loop())

        return {"status": "deployed", "message": "AethelBot is now active."}
    return {"status": "error", "message": "Bot is already deployed."}

@router.post("/v1/strategy/stop")
async def stop_strategy():
    global bot_state
    if bot_state["is_deployed"]:
        bot_state["is_deployed"] = False
        if bot_state["bot_task"]:
            bot_state["bot_task"].cancel()
            bot_state["bot_task"] = None
        
        await manager.broadcast_json({
            "type": "LOG_ENTRY",
            "payload": {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": "SYSTEM",
                "message": "AethelBot Halted by Executive Order."
            }
        })
        return {"status": "stopped", "message": "AethelBot has been halted."}
    return {"status": "error", "message": "Bot is not running."}

@router.post("/v1/capital/inject")
async def add_capital(body: CapitalInjectBody):
    global bot_state
    if not bot_state["is_deployed"]:
        return {"status": "error", "message": "Bot must be deployed to inject capital."}
    
    bot_state["total_external_funding"] += body.amount
    bot_state["equity"] += body.amount

    await manager.broadcast_json({
        "type": "LOG_ENTRY",
        "payload": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "SYSTEM",
            "message": f"Injected additional external funding: ${body.amount}."
        }
    })
    return {"status": "success", "newTotal": bot_state["total_external_funding"]}

@router.post("/v1/research/tso")
async def get_tso_signal(query: TsoQuery):
    if not agent_executor:
        return {"error": "Agent not initialized. Check GOOGLE_API_KEY."}
    
    try:
        response = await agent_executor.ainvoke({
            "input": f"Analyze the trade signal for {query.ticker}"
        })

        return {
            "ticker": query.ticker,
            "summary": response["output"]
        }
    except Exception as e:
        print(f"Agent invocation error: {e}")
        return {"error": f"Agent failed to process request: {e}"}

# --- 2. WebSocket Endpoint (Real-Time Data Stream) ---

@router.websocket("/v1/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Dashboard connected.")
    try:
        await manager.broadcast_json({
            "type": "LOG_ENTRY",
            "payload": {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": "SYSTEM",
                "message": "Dashboard connected to AethelBot backend."
            }
        })
        while True:
            # Keep the connection alive
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)