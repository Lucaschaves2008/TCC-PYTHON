"""
ReservaService — regras de negócio para reservas.

Aqui ficam as validações mais importantes do sistema:
- Conflito de datas (quarto não pode ter duas reservas no mesmo período)
- Cálculo do valor total
- Transições de status (ciclo de vida da reserva)
"""
from datetime import datetime
from typing import List, Optional

from config.database import get_session
from models.quarto import StatusQuarto
from models.reserva import Reserva, StatusReserva
from repositories.quarto_repository import QuartoRepository
from repositories.reserva_repository import ReservaRepository
from utils.validators import validar_datas_reserva


def criar_reserva(
    cliente_id: int,
    quarto_id: int,
    check_in: datetime,
    check_out: datetime,
    observacoes: str = "",
) -> dict:
    valido, erro = validar_datas_reserva(check_in.date(), check_out.date())
    if not valido:
        raise ValueError(erro)

    with get_session() as session:
        repo_reserva = ReservaRepository(session)
        repo_quarto = QuartoRepository(session)

        quarto = repo_quarto.buscar_por_id(quarto_id)
        if not quarto:
            raise ValueError("Quarto não encontrado.")
        if quarto.status == StatusQuarto.MANUTENCAO:
            raise ValueError("Quarto em manutenção — não pode ser reservado.")

        if repo_reserva.verificar_conflito(quarto_id, check_in, check_out):
            raise ValueError(
                "O quarto já possui uma reserva nesse período. "
                "Escolha outras datas ou outro quarto."
            )

        numero_dias = (check_out - check_in).days
        total = numero_dias * float(quarto.preco_diaria)

        reserva = Reserva(
            cliente_id=cliente_id,
            quarto_id=quarto_id,
            check_in=check_in,
            check_out=check_out,
            status=StatusReserva.CONFIRMADA,
            total=total,
            observacoes=observacoes.strip() or None,
        )
        resultado = repo_reserva.criar(reserva)
        # Acessa relações enquanto sessão está aberta
        return resultado.to_dict()


def listar_reservas(filtro_status: str = "") -> List[dict]:
    with get_session() as session:
        repo = ReservaRepository(session)
        if filtro_status:
            # Filtra por status ao listar todas e depois filtra em memória
            todas = repo.listar_todas()
            return [
                r.to_dict()
                for r in todas
                if r.status.value == filtro_status.lower()
            ]
        return [r.to_dict() for r in repo.listar_todas()]


def buscar_reserva(reserva_id: int) -> Optional[dict]:
    with get_session() as session:
        repo = ReservaRepository(session)
        reserva = repo.buscar_por_id(reserva_id)
        return reserva.to_dict() if reserva else None


def listar_por_cliente(cliente_id: int) -> List[dict]:
    with get_session() as session:
        repo = ReservaRepository(session)
        return [r.to_dict() for r in repo.listar_por_cliente(cliente_id)]


def alterar_status(reserva_id: int, novo_status: str) -> dict:
    """
    Transições válidas no ciclo de vida de uma reserva:
    CONFIRMADA → CHECKIN → CHECKOUT
    qualquer estado ativo → CANCELADA
    """
    try:
        status_enum = StatusReserva[novo_status.upper()]
    except KeyError:
        raise ValueError(f"Status inválido: {novo_status}")

    with get_session() as session:
        repo = ReservaRepository(session)
        reserva = repo.buscar_por_id(reserva_id)
        if not reserva:
            raise ValueError("Reserva não encontrada.")

        # Ao fazer checkout, libera o quarto
        if status_enum == StatusReserva.CHECKOUT:
            quarto_repo = QuartoRepository(session)
            quarto = quarto_repo.buscar_por_id(reserva.quarto_id)
            if quarto:
                quarto.status = StatusQuarto.DISPONIVEL

        reserva.status = status_enum
        resultado = repo.atualizar(reserva)
        return resultado.to_dict()


def deletar_reserva(reserva_id: int) -> None:
    with get_session() as session:
        repo = ReservaRepository(session)
        reserva = repo.buscar_por_id(reserva_id)
        if not reserva:
            raise ValueError("Reserva não encontrada.")
        if reserva.status == StatusReserva.CHECKIN:
            raise ValueError(
                "Não é possível excluir uma reserva com check-in ativo. "
                "Faça o check-out primeiro."
            )
        repo.deletar(reserva)


def contar_ativas() -> int:
    with get_session() as session:
        return ReservaRepository(session).contar_ativas()


def contar_reservas() -> int:
    with get_session() as session:
        return ReservaRepository(session).contar()
