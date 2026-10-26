
# ============================================================
# PROGETTO DATA ANALYSIS - BRESAOLIFICIO
# Dataset sintetico 2024-2025
# Parte 1 di 4: configurazione e anagrafiche
# ============================================================

from pathlib import Path
import json
import numpy as np
import pandas as pd
from faker import Faker

# ------------------------------------------------------------
# 1. CONFIGURAZIONE GENERALE
# ------------------------------------------------------------

SEED = 20261017
START = pd.Timestamp("2024-01-01")
END = pd.Timestamp("2025-12-31")

OUT = Path("data")
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

N_CLIENTS = 1200


def save(df, name):
    """Salva un DataFrame in CSV nella cartella data."""
    df.to_csv(
        OUT / f"{name}.csv",
        index=False,
        date_format="%Y-%m-%d"
    )


def weighted_choice(values, weights, size=None):
    """Estrae valori usando probabilita' ponderate."""
    p = np.asarray(weights, dtype=float)
    p = p / p.sum()
    return rng.choice(values, size=size, p=p)


def date_string(value):
    """Converte una data nel formato ISO."""
    return pd.Timestamp(value).strftime("%Y-%m-%d")


# ------------------------------------------------------------
# 2. ANAGRAFICA PRODOTTI
# ------------------------------------------------------------

products = pd.DataFrame([
    ("SKU001", "Punta d'anca", "Intera", 2.00, 34.00, 19.00, 0.83),
    ("SKU002", "Punta d'anca", "Trancio 1kg", 1.00, 37.00, 21.00, 0.83),
    ("SKU003", "Punta d'anca", "Affettata 90g", 0.09, 2.20, 1.15, 0.82),
    ("SKU004", "Punta d'anca", "Affettata 100g", 0.10, 2.40, 1.22, 0.82),
    ("SKU005", "Fesa", "Intera", 2.50, 32.00, 18.50, 0.84),
    ("SKU006", "Fesa", "Trancio 500g", 0.50, 18.00, 10.00, 0.83),
    ("SKU007", "Fesa", "Affettata 90g", 0.09, 2.00, 1.05, 0.82),
    ("SKU008", "Fesa", "Affettata 100g", 0.10, 2.20, 1.12, 0.82),
    ("SKU009", "Magatello", "Intero", 1.00, 30.00, 17.00, 0.85),
    ("SKU010", "Magatello", "Trancio 500g", 0.50, 16.00, 8.80, 0.84),
    ("SKU011", "Magatello", "Affettata 90g", 0.09, 1.80, 0.92, 0.82),
    ("SKU012", "Magatello", "Affettata 100g", 0.10, 2.00, 1.00, 0.82),
    ("SKU013", "Sottofesa", "Intera", 1.80, 28.00, 16.00, 0.84),
    ("SKU014", "Sottofesa", "Trancio 1kg", 1.00, 31.00, 17.50, 0.83),
    ("SKU015", "Sottofesa", "Affettata 90g", 0.09, 1.75, 0.90, 0.81),
    ("SKU016", "Sottofesa", "Affettata 100g", 0.10, 1.95, 0.98, 0.81),
    ("SKU017", "Punta d'anca", "Cubetti 100g", 0.10, 2.30, 1.20, 0.81),
    ("SKU018", "Fesa", "Julienne 100g", 0.10, 2.15, 1.10, 0.81),
    ("SKU019", "Magatello", "Petali 80g", 0.08, 1.65, 0.82, 0.80),
    ("SKU020", "Sottofesa", "Cubetti 100g", 0.10, 1.85, 0.94, 0.80),
    ("SKU021", "Punta d'anca", "Food service 500g", 0.50, 15.00, 8.00, 0.82),
    ("SKU022", "Fesa", "Food service 1kg", 1.00, 29.00, 16.00, 0.83),
    ("SKU023", "Magatello", "Food service 1kg", 1.00, 27.00, 14.50, 0.84),
    ("SKU024", "Sottofesa", "Food service 500g", 0.50, 13.50, 7.20, 0.81),
], columns=[
    "sku",
    "famiglia",
    "formato",
    "kg_per_unita",
    "prezzo_listino",
    "costo_standard_unitario",
    "resa_target"
])

# Vita commerciale simulata in base al formato.
products["shelf_life_days"] = np.where(
    products["formato"].str.contains(
        "Affettata|Cubetti|Julienne|Petali",
        case=False,
        regex=True
    ),
    75,
    150
)

# Durata indicativa della fase di stagionatura.
products["lead_stagionatura_days"] = rng.integers(
    35,
    56,
    size=len(products)
)

products["attivo"] = True

save(products, "dim_prodotti")

# Dizionario di supporto per le simulazioni successive.
product_lookup = products.set_index("sku").to_dict("index")
sku_ids = products["sku"].to_numpy()



# ------------------------------------------------------------
# 3. ANAGRAFICA CLIENTI: 1.200 CLIENTI CON FAKER
# ------------------------------------------------------------
# Faker genera i campi descrittivi.
# NumPy mantiene la simulazione quantitativa.
# Le localita' sono predefinite per mantenere coerenza
# tra citta', provincia, CAP e regione.
#
# Gli ID cliente restano invariati.
# Le email usano example.com, dominio riservato agli esempi.

fake_it = Faker("it_IT")
fake_it.seed_instance(SEED + 1)

channels = [
    "GDO",
    "Grossista",
    "HoReCa",
    "Industria",
    "Retail"
]

# Regione, provincia, citta', CAP rappresentativo, peso.
# I CAP sono valori indicativi per la localita', non verificano
# l'indirizzo specifico generato.
locations = [
    ("Lombardia", "MI", "Milano", "20121", 0.17),
    ("Lombardia", "BG", "Bergamo", "24121", 0.08),
    ("Lombardia", "BS", "Brescia", "25121", 0.08),
    ("Lombardia", "CO", "Como", "22100", 0.05),
    ("Piemonte", "TO", "Torino", "10121", 0.09),
    ("Veneto", "VR", "Verona", "37121", 0.08),
    ("Veneto", "PD", "Padova", "35121", 0.06),
    ("Emilia-Romagna", "BO", "Bologna", "40121", 0.08),
    ("Emilia-Romagna", "PR", "Parma", "43121", 0.04),
    ("Liguria", "GE", "Genova", "16121", 0.04),
    ("Toscana", "FI", "Firenze", "50121", 0.05),
    ("Lazio", "RM", "Roma", "00118", 0.08),
    ("Campania", "NA", "Napoli", "80121", 0.04),
    ("Trentino-Alto Adige", "TN", "Trento", "38121", 0.03),
    ("Estero", "EE", "Cliente estero", "", 0.03)
]

location_weights = np.array(
    [item[4] for item in locations],
    dtype=float
)
location_weights /= location_weights.sum()

selected_locations = rng.choice(
    len(locations),
    size=N_CLIENTS,
    p=location_weights
)

client_ids_generated = [
    f"C{i:04d}"
    for i in range(1, N_CLIENTS + 1)
]

# Generazione dei dati descrittivi con Faker.
company_names = [
    fake_it.company()
    for _ in range(N_CLIENTS)
]

first_names = [
    fake_it.first_name()
    for _ in range(N_CLIENTS)
]

last_names = [
    fake_it.last_name()
    for _ in range(N_CLIENTS)
]

addresses = [
    fake_it.street_address()
    for _ in range(N_CLIENTS)
]

# Evita ragioni sociali duplicate senza modificare gli ID.
seen_companies = set()
unique_company_names = []

for company, client_id in zip(
    company_names,
    client_ids_generated
):
    candidate = company
    suffix = 2

    while candidate.casefold() in seen_companies:
        candidate = f"{company} {suffix}"
        suffix += 1

    seen_companies.add(candidate.casefold())
    unique_company_names.append(candidate)

# Costruzione dell'anagrafica.
clients = pd.DataFrame({
    "cliente_id": client_ids_generated,

    "ragione_sociale": unique_company_names,

    "referente_nome": first_names,

    "referente_cognome": last_names,

    "canale": weighted_choice(
        channels,
        [0.22, 0.28, 0.27, 0.08, 0.15],
        N_CLIENTS
    ),

    "regione": [
        locations[i][0]
        for i in selected_locations
    ],

    "provincia": [
        locations[i][1]
        for i in selected_locations
    ],

    "citta": [
        locations[i][2]
        for i in selected_locations
    ],

    "cap": [
        locations[i][3]
        for i in selected_locations
    ],

    "indirizzo": addresses,

    "email": [
        f"cliente.{client_id.lower()}@example.com"
        for client_id in client_ids_generated
    ],

    "data_acquisizione": pd.to_datetime(
        rng.choice(
            pd.date_range("2019-01-01", END),
            size=N_CLIENTS
        )
    ),

    "classe_commerciale": weighted_choice(
        ["A", "B", "C"],
        [0.12, 0.28, 0.60],
        N_CLIENTS
    ),

    "termine_pagamento_giorni": rng.choice(
        [30, 45, 60, 90],
        size=N_CLIENTS,
        p=[0.30, 0.35, 0.25, 0.10]
    ),

    "costo_consegna_standard": np.round(
        rng.uniform(15, 120, N_CLIENTS),
        2
    )
})

clients["attivo"] = True

# Referente completo, utile nelle tabelle Power BI.
clients["referente"] = (
    clients["referente_nome"]
    + " "
    + clients["referente_cognome"]
)

# Controllo di unicita' e completezza.
assert len(clients) == N_CLIENTS
assert clients["cliente_id"].is_unique
assert clients["ragione_sociale"].is_unique
assert clients["email"].is_unique
assert clients["regione"].notna().all()

save(clients, "dim_clienti")

client_lookup = clients.set_index(
    "cliente_id"
).to_dict("index")

client_ids = clients["cliente_id"].to_numpy()

# ------------------------------------------------------------
# FINE ANAGRAFICA CLIENTI
# ------------------------------------------------------------



# ------------------------------------------------------------
# 4. LINEE PRODUTTIVE
# ------------------------------------------------------------

lines = pd.DataFrame({
    "linea_id": ["L1", "L2", "L3", "L4"],

    "reparto": [
        "Affettamento",
        "Affettamento",
        "Confezionamento",
        "Confezionamento"
    ],

    "capacita_kg_ora": [
        220,
        240,
        200,
        230
    ],

    "target_oee": [
        0.78,
        0.80,
        0.79,
        0.81
    ]
})

save(lines, "dim_linee")


# ------------------------------------------------------------
# 5. DIMENSIONE CALENDARIO
# ------------------------------------------------------------

calendar = pd.DataFrame({
    "data": pd.date_range(
        START,
        END,
        freq="D"
    )
})

calendar["anno"] = calendar["data"].dt.year
calendar["mese"] = calendar["data"].dt.month
calendar["nome_mese"] = calendar["data"].dt.month_name()
calendar["trimestre"] = calendar["data"].dt.quarter

calendar["settimana"] = (
    calendar["data"]
    .dt.isocalendar()
    .week
    .astype(int)
)

calendar["giorno_mese"] = calendar["data"].dt.day
calendar["giorno_settimana"] = calendar["data"].dt.dayofweek

calendar["giorno_lavorativo"] = (
    calendar["giorno_settimana"] < 5
)

calendar["weekend"] = (
    calendar["giorno_settimana"] >= 5
)

save(calendar, "dim_calendario")


# ============================================================
# FINE PARTE 1
# La Parte 2 continuera' con la produzione e i lotti.
# Non eseguire ancora il file.
# ============================================================


# ============================================================
# PARTE 2 DI 4
# PRODUZIONE, LOTTI E VENDITE
# ============================================================

# ------------------------------------------------------------
# 6. GENERAZIONE DELLA PRODUZIONE E DEI LOTTI
# ------------------------------------------------------------

production_dates = pd.date_range(
    "2023-11-01",
    END,
    freq="3D"
)

production_records = []
lot_number = 1

for date in production_dates:
    for sku in sku_ids:
        p = product_lookup[sku]

        # Volume produttivo simulato per lotto.
        base_input = rng.uniform(300, 650)

        if "Affettata" in p["formato"]:
            base_input *= 1.15

        line = rng.choice(["L1", "L2", "L3", "L4"])
        target = float(p["resa_target"])

        # Anomalia latente:
        # la linea L3 ha una resa inferiore su due famiglie.
        penalty = 0.0

        if (
            line == "L3"
            and p["famiglia"] in ["Fesa", "Sottofesa"]
        ):
            penalty = 0.035

        shift = rng.choice(
            ["Mattina", "Pomeriggio", "Notte"],
            p=[0.48, 0.42, 0.10]
        )

        shift_penalty = 0.012 if shift == "Notte" else 0.0
        noise = rng.normal(0, 0.012)

        yield_rate = float(np.clip(
            target - penalty - shift_penalty + noise,
            0.70,
            0.90
        ))

        input_kg = round(float(base_input), 2)
        output_kg = round(input_kg * yield_rate, 2)
        scrap_kg = round(input_kg - output_kg, 2)

        maturation_days = int(
            p["lead_stagionatura_days"]
        )

        release_date = date + pd.Timedelta(
            days=maturation_days
        )

        expiry_date = release_date + pd.Timedelta(
            days=int(p["shelf_life_days"])
        )

        production_records.append({
            "lotto_id": f"LOT{lot_number:06d}",
            "data_produzione": date,
            "data_disponibilita": release_date,
            "data_scadenza": expiry_date,
            "sku": sku,
            "linea_id": line,
            "turno": shift,
            "kg_input": input_kg,
            "kg_output_conforme": output_kg,
            "kg_scarto": scrap_kg,
            "resa_effettiva": round(yield_rate, 5),
            "durata_stagionatura_giorni": maturation_days,
            "costo_materia_prima_kg": round(
                rng.uniform(8.0, 13.5), 2
            ),
            "costo_lavorazione_lotto": round(
                rng.uniform(80, 240), 2
            )
        })

        lot_number += 1

production = pd.DataFrame(production_records)

production["data_produzione"] = pd.to_datetime(
    production["data_produzione"]
)

production["data_disponibilita"] = pd.to_datetime(
    production["data_disponibilita"]
)

production["data_scadenza"] = pd.to_datetime(
    production["data_scadenza"]
)

save(production, "fact_produzione")


# ------------------------------------------------------------
# 7. PREPARAZIONE DEI LOTTI PER L'ALLOCAZIONE FIFO
# ------------------------------------------------------------
# FIFO = si utilizza prima il lotto disponibile da più tempo.
# La disponibilità decorre dalla fine della stagionatura.
# I lotti scaduti non potranno essere assegnati alle vendite.

lots_by_sku = {}

production_fifo = production.sort_values(
    [
        "data_disponibilita",
        "data_scadenza",
        "lotto_id"
    ]
)

for sku, group in production_fifo.groupby("sku"):
    lots_by_sku[sku] = [
        {
            "lotto_id": row.lotto_id,
            "available_date": row.data_disponibilita,
            "expiry": row.data_scadenza,
            "remaining": float(row.kg_output_conforme)
        }
        for row in group.itertuples()
    ]


# ------------------------------------------------------------
# 8. GENERAZIONE DEGLI ORDINI COMMERCIALI
# ------------------------------------------------------------

sku_weights = np.array([
    1.4 if "Affettata" in product_lookup[sku]["formato"]
    else 0.75
    for sku in sku_ids
], dtype=float)

sku_weights /= sku_weights.sum()

order_records = []
order_number = 1
line_number = 1

for date in pd.date_range(START, END, freq="D"):

    # Stagionalità commerciale.
    month_factor = (
        1.25 if date.month in [10, 11, 12] else 1.0
    )

    if date.month in [3, 4, 5]:
        month_factor *= 1.12

    # Ordini meno frequenti nel fine settimana.
    weekday_factor = (
        1.0 if date.dayofweek < 5 else 0.18
    )

    n_orders = rng.poisson(
        27 * month_factor * weekday_factor
    )

    for _ in range(n_orders):

        client = rng.choice(client_ids)
        client_data = client_lookup[client]

        channel = client_data["canale"]
        client_class = client_data["classe_commerciale"]

        n_lines = int(rng.choice(
            [1, 2, 3, 4, 5],
            p=[0.16, 0.30, 0.29, 0.17, 0.08]
        ))

        selected_skus = rng.choice(
            sku_ids,
            size=min(n_lines, len(sku_ids)),
            replace=False,
            p=sku_weights
        )

        order_id = f"ORD{order_number:07d}"
        order_number += 1

        for sku in selected_skus:

            p = product_lookup[sku]

            # Quantità ordinate in unità commerciali.
            units = int(rng.integers(10, 90))

            kg_ordered = round(
                units * float(p["kg_per_unita"]),
                3
            )

            # Politica sconti simulata per classe e canale.
            discount = rng.uniform(0.02, 0.10)

            if client_class == "A":
                discount += 0.04

            if channel == "GDO":
                discount += 0.025

            discount = float(np.clip(
                discount,
                0,
                0.25
            ))

            unit_price = round(
                float(p["prezzo_listino"]) * (1 - discount),
                2
            )

            # Resi registrati separatamente dalla spedizione.
            return_rate = 0.012

            if channel == "GDO":
                return_rate += 0.012

            returned_units = int(rng.binomial(
                units,
                min(return_rate, 0.08)
            ))

            requested_date = date + pd.Timedelta(
                days=int(rng.integers(1, 5))
            )

            # Ritardi realistici, con una piccola quota anomala.
            delay = int(rng.choice(
                [0, 1, 2, 3, 5],
                p=[0.70, 0.14, 0.09, 0.05, 0.02]
            ))

            delivered_date = requested_date + pd.Timedelta(
                days=delay
            )

            if rng.random() < 0.025:
                delivered_date += pd.Timedelta(
                    days=int(rng.integers(3, 8))
                )

            order_records.append({
                "riga_ordine_id": f"R{line_number:08d}",
                "ordine_id": order_id,
                "data_ordine": date,
                "data_richiesta": requested_date,
                "data_consegna": delivered_date,
                "cliente_id": client,
                "sku": sku,
                "unita_ordinate": units,
                "unita_reso": returned_units,
                "kg_ordinati": kg_ordered,
                "kg_resi": round(
                    returned_units * float(p["kg_per_unita"]),
                    3
                ),
                "prezzo_unitario_netto": unit_price,
                "sconto_pct": round(discount, 4),
                "costo_consegna": float(
                    client_data["costo_consegna_standard"]
                ),
                "stato": "Consegnato"
            })

            line_number += 1


# ------------------------------------------------------------
# 9. DATAFRAME DELLE VENDITE
# ------------------------------------------------------------

sales = pd.DataFrame(order_records)

if sales.empty:
    raise RuntimeError(
        "Nessuna vendita generata. Verificare la configurazione."
    )

sales["data_ordine"] = pd.to_datetime(
    sales["data_ordine"]
)

sales["data_richiesta"] = pd.to_datetime(
    sales["data_richiesta"]
)

sales["data_consegna"] = pd.to_datetime(
    sales["data_consegna"]
)

# Ordinamento cronologico per la successiva allocazione FIFO.
sales = sales.sort_values(
    [
        "data_consegna",
        "riga_ordine_id"
    ]
).reset_index(drop=True)


# ============================================================
# FINE PARTE 2
# La Parte 3 continuera' con l'allocazione ai lotti,
# i movimenti di magazzino, la qualita' e il forecast.
# Non eseguire ancora il file.
# ============================================================


# ============================================================
# PARTE 3 DI 4
# ALLOCAZIONE FIFO, MAGAZZINO, QUALITA' E FORECAST
# ============================================================

# ------------------------------------------------------------
# 10. ALLOCAZIONE FIFO DELLE VENDITE AI LOTTI
# ------------------------------------------------------------
# Regole:
# - Il lotto deve essere disponibile alla data di consegna.
# - Il lotto non deve essere scaduto alla data di consegna.
# - Si prelevano prima i lotti con disponibilita' piu' vecchia.
# - La quantita' evasa non puo' superare quella ordinata.
# - La merce non disponibile resta non evasa.
# - I resi non vengono automaticamente reinseriti a magazzino.

allocations = []
unfulfilled = []
movement_issues = []

allocation_number = 1
movement_issue_number = 1

for row in sales.itertuples():

    remaining = float(row.kg_ordinati)
    ship_date = row.data_consegna

    candidates = lots_by_sku[row.sku]

    for lot in candidates:

        if remaining <= 0.001:
            break

        if lot["available_date"] > ship_date:
            continue

        if lot["expiry"] < ship_date:
            continue

        if lot["remaining"] <= 0.001:
            continue

        qty = min(remaining, lot["remaining"])
        qty = round(qty, 3)

        lot["remaining"] = round(
            lot["remaining"] - qty,
            3
        )

        remaining = round(
            remaining - qty,
            3
        )

        allocations.append({
            "allocazione_id": f"AL{allocation_number:09d}",
            "riga_ordine_id": row.riga_ordine_id,
            "lotto_id": lot["lotto_id"],
            "data_movimento": ship_date,
            "sku": row.sku,
            "kg": qty
        })

        movement_issues.append({
            "movimento_id": f"MOV{movement_issue_number:09d}",
            "data_movimento": ship_date,
            "tipo_movimento": "Uscita vendita",
            "lotto_id": lot["lotto_id"],
            "sku": row.sku,
            "kg_delta": -qty,
            "riga_ordine_id": row.riga_ordine_id
        })

        allocation_number += 1
        movement_issue_number += 1

    if remaining > 0.001:

        unfulfilled.append({
            "riga_ordine_id": row.riga_ordine_id,
            "sku": row.sku,
            "kg_non_evaso": round(remaining, 3)
        })


# ------------------------------------------------------------
# 11. BRIDGE TRA VENDITE E LOTTI
# ------------------------------------------------------------

sales_alloc = pd.DataFrame(allocations)

if sales_alloc.empty:
    sales_alloc = pd.DataFrame(columns=[
        "allocazione_id",
        "riga_ordine_id",
        "lotto_id",
        "data_movimento",
        "sku",
        "kg"
    ])

save(
    sales_alloc,
    "bridge_vendite_lotti"
)

unfulfilled_df = pd.DataFrame(unfulfilled)

if unfulfilled_df.empty:
    unfulfilled_df = pd.DataFrame(columns=[
        "riga_ordine_id",
        "sku",
        "kg_non_evaso"
    ])

save(
    unfulfilled_df,
    "fact_ordini_non_evasi"
)


# ------------------------------------------------------------
# 12. RICONCILIAZIONE DELLE QUANTITA' EVASE
# ------------------------------------------------------------

allocated = (
    sales_alloc
    .groupby("riga_ordine_id", as_index=False)["kg"]
    .sum()
    .rename(columns={"kg": "kg_evaso"})
)

sales = sales.merge(
    allocated,
    on="riga_ordine_id",
    how="left",
    validate="one_to_one"
)

sales["kg_evaso"] = (
    sales["kg_evaso"]
    .fillna(0)
    .round(3)
)

sales["kg_non_evaso"] = (
    sales["kg_ordinati"] - sales["kg_evaso"]
).clip(lower=0).round(3)

sales["percentuale_evasione"] = np.where(
    sales["kg_ordinati"] > 0,
    sales["kg_evaso"] / sales["kg_ordinati"],
    0
).clip(0, 1).round(4)


# ------------------------------------------------------------
# 13. MOVIMENTI DI MAGAZZINO
# ------------------------------------------------------------
# Entrate: prodotto conforme alla data di disponibilita'.
# Uscite: quantita' realmente assegnate ai lotti.
# I kg_delta positivi aumentano la giacenza.
# I kg_delta negativi riducono la giacenza.

receipts = production[[
    "lotto_id",
    "sku",
    "data_disponibilita",
    "kg_output_conforme"
]].copy()

receipts = receipts.rename(columns={
    "data_disponibilita": "data_movimento",
    "kg_output_conforme": "kg_delta"
})

receipts["tipo_movimento"] = "Entrata produzione"
receipts["riga_ordine_id"] = None

receipts["movimento_id"] = [
    f"MR{i:09d}"
    for i in range(1, len(receipts) + 1)
]

issues = pd.DataFrame(movement_issues)

if issues.empty:
    issues = pd.DataFrame(columns=[
        "movimento_id",
        "data_movimento",
        "tipo_movimento",
        "lotto_id",
        "sku",
        "kg_delta",
        "riga_ordine_id"
    ])

movements = pd.concat(
    [receipts, issues],
    ignore_index=True
)

movements["data_movimento"] = pd.to_datetime(
    movements["data_movimento"]
)

movements["kg_delta"] = pd.to_numeric(
    movements["kg_delta"]
)

movements = movements.sort_values(
    [
        "data_movimento",
        "movimento_id"
    ]
).reset_index(drop=True)

save(
    movements,
    "fact_movimenti_magazzino"
)



# ------------------------------------------------------------
# 14. GIACENZA CUMULATIVA PER LOTTO - VERSIONE CORRETTA
# ------------------------------------------------------------
# Regola: in caso di movimenti nello stesso giorno, le entrate
# devono essere contabilizzate prima delle uscite.
#
# La priorita' e' applicata separatamente per ogni lotto.
# Questo evita falsi negativi causati dall'ordinamento degli ID.

stock_daily = movements.copy()

stock_daily["data_movimento"] = pd.to_datetime(
    stock_daily["data_movimento"]
)

stock_daily["_priorita_movimento"] = np.where(
    stock_daily["tipo_movimento"].eq("Entrata produzione"),
    0,
    1
)

stock_daily = stock_daily.sort_values(
    [
        "lotto_id",
        "data_movimento",
        "_priorita_movimento",
        "movimento_id"
    ],
    kind="mergesort"
).reset_index(drop=True)

stock_daily["giacenza_cumulata_kg"] = (
    stock_daily
    .groupby("lotto_id")["kg_delta"]
    .cumsum()
).round(3)

stock_daily = stock_daily.drop(
    columns=["_priorita_movimento"]
)

save(
    stock_daily,
    "fact_stock_movimenti"
)



# ------------------------------------------------------------
# 15. SIMULAZIONE DEI FERMI PRODUTTIVI
# ------------------------------------------------------------

downtime_records = []

for row in production.itertuples():

    probability = (
        0.32 if row.linea_id == "L3"
        else 0.22
    )

    if rng.random() < probability:

        reason = weighted_choice(
            [
                "Cambio formato",
                "Guasto",
                "Pulizia",
                "Attesa materiale",
                "Microfermata"
            ],
            [0.34, 0.17, 0.20, 0.13, 0.16]
        )

        duration = int(
            rng.gamma(2.0, 18.0)
        )

        downtime_records.append({
            "fermo_id": (
                f"FER{len(downtime_records) + 1:07d}"
            ),
            "data": row.data_produzione,
            "linea_id": row.linea_id,
            "lotto_id": row.lotto_id,
            "sku": row.sku,
            "causale": reason,
            "durata_minuti": duration
        })

downtime = pd.DataFrame(downtime_records)

if downtime.empty:
    downtime = pd.DataFrame(columns=[
        "fermo_id",
        "data",
        "linea_id",
        "lotto_id",
        "sku",
        "causale",
        "durata_minuti"
    ])

save(
    downtime,
    "fact_fermi"
)


# ------------------------------------------------------------
# 16. SIMULAZIONE DEI CONTROLLI QUALITA'
# ------------------------------------------------------------

quality_records = []

for row in production.itertuples():

    # Non tutti i lotti vengono sottoposti a questo controllo.
    if rng.random() >= 0.88:
        continue

    probability = 0.035

    # Rischio simulato maggiore sulla linea L3.
    if row.linea_id == "L3":
        probability += 0.025

    if row.turno == "Notte":
        probability += 0.012

    defect = rng.random() < probability

    if defect:

        cause = weighted_choice(
            [
                "Difetto confezione",
                "Peso fuori tolleranza",
                "Difetto visivo",
                "Tenuta vuoto"
            ],
            [0.32, 0.24, 0.20, 0.24]
        )

        outcome = "Non conforme"

    else:
        cause = "Nessuna"
        outcome = "Conforme"

    quality_records.append({
        "controllo_id": (
            f"QC{len(quality_records) + 1:08d}"
        ),
        "data_controllo": row.data_disponibilita,
        "lotto_id": row.lotto_id,
        "sku": row.sku,
        "linea_id": row.linea_id,
        "controllo_eseguito": True,
        "esito": outcome,
        "causale": cause
    })

quality = pd.DataFrame(quality_records)

if quality.empty:
    quality = pd.DataFrame(columns=[
        "controllo_id",
        "data_controllo",
        "lotto_id",
        "sku",
        "linea_id",
        "controllo_eseguito",
        "esito",
        "causale"
    ])

save(
    quality,
    "fact_qualita"
)


# ------------------------------------------------------------
# 17. FORECAST MENSILE PER SKU
# ------------------------------------------------------------
# Il forecast e' generato separatamente dalla domanda effettiva.
# Questo consente di misurare gli errori di previsione.
# I valori sono sintetici e non derivano da un modello addestrato.

sales["mese"] = (
    sales["data_ordine"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

actual = (
    sales
    .groupby(["mese", "sku"], as_index=False)["kg_ordinati"]
    .sum()
    .rename(columns={
        "kg_ordinati": "kg_domanda_effettiva"
    })
)

forecast_records = []

for sku in sku_ids:

    baseline = float(
        rng.uniform(2500, 7000)
    )

    for month in pd.date_range(
        "2024-01-01",
        "2025-12-01",
        freq="MS"
    ):

        seasonal = (
            1.20 if month.month in [10, 11, 12]
            else 1.0
        )

        if month.month in [3, 4, 5]:
            seasonal *= 1.08

        forecast_value = max(
            0,
            baseline
            * seasonal
            * rng.normal(1, 0.12)
        )

        forecast_records.append({
            "mese": month,
            "sku": sku,
            "kg_domanda_prevista": round(
                forecast_value,
                2
            )
        })

forecast = pd.DataFrame(
    forecast_records
)

forecast = forecast.merge(
    actual,
    on=["mese", "sku"],
    how="left",
    validate="one_to_one"
)

forecast["kg_domanda_effettiva"] = (
    forecast["kg_domanda_effettiva"]
    .fillna(0)
    .round(2)
)

forecast["errore_forecast_kg"] = (
    forecast["kg_domanda_effettiva"]
    - forecast["kg_domanda_prevista"]
).round(2)

save(
    forecast,
    "fact_forecast"
)


# ============================================================
# FINE PARTE 3
# La Parte 4 completera' vendite, KPI e controlli.
# Non eseguire ancora il file.
# ============================================================


# ============================================================
# PARTE 4 DI 4
# KPI COMMERCIALI, CONTROLLI E RIEPILOGO
# ============================================================

# ------------------------------------------------------------
# 18. KPI COMMERCIALI
# ------------------------------------------------------------
# Il fatturato viene calcolato sulle quantita' effettivamente
# evase, non su quelle ordinate.
#
# I resi sono tracciati separatamente e non vengono considerati
# automaticamente recuperati a magazzino.
#
# Nota: i costi sono standard sintetici, non costi contabili reali.

sales = sales.merge(
    products[
        [
            "sku",
            "costo_standard_unitario",
            "kg_per_unita"
        ]
    ],
    on="sku",
    how="left",
    validate="many_to_one"
)

# Unita' equivalenti spedite, anche quando l'evasione e' parziale.
sales["unita_equivalenti_evasе"] = (
    sales["kg_evaso"] / sales["kg_per_unita"]
)

# Ricavo calcolato sulle unita' effettivamente spedite.
sales["ricavo_netto"] = (
    sales["unita_equivalenti_evasе"]
    * sales["prezzo_unitario_netto"]
).round(2)

# Costo standard associato alle quantita' effettivamente spedite.
sales["costo_prodotto_standard"] = (
    sales["unita_equivalenti_evasе"]
    * sales["costo_standard_unitario"]
).round(2)

sales["margine_lordo_stimato"] = (
    sales["ricavo_netto"]
    - sales["costo_prodotto_standard"]
).round(2)

sales["margine_percentuale_stimato"] = np.where(
    sales["ricavo_netto"] != 0,
    sales["margine_lordo_stimato"] / sales["ricavo_netto"],
    0
).round(4)

# Giorni di ritardo effettivi rispetto alla data richiesta.
sales["giorni_ritardo"] = (
    sales["data_consegna"] - sales["data_richiesta"]
).dt.days.clip(lower=0)

sales["puntuale"] = (
    sales["data_consegna"] <= sales["data_richiesta"]
)

sales["evasione_completa"] = (
    sales["kg_evaso"] >= sales["kg_ordinati"] - 0.001
)

sales["evasione_completa_e_puntuale"] = (
    sales["evasione_completa"]
    & sales["puntuale"]
)

save(
    sales,
    "fact_vendite"
)


# ------------------------------------------------------------
# 19. RIEPILOGO MENSILE DEI KPI
# ------------------------------------------------------------

sales["mese"] = (
    sales["data_ordine"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

monthly_sales = (
    sales
    .groupby("mese", as_index=False)
    .agg(
        righe_ordine=("riga_ordine_id", "nunique"),
        clienti_attivi=("cliente_id", "nunique"),
        kg_ordinati=("kg_ordinati", "sum"),
        kg_evaso=("kg_evaso", "sum"),
        kg_non_evaso=("kg_non_evaso", "sum"),
        ricavo_netto=("ricavo_netto", "sum"),
        costo_standard=("costo_prodotto_standard", "sum"),
        margine_lordo=("margine_lordo_stimato", "sum"),
        giorni_ritardo_medio=("giorni_ritardo", "mean"),
        righe_puntuali=("puntuale", "sum"),
        righe_complete=("evasione_completa", "sum"),
        righe_otif=("evasione_completa_e_puntuale", "sum")
    )
)

monthly_sales["tasso_evasione"] = np.where(
    monthly_sales["kg_ordinati"] > 0,
    monthly_sales["kg_evaso"] / monthly_sales["kg_ordinati"],
    0
)

monthly_sales["margine_percentuale"] = np.where(
    monthly_sales["ricavo_netto"] > 0,
    monthly_sales["margine_lordo"] / monthly_sales["ricavo_netto"],
    0
)

monthly_sales["otif_righe"] = np.where(
    monthly_sales["righe_ordine"] > 0,
    monthly_sales["righe_otif"] / monthly_sales["righe_ordine"],
    0
)

save(
    monthly_sales,
    "kpi_vendite_mensili"
)


# ------------------------------------------------------------
# 20. KPI PRODUTTIVI PER LINEA E MESE
# ------------------------------------------------------------

production["mese"] = (
    production["data_produzione"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

production_kpi = (
    production
    .groupby(["mese", "linea_id"], as_index=False)
    .agg(
        lotti=("lotto_id", "nunique"),
        kg_input=("kg_input", "sum"),
        kg_output_conforme=("kg_output_conforme", "sum"),
        kg_scarto=("kg_scarto", "sum"),
        costo_materia_prima_kg_medio=(
            "costo_materia_prima_kg", "mean"
        ),
        costo_lavorazione=("costo_lavorazione_lotto", "sum")
    )
)

production_kpi["resa_produttiva"] = np.where(
    production_kpi["kg_input"] > 0,
    production_kpi["kg_output_conforme"]
    / production_kpi["kg_input"],
    0
)

production_kpi["tasso_scarto"] = np.where(
    production_kpi["kg_input"] > 0,
    production_kpi["kg_scarto"]
    / production_kpi["kg_input"],
    0
)

save(
    production_kpi,
    "kpi_produzione_mensili"
)


# ------------------------------------------------------------
# 21. CONTROLLI AUTOMATICI DI QUALITA' DEI DATI
# ------------------------------------------------------------

checks = []


def check(name, passed, detail):
    """Aggiunge un controllo al report di qualita'."""
    checks.append({
        "controllo": name,
        "esito": "OK" if bool(passed) else "ATTENZIONE",
        "dettaglio": str(detail)
    })


# Chiavi primarie.
check(
    "Clienti univoci",
    clients["cliente_id"].is_unique,
    f"Righe={len(clients)}"
)

check(
    "SKU univoci",
    products["sku"].is_unique,
    f"Righe={len(products)}"
)

check(
    "ID righe vendita univoci",
    sales["riga_ordine_id"].is_unique,
    f"Righe={len(sales)}"
)

check(
    "ID ordini presenti",
    sales["ordine_id"].notna().all(),
    f"Righe={len(sales)}"
)

check(
    "ID lotti univoci",
    production["lotto_id"].is_unique,
    f"Righe={len(production)}"
)

# Integrita' referenziale.
check(
    "Foreign key cliente valida",
    sales["cliente_id"].isin(
        clients["cliente_id"]
    ).all(),
    "Ogni vendita deve avere un cliente valido"
)

check(
    "Foreign key SKU vendite valida",
    sales["sku"].isin(
        products["sku"]
    ).all(),
    "Ogni vendita deve avere uno SKU valido"
)

check(
    "Foreign key SKU produzione valida",
    production["sku"].isin(
        products["sku"]
    ).all(),
    "Ogni lotto deve avere uno SKU valido"
)

check(
    "Foreign key linea produttiva valida",
    production["linea_id"].isin(
        lines["linea_id"]
    ).all(),
    "Ogni lotto deve avere una linea valida"
)

check(
    "Foreign key lotti nelle allocazioni",
    sales_alloc["lotto_id"].isin(
        production["lotto_id"]
    ).all() if not sales_alloc.empty else True,
    f"Allocazioni={len(sales_alloc)}"
)

check(
    "Foreign key righe vendita nelle allocazioni",
    sales_alloc["riga_ordine_id"].isin(
        sales["riga_ordine_id"]
    ).all() if not sales_alloc.empty else True,
    f"Allocazioni={len(sales_alloc)}"
)

# Vincoli produttivi.
check(
    "Resa compresa tra zero e uno",
    production["resa_effettiva"].between(0, 1).all(),
    f"Resa media={production['resa_effettiva'].mean():.4f}"
)

check(
    "Input produzione positivo",
    (production["kg_input"] > 0).all(),
    f"Lotti={len(production)}"
)

check(
    "Output non superiore all'input",
    (
        production["kg_output_conforme"]
        <= production["kg_input"] + 0.011
    ).all(),
    "Output conforme <= input"
)

check(
    "Bilancio input output scarto",
    np.allclose(
        production["kg_input"],
        production["kg_output_conforme"]
        + production["kg_scarto"],
        atol=0.011
    ),
    "Input = output conforme + scarto"
)

check(
    "Scarto non negativo",
    (production["kg_scarto"] >= 0).all(),
    "Nessuno scarto negativo"
)

check(
    "Scadenza successiva alla disponibilita'",
    (
        production["data_scadenza"]
        >= production["data_disponibilita"]
    ).all(),
    "Validita' cronologica dei lotti"
)

# Vincoli commerciali.
check(
    "Date ordine nel periodo",
    sales["data_ordine"].between(START, END).all(),
    "Ordini compresi nel 2024-2025"
)

check(
    "Quantita' ordinate non negative",
    (sales["kg_ordinati"] >= 0).all(),
    "Quantita' valide"
)

check(
    "Quantita' evase non superiori agli ordini",
    (
        sales["kg_evaso"]
        <= sales["kg_ordinati"] + 0.011
    ).all(),
    "Kg evasi <= kg ordinati"
)

check(
    "Riconciliazione ordinato evaso",
    np.allclose(
        sales["kg_ordinati"],
        sales["kg_evaso"] + sales["kg_non_evaso"],
        atol=0.011
    ),
    "Ordinato = evaso + non evaso"
)

check(
    "Ricavi non negativi",
    (sales["ricavo_netto"] >= 0).all(),
    "Ricavi >= 0"
)

check(
    "Prezzi non negativi",
    (sales["prezzo_unitario_netto"] >= 0).all(),
    "Prezzi >= 0"
)

check(
    "Percentuale evasione nel range",
    sales["percentuale_evasione"].between(0, 1).all(),
    "Range [0,1]"
)

# Coerenza delle allocazioni.
if not sales_alloc.empty:

    allocated_by_row = (
        sales_alloc
        .groupby("riga_ordine_id")["kg"]
        .sum()
    )

    allocated_map = sales.set_index(
        "riga_ordine_id"
    )["kg_evaso"]

    aligned = allocated_map.reindex(
        allocated_by_row.index
    )

    allocation_consistent = np.allclose(
        allocated_by_row.to_numpy(),
        aligned.to_numpy(),
        atol=0.011
    )

else:
    allocation_consistent = True

check(
    "Riconciliazione allocazioni e vendite",
    allocation_consistent,
    "Somma allocazioni = kg evasi"
)

# Controllo temporale dei lotti spediti.
if not sales_alloc.empty:

    allocation_dates = sales_alloc.merge(
        production[
            [
                "lotto_id",
                "data_disponibilita",
                "data_scadenza"
            ]
        ],
        on="lotto_id",
        how="left",
        validate="many_to_one"
    )

    valid_dates = (
        (
            allocation_dates["data_movimento"]
            >= allocation_dates["data_disponibilita"]
        )
        &
        (
            allocation_dates["data_movimento"]
            <= allocation_dates["data_scadenza"]
        )
    )

    check(
        "Allocazioni entro la validita' del lotto",
        valid_dates.all(),
        f"Allocazioni non valide={(~valid_dates).sum()}"
    )

else:
    check(
        "Allocazioni entro la validita' del lotto",
        True,
        "Nessuna allocazione"
    )

# Controllo delle giacenze.
check(
    "Giacenze cumulative non negative",
    (
        stock_daily["giacenza_cumulata_kg"] >= -0.011
    ).all(),
    f"Minimo={stock_daily['giacenza_cumulata_kg'].min():.3f} kg"
)

# Il report e' un file da consultare prima di usare il dataset.
quality_report = pd.DataFrame(checks)

save(
    quality_report,
    "data_quality_checks"
)


# ------------------------------------------------------------
# 22. RIEPILOGO FINALE DELLA GENERAZIONE
# ------------------------------------------------------------

summary = {
    "seed": SEED,

    "periodo_vendite": [
        date_string(START),
        date_string(END)
    ],

    "clienti": int(len(clients)),
    "prodotti": int(len(products)),
    "linee_produttive": int(len(lines)),

    "righe_vendita": int(len(sales)),
    "ordini_distinti": int(sales["ordine_id"].nunique()),

    "lotti_produzione": int(len(production)),
    "movimenti_magazzino": int(len(movements)),
    "allocazioni_vendite_lotti": int(len(sales_alloc)),

    "righe_con_evasione_parziale_o_nulla": int(
        (sales["kg_non_evaso"] > 0.001).sum()
    ),

    "kg_ordinati": round(
        float(sales["kg_ordinati"].sum()),
        2
    ),

    "kg_evasi": round(
        float(sales["kg_evaso"].sum()),
        2
    ),

    "kg_non_evasi": round(
        float(sales["kg_non_evaso"].sum()),
        2
    ),

    "ricavo_netto_stimato": round(
        float(sales["ricavo_netto"].sum()),
        2
    ),

    "margine_lordo_stimato": round(
        float(sales["margine_lordo_stimato"].sum()),
        2
    ),

    "kg_input_produzione": round(
        float(production["kg_input"].sum()),
        2
    ),

    "kg_output_conforme": round(
        float(production["kg_output_conforme"].sum()),
        2
    ),

    "kg_scarto": round(
        float(production["kg_scarto"].sum()),
        2
    ),

    "resa_produttiva_media_ponderata": round(
        float(
            production["kg_output_conforme"].sum()
            / production["kg_input"].sum()
        ),
        4
    ),

    "controlli_qualita": int(len(quality)),
    "fermi_produttivi": int(len(downtime)),
    "righe_forecast": int(len(forecast)),

    "controlli_ok": int(
        (quality_report["esito"] == "OK").sum()
    ),

    "controlli_attenzione": int(
        (quality_report["esito"] != "OK").sum()
    )
}

with open(
    OUT / "generation_summary.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        summary,
        f,
        indent=2,
        ensure_ascii=False,
        default=str
    )


# ------------------------------------------------------------
# 23. REPORT DI ESECUZIONE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("GENERAZIONE DATASET COMPLETATA")
print("=" * 60)

print(
    json.dumps(
        summary,
        indent=2,
        ensure_ascii=False
    )
)

print("\nCONTROLLI DI QUALITA'")

print(
    quality_report.to_string(index=False)
)

print(f"\nFile salvati in: {OUT.resolve()}")

if (quality_report["esito"] != "OK").any():

    print(
        "\nATTENZIONE: alcuni controlli non sono superati. "
        "Esamina data_quality_checks.csv."
    )

else:

    print(
        "\nTutti i controlli implementati sono superati."
    )

print(
    "\nI dati sono sintetici e destinati a esercitazioni "
    "e portfolio, non a decisioni operative reali."
)

# ============================================================
# FINE SCRIPT
# ============================================================
