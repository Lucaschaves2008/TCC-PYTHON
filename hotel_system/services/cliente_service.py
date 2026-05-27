"""
ClienteService — regras de negócio para clientes.

Esta camada fica entre a View (Streamlit) e o Repository (banco).
Ela valida, aplica regras e converte objetos para dicionários.
"""
from typing import List, Optional

from config.database import get_session
from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository
from utils.validators import validar_cpf, validar_email


def criar_cliente(nome: str, email: str, cpf: str, telefone: str = "") -> dict:
    nome = nome.strip()
    email = email.strip().lower()
    cpf = cpf.strip()
    telefone = telefone.strip() or None

    if not nome:
        raise ValueError("O nome é obrigatório.")
    if not validar_email(email):
        raise ValueError("E-mail inválido.")
    if not validar_cpf(cpf):
        raise ValueError("CPF inválido. Use o formato 000.000.000-00.")

    with get_session() as session:
        repo = ClienteRepository(session)
        if repo.buscar_por_cpf(cpf):
            raise ValueError("CPF já cadastrado no sistema.")
        if repo.buscar_por_email(email):
            raise ValueError("E-mail já cadastrado no sistema.")
        cliente = Cliente(nome=nome, email=email, cpf=cpf, telefone=telefone)
        return repo.criar(cliente).to_dict()


def listar_clientes() -> List[dict]:
    with get_session() as session:
        repo = ClienteRepository(session)
        return [c.to_dict() for c in repo.listar_todos()]


def buscar_cliente(cliente_id: int) -> Optional[dict]:
    with get_session() as session:
        repo = ClienteRepository(session)
        cliente = repo.buscar_por_id(cliente_id)
        return cliente.to_dict() if cliente else None


def pesquisar_clientes(termo: str) -> List[dict]:
    with get_session() as session:
        repo = ClienteRepository(session)
        return [c.to_dict() for c in repo.pesquisar(termo)]


def atualizar_cliente(
    cliente_id: int, nome: str, email: str, cpf: str, telefone: str = ""
) -> dict:
    nome = nome.strip()
    email = email.strip().lower()
    cpf = cpf.strip()
    telefone = telefone.strip() or None

    if not nome:
        raise ValueError("O nome é obrigatório.")
    if not validar_email(email):
        raise ValueError("E-mail inválido.")
    if not validar_cpf(cpf):
        raise ValueError("CPF inválido.")

    with get_session() as session:
        repo = ClienteRepository(session)
        cliente = repo.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        existente = repo.buscar_por_cpf(cpf)
        if existente and existente.id != cliente_id:
            raise ValueError("CPF já pertence a outro cliente.")

        existente = repo.buscar_por_email(email)
        if existente and existente.id != cliente_id:
            raise ValueError("E-mail já pertence a outro cliente.")

        cliente.nome = nome
        cliente.email = email
        cliente.cpf = cpf
        cliente.telefone = telefone
        return repo.atualizar(cliente).to_dict()


def deletar_cliente(cliente_id: int) -> None:
    with get_session() as session:
        repo = ClienteRepository(session)
        cliente = repo.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado.")
        if cliente.reservas:
            raise ValueError(
                "Não é possível excluir um cliente que possui reservas. "
                "Cancele ou exclua as reservas primeiro."
            )
        repo.deletar(cliente)


def contar_clientes() -> int:
    with get_session() as session:
        return ClienteRepository(session).contar()
