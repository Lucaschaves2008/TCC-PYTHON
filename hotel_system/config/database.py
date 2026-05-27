import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Localiza o .env dois níveis acima deste arquivo (TCC-PYTHON/.env)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Variáveis do banco
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# URL de conexão do SQLAlchemy
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Cria a engine de conexão
engine = create_engine(DATABASE_URL)

# Cria sessões do banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@contextmanager
def get_session():
    """
    Gerenciador de contexto para sessões do banco.

    Uso:
        with get_session() as session:
            repo = ClienteRepository(session)
            ...

    - Em caso de erro: faz rollback automaticamente
    - Sempre fecha a sessão ao sair do bloco
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Teste de conexão (executado apenas quando o módulo é rodado diretamente)
if __name__ == "__main__":
    try:
        connection = engine.connect()
        print("Conexão com MySQL realizada com sucesso!")
        connection.close()
    except Exception as error:
        print(" Erro ao conectar no banco:")
        print(error)