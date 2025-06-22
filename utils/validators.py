import re

def validar_cpf(cpf):
    """Valida se o CPF contém apenas números"""
    return cpf.isdigit() and len(cpf) == 11

def validar_email(email):
    """Valida se o email tem formato correto"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_matricula(matricula):
    """Valida se a matrícula contém apenas números"""
    return matricula.isdigit() if matricula else True