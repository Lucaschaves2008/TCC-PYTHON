import re


def formatar_moeda(valor: float) -> str:
    """R$ 1.250,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_cpf(cpf: str) -> str:
    """00000000000 → 000.000.000-00"""
    digitos = re.sub(r"\D", "", cpf)
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return cpf


def status_quarto_badge(status: str) -> str:
    badges = {
        "disponivel":  "🟢 Disponível",
        "ocupado":     "🔴 Ocupado",
        "manutencao":  "🟡 Manutenção",
    }
    return badges.get(status.lower(), status)


def status_reserva_badge(status: str) -> str:
    badges = {
        "pendente":    "🟡 Pendente",
        "confirmada":  "🟢 Confirmada",
        "checkin":     "🔵 Check-in",
        "checkout":    "⚪ Check-out",
        "cancelada":   "🔴 Cancelada",
    }
    return badges.get(status.lower(), status)


def tipo_quarto_label(tipo: str) -> str:
    labels = {
        "solteiro": "🛏 Solteiro",
        "casal":    "🛏🛏 Casal",
        "luxo":     "⭐ Luxo",
        "suite":    "👑 Suíte",
    }
    return labels.get(tipo.lower(), tipo)
