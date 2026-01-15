import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | General Tax Simulator", page_icon="📊", layout="centered")

# --- DATABASE COEFFICIENTI & ATTIVITÀ ---
ATTIVITA_DB = {
    "Professionista (Freelance/Consulenti)": (0.78, "GS"),
    "Commercio (E-commerce/Negozi)": (0.40, "AC"),
    "Commercio ambulante (Alimentari)": (0.40, "AC"),
    "Commercio ambulante (Altri prodotti)": (0.54, "AC"),
    "Artigiano (Parrucchiere/Estetista)": (0.67, "AC"),
    "Edilizia e Costruzioni": (0.86, "AC"),
    "Intermediari (Agenti Immobiliari)": (0.62, "AC"),
    "Attività immobiliari": (0.40, "GS"),
    "Ristorazione (Bar/Ristoranti/B&B)": (0.40, "AC"),
    "Altre attività economiche": (0.67, "GS")
}

# --- CSS LUXURY (FORCE DARK SELECTBOX) ---
st.markdown("""
    <style>
    /* === SFONDO GENERALE === */
    .stApp {
        background: linear-gradient(180deg, #001529 0%, #001e3c 100%);
    }

    /* === TESTI GLOBALI === */
    h1, h2, h3, h4, h5, h6, p, li, div, label, span {
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Etichette (Domande) in Oro */
    .stSelectbox > label, .stNumberInput > label, .stRadio > label, .stCheckbox > label {
        color: #D4AF37 !important;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    
    /* Testi piccoli */
    .stCaption, small {
        color: #cccccc !important;
    }

    /* === MENU A TENDINA (SELECTBOX) - FORZATURA TOTALE === */
    div[data-baseweb="select"] > div {
        background-color: #001529 !important; /* FORZA BLU SCURO */
        border: 2px solid #D4AF37 !important; /* BORDO ORO */
        color: white !important; /* TESTO BIANCO */
    }
    div[data-baseweb="select"] span {
        color: white !important;
    }
    div[data-baseweb="select"] svg {
        fill: white !important;
        stroke: white !important;
    }
    div[data-baseweb="popover"] div, 
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background-color: #001529 !important;
        border: 1px solid #D4AF37 !important;
    }
    li[data-baseweb="option"] {
        color: white !important;
    }
    li[data-baseweb="option"]:hover,
    li[aria-selected="true"] {
        background-color: #D4AF37 !important;
        color: #001529 !important;
    }

    /* === PULSANTI === */
    .stButton>button {
        background-color: #001529;
        color: #D4AF37 !important;
        font-weight: bold;
        border: 2px solid #D4AF37;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        width: 100%;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #D4AF37;
        color: #001529 !important;
        border-color: #ffffff;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6);
    }
    
    /* === BOX RISULTATI (BIANCO) === */
    .result-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 3px solid #D4AF37;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        text-align: center;
    }
    .result-card h1, .result-card h3, .result-card span, .result-card small, .result-card div {
        color: #001529 !important;
    }
    .result-card h1 {
        font-size: 2.8em !important;
        margin: 10px 0 !important;
    }

    /* === TABELLE === */
    .dataframe {
        background-color: white;
        color: #333 !important;
        border-radius: 5px;
    }
    .dataframe th {
        background-color: #D4AF37 !important;
        color: #001529 !important;
    }
    .dataframe td {
        color: #333 !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background-color: #000f1f;
        border-right: 1px solid #D4AF37;
    }
    hr { border-color: #D4AF37; opacity: 0.5; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE STUDIO ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>📊</h1>", unsafe_allow_html=True)
with col_title:
    st.title("STUDIO GAETANI")
    st.markdown("<span style='color: #D4AF37; font-style: italic;'>Simulatore Fiscale Universale Forfettari</span>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: CONFIGURAZIONE PROFILO ---
st.sidebar.header("⚙️ Configurazione Attività")

# 1. SCELTA ATTIVITÀ
scelta_attivita = st.sidebar.selectbox(
    "Seleziona il tipo di attività:",
    options=list(ATTIVITA_DB.keys())
)

# Recupero dati in base alla scelta
coeff_redditivita = ATTIVITA_DB[scelta_attivita][0]
tipo_inps_suggest = ATTIVITA_DB[scelta_attivita][1]

st.sidebar.markdown(f"**Coeff. Redditività rilevato:** {int(coeff_redditivita*100)}%")

st.sidebar.markdown("---")

# 2. CONFIGURAZIONE INPS
st.sidebar.subheader("🏦 Configurazione INPS")

opzioni_inps = ["Gestione Separata (Freelance)", "Artigiani & Commercianti"]

tipo_inps = st.sidebar.radio(
    "Cassa Previdenziale:",
    opzioni_inps,
    index=0 if tipo_inps_suggest == "GS" else 1
)

riduzione_inps = False
aliquota_inps = 0.0

if "Separata" in tipo_inps:
    aliquota_inps = 0.2607  # Aliquota 2024 ~26.07%
    st.sidebar.caption("Aliquota Gest. Separata: 26.07%")
else:
    # Artigiani/Commercianti
    base_aliquota_ac = 0.24 # Media circa 24%
    riduzione_inps = st.sidebar.checkbox("Richiesta Riduzione 35% (Art/Com)", value=True)
    
    if riduzione_inps:
        aliquota_inps = base_aliquota_ac * 0.65 
        st.sidebar.caption(f"Aliquota ridotta stimata: {aliquota_inps*100:.2f}%")
    else:
        aliquota_inps = base_aliquota_ac
        st.sidebar.caption(f"Aliquota piena stimata: {aliquota_inps*100:.2f}%")

st.sidebar.markdown("---")

# 3. CONFIGURAZIONE TASSE
st.sidebar.subheader("⚖️ Tassazione")
regime_scelta = st.sidebar.radio(
    "Aliquota Imposta Sostitutiva:",
    ["Start-up (5%)", "Ordinario (15%)"],
    index=1
)
aliquota_tassa = 0.05 if "Start-up" in regime_scelta else 0.15

# --- LOGICA DI CALCOLO ---

def calcoli_forfettario(lordo, coeff, al_inps, al_tassa):
    """Calcola tutto partendo dal lordo"""
    reddito_forfettario = lordo * coeff
    contributi = reddito_forfettario * al_inps
    imponibile_fiscale = reddito_forfettario - contributi
    if imponibile_fiscale < 0: imponibile_fiscale = 0
    
    tasse = imponibile_fiscale * al_tassa
    netto = lordo - contributi - tasse
    
    return {
        "lordo": lordo,
        "costi_forfettari": lordo * (1 - coeff),
        "reddito": reddito_forfettario,
        "inps": contributi,
        "imponibile": imponibile_fiscale,
        "tasse": tasse,
        "netto": netto,
        "peso_totale": contributi + tasse
    }

def calcola_lordo_da_netto(netto, coeff, al_inps, al_tassa):
    """Reverse engineering"""
    fattore_inps = coeff * al_inps
    fattore_tasse = coeff * (1 - al_inps) * al_tassa
    
    denominatore = 1 - fattore_inps - fattore_tasse
    
    if denominatore <= 0: return 0
    return netto / denominatore

def genera_tabella_dettaglio(risultati, coeff, al_inps, al_tassa):
    """Genera il DataFrame per la visualizzazione"""
    # Calcolo percentuale costi forfettari arrotondata correttamente
    pct_costi = round((1 - coeff) * 100)
    
    df = pd.DataFrame({
        "Voce": [
            "1. Fatturato Lordo",
            f"2. Costi Forfettari ({pct_costi}%)",
            "3. Reddito Imponibile Lordo",
            f"4. Contributi INPS ({aliquota_inps*100:.2f}%)",
            "5. Base Imponibile Fiscale",
            f"6. Imposta Sostitutiva ({int(al_tassa*100)}%)",
            "👉 NETTO REALE"
        ],
        "Importo (€)": [
            risultati['lordo'],
            -risultati['costi_forfettari'],
            risultati['reddito'],
            -risultati['inps'],
            risultati['imponibile'],
            -risultati['tasse'],
            risultati['netto']
        ]
    })
    return df

# --- TAB NAVIGAZIONE ---
tab1, tab2 = st.tabs(["📉 Dal Lordo al Netto", "🎯 Dal Netto al Lordo"])

# === TAB 1: LORDO -> NETTO ===
with tab1:
    st.markdown("### Calcolo Redditività")
    st.write("Inserisci il fatturato annuo incassato per calcolare il netto reale.")
    
    lordo_input = st.number_input("Fatturato Lordo Annuo (€)", min_value=0.0, value=30000.0, step=1000.0)
    
    if st.button("CALCOLA NETTO", key="btn_normale"):
        risultati = calcoli_forfettario(lordo_input, coeff_redditivita, aliquota_inps, aliquota_tassa)
        incidenza_pct = (risultati['peso_totale'] / lordo_input * 100) if lordo_input > 0 else 0
        
        # CARD RISULTATO
        st.markdown(f"""
        <div class="result-card">
            <h3>Netto Disponibile:</h3>
            <h1 style="color: #002a52;">€ {risultati['netto']:,.2f}</h1>
            <span>Incidenza Tasse e INPS: <b style="color: #b8860b;">{incidenza_pct:.1f}%</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        # TABELLA DETTAGLIO
        st.write("#### 🔍 Dettaglio Fiscale")
        df_dettaglio = genera_tabella_dettaglio(risultati, coeff_redditivita, aliquota_inps, aliquota_tassa)
        st.table(df_dettaglio.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        if "Artigiani" in tipo_inps:
            st.info("ℹ️ **Nota:** Il calcolo INPS Artigiani/Comm. è simulato in percentuale sul reddito. Ricorda che esistono minimali fissi da versare anche a fatturato zero.")

# === TAB 2: NETTO -> LORDO ===
with tab2:
    st.markdown("### Pianificazione Obiettivi")
    st.write("Quanto vuoi guadagnare 'pulito' in tasca?")
    
    netto_input = st.number_input("Netto Desiderato Annuo (€)", min_value=0.0, value=20000.0, step=1000.0)
    
    if st.button("CALCOLA FATTURATO NECESSARIO", key="btn_inverso"):
        # 1. Trovo il lordo necessario
        lordo_nec = calcola_lordo_da_netto(netto_input, coeff_redditivita, aliquota_inps, aliquota_tassa)
        
        # 2. Ricalcolo tutti i passaggi partendo da quel lordo per generare la tabella identica
        risultati_verifica = calcoli_forfettario(lordo_nec, coeff_redditivita, aliquota_inps, aliquota_tassa)
        
        # CARD RISULTATO
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #D4AF37;">
            <h3>Devi Fatturare:</h3>
            <h1 style="color: #b8860b;">€ {lordo_nec:,.2f}</h1>
            <small>Per avere esattamente € {netto_input:,.2f} netti</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 🔢 Dimostrazione del calcolo (Prova del 9)")
        st.write("Se fatturi la cifra indicata sopra, ecco come arrivi al netto desiderato:")
        
        # Genero la stessa tabella del Tab 1 per coerenza
        df_ver = genera_tabella_dettaglio(risultati_verifica, coeff_redditivita, aliquota_inps, aliquota_tassa)
        st.table(df_ver.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        if lordo_nec > 85000:
            st.error("⚠️ ATTENZIONE: Questo importo supera il limite di € 85.000 per il regime forfettario!")

st.markdown("<br><center style='color: #D4AF37; font-size: 0.8em;'>Studio Gaetani © 2024 - Software Professionale Gestione Forfettari</center>", unsafe_allow_html=True)
