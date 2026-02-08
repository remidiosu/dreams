from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.logger import logger
from app.config import settings
from app.patches.graphrag_igraph_fix import apply_graphrag_igraph_patch

apply_graphrag_igraph_patch()

from app.controllers.auth_controllers import auth_router
from app.controllers.dream_controllers import dream_router
from app.controllers.symbol_controllers import symbol_router, dream_symbol_router
from app.controllers.character_controllers import character_router, dream_character_router
from app.controllers.chat_controllers import chat_router
from app.controllers.graph_controllers import graph_router
from app.controllers.analytics_controllers import analytics_router
from app.controllers.extraction_controller import extraction_router
from app.controllers.demo import demo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("dream service starting")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    logger.info("Shutting down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dream_router)
app.include_router(dream_symbol_router)
app.include_router(dream_character_router)
app.include_router(symbol_router)
app.include_router(character_router)
app.include_router(graph_router)
app.include_router(analytics_router)
app.include_router(chat_router)
app.include_router(extraction_router)
app.include_router(demo_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f'Starting app with host={settings.host} port={settings.port} debug={settings.debug}')
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
