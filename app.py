import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | Tax Simulator", page_icon="⚖️", layout="centered")

# --- DESIGN & CSS LUXURY (HIGH CONTRAST) ---
st.markdown("""
    <style>
    /* === 1. SFONDO GENERALE (BLU NOTTE PROFONDO) === */
    .stApp {
        background: linear-gradient(180deg, #001529 0%, #001e3c 100%);
    }

    /* === 2. TESTI GLOBALI (BIANCO SU BLU) === */
    /* Forza tutti i testi principali ad essere bianchi */
    h1, h2, h3, h4, h5, h6, p, li, span, div {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Colore specifico per le etichette sopra i campi di input (es. "Compensi Lordi") */
    .stNumberInput > label, .stRadio > label {
        color: #D4AF37 !important; /* Oro per le domande */
        font-weight: bold;
        font-size: 1.1em;
    }
    
    /* Testo piccolo (caption) */
    .stCaption {
        color: #cccccc !important;
    }

    /* === 3. PULSANTI === */
    .stButton>button {
        background-color: #001529; /* Sfondo scuro */
        color: #D4AF37 !important; /* Testo ORO */
        font-weight: bold;
        border: 2px solid #D4AF37; /* Bordo ORO */
        border-radius: 8px;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #D4AF37; /* Diventa Oro */
        color: #001529 !important; /* Testo Blu */
        border-color: #ffffff;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6);
    }
    .stButton>button p {
        color: inherit !important; /* Assicura che il testo dentro il bottone segua la regola hover */
    }

    /* === 4. BOX DEI RISULTATI (SCHEDA BIANCA PER LEGGIBILITÀ) === */
    /* Qui usiamo sfondo bianco per far risaltare i numeri, quindi il testo DENTRO qui deve tornare scuro */
    .result-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 3px solid #D4AF37;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        text-align: center;
    }
    /* Forziamo il colore del testo SOLO dentro la card risultato */
    .result-card h1, .result-card h3, .result-card small, .result-card span {
        color: #001529 !important; /* Blu scuro */
    }
    .result-card h1 {
        font-size: 2.8em !important;
        margin: 10px 0 !important;
    }

    /* === 5. TABELLE === */
    /* Rendiamo la tabella leggibile */
    .dataframe {
        background-color: white;
        color: #333 !important; /* Testo nero dentro la tabella */
        border-radius: 5px;
    }
    .dataframe th {
        background-color: #D4AF37 !important; /* Intestazione Oro */
        color: #001529 !important; /* Testo Blu */
    }
    .dataframe td {
        color: #333 !important;
    }

    /* === 6. SIDEBAR === */
    [data-testid="stSidebar"] {
        background-color: #000f1f;
        border-right: 1px solid #D4AF37;
    }
    
    /* Separatori (HR) */
    hr {
        border-color: #D4AF37;
        opacity: 0.5;
    }
    
    /* Nascondi elementi standard */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE STUDIO ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚖️</h1>", unsafe_allow_html=True)
with col_title:
    st.title("STUDIO GAETANI")
    st.markdown("<span style='color: #D4AF37; font-style: italic; font-size: 1.1em;'>Partner Fiscale per l'Avvocatura</span>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: PARAMETRI ---
st.sidebar.header("⚙️ Configurazione")
st.sidebar.write("Seleziona il profilo fiscale:")

aliquota_scelta = st.sidebar.radio(
    "Tipologia:",
    ["Start-up (5%)", "Ordinario (15%)"],
    index=1
)
aliquota_imposta = 0.05 if "Start-up" in aliquota_scelta else 0.15

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Dati Tecnici")
st.sidebar.info("""
**Codice ATECO:** 69.10.10  
**Coeff. Redditività:** 78%  
**Cassa Forense:** ~15%  
""")

# --- LOGICA CALCOLO ---
def calcola_lordo_da_netto(netto, aliquota):
    fattore_cassa = 0.78 * 0.15
    fattore_tasse = (0.78 - fattore_cassa) * aliquota
    denominatore = 1 - fattore_cassa - fattore_tasse
    if denominatore <= 0: return 0
    return netto / denominatore

def genera_dataframe_dettaglio(fatturato, aliquota):
    reddito_forfettario = fatturato * 0.78
    cassa = reddito_forfettario * 0.15
    imponibile_fiscale = reddito_forfettario - cassa
    tasse = imponibile_fiscale * aliquota
    netto = fatturato - cassa - tasse
    
    data = {
        "Descrizione": [
            "1. Fatturato (Onorari)",
            "2. Abbattimento Costi (22%)",
            "3. Reddito Professionale (78%)",
            "4. Cassa Forense (15% ded.)", 
            "5. Base Imponibile Fiscale",
            f"6. Imposta Sostitutiva ({int(aliquota*100)}%)",
            "👉 NETTO DISPONIBILE"
        ],
        "Importo (€)": [
            fatturato,
            -(fatturato * 0.22),
            reddito_forfettario,
            -cassa,
            imponibile_fiscale,
            -tasse,
            netto
        ]
    }
    return pd.DataFrame(data)

# --- TAB NAVIGAZIONE ---
tab1, tab2 = st.tabs(["📉 Dal Lordo al Netto", "🎯 Dal Netto al Lordo"])

# === TAB 1 ===
with tab1:
    st.markdown("### Analisi redditività")
    st.write("Inserisci i tuoi onorari per scoprire il netto reale.")
    
    compenso_lordo = st.number_input("Inserisci Fatturato Lordo (€)", min_value=0.0, value=30000.0, step=1000.0)

    if st.button("CALCOLA NETTO", key="btn1"):
        df = genera_dataframe_dettaglio(compenso_lordo, aliquota_imposta)
        netto_finale = df.iloc[-1]["Importo (€)"]
        
        # RISULTATO IN CARD BIANCA (Per contrasto)
        st.markdown(f"""
        <div class="result-card">
            <h3>Netto in Tasca:</h3>
            <h1>€ {netto_finale:,.2f}</h1>
            <small style='color:#666 !important'>Su un fatturato di € {compenso_lordo:,.2f}</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 🔍 Dettaglio calcoli:")
        st.table(df.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        cpa = compenso_lordo * 0.04
        st.warning(f"⚠️ Ricorda: In fattura aggiungi il 4% CPA (€ {cpa:,.2f}) che non è reddito tuo.")

# === TAB 2 ===
with tab2:
    st.markdown("### Pianificazione Obiettivi")
    st.write("Quanto vuoi guadagnare 'pulito' all'anno?")
    
    netto_desiderato = st.number_input("Netto Desiderato (€)", min_value=0.0, value=24000.0, step=1000.0)
    
    if st.button("CALCOLA FATTURATO", key="btn2"):
        lordo = calcola_lordo_da_netto(netto_desiderato, aliquota_imposta)
        
        # RISULTATO IN CARD BIANCA
        st.markdown(f"""
        <div class="result-card">
            <h3>Devi Fatturare (Onorari):</h3>
            <h1 style="color: #b8860b !important;">€ {lordo:,.2f}</h1>
            <span style='font-weight:bold;'>+ 4% CPA = Totale Bonifico € {lordo*1.04:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 🔢 Verifica inversa (Prova del 9):")
        df_ver = genera_dataframe_dettaglio(lordo, aliquota_imposta)
        st.table(df_ver.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        if lordo > 85000:
            st.error("ATTENZIONE: Con questo importo superi il limite forfettario di 85.000€!")

st.markdown("<br><center style='color: #D4AF37; font-size: 0.8em;'>Studio Gaetani © 2024 - Luxury Tax Simulator</center>", unsafe_allow_html=True)
