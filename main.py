# main.py
#
# This is the new application entry point.
# Its only job is to build the app and attach the routes.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes  # Import our new routes file

# --- 1. Application Setup ---
app = FastAPI(
    title="AethelBot Agentic Backend",
    description="Backend with a real agentic TSO powered by LangChain.",
    version="10.0.0"
)

# --- 2. Add CORS Middleware (CRITICAL) ---
origins = ["*"]  # Allow all origins for the prototype

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End of CORS Block ---

# --- 3. Include API Routes ---
# This is the magic. We tell our main app to use all the
# endpoints defined in the 'routes.py' file.
app.include_router(routes.router)