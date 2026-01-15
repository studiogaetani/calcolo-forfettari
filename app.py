import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | Tax Simulator", page_icon="⚖️", layout="centered")

# --- DESIGN & CSS AVANZATO (LOOK PROFESSIONALE) ---
st.markdown("""
    <style>
    /* Sfondo generale con gradiente elegante */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Titoli */
    h1 {
        color: #0f3460;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
    }
    h2, h3 {
        color: #16213e;
    }
    
    /* Card bianca stile "Material Design" */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: white; 
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    
    /* Stile personalizzato per i riquadri dei risultati */
    .result-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #0f3460;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Pulsanti */
    .stButton>button {
        background-color: #0f3460;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1a1a2e;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Tabelle */
    thead tr th:first-child {display:none}
    tbody th {display:none}
    .dataframe {
        font-family: "Arial", sans-serif;
        border-collapse: collapse;
        width: 100%;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e6e6e6;
    }
    </style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE STUDIO ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.write("⚖️") 
with col_title:
    st.title("STUDIO GAETANI")
    st.markdown("**Simulatore Fiscale Avanzato - Regime Forfettario**")

st.markdown("---")

# --- SIDEBAR: PARAMETRI ---
st.sidebar.header("⚙️ Configurazione")
st.sidebar.markdown("Seleziona il profilo fiscale:")

aliquota_scelta = st.sidebar.radio(
    "Aliquota Imposta Sostitutiva",
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
st.sidebar.markdown("<small>Versione App: 2.1</small>", unsafe_allow_html=True)

# --- FUNZIONI DI CALCOLO ---

def calcola_lordo_da_netto(netto, aliquota):
    """
    Formula inversa:
    Netto = Fatturato * (1 - Coeff_Cassa - Coeff_Tasse)
    Dove Coeff_Cassa = 0.78 * 0.15 = 0.117
    Dove Coeff_Tasse = (0.78 - 0.117) * aliquota
    """
    fattore_cassa = 0.78 * 0.15
    fattore_tasse = (0.78 - fattore_cassa) * aliquota
    denominatore = 1 - fattore_cassa - fattore_tasse
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
            "2. Abbattimento Costi Forfettari (22%)",
            "3. Reddito Professionale (78%)",
            "4. Cassa Forense (15% deducibile)", 
            "5. Base Imponibile Fiscale (3 - 4)",
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

# --- NAVIGAZIONE TABS ---
tab1, tab2 = st.tabs(["📉 Dal Lordo al Netto", "🎯 Dal Netto al Lordo"])

# === TAB 1: CALCOLO CLASSICO ===
with tab1:
    st.markdown("### Analisi redditività")
    st.write("Inserisci l'importo degli onorari annui per calcolare il netto reale.")
    
    col_in, col_space = st.columns([1,1])
    with col_in:
        compenso_lordo = st.number_input("Compensi Lordi Annui (€)", min_value=0, value=30000, step=1000)

    if st.button("Calcola Netto", key="btn_netto"):
        df_dettaglio = genera_dataframe_dettaglio(compenso_lordo, aliquota_imposta)
        netto_finale = df_dettaglio.iloc[-1]["Importo (€)"]
        
        # CARD RISULTATO
        st.markdown(f"""
        <div class="result-card">
            <h3 style="margin:0; color:#666;">Netto in tasca stimato:</h3>
            <h1 style="margin:0; color:#0f3460; font-size: 2.5em;">€ {netto_finale:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔍 Dettaglio del calcolo")
        st.table(df_dettaglio.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        cassa_integrativa = compenso_lordo * 0.04
        st.info(f"ℹ️ **Nota:** Ricorda che in fattura incasserai anche il **4% C.P.A.** (€ {cassa_integrativa:,.2f}), che dovrai versare interamente alla Cassa e non rientra in questo calcolo.")

# === TAB 2: CALCOLO INVERSO ===
with tab2:
    st.markdown("### Pianificazione Obiettivi")
    st.write("Inserisci quanto vuoi guadagnare 'pulito' per sapere quanto devi fatturare.")
    
    col_in2, col_space2 = st.columns([1,1])
    with col_in2:
        netto_desiderato = st.number_input("Netto Desiderato Annuo (€)", min_value=0, value=24000, step=1000)
    
    if st.button("Calcola Fatturato Necessario", key="btn_lordo"):
        lordo_necessario = calcola_lordo_da_netto(netto_desiderato, aliquota_imposta)
        
        # CARD RISULTATO
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #e02e49;">
            <h3 style="margin:0; color:#666;">Devi fatturare (Onorari):</h3>
            <h1 style="margin:0; color:#e02e49; font-size: 2.5em;">€ {lordo_necessario:,.2f}</h1>
            <small>+ 4% CPA in fattura = Totale incasso € {lordo_necessario*1.04:,.2f}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # RI-CALCOLO PER DIMOSTRAZIONE (Prova del 9)
        st.markdown("#### 🔢 Prova del nove (Verifica)")
        st.write("Partendo dal fatturato calcolato sopra, ecco come si arriva al tuo netto:")
        
        df_verifica = genera_dataframe_dettaglio(lordo_necessario, aliquota_imposta)
        st.table(df_verifica.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        if lordo_necessario > 85000:
            st.warning("⚠️ **Attenzione:** Con questo importo superi il limite di € 85.000 e fuoriuscirai dal regime forfettario l'anno successivo!")

st.markdown("<br><hr><center style='color:#888;'>Studio Gaetani © 2024 | Software ad uso interno per simulazioni fiscali</center>", unsafe_allow_html=True)
