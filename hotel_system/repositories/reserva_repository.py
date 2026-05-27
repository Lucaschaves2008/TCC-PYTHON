from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from models.reserva import Reserva, StatusReserva


class ReservaRepository:
    """Camada de acesso ao banco para a entidade Reserva."""

    def __init__(self, session: Session):
        self.session = session

    def _query_com_joins(self):
        """Query base que carrega cliente e quarto junto (evita N+1 queries)."""
        return self.session.query(Reserva).options(
            joinedload(Reserva.cliente),
            joinedload(Reserva.quarto),
        )

    def criar(self, reserva: Reserva) -> Reserva:
        self.session.add(reserva)
        self.session.commit()
        self.session.refresh(reserva)
        return reserva

    def buscar_por_id(self, reserva_id: int) -> Optional[Reserva]:
        return (
            self._query_com_joins()
            .filter(Reserva.id == reserva_id)
            .first()
        )

    def listar_todas(self) -> List[Reserva]:
        return (
            self._query_com_joins()
            .order_by(Reserva.check_in.desc())
            .all()
        )

    def listar_por_cliente(self, cliente_id: int) -> List[Reserva]:
        return (
            self._query_com_joins()
            .filter(Reserva.cliente_id == cliente_id)
            .order_by(Reserva.check_in.desc())
            .all()
        )

    def listar_ativas(self) -> List[Reserva]:
        return (
            self._query_com_joins()
            .filter(
                Reserva.status.in_([StatusReserva.CONFIRMADA, StatusReserva.CHECKIN])
            )
            .all()
        )

    def verificar_conflito(
        self,
        quarto_id: int,
        check_in: datetime,
        check_out: datetime,
        excluir_id: Optional[int] = None,
    ) -> bool:
        """
        Verifica se existe reserva ativa para o quarto no período informado.
        Dois períodos conflitam quando: A.check_in < B.check_out E A.check_out > B.check_in
        """
        query = self.session.query(Reserva).filter(
            Reserva.quarto_id == quarto_id,
            Reserva.status.in_(
                [StatusReserva.PENDENTE, StatusReserva.CONFIRMADA, StatusReserva.CHECKIN]
            ),
            and_(
                Reserva.check_in < check_out,
                Reserva.check_out > check_in,
            ),
        )
        if excluir_id:
            query = query.filter(Reserva.id != excluir_id)
        return query.first() is not None

    def atualizar(self, reserva: Reserva) -> Reserva:
        self.session.commit()
        self.session.refresh(reserva)
        return reserva

    def deletar(self, reserva: Reserva) -> None:
        self.session.delete(reserva)
        self.session.commit()

    def contar_ativas(self) -> int:
        return (
            self.session.query(Reserva)
            .filter(
                Reserva.status.in_([StatusReserva.CONFIRMADA, StatusReserva.CHECKIN])
            )
            .count()
        )

    def contar(self) -> int:
        return self.session.query(Reserva).count()
