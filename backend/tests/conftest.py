"""
Configuração dos testes: banco SQLite em memória, isolado por teste.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from app.dependencies import get_db
from app.models.tecnico import Tecnico
from app.core.config import settings

# Força DEV_MODE para que os testes não precisem de JWT
settings.DEV_MODE = True

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente HTTP com banco de teste injetado."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Cria técnico padrão para DEV_MODE (get_current_user precisa de pelo menos 1)
    tecnico = Tecnico(
        TbNomeTecnico="TESTE",
        TbSenha="teste123",
        TbNivel=3,
        TbStatus="Ativo",
    )
    db_session.add(tecnico)
    db_session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
