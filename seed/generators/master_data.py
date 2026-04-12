"""
Master data generators: Empresa, Passageiro, Colaboradores, Frota.
"""

import random
from faker import Faker
from seed.config import (
    COMPANIES,
    DRIVERS,
    VEHICLES,
    PASSENGERS_PER_LARGE_COMPANY,
    PASSENGERS_PER_MEDIUM_COMPANY,
    PASSENGERS_PER_SMALL_COMPANY,
)

fake = Faker("pt_BR")
random.seed(42)
Faker.seed(42)

LARGE_COMPANY_THRESHOLD = 0.09
MEDIUM_COMPANY_THRESHOLD = 0.03

VEHICLE_COLORS = ["Branco", "Prata", "Preto", "Cinza", "Vermelho"]
VEHICLE_MODEL = "Onix Plus"
VEHICLE_YEAR_MIN = 2019
VEHICLE_YEAR_MAX = 2023

PROGRAMMER_ROLES = ["Programador", "Analista de Sistemas", "Desenvolvedor"]
ADMIN_ROLES = ["Administrativo", "Coordenador", "Gerente"]


def _passenger_count_for(ride_share: float) -> int:
    if ride_share >= LARGE_COMPANY_THRESHOLD:
        return PASSENGERS_PER_LARGE_COMPANY
    elif ride_share >= MEDIUM_COMPANY_THRESHOLD:
        return PASSENGERS_PER_MEDIUM_COMPANY
    else:
        return PASSENGERS_PER_SMALL_COMPANY


def generate_empresa() -> list[dict]:
    """Generate Empresa sheet rows, one per company with full rate structure."""
    rows = []
    for name, cfg in COMPANIES.items():
        rows.append({
            "Empresa": name,
            "Participação": cfg["ride_share"],
            "Km Rate (R$)": cfg["km_rate"],
            "HP Rate (R$/h)": cfg["idle_rate"],
            "HP Cortesia (h)": cfg["idle_courtesy_hours"],
            "Taxa NF (%)": cfg["tax_rate"],
            "Adicional Noturno (%)": cfg["night_surcharge"],
            "Adicional Feriado (%)": cfg["holiday_surcharge"],
            "Adicional Domingo (%)": cfg["sunday_surcharge"],
            "Taxa Pedágio": cfg["toll_tax_rate"],
            "Retorno Rate": cfg["return_rate"],
            "Taxa Passagem": cfg["transit_rate"],
            "Status": "Ativo",
        })
    return rows


def generate_passageiro() -> list[dict]:
    """Generate Passageiro sheet rows, passengers distributed across companies."""
    rows = []
    for company, cfg in COMPANIES.items():
        count = _passenger_count_for(cfg["ride_share"])
        # ~80% Ativo, ~20% Autorizado
        ativo_count = int(count * 0.80)
        for i in range(count):
            permission = "Ativo" if i < ativo_count else "Autorizado"
            rows.append({
                "Nome": fake.name(),
                "Empresa": company,
                "Permissão": permission,
                "Email": fake.email(),
                "Telefone": fake.phone_number(),
            })
    return rows


def generate_colaboradores() -> list[dict]:
    """Generate Colaboradores sheet rows, drivers + programmers + admin staff."""
    rows = []

    for name in DRIVERS:
        rows.append({
            "Nome": name,
            "Cargo": "Motorista",
            "Status": "Ativo",
            "CPF": fake.cpf(),
            "Telefone": fake.phone_number(),
        })

    for _ in range(5):
        rows.append({
            "Nome": fake.name(),
            "Cargo": random.choice(PROGRAMMER_ROLES),
            "Status": "Ativo",
            "CPF": fake.cpf(),
            "Telefone": fake.phone_number(),
        })

    for _ in range(3):
        rows.append({
            "Nome": fake.name(),
            "Cargo": random.choice(ADMIN_ROLES),
            "Status": "Ativo",
            "CPF": fake.cpf(),
            "Telefone": fake.phone_number(),
        })

    return rows


def generate_frota() -> list[dict]:
    """Generate Frota sheet rows, one per vehicle, all Onix Plus."""
    rows = []
    for i, plate in enumerate(VEHICLES):
        driver = DRIVERS[i] if i < len(DRIVERS) else None
        rows.append({
            "Placa": plate,
            "Modelo": VEHICLE_MODEL,
            "Ano": random.randint(VEHICLE_YEAR_MIN, VEHICLE_YEAR_MAX),
            "Cor": random.choice(VEHICLE_COLORS),
            "Motorista": driver,
            "Status": "Ativo",
        })
    return rows
