# Load environment variables first
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routes import screenshot, generate_code, home, evals, auth
from config import ALLOWED_ORIGINS, IS_PROD
from middleware.rate_limit import rate_limit_middleware
from websocket_manager import ws_manager
import logging
from contextlib import asynccontextmanager

# Application lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Start async logging - commented out due to missing module
    # async with async_logger_context() as logger_mgr:
    # Start WebSocket manager
    await ws_manager.start()
    print("WebSocket manager started")
    # print("Async logging system started")
    
    yield
    
    # Shutdown
    await ws_manager.stop()
    print("WebSocket manager stopped")
    # print("Async logging system stopped")

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None, lifespan=lifespan)

# Add security middleware
if IS_PROD:
    # Only allow specific hosts in production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["code.yun7.de", "*.yun7.de", "localhost", "127.0.0.1"]
    )

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Configure CORS settings with security in mind
# In production, only allow specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True if "*" not in ALLOWED_ORIGINS else False,  # Don't allow credentials with wildcard origins
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Only allow necessary headers
    expose_headers=["Content-Length"],  # Expose only necessary headers
)

# Log security configuration on startup
logger = logging.getLogger("main")
if IS_PROD:
    logger.info("Running in PRODUCTION mode")
    logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")
else:
    logger.info("Running in DEVELOPMENT mode")
    if "*" in ALLOWED_ORIGINS:
        logger.warning("CORS is configured to allow ALL origins. This should only be used in development!")

# Add routes
app.include_router(auth.router)
app.include_router(generate_code.router)
app.include_router(screenshot.router)
app.include_router(home.router)
app.include_router(evals.router)
