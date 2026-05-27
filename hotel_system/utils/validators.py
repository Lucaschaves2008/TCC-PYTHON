import re
from datetime import date


def validar_cpf(cpf: str) -> bool:
    """Aceita formatos: 000.000.000-00 ou 00000000000"""
    cpf_limpo = re.sub(r"\D", "", cpf)
    if len(cpf_limpo) != 11:
        return False
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    return True


def validar_email(email: str) -> bool:
    padrao = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email.strip()))


def validar_datas_reserva(check_in: date, check_out: date) -> tuple:
    """Retorna (valido: bool, mensagem_erro: str)"""
    if check_out <= check_in:
        return False, "A data de check-out deve ser posterior ao check-in."
    if (check_out - check_in).days > 365:
        return False, "A reserva não pode exceder 365 dias."
    return True, ""


def validar_preco(preco: float) -> bool:
    return preco > 0


def validar_capacidade(capacidade: int) -> bool:
    return 1 <= capacidade <= 20
