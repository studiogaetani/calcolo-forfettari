import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | Tax Simulator", page_icon="⚖️", layout="centered")

# --- STILE PERSONALIZZATO (CSS) ---
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0f3460; font-family: 'Helvetica', sans-serif;}
    h2, h3 {color: #16213e;}
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        background-color: #0f3460;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE STUDIO ---
col1, col2 = st.columns([1, 4])
with col1:
    st.write("⚖️") # Qui potresti mettere st.image("logo_studio.png")
with col2:
    st.title("STUDIO GAETANI")
    st.caption("Consulenza Fiscale e Tributaria - Area Riservata Avvocati")

st.markdown("---")

# --- SIDEBAR: PARAMETRI FISCALI ---
st.sidebar.header("⚙️ Impostazioni Profilo")
st.sidebar.info("Configura il tuo regime fiscale")

aliquota_scelta = st.sidebar.radio(
    "Tipologia Forfettario",
    ["Start-up (5%)", "Ordinario (15%)"],
    index=1
)

# Gestione Aliquota
aliquota_imposta = 0.05 if "Start-up" in aliquota_scelta else 0.15

st.sidebar.markdown("---")
st.sidebar.write("**Parametri Fissi Avvocati:**")
st.sidebar.write("- Codice ATECO: **69.10.10**")
st.sidebar.write("- Coeff. Redditività: **78%**")
st.sidebar.write("- Cassa Forense: **~15%** (Soggettivo)")

# --- LOGICA APPLICAZIONE (TAB) ---
tab1, tab2 = st.tabs(["📉 Dal Lordo al Netto", "🎯 Dal Netto al Lordo"])

# === TAB 1: CALCOLO TASSE E NETTO ===
with tab1:
    st.header("Analisi Carico Fiscale")
    st.write("Inserisci il fatturato annuo previsto (Onorari) per scoprire quanto ti rimane in tasca.")
    
    compenso_lordo = st.number_input("Inserisci i tuoi Compensi Lordi annui (€)", min_value=0, value=30000, step=1000)
    
    if st.button("Calcola Netto", key="btn_netto"):
        # Calcoli
        reddito_forfettario = compenso_lordo * 0.78
        
        # Stima Contributi Soggettivi (15% del reddito forfettario)
        # Nota: Qui assumiamo il regime "a regime" dove i contributi sono deducibili
        cassa_soggettiva = reddito_forfettario * 0.15 
        
        # Imponibile Fiscale (Reddito - Contributi)
        imponibile_fiscale = reddito_forfettario - cassa_soggettiva
        
        # Calcolo Tasse
        tasse = imponibile_fiscale * aliquota_imposta
        
        # Netto
        netto = compenso_lordo - cassa_soggettiva - tasse
        
        # Percentuale Incidenza
        incidenza = ((cassa_soggettiva + tasse) / compenso_lordo) * 100 if compenso_lordo > 0 else 0
        
        # VISUALIZZAZIONE RISULTATI
        st.success(f"💶 **Netto Disponibile: € {netto:,.2f}**")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Tasse (Imposta)", f"€ {tasse:,.2f}")
        col_res2.metric("Cassa Forense (Stima)", f"€ {cassa_soggettiva:,.2f}")
        col_res3.metric("Pressione Fiscale", f"{incidenza:.1f}%")
        
        # Tabella Dettagliata
        df_results = pd.DataFrame({
            "Voce": ["Fatturato (Compensi)", "Reddito Imponibile (78%)", "Cassa Forense (dedotta)", "Base Imponibile Netta", "Imposta Sostitutiva", "NETTO REALE"],
            "Importo (€)": [compenso_lordo, reddito_forfettario, -cassa_soggettiva, imponibile_fiscale, -tasse, netto]
        })
        st.table(df_results.style.format({"Importo (€)": "€ {:,.2f}"}))
        
        st.info("💡 Nota: Al cliente in fattura addebiterai anche il 4% di Cassa (Integrativo), che non è un tuo ricavo ma va girato all'ente.")

# === TAB 2: REVERSE CHARGE (DAL NETTO AL LORDO) ===
with tab2:
    st.header("Pianificazione Obiettivi")
    st.write("Quanto devi fatturare per avere esattamente una certa cifra in tasca?")
    
    netto_desiderato = st.number_input("Quanto vuoi guadagnare NETTO l'anno? (€)", min_value=0, value=24000, step=1000)
    
    if st.button("Calcola Fatturato Necessario", key="btn_lordo"):
        # Matematica inversa
        # Netto = Fatturato - (Fatturato * 0.78 * 0.15) - [(Fatturato * 0.78 - Fatturato * 0.78 * 0.15) * Aliquota]
        # Fattorizziamo 'Fatturato':
        # Fattore Cassa = 0.78 * 0.15 = 0.117
        # Fattore Imponibile Tasse = 0.78 - 0.117 = 0.663
        # Fattore Tasse = 0.663 * Aliquota
        
        fattore_cassa = 0.78 * 0.15
        fattore_tasse = (0.78 - fattore_cassa) * aliquota_imposta
        
        denominatore = 1 - fattore_cassa - fattore_tasse
        
        fatturato_necessario = netto_desiderato / denominatore
        
        # Calcolo componenti inversi per verifica
        cassa_inv = fatturato_necessario * 0.78 * 0.15
        tasse_inv = (fatturato_necessario * 0.78 - cassa_inv) * aliquota_imposta
        
        st.success(f"🎯 Per avere € {netto_desiderato:,.0f} netti, devi fatturare:")
        st.header(f"€ {fatturato_necessario:,.2f}")
        
        st.write("### Come comporre la fattura (totale annuo):")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="metric-card">
            <b>Imponibile (Onorari)</b><br>
            <span style="font-size: 1.5em; color: #0f3460">€ {:,.2f}</span>
            </div>
            """.format(fatturato_necessario), unsafe_allow_html=True)
            
        with col_b:
            st.markdown("""
            <div class="metric-card">
            <b>Totale da Incassare (+4% CAP)</b><br>
            <span style="font-size: 1.5em; color: #16213e">€ {:,.2f}</span>
            </div>
            """.format(fatturato_necessario * 1.04), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="warning-box">
        <b>Analisi:</b><br>
        Su questo importo pagherai circa <b>€ {cassa_inv:,.2f}</b> di Cassa Forense (Soggettivo) e 
        <b>€ {tasse_inv:,.2f}</b> di Imposta Sostitutiva.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><small>Applicazione offerta dallo <b>Studio Gaetani</b>. Simulazione a scopo indicativo non costituente parere professionale vincolante.</small></center>", unsafe_allow_html=True)
