from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.quarto import Quarto, StatusQuarto, TipoQuarto


class QuartoRepository:
    """Camada de acesso ao banco para a entidade Quarto."""

    def __init__(self, session: Session):
        self.session = session

    def criar(self, quarto: Quarto) -> Quarto:
        self.session.add(quarto)
        self.session.commit()
        self.session.refresh(quarto)
        return quarto

    def buscar_por_id(self, quarto_id: int) -> Optional[Quarto]:
        return self.session.query(Quarto).filter(Quarto.id == quarto_id).first()

    def buscar_por_numero(self, numero: str) -> Optional[Quarto]:
        return self.session.query(Quarto).filter(Quarto.numero == numero).first()

    def listar_todos(self) -> List[Quarto]:
        return self.session.query(Quarto).order_by(Quarto.numero).all()

    def listar_por_status(self, status: StatusQuarto) -> List[Quarto]:
        return (
            self.session.query(Quarto)
            .filter(Quarto.status == status)
            .order_by(Quarto.numero)
            .all()
        )

    def listar_disponiveis(self) -> List[Quarto]:
        return self.listar_por_status(StatusQuarto.DISPONIVEL)

    def listar_por_tipo(self, tipo: TipoQuarto) -> List[Quarto]:
        return (
            self.session.query(Quarto)
            .filter(Quarto.tipo == tipo)
            .order_by(Quarto.numero)
            .all()
        )

    def atualizar(self, quarto: Quarto) -> Quarto:
        self.session.commit()
        self.session.refresh(quarto)
        return quarto

    def deletar(self, quarto: Quarto) -> None:
        self.session.delete(quarto)
        self.session.commit()

    def contar_por_status(self) -> Dict[str, int]:
        """Retorna {status_value: quantidade} para o dashboard."""
        resultado = (
            self.session.query(Quarto.status, func.count(Quarto.id))
            .group_by(Quarto.status)
            .all()
        )
        return {status.value: count for status, count in resultado}

    def contar(self) -> int:
        return self.session.query(Quarto).count()
