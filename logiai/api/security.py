"""Authentification et autorisation des routes de l'API."""
import secrets

from fastapi import Depends, Header, HTTPException

from logiai import config


def _egal(received: str | None, expected: str | None) -> bool:
    return bool(received and expected and secrets.compare_digest(received, expected))


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if _egal(x_api_key, config.ADMIN_KEY):
        return "admin"
    if _egal(x_api_key, config.API_KEY):
        return "user"
    raise HTTPException(status_code=401, detail="Clé API absente ou invalide")


def require_admin(role: str = Depends(verify_api_key)) -> str:
    if role != "admin":
        raise HTTPException(status_code=403, detail="Droits administrateur requis")
    return role
