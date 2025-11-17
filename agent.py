# agent.py
#
# Contains all logic for the LangChain TSO Agent.
# This includes tool definitions and agent construction.

import random
from langchain.agents import create_tool_calling_agent
from langchain_community.agent_toolkits import AgentExecutor
from langchain.tools import BaseTool, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. DEFINE THE AGENT'S TOOLS ---
@tool
def get_realtime_price(ticker: str) -> str:
    """
    Gets the current, real-time market price for a given ticker.
    (This is a simulation, in real-life this would call Polygon.io or Alpaca).
    """
    print(f"[Agent Tool Called]: get_realtime_price(ticker='{ticker}')")
    prices = {
        "CSCO": 78.14,
        "PLTR": 24.50,
        "BTC/USD": 72104.50,
        "NVDA": 451.23
    }
    price = prices.get(ticker.upper(), random.uniform(50, 500))
    return f"The current price of {ticker} is ${price}."

@tool
def search_research_database(query: str) -> str:
    """
    Searches the firm's Vector Database for qualitative research, news, 
    and SEC filings related to a query.
    """
    print(f"[Agent Tool Called]: search_research_database(query='{query}')")
    if "csco" in query.lower() or "cisco" in query.lower():
        return "Found 3 documents: 1) 'US-China Tariff Talks Progressing, Tech Sector Impacted'. 2) 'CSCO reports Q3 earnings beat'. 3) 'SEC Filing: Cisco Systems, Inc. (CSCO) Form 8-K'."
    return "No specific research found. General market sentiment is cautious."

@tool
def search_capitol_trades(ticker: str) -> str:
    """
    Searches the Capitol Trades signal feed for any trades by
    politically-exposed persons for a given ticker.
    """
    print(f"[Agent Tool Called]: search_capitol_trades(ticker='{ticker}')")
    if ticker.upper() == "CSCO":
        return "Signal Found: 'Nancy Pelosi (House) reports purchase of +10,000 units of CSCO.' This is a strong correlated signal."
    return "No unusual political/insider trades detected for this ticker."


# --- 2. CREATE THE AGENT ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
except Exception as e:
    print(f"Error initializing Gemini LLM: {e}")
    llm = None

tools = [get_realtime_price, search_research_database, search_capitol_trades]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are the AethelBot Trade Signal Oracle (TSO). Your mission is to provide a high-conviction, justifiable trade signal (BUY, SELL, or HOLD) by synthesizing data from all available tools.
You MUST follow this logic:

Always get the get_realtime_price for the ticker.
Always search_research_database for news and filings.
Always search_capitol_trades for insider signals.
Synthesize ALL THREE data points into a single, authoritative paragraph.
Conclude your analysis with a final, one-word signal: "Signal: BUY", "Signal: SELL", or "Signal: HOLD". """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create the executable agent
if llm:
    agent = create_tool_calling_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
else:
    agent_executor = None