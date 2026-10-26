# Bresaolificio-Analytics
Analisi degli scarti di un bresaolificio fittizio (dati generati da Python con IA) e creazione di dashboard dedicata.

# Description
Le domande di business principali sono riassumibili in:
* analizzare la situazione della resa delle linee produttive
* identificare eventuali problemi e attribuirli

*Dataset* = generato, nella cartella "data"

*Tools* = Python, Power BI

# Database schema
Le tabelle si trovano in "documentation/data_dictionary.xlsx" e lo schema visivo è presente nel file "project_outline.pptx"

# Example analysis
## Python
Quanti kg di materiale vengono lavorati e scartati da ogni linea produttiva?
```python
scarti_linea = df.groupby("linea_id")[["kg_input", "kg_output_conforme", "kg_scarto"]].sum().reset_index()
```

Mostra in grafico la resa delle linee produttive nel tempo
```python
scarti_linea_trend_plot = scarti_linea_trend.pivot(
                                                    index="anno-mese",
                                                    columns="linea_id",
                                                    values="resa"
                                                    )

scarti_linea_trend_plot.plot(
    kind="line",
    x=None,
    ylabel="resa",
    xlabel="anno-mese",
    figsize=(12, 6),
    marker="o"
)
```

Quale è la frazione di lotti non conformi sul totale dei lotti controllati?
```python
qualita = pd.read_csv("fact_qualita.csv")
conformi = qualita["controllo_id"].loc[qualita["esito"] == "Conforme"].count()
non_conformi = qualita["controllo_id"].loc[qualita["esito"] == "Non conforme"].count()
pct_conformi = round(conformi / (conformi + non_conformi), 3)
pct_non_conformi = round(1 - pct_conformi, 3)
print(f"La frazione di conformi è {pct_conformi}, mentre i non conformi sono {pct_non_conformi}")
```

## Power BI 
Colore per formattazione condizionale della resa effettiva in funzione del target
```dax
Colore resa = 
VAR resa_target = 
SELECTEDVALUE(dim_linee[target_oee])

RETURN
    IF(
        [Resa produttiva] >= resa_target,
        "#35D411",
        "#FF0000"
        )
```

Costo degli scarti
```dax
Costo scarto = 
SUMX(
    fact_produzione,
    fact_produzione[kg_scarto] * fact_produzione[costo_materia_prima_kg]
)
```

Lotti non conformi
```dax
Non conformi = 
CALCULATE(
    COUNTROWS(
            fact_qualita
        ),
    fact_qualita[esito] = "Non conforme"
)
```

Derivazione della famiglia di prodotto dall'SKU di una tabella non correlata
```dax
Famiglia = 
CALCULATE(
    SELECTEDVALUE(
        dim_prodotti[famiglia]
    ),
    TREATAS(                                -- Non essendoci una relazione corretta nel modello, devo usare TREATAS
        VALUES(fact_produzione[sku]),
        dim_prodotti[sku]
    )
)
```

# Insights
Riassunti nel file "analysis/results.pptx".
Alcuni esempi sono: 
* Le linee processano volumi paragonabili di prodotti e processano tutte le famiglie, con rese stabili nel tempo
* La Linea 3 ha una resa più bassa delle altre, su tutti i turni e prodotti
* La Linea 3 genera più difetti specialmente nel confezionamento e al sottovuoto
* La Linea 3 ha lo stesso numero di fermi delle altre linee, ma questi hanno durata maggiore (specialmente nel cambio formato)
* Con cambiamenti al planning si potrebbe ridurre la percentuale di lotti difettosi
* Con interventi sulla Linea 3 si potrebbe generare un *saving* di circa 72k € annui

# How to
Il notebook "analysis/exploratory_data_analysis.ipynb" consente di ripercorrere gli step dell'analisi puntuale riportata nella presentazione "analysis/results.pptx".

I dati in formato CSV sono in "data", e se si vuole avere una panoramica di come sono strutturati si può trovare una guida in "documentation".

Il report Power BI per navigare i dati in autonomia è "visualization/bresaolificio_analytics.pbix".
