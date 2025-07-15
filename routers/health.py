from fastapi import APIRouter

# Create a router instance
health_router = APIRouter()

# Define routes within the router
@health_router.get("")
def health():
    return {"status": "ok"}
