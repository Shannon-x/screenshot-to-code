# Load environment variables first
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routes import screenshot, generate_code, home, evals, auth
from config import ALLOWED_ORIGINS, IS_PROD
from middleware.rate_limit import rate_limit_middleware

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# Add security middleware
if IS_PROD:
    # Only allow specific hosts in production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
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
if IS_PROD:
    print("Running in PRODUCTION mode")
    print(f"CORS allowed origins: {ALLOWED_ORIGINS}")
else:
    print("Running in DEVELOPMENT mode")
    if "*" in ALLOWED_ORIGINS:
        print("WARNING: CORS is configured to allow ALL origins. This should only be used in development!")

# Add routes
app.include_router(auth.router)
app.include_router(generate_code.router)
app.include_router(screenshot.router)
app.include_router(home.router)
app.include_router(evals.router)
