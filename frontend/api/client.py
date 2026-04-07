import requests
import streamlit as st

API_BASE = "http://localhost:8000"


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _log(method: str, endpoint: str, params: dict = None, data: dict = None):
    parts = [f"[API] {method} {API_BASE}{endpoint}"]
    if params:
        parts.append(f"params={params}")
    if data:
        parts.append(f"body={data}")
    print(" | ".join(parts), flush=True)


def get(endpoint: str, params: dict = None):
    _log("GET", endpoint, params=params)
    r = requests.get(f"{API_BASE}{endpoint}", headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()


def post(endpoint: str, data: dict):
    _log("POST", endpoint, data=data)
    r = requests.post(f"{API_BASE}{endpoint}", json=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def put(endpoint: str, data: dict):
    _log("PUT", endpoint, data=data)
    r = requests.put(f"{API_BASE}{endpoint}", json=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def delete(endpoint: str):
    r = requests.delete(f"{API_BASE}{endpoint}", headers=_headers())
    r.raise_for_status()
    return r.json() if r.content else {}


def login(nome: str, senha: str) -> dict:
    r = requests.post(
        f"{API_BASE}/auth/login",
        data={"username": nome, "password": senha}
    )
    r.raise_for_status()
    return r.json()