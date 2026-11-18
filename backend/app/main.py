import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router
from .core import config
from .services.engine import Engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = Engine() if config.DATA_PATH.exists() else None
    yield


app = FastAPI(title="MGA Discovery API", version="1.0.0", lifespan=lifespan,
              description="API do Mackenzie Game Algorithm: recomendação baseada em conteúdo com similaridade de cosseno.")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

# Capas baixadas por scripts/fetch_covers.py (opcional): servidas em /covers/*
COVERS_DIR = config.DATA_DIR / "covers"
if COVERS_DIR.exists():
    app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

# Se o frontend foi compilado (frontend/dist), a própria API o serve: um único endereço para tudo.
DIST = Path(os.environ.get("MGA_FRONTEND_DIST") or config.BASE.parent / "frontend" / "dist")
if (DIST / "index.html").exists():
    if (DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = (DIST / path).resolve()
        if path and not path.startswith("api") and f.is_file() and DIST.resolve() in f.parents:
            return FileResponse(f)
        return FileResponse(DIST / "index.html")
else:
    from fastapi.responses import HTMLResponse

    @app.get("/", include_in_schema=False)
    def raiz():
        return HTMLResponse("<h2>MGA Discovery API</h2><p>API no ar. A interface ainda não foi compilada: "
                            "rode <code>cd frontend &amp;&amp; npm install &amp;&amp; npm run build</code> "
                            "(ou <code>npm run dev</code> em http://localhost:5173). Documentação: <a href='/docs'>/docs</a>.</p>")
