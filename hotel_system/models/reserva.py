import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from models.base import Base


# --- ENUM ---

class StatusReserva(str, enum.Enum):
    """
    Ciclo de vida de uma reserva:

    PENDENTE → CONFIRMADA → CHECKIN → CHECKOUT
                   ↓
               CANCELADA
    """
    PENDENTE   = "pendente"
    CONFIRMADA = "confirmada"
    CHECKIN    = "checkin"
    CHECKOUT   = "checkout"
    CANCELADA  = "cancelada"


# --- ENTIDADE ---

class Reserva(Base):
    """
    Entidade central do sistema — conecta Cliente e Quarto.

    Uma Reserva é criada quando um cliente ocupa um quarto
    por um período específico (check_in → check_out).

    REGRAS DE NEGÓCIO (validadas nos Services, não aqui):
    - check_out deve ser depois de check_in
    - o quarto deve estar disponível no período solicitado
    - não pode ter duas reservas ativas para o mesmo quarto no mesmo período
    """

    __tablename__ = "reservas"

    # --- COLUNAS DA TABELA ---

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ForeignKey: guarda o ID do cliente no banco.
    # O MySQL garante que o cliente_id sempre exista na tabela clientes.
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ForeignKey: guarda o ID do quarto no banco.
    quarto_id = Column(
        Integer,
        ForeignKey("quartos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Período da reserva
    check_in  = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)

    # Status começa como PENDENTE — é confirmada depois de validação
    status = Column(
        Enum(StatusReserva),
        nullable=False,
        default=StatusReserva.PENDENTE,
    )

    # Valor total calculado no momento da confirmação
    # Numeric(10, 2) → nunca Float para dinheiro
    total = Column(Numeric(10, 2), nullable=True)

    # Campo livre para anotações do recepcionista
    observacoes = Column(String(500), nullable=True)

    # Timestamps automáticos
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # --- RELACIONAMENTOS ---

    # Acessa o objeto Cliente completo via reserva.cliente
    # back_populates="reservas" → liga com cliente.reservas
    cliente = relationship("Cliente", back_populates="reservas")

    # Acessa o objeto Quarto completo via reserva.quarto
    # back_populates="reservas" → liga com quarto.reservas
    quarto = relationship("Quarto", back_populates="reservas")

    # --- MÉTODOS DE NEGÓCIO ---

    def calcular_total(self) -> float:
        """
        Calcula o valor total da reserva com base no número de diárias.

        Fórmula: (data_checkout - data_checkin).days × preco_diaria_do_quarto
        Retorna 0.0 se faltar alguma informação necessária.
        """
        if not (self.check_in and self.check_out and self.quarto):
            return 0.0

        numero_de_dias = (self.check_out - self.check_in).days

        if numero_de_dias <= 0:
            return 0.0

        return numero_de_dias * float(self.quarto.preco_diaria)

    def get_numero_dias(self) -> int:
        """Retorna a quantidade de diárias da reserva."""
        if self.check_in and self.check_out:
            return max(0, (self.check_out - self.check_in).days)
        return 0

    def esta_ativa(self) -> bool:
        """Verifica se a reserva está em estado ativo (confirmada ou em checkin)."""
        return self.status in (StatusReserva.CONFIRMADA, StatusReserva.CHECKIN)

    # --- MÉTODOS ESPECIAIS ---

    def __repr__(self) -> str:
        return (
            f"<Reserva(id={self.id}, cliente_id={self.cliente_id}, "
            f"quarto_id={self.quarto_id}, status={self.status.value})>"
        )

    def to_dict(self) -> dict:
        """Converte o objeto para dicionário — usado pelo Streamlit."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente.nome if self.cliente else "",
            "quarto_id": self.quarto_id,
            "quarto_numero": self.quarto.numero if self.quarto else "",
            "check_in": self.check_in.strftime("%d/%m/%Y") if self.check_in else "",
            "check_out": self.check_out.strftime("%d/%m/%Y") if self.check_out else "",
            "numero_dias": self.get_numero_dias(),
            "status": self.status.value,
            "total": float(self.total) if self.total else 0.0,
            "observacoes": self.observacoes or "",
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else "",
        }
