from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(tags=["Admin"])

@router.get("/admin", response_class=HTMLResponse)
async def serve_admin_panel():
    """Serves the single-page admin panel HTML."""
    html_path = os.path.join("static", "admin", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>Admin Panel UI not found</h1>", status_code=404)
