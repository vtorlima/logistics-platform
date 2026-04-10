# All company names here are made up and don’t represent real businesses,
# the values and constants are also arbitrary, just chosen to be close to real-life scenarios.

COMPANIES = {
    "Aço Forte Siderurgia": {
        "ride_share": 0.72,
        "km_rate": 4.50,
        "idle_rate": 85.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.00,
        "night_surcharge": 0.20,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "TransQuímica Martins": {
        "ride_share": 0.10,
        "km_rate": 4.80,
        "idle_rate": 90.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.05,
        "night_surcharge": 0.25,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Construtora Pilar": {
        "ride_share": 0.09,
        "km_rate": 4.20,
        "idle_rate": 80.00,
        "idle_courtesy_hours": 0.75,
        "tax_rate": 0.03,
        "night_surcharge": 0.20,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Gastech Serviços": {
        "ride_share": 0.05,
        "km_rate": 5.00,
        "idle_rate": 95.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.04,
        "night_surcharge": 0.25,
        "holiday_surcharge": 0.60,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Manutenção Global": {
        "ride_share": 0.02,
        "km_rate": 4.60,
        "idle_rate": 85.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.00,
        "night_surcharge": 0.20,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Logística Rápida": {
        "ride_share": 0.01,
        "km_rate": 4.40,
        "idle_rate": 80.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.02,
        "night_surcharge": 0.20,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Avulso": {
        "ride_share": 0.005,
        "km_rate": 5.50,
        "idle_rate": 100.00,
        "idle_courtesy_hours": 0.0,
        "tax_rate": 0.00,
        "night_surcharge": 0.30,
        "holiday_surcharge": 0.60,
        "sunday_surcharge": 0.60,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
    "Petro Engenharia": {
        "ride_share": 0.005,
        "km_rate": 5.20,
        "idle_rate": 90.00,
        "idle_courtesy_hours": 0.5,
        "tax_rate": 0.05,
        "night_surcharge": 0.25,
        "holiday_surcharge": 0.50,
        "sunday_surcharge": 0.50,
        "transit_rate": 0.0,
        "return_rate": 0.0,
        "toll_tax_rate": 0.0,
    },
}
# DRIVERS (Motoristas) - Generic and fictional brazilian names 

DRIVERS = [
    "João Silva",
    "Maria Santos",
    "Carlos Oliveira",
    "Ana Costa",
    "Pedro Ferreira",
    "Francisca Martins",
    "Antonio Rodrigues",
    "Joana Pereira",
    "Ricardo Sousa",
    "Lucia Alves",
    "Fernando Dias",
    "Rosana Monteiro",
    "Sergio Cardoso",
    "Gisele Barros",
    "Gabriel Mendes",
    "Vanessa Silva",
    "Thiago Gomes",
    "Camila Neves",
    "Leonardo Rocha",
    "Isabella Castro",
    "Mateus Barbosa",
    "Mariana Duarte",
    "Henrique Faria",
    "Beatriz Ribeiro",
    "Lucas Paiva",
]

# VEHICLES (Frota) - 26 fictional Mercosul format plates

VEHICLES = [
    "ABC1D23",
    "DEF2G45",
    "GHI3J67",
    "JKL4M89",
    "MNO5P01",
    "PQR6S23",
    "STU7V45",
    "VWX8Y67",
    "YZA9B89",
    "BCD0C01",
    "CDE1D23",
    "EFG2F45",
    "GHI3H67",
    "IJK4J89",
    "KLM5L01",
    "MNO6N23",
    "OPQ7P45",
    "QRS8R67",
    "STU9T89",
    "UVW0V01",
    "VWX1X23",
    "WXY2Y45",
    "XYZ3Z67",
    "YZA4A89",
    "ZAB5B01",
    "ABC6C23",
]
# ROUTES - 28 routes mixing municipal and intercity

ROUTES = [
    # Municipal (Cubatão neighborhoods)
    {"origin": "Centro", "destination": "Vila Parisi", "km": 5, "type": "MUNIC"},
    {"origin": "Centro", "destination": "Jardim Independência", "km": 8, "type": "MUNIC"},
    {"origin": "Centro", "destination": "Vila Propício", "km": 6, "type": "MUNIC"},
    {"origin": "Vila Parisi", "destination": "Jardim Independência", "km": 4, "type": "MUNIC"},
    {"origin": "Vila Parisi", "destination": "Calcário", "km": 7, "type": "MUNIC"},
    {"origin": "Vila Parisi", "destination": "Chico de Assis", "km": 9, "type": "MUNIC"},
    {"origin": "Jardim Independência", "destination": "Vila Propício", "km": 5, "type": "MUNIC"},
    {"origin": "Jardim Independência", "destination": "Calcário", "km": 6, "type": "MUNIC"},
    {"origin": "Calcário", "destination": "Chico de Assis", "km": 3, "type": "MUNIC"},
    {"origin": "Chico de Assis", "destination": "Vila Propício", "km": 10, "type": "MUNIC"},
    {"origin": "Centro", "destination": "Calcário", "km": 11, "type": "MUNIC"},
    {"origin": "Centro", "destination": "Chico de Assis", "km": 14, "type": "MUNIC"},
    # Intercity (to nearby cities)
    {"origin": "Centro", "destination": "Santos - Centro", "km": 25, "type": "INTER"},
    {"origin": "Centro", "destination": "Santos - Praia", "km": 28, "type": "INTER"},
    {"origin": "Centro", "destination": "São Vicente", "km": 20, "type": "INTER"},
    {"origin": "Centro", "destination": "Praia Grande", "km": 35, "type": "INTER"},
    {"origin": "Centro", "destination": "Guarujá", "km": 40, "type": "INTER"},
    {"origin": "Vila Parisi", "destination": "Santos - Centro", "km": 27, "type": "INTER"},
    {"origin": "Vila Parisi", "destination": "São Vicente", "km": 22, "type": "INTER"},
    {"origin": "Jardim Independência", "destination": "Santos - Praia", "km": 30, "type": "INTER"},
    {"origin": "Jardim Independência", "destination": "Praia Grande", "km": 37, "type": "INTER"},
    {"origin": "Calcário", "destination": "São Vicente", "km": 23, "type": "INTER"},
    {"origin": "Calcário", "destination": "Guarujá", "km": 42, "type": "INTER"},
    {"origin": "Chico de Assis", "destination": "Santos - Centro", "km": 28, "type": "INTER"},
    {"origin": "Chico de Assis", "destination": "Praia Grande", "km": 38, "type": "INTER"},
    {"origin": "Vila Propício", "destination": "Santos - Centro", "km": 26, "type": "INTER"},
    {"origin": "Vila Propício", "destination": "São Vicente", "km": 21, "type": "INTER"},
    {"origin": "Vila Propício", "destination": "Guarujá", "km": 41, "type": "INTER"},
]

# LOCATIONS - Real Baixada Santista neighborhoods (public geographic data)

LOCATIONS = [
    "Centro",
    "Vila Parisi",
    "Jardim Independência",
    "Vila Propício",
    "Calcário",
    "Chico de Assis",
    "Bairro Fabril",
    "Vila São Paulo",
    "Vila Santa Rosa",
    "Conceição",
    "Santos - Centro",
    "Santos - Praia",
    "São Vicente",
    "Praia Grande",
    "Guarujá",
]

# SERVICE TYPES

SERVICE_TYPES = [
    "Transporte Executivo",
    "Transporte de Funcionários",
    "Serviço Sob Demanda",
    "Translado",
    "Transfer",
]

# TRIP TYPES

TRIP_TYPES = [
    "Ida",
    "Volta",
    "Ida e Volta",
]

# CHANNELS

CHANNELS = [
    "Email",
    "Whatsapp",
    "Telefone",
]

# MONTHS TO GENERATE

MONTHS = ["2026-01", "2026-02", "2026-03"]

# GENERATION PARAMETERS

RIDES_PER_MONTH = 2400
PASSENGERS_PER_LARGE_COMPANY = 200
PASSENGERS_PER_MEDIUM_COMPANY = 50
PASSENGERS_PER_SMALL_COMPANY = 10

# Ride distribution percentages
IDLE_TIME_PERCENTAGE = 0.15  
NIGHT_RIDE_PERCENTAGE = 0.25  
HOLIDAY_RIDE_PERCENTAGE = 0.03  
SUNDAY_RIDE_PERCENTAGE = 0.14  
RETURN_TRIP_PERCENTAGE = 0.05  

# Time patterns
MORNING_PEAK_START = 5  
MORNING_PEAK_END = 8  
EVENING_PEAK_START = 16  
EVENING_PEAK_END = 19  

# KM ranges
KM_LOADED_MIN = 10
KM_LOADED_MAX = 80
KM_EMPTY_RATIO_MIN = 0.30
KM_EMPTY_RATIO_MAX = 0.60

# Passengers
PASSENGERS_MIN = 1
PASSENGERS_MAX = 4
PASSENGERS_AVG = 1.5

# OS number sequence start
OS_NUMBER_START = 280000
