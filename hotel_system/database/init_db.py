"""
Script de inicialização do banco de dados.

O que ele faz:
1. Importa todos os models (isso os registra na Base)
2. Cria o banco 'hotel_system' se não existir
3. Cria todas as tabelas mapeadas pelos models

Como usar:
    cd hotel_system
    python database/init_db.py

IMPORTANTE: execute este script UMA VEZ para configurar o banco.
Nas próximas execuções ele não recria tabelas que já existem (CREATE IF NOT EXISTS).
"""

import sys
import os

# Garante que o Python encontre os módulos do projeto ao rodar direto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine
from models.base import Base

# Importar TODOS os models é obrigatório aqui.
# Sem o import, o SQLAlchemy não sabe da existência dessas tabelas.
from models.cliente import Cliente   # noqa: F401
from models.quarto import Quarto     # noqa: F401
from models.reserva import Reserva   # noqa: F401


def criar_tabelas():
    """
    Cria todas as tabelas mapeadas pelos models ORM.

    Base.metadata contém o mapa de todas as tabelas registradas.
    create_all() verifica quais ainda não existem e cria apenas essas.
    Tabelas já existentes são ignoradas (não apaga dados!).
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print()
    print("   Tabelas no banco:")
    for table_name in Base.metadata.tables:
        print(f"   → {table_name}")


def inicializar():
    """Ponto de entrada: cria banco e tabelas em sequência."""
    print("=" * 50)
    print("   INICIALIZANDO BANCO DE DADOS")
    print("=" * 50)
    print()

    try:
        criar_tabelas()
        print()
        print("=" * 50)
        print("   BANCO PRONTO PARA USO!")
        print("=" * 50)

    except Exception as erro:
        print()
        print("❌ Erro ao inicializar o banco:")
        print(f"   {erro}")
        sys.exit(1)


if __name__ == "__main__":
    inicializar()
