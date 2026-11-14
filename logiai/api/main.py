"""L'API LogiAI : python -m uvicorn logiai.api.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse

from logiai.api.schemas import Livraison, PredictionOut
from logiai.api.security import require_admin, verify_api_key
from logiai.config import ALLOWED_ORIGINS, MODEL_PATH, ROOT_PATH
from logiai.predict import Predictor

state: dict = {}  # contient le "predictor" une fois le modèle chargé


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exécuté UNE fois, au démarrage du serveur (pas à chaque requête)
    if MODEL_PATH.exists():
        state["predictor"] = Predictor(MODEL_PATH)
    yield
    state.clear()


app = FastAPI(
    title="LogiAI",
    version="1.0.0",
    description="Prédit le risque de retard d'une livraison à partir de ses caractéristiques.",
    lifespan=lifespan,
    docs_url=None,
    root_path=ROOT_PATH,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "predictor" in state}


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/docs")


@app.get("/docs", include_in_schema=False)
def documentation():
    # Le chemin relatif fonctionne en accès direct et derrière /api/ dans Nginx.
    return get_swagger_ui_html(openapi_url="./openapi.json", title="LogiAI API")


@app.post("/v1/predict", response_model=PredictionOut, dependencies=[Depends(verify_api_key)])
def predict(livraison: Livraison):
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle indisponible")
    return PredictionOut(**predictor.predict(livraison.model_dump()))


@app.get("/v1/model-info", dependencies=[Depends(require_admin)])
def model_info():
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle indisponible")
    return {"model_version": predictor.version, "seuil": predictor.threshold}
