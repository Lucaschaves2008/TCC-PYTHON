from typing import List, Optional

from sqlalchemy.orm import Session

from models.cliente import Cliente


class ClienteRepository:
    """
    Camada de acesso ao banco para a entidade Cliente.
    Só faz CRUD — sem regras de negócio aqui.
    Regras ficam nos Services.
    """

    def __init__(self, session: Session):
        self.session = session

    def criar(self, cliente: Cliente) -> Cliente:
        self.session.add(cliente)
        self.session.commit()
        self.session.refresh(cliente)
        return cliente

    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        return self.session.query(Cliente).filter(Cliente.id == cliente_id).first()

    def buscar_por_cpf(self, cpf: str) -> Optional[Cliente]:
        return self.session.query(Cliente).filter(Cliente.cpf == cpf).first()

    def buscar_por_email(self, email: str) -> Optional[Cliente]:
        return self.session.query(Cliente).filter(Cliente.email == email).first()

    def listar_todos(self) -> List[Cliente]:
        return self.session.query(Cliente).order_by(Cliente.nome).all()

    def pesquisar(self, termo: str) -> List[Cliente]:
        like = f"%{termo}%"
        return (
            self.session.query(Cliente)
            .filter(
                Cliente.nome.ilike(like)
                | Cliente.email.ilike(like)
                | Cliente.cpf.ilike(like)
            )
            .order_by(Cliente.nome)
            .all()
        )

    def atualizar(self, cliente: Cliente) -> Cliente:
        self.session.commit()
        self.session.refresh(cliente)
        return cliente

    def deletar(self, cliente: Cliente) -> None:
        self.session.delete(cliente)
        self.session.commit()

    def contar(self) -> int:
        return self.session.query(Cliente).count()
