"""
QuartoService — regras de negócio para quartos.
"""
from typing import Dict, List, Optional

from config.database import get_session
from models.quarto import Quarto, StatusQuarto, TipoQuarto
from repositories.quarto_repository import QuartoRepository
from utils.validators import validar_capacidade, validar_preco


def criar_quarto(
    numero: str,
    tipo: str,
    preco_diaria: float,
    capacidade: int = 1,
    descricao: str = "",
) -> dict:
    numero = numero.strip().upper()

    if not numero:
        raise ValueError("O número do quarto é obrigatório.")
    if not validar_preco(preco_diaria):
        raise ValueError("O preço da diária deve ser maior que zero.")
    if not validar_capacidade(capacidade):
        raise ValueError("A capacidade deve ser entre 1 e 20 pessoas.")

    try:
        tipo_enum = TipoQuarto[tipo.upper()]
    except KeyError:
        raise ValueError(f"Tipo de quarto inválido: {tipo}")

    with get_session() as session:
        repo = QuartoRepository(session)
        if repo.buscar_por_numero(numero):
            raise ValueError(f"Já existe um quarto com o número '{numero}'.")
        quarto = Quarto(
            numero=numero,
            tipo=tipo_enum,
            status=StatusQuarto.DISPONIVEL,
            capacidade=capacidade,
            preco_diaria=preco_diaria,
            descricao=descricao.strip() or None,
        )
        return repo.criar(quarto).to_dict()


def listar_quartos(filtro_status: str = "") -> List[dict]:
    with get_session() as session:
        repo = QuartoRepository(session)
        if filtro_status:
            try:
                status = StatusQuarto[filtro_status.upper()]
                quartos = repo.listar_por_status(status)
            except KeyError:
                quartos = repo.listar_todos()
        else:
            quartos = repo.listar_todos()
        return [q.to_dict() for q in quartos]


def buscar_quarto(quarto_id: int) -> Optional[dict]:
    with get_session() as session:
        repo = QuartoRepository(session)
        quarto = repo.buscar_por_id(quarto_id)
        return quarto.to_dict() if quarto else None


def atualizar_quarto(
    quarto_id: int,
    numero: str,
    tipo: str,
    preco_diaria: float,
    capacidade: int,
    descricao: str = "",
) -> dict:
    numero = numero.strip().upper()

    if not validar_preco(preco_diaria):
        raise ValueError("O preço da diária deve ser maior que zero.")
    if not validar_capacidade(capacidade):
        raise ValueError("A capacidade deve ser entre 1 e 20 pessoas.")

    try:
        tipo_enum = TipoQuarto[tipo.upper()]
    except KeyError:
        raise ValueError(f"Tipo de quarto inválido: {tipo}")

    with get_session() as session:
        repo = QuartoRepository(session)
        quarto = repo.buscar_por_id(quarto_id)
        if not quarto:
            raise ValueError("Quarto não encontrado.")

        existente = repo.buscar_por_numero(numero)
        if existente and existente.id != quarto_id:
            raise ValueError(f"Número '{numero}' já pertence a outro quarto.")

        quarto.numero = numero
        quarto.tipo = tipo_enum
        quarto.preco_diaria = preco_diaria
        quarto.capacidade = capacidade
        quarto.descricao = descricao.strip() or None
        return repo.atualizar(quarto).to_dict()


def alterar_status(quarto_id: int, novo_status: str) -> dict:
    try:
        status_enum = StatusQuarto[novo_status.upper()]
    except KeyError:
        raise ValueError(f"Status inválido: {novo_status}")

    with get_session() as session:
        repo = QuartoRepository(session)
        quarto = repo.buscar_por_id(quarto_id)
        if not quarto:
            raise ValueError("Quarto não encontrado.")
        quarto.status = status_enum
        return repo.atualizar(quarto).to_dict()


def deletar_quarto(quarto_id: int) -> None:
    with get_session() as session:
        repo = QuartoRepository(session)
        quarto = repo.buscar_por_id(quarto_id)
        if not quarto:
            raise ValueError("Quarto não encontrado.")
        if quarto.reservas:
            raise ValueError(
                "Não é possível excluir um quarto que possui reservas. "
                "Cancele ou exclua as reservas primeiro."
            )
        repo.deletar(quarto)


def contar_por_status() -> Dict[str, int]:
    with get_session() as session:
        return QuartoRepository(session).contar_por_status()


def contar_quartos() -> int:
    with get_session() as session:
        return QuartoRepository(session).contar()
