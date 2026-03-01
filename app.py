import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
import base64

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | Avvocati", page_icon="⚖️", layout="centered")

# --- 2. GESTIONE LOGIN ---
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <style>
        .stApp {background: linear-gradient(180deg, #001529 0%, #001e3c 100%);}
        h1, h3, p {color: white; text-align: center; font-family: 'Helvetica Neue', sans-serif;}
        .stTextInput > label {color: #D4AF37 !important; font-weight: bold;}
        .stButton > button {background-color: #D4AF37; color: #001529; width: 100%; border: none;}
        #MainMenu, header, footer {visibility: hidden;}
        input {color: white !important;}
        div[data-baseweb="input"] > div {background-color: #002a52 !important; border-color: #D4AF37 !important;}
        </style>
        """, unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 20px;'><span style='font-size: 60px;'>⚖️</span></div>", unsafe_allow_html=True)
        st.markdown("<h1>STUDIO GAETANI</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #D4AF37; margin-top: -20px; font-style: italic;'>Partner Fiscale dell'Avvocatura</h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<p style='color: white;'>Accesso Area Riservata</p>", unsafe_allow_html=True)
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("ACCEDI", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.error("⛔ Credenziali non valide.")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Riprova", on_click=password_entered)
        return False
    else:
        return True

if not check_password():
    st.stop()

# ==============================================================================
#  COSTANTI FISCALI E PREVIDENZIALI — aggiornare a inizio ogni anno
# ==============================================================================

ANNO_IMPOSTA = 2025

# Cassa Forense – Regolamento Unico Previdenza Forense, vigente dal 01.01.2024
# art. 16 Reg. Unico: 16% per 2024-2025, 17% dal 2026
ALIQUOTE_CFA = {2024: 0.16, 2025: 0.16, 2026: 0.17}
ALIQUOTA_CFA = ALIQUOTE_CFA.get(ANNO_IMPOSTA, 0.16)

# Contributi minimi soggettivi CFA (art. 21 Reg. Unico)
# Anni 1-4 di iscrizione: nessun minimo soggettivo (solo proporzionale)
# Anni 5-8: minimo ridotto al 50%
# Dal 9° anno: minimo pieno
MINIMO_SOGGETTIVO_PIENO = 2_750.0       # 2025
MINIMO_SOGGETTIVO_RIDOTTO = 1_375.0     # 2025 – anni 5-8

# Contributo di maternità (art. 30 Reg. Unico – fisso annuo, deducibile)
MATERNITA_CFA = 96.76     # 2024; aggiornare per 2025 quando comunicato da CFA

# Soglie regime forfetario (art. 1, co. 54 e 71, L. 190/2014)
SOGLIA_FORFETTARIO       = 85_000.0
SOGLIA_USCITA_IMMEDIATA  = 100_000.0

# ATECO 69.10.10 – Avvocatura: Allegato 2, L. 145/2018
COEFF_REDDITIVITA = 0.78

# ==============================================================================
#  CSS
# ==============================================================================
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #001529 0%, #001e3c 100%); }
    #MainMenu, header, footer, [data-testid="stToolbar"] {visibility: hidden; display: none;}
    h1, h2, h3, h4, h5, h6, p, li, div, label, span { color: #ffffff; font-family: 'Helvetica Neue', sans-serif; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    a:hover { color: #ffffff !important; text-decoration: underline; }
    [data-testid="stSidebar"] { background-color: #000f1f; border-right: 1px solid #D4AF37; }
    hr { border-color: #D4AF37; opacity: 0.5; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    input, textarea, .stNumberInput input, .stTextInput input, .stTextArea textarea {
        color: #ffffff !important; caret-color: #D4AF37 !important; font-weight: 500;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="base-input"], textarea {
        background-color: #002a52 !important; border: 2px solid #D4AF37 !important; border-radius: 5px;
    }
    .stSelectbox > label, .stNumberInput > label, .stRadio > label, .stCheckbox > label,
    .stTextInput > label, .stDateInput > label, .stTextArea > label {
        color: #D4AF37 !important; font-weight: bold; font-size: 1.1em; margin-bottom: 5px;
    }
    div[data-baseweb="select"] > div {
        background-color: #002a52 !important; border: 2px solid #D4AF37 !important; color: white !important;
    }
    div[data-baseweb="select"] span { color: white !important; }
    div[data-baseweb="select"] svg { fill: white !important; }
    div[data-baseweb="popover"] div, ul[data-baseweb="menu"] {
        background-color: #001529 !important; border: 1px solid #D4AF37 !important;
    }
    li[data-baseweb="option"] { color: white !important; }
    li[data-baseweb="option"]:hover, li[aria-selected="true"] {
        background-color: #D4AF37 !important; color: #001529 !important;
    }
    .stButton>button {
        background-color: #001529; color: #D4AF37 !important; font-weight: bold;
        border: 2px solid #D4AF37; border-radius: 8px; padding: 0.8rem 1rem;
        width: 100%; text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #D4AF37; color: #001529 !important; border-color: #ffffff; }
    .result-card {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 3px solid #D4AF37; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px; text-align: center;
    }
    .result-card h1, .result-card h3, .result-card span, .result-card small, .result-card div { color: #001529 !important; }
    .result-card h1 { font-size: 2.8em !important; margin: 10px 0 !important; }
    .dataframe { background-color: white; color: #333 !important; border-radius: 5px; }
    .dataframe th { background-color: #D4AF37 !important; color: #001529 !important; }
    .dataframe td { color: #333 !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
#  HEADER
# ==============================================================================
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 100%;'><span style='font-size: 3.5em;'>⚖️</span></div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin-bottom: 0px;'>STUDIO GAETANI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #D4AF37; margin-top: -10px; font-style: italic; font-weight: 300;'>Partner Fiscale dell'Avvocatura</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #cccccc; font-size: 0.9em; font-weight: 400; letter-spacing: 1px; margin-bottom: 10px;'>
    CONTABILITÀ • PIANIFICAZIONE FISCALE • CONSULENZA TRIBUTARIA
    </div>
    """, unsafe_allow_html=True)
    try:
        user_name = st.secrets["passwords"].get('user_display_name', 'Gentile Cliente')
        st.markdown(f"<div style='background-color: #002a52; padding: 5px 10px; border-radius: 5px; display: inline-block; border: 1px solid #D4AF37;'><small>Area Riservata Clienti | 👤 <b>{user_name}</b></small></div>", unsafe_allow_html=True)
    except:
        st.markdown("<div style='background-color: #002a52; padding: 5px 10px; border-radius: 5px; display: inline-block; border: 1px solid #D4AF37;'><small>Area Riservata Clienti</small></div>", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
#  SIDEBAR
# ==============================================================================
st.sidebar.header("⚙️ Parametri Fiscali")

regime_scelta = st.sidebar.radio(
    "Aliquota Imposta Sostitutiva:",
    ["Start-up (5%)", "Ordinario (15%)"],
    index=1
)
aliquota_tassa = 0.05 if "Start-up" in regime_scelta else 0.15

# Avviso requisiti aliquota 5% (art. 1, co. 65, L. 190/2014)
if "Start-up" in regime_scelta:
    st.sidebar.warning(
        "⚠️ **Requisiti aliquota 5%** (art. 1, co. 65, L. 190/2014):\n\n"
        "1. Nessuna attività professionale/d'impresa esercitata nei **3 anni precedenti**;\n"
        "2. L'attività non è mera continuazione di un precedente lavoro dipendente "
        "(salvo pratica forense obbligatoria);\n"
        "3. L'attività eventualmente rilevata da terzi non aveva ricavi > €85.000 "
        "nell'anno precedente.\n\n"
        "**Durata massima: 5 anni.** In assenza dei requisiti si applica il 15%."
    )

anni_iscrizione = st.sidebar.selectbox(
    "Anni di iscrizione a Cassa Forense:",
    ["1° – 4° anno (esonero minimo)", "5° – 8° anno (minimo ridotto 50%)", "Dal 9° anno (minimo pieno)"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Dati Fiscali e Previdenziali")
st.sidebar.info(f"""
**Attività:** Studio Legale
**Codice ATECO:** 69.10.10
**Coeff. Redditività:** 78%

**Cassa Forense – Contributo Soggettivo:**
• 2024-2025: **16%** sul reddito (Reg. Unico CFA, art. 16)
• Dal 2026: **17%** sul reddito
• Anno in uso: **{int(ALIQUOTA_CFA*100)}%**

**Contributo Integrativo CPA:** 4% (addebitato al cliente in fattura)
**Minimo soggettivo 2025:** €2.750 (pieno) | €1.375 (ridotto)
**Contributo di maternità 2024:** €96,76 (fisso, deducibile)
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Risorse Ufficiali")
st.sidebar.markdown("""
<div style="margin-left: 5px; font-size: 0.9em;">
    <a href="https://www.cassaforense.it/" target="_blank">▪️ Cassa Forense</a><br>
    <a href="https://www.agenziaentrate.gov.it/" target="_blank">▪️ Agenzia delle Entrate</a><br>
    <a href="https://www.consiglionazionaleforense.it/" target="_blank">▪️ CNF</a>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Esci / Logout"):
    del st.session_state["password_correct"]
    st.rerun()

# ==============================================================================
#  FUNZIONI DI CALCOLO
# ==============================================================================

def _minimo_cfa(anni_iscrizione_str):
    """Restituisce il minimo soggettivo CFA in base agli anni di iscrizione."""
    if "1°" in anni_iscrizione_str:
        return 0.0          # Anni 1-4: nessun minimo soggettivo (Reg. Unico CFA art. 21)
    elif "5°" in anni_iscrizione_str:
        return MINIMO_SOGGETTIVO_RIDOTTO   # Anni 5-8: 50%
    else:
        return MINIMO_SOGGETTIVO_PIENO     # Dal 9° anno: pieno


def calcoli_avvocato(lordo, al_tassa, anni_iscr):
    """
    Calcolo per COMPETENZA: ogni voce è riferita all'anno d'imposta corrente.
    I contributi vengono dedotti dal reddito imponibile nell'anno di riferimento,
    indipendentemente da quando vengono effettivamente versati (vedi nota sul
    disallineamento competenza/cassa nella sezione apposita).
    """
    minimo_cfa = _minimo_cfa(anni_iscr)
    reddito_forfettario = lordo * COEFF_REDDITIVITA
    cassa_soggettiva = max(reddito_forfettario * ALIQUOTA_CFA, minimo_cfa)
    maternita = MATERNITA_CFA
    deduzioni_totali = cassa_soggettiva + maternita
    imponibile_fiscale = max(reddito_forfettario - deduzioni_totali, 0)
    tasse = imponibile_fiscale * al_tassa
    netto = lordo - cassa_soggettiva - maternita - tasse

    return {
        "lordo": lordo,
        "costi_forfettari": lordo * (1 - COEFF_REDDITIVITA),
        "reddito": reddito_forfettario,
        "cassa": cassa_soggettiva,
        "maternita": maternita,
        "deduzioni": deduzioni_totali,
        "imponibile": imponibile_fiscale,
        "tasse": tasse,
        "netto": netto,
        "peso_totale": cassa_soggettiva + maternita + tasse,
    }


def calcola_lordo_da_netto_avvocato(netto, al_tassa, anni_iscr):
    """
    Calcolo inverso. Usa l'aliquota CFA aggiornata e il minimo CFA.
    Stima algebrica valida per redditi sopra il minimo CFA.
    Per redditi molto bassi (sotto la soglia del minimo), il calcolo è iterativo.
    """
    min_cfa = _minimo_cfa(anni_iscr)

    # Stima algebrica: netto = L - max(L*0.78*ALIQ, min) - MATERNITA - (L*0.78 - max(L*0.78*ALIQ,min) - MATERNITA)*al
    # Per redditi normali (sopra il minimo):
    fattore_cassa = COEFF_REDDITIVITA * ALIQUOTA_CFA
    fattore_tasse = COEFF_REDDITIVITA * (1 - ALIQUOTA_CFA) * al_tassa - MATERNITA_CFA * al_tassa / max(netto, 1)
    denominatore = 1 - fattore_cassa - fattore_tasse

    if denominatore <= 0:
        return 0

    lordo_stima = (netto + MATERNITA_CFA * (1 - al_tassa)) / denominatore

    # Verifica che il proporzionale superi il minimo; se no, aggiusta
    reddito_stima = lordo_stima * COEFF_REDDITIVITA
    if reddito_stima * ALIQUOTA_CFA < min_cfa and min_cfa > 0:
        # Regime a minimo: netto = L - min_cfa - maternita - (L*0.78 - min_cfa - maternita)*al
        den2 = 1 - COEFF_REDDITIVITA * al_tassa
        if den2 <= 0:
            return 0
        lordo_stima = (netto + (min_cfa + MATERNITA_CFA) * (1 - al_tassa)) / den2

    return lordo_stima


def calcoli_cassa(lordo_corrente, al_tassa, anni_iscr, primo_anno, lordo_precedente=0.0):
    """
    Calcolo per CASSA: riflette l'effettivo cash-out nell'anno corrente.

    Nel regime forfetario i contributi previdenziali seguono il principio di cassa
    (art. 1, co. 64, L. 190/2014): sono deducibili nell'anno in cui vengono
    effettivamente versati, non nell'anno a cui si riferiscono.

    Struttura versamenti CFA nell'anno corrente (es. 2025):
    ┌────────────────────────────────────────────────────────────────────┐
    │ Feb / Mag / Lug / Set 2025 → 4 rate minimali CFA anno 2025        │
    │ Entro 30/9/2025 (Mod. 5)  → Conguaglio CFA su reddito 2024        │
    │ Entro 30/9/2026 (Mod. 5)  → Conguaglio CFA su reddito 2025 (*)    │
    └────────────────────────────────────────────────────────────────────┘
    (*) = il conguaglio sull'anno corrente viene versato l'anno PROSSIMO

    Struttura versamenti Imposta Sostitutiva nell'anno corrente:
    ┌────────────────────────────────────────────────────────────────────┐
    │ Giugno anno corrente   → Saldo imposta anno precedente             │
    │ Giugno anno corrente   → Acconto 40% (metodo storico, anno prec.)  │
    │ Novembre anno corrente → Acconto 60% (metodo storico, anno prec.)  │
    │ Giugno anno successivo → Saldo imposta anno corrente (*)           │
    └────────────────────────────────────────────────────────────────────┘
    (*) = il saldo sull'anno corrente si paga l'anno PROSSIMO

    PRIMO ANNO: nessun acconto imposta (non dovuto); nessun conguaglio CFA
    (non esiste anno precedente). L'avvocato versa solo le rate minime CFA
    durante l'anno → cash flow più alto, ma "rimandato" all'anno 2.
    """
    minimo_cfa = _minimo_cfa(anni_iscr)

    # ── CFA VERSATA NELL'ANNO CORRENTE ─────────────────────────────────
    # Rate minime anno corrente (4 installments: feb, mag, lug, set)
    cfa_rate_minime = minimo_cfa
    maternita = MATERNITA_CFA

    # Conguaglio anno PRECEDENTE (pagato a settembre anno corrente con Mod. 5)
    if primo_anno or lordo_precedente <= 0:
        cfa_conguaglio_prec = 0.0
    else:
        reddito_prec = lordo_precedente * COEFF_REDDITIVITA
        cfa_totale_prec = max(reddito_prec * ALIQUOTA_CFA, minimo_cfa)
        cfa_conguaglio_prec = max(cfa_totale_prec - minimo_cfa, 0)

    cfa_versata_totale = cfa_rate_minime + cfa_conguaglio_prec + maternita

    # ── IMPOSTA VERSATA NELL'ANNO CORRENTE ─────────────────────────────
    # Primo anno: nessun acconto dovuto. Il saldo 2025 si versa a giugno 2026.
    if primo_anno or lordo_precedente <= 0:
        imposta_versata = 0.0
        saldo_prec = 0.0
        acconto_corrente = 0.0
    else:
        # Imposta dell'anno precedente (per metodo storico)
        r_prec = calcoli_avvocato(lordo_precedente, al_tassa, anni_iscr)
        imposta_prec = r_prec["tasse"]

        # Saldo anno precedente = imposta prec. − acconto versato in anno prec.
        # Con metodo storico al 100%, acconto versato in anno prec. = imposta di due anni fa.
        # Per semplicità (e per il caso "anni a regime con reddito stabile"):
        # assumiamo acconto anno prec. = imposta anno prec. → saldo ≈ 0 a regime stabile.
        # Se il reddito è cambiato il saldo sarà diverso; il calcolo esatto richiede
        # la dichiarazione dell'anno precedente.
        acconto_prec = imposta_prec   # assunzione: reddito stabile anno N-2 ≈ N-1
        saldo_prec = max(imposta_prec - acconto_prec, 0)   # = 0 se reddito stabile

        # Acconto anno corrente (100% metodo storico = 100% × imposta anno prec.)
        acconto_corrente = imposta_prec

        imposta_versata = saldo_prec + acconto_corrente

    # ── CASH OUT FUTURO (ciò che verrà versato l'anno PROSSIMO) ─────────
    reddito_corrente = lordo_corrente * COEFF_REDDITIVITA
    cfa_totale_corrente = max(reddito_corrente * ALIQUOTA_CFA, minimo_cfa)
    cfa_conguaglio_futuro = max(cfa_totale_corrente - minimo_cfa, 0)

    r_corrente = calcoli_avvocato(lordo_corrente, al_tassa, anni_iscr)
    imposta_corrente = r_corrente["tasse"]
    # Saldo anno corrente (pagato a giugno anno prossimo)
    saldo_futuro = imposta_corrente     # in primo anno: tutto; anni successivi: dipende da acconto versato
    if not primo_anno and lordo_precedente > 0:
        saldo_futuro = max(imposta_corrente - acconto_corrente, 0)

    netto_cassa = lordo_corrente - cfa_versata_totale - imposta_versata

    return {
        "lordo": lordo_corrente,
        "cfa_rate_minime": cfa_rate_minime,
        "cfa_conguaglio_prec": cfa_conguaglio_prec,
        "maternita": maternita,
        "cfa_versata_totale": cfa_versata_totale,
        "saldo_prec": saldo_prec,
        "acconto_corrente": acconto_corrente,
        "imposta_versata": imposta_versata,
        "netto_cassa": netto_cassa,
        # Uscite rinviate all'anno prossimo
        "cfa_conguaglio_futuro": cfa_conguaglio_futuro,
        "saldo_futuro": saldo_futuro,
        "totale_uscite_future": cfa_conguaglio_futuro + saldo_futuro,
    }


def genera_tabella_avvocato(risultati, al_tassa):
    """Tabella riepilogativa calcolo per competenza."""
    pct_cfa = int(ALIQUOTA_CFA * 100)
    pct_tax = int(al_tassa * 100)
    df = pd.DataFrame({
        "Voce": [
            "1. Fatturato (Onorari)",
            f"2. Abbattimento Forfetario ({int((1-COEFF_REDDITIVITA)*100)}% costi)",
            f"3. Reddito Professionale ({int(COEFF_REDDITIVITA*100)}%)",
            f"4. Cassa Forense – Soggettivo ({pct_cfa}% – deducibile per cassa)",
            "5. Contributo di Maternità CFA (deducibile per cassa)",
            "6. Base Imponibile Fiscale",
            f"7. Imposta Sostitutiva ({pct_tax}%)",
            "👉 NETTO PER COMPETENZA",
        ],
        "Importo (€)": [
            risultati["lordo"],
            -risultati["costi_forfettari"],
            risultati["reddito"],
            -risultati["cassa"],
            -risultati["maternita"],
            risultati["imponibile"],
            -risultati["tasse"],
            risultati["netto"],
        ],
    })
    return df


# ==============================================================================
#  PDF
# ==============================================================================
def create_pdf_avvocato(dati):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Intestazione
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="NOTA DI ONORARI / AVVISO DI PARCELLA", ln=1, align="C")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)

    # Dati Fornitore/Cliente
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 10, txt="AVVOCATO (Emittente):", border=0)
    pdf.cell(95, 10, txt="CLIENTE (Destinatario):", border=0, ln=1)
    pdf.set_font("Arial", "", 10)
    y_start = pdf.get_y()
    pdf.multi_cell(95, 5, txt=dati["mittente"])
    y_end_left = pdf.get_y()
    pdf.set_xy(105, y_start)
    pdf.multi_cell(95, 5, txt=dati["destinatario"])
    y_end_right = pdf.get_y()
    pdf.set_xy(10, max(y_end_left, y_end_right) + 10)

    # Dati Documento
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(200, 8, txt=f"Documento n. {dati['numero']} del {dati['data']}", ln=1, fill=True)
    pdf.ln(5)

    # Tabella voci
    pdf.set_font("Arial", "B", 10)
    pdf.cell(130, 8, txt="Descrizione", border=1)
    pdf.cell(60, 8, txt="Importo", border=1, align="R", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 8, txt=dati["descrizione"], border=1)
    pdf.cell(60, 8, txt=f"EUR {dati['onorari']:,.2f}", border=1, align="R", ln=1)
    pdf.cell(130, 8, txt="Contributo Integrativo CPA 4% (ex art. 11, L. 576/1980)", border=1)
    pdf.cell(60, 8, txt=f"EUR {dati['cpa']:,.2f}", border=1, align="R", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(130, 8, txt="TOTALE DOCUMENTO", border=0, align="R")
    pdf.cell(60, 8, txt=f"EUR {dati['totale_lordo']:,.2f}", border=1, align="R", ln=1)

    if dati["bollo"] > 0:
        pdf.set_font("Arial", "", 10)
        pdf.cell(130, 8, txt="Imposta di bollo (DPR 26.10.1972, n. 642 - All. A, art. 13)", border=0, align="R")
        pdf.cell(60, 8, txt=f"EUR {dati['bollo']:,.2f}", border=0, align="R", ln=1)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(130, 8, txt="TOTALE A PAGARE", border=0, align="R")
        pdf.cell(60, 8, txt=f"EUR {dati['totale_pagare']:,.2f}", border=0, align="R", ln=1)

    pdf.ln(15)

    # Note legali corrette
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 4, txt=(
        "Operazione effettuata ai sensi dell'art. 1, commi 54-89, L. 23.12.2014, n. 190 e s.m.i. "
        "(Regime Forfetario) - Operazione non soggetta ad IVA.\n"
        "Operazione non soggetta a ritenuta alla fonte a titolo di acconto "
        "ai sensi dell'art. 1, co. 67, L. 23.12.2014, n. 190.\n"
        "Contributo Integrativo CPA 4% ex art. 11, L. 20.09.1980, n. 576.\n"
        "Imposta di bollo assolta sull'originale ai sensi del DPR 26.10.1972, n. 642, "
        "Tariffa All. A, art. 13 - Euro 2,00."
        if dati["bollo"] > 0 else
        "Operazione effettuata ai sensi dell'art. 1, commi 54-89, L. 23.12.2014, n. 190 e s.m.i. "
        "(Regime Forfetario) - Operazione non soggetta ad IVA.\n"
        "Operazione non soggetta a ritenuta alla fonte a titolo di acconto "
        "ai sensi dell'art. 1, co. 67, L. 23.12.2014, n. 190.\n"
        "Contributo Integrativo CPA 4% ex art. 11, L. 20.09.1980, n. 576."
    ))

    pdf.ln(8)
    pdf.set_font("Arial", "BI", 7)
    pdf.set_text_color(200, 100, 0)
    pdf.multi_cell(0, 4, txt=(
        "AVVISO IMPORTANTE: Dal 01.01.2024 la fattura elettronica è OBBLIGATORIA per tutti i "
        "soggetti in regime forfetario (D.Lgs. 5.02.2021, n. 36). Questo documento è una "
        "nota pro-forma di supporto. La fattura ufficiale deve essere emessa e trasmessa "
        "tramite SDI con: Codice Regime Fiscale RF19 | Natura Operazione N2.2."
    ))

    return pdf.output(dest="S").encode("latin-1")


# ==============================================================================
#  TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📉 Dal Lordo al Netto",
    "🎯 Dal Netto al Lordo",
    "📝 Genera Fattura",
    "ℹ️ Info & Adempimenti",
])

# ──────────────────────────────────────────────────────────────────────────────
#  TAB 1 – DAL LORDO AL NETTO
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📉 Calcolo Redditività – Dal Lordo al Netto")
    st.write("Inserisci gli onorari annui incassati (esclusa CPA 4%).")
    lordo_input = st.number_input(
        "Compensi Lordi Annuo (€)", min_value=0.0, value=30_000.0, step=1_000.0, key="lordo_t1"
    )

    if st.button("CALCOLA NETTO", key="btn_netto"):
        if lordo_input <= 0:
            st.warning("Inserisci un valore di fatturato maggiore di zero.")
        else:
            risultati = calcoli_avvocato(lordo_input, aliquota_tassa, anni_iscrizione)
            incidenza_pct = risultati["peso_totale"] / lordo_input * 100

            # ── Soglie ──────────────────────────────────────────────────────
            if lordo_input >= SOGLIA_USCITA_IMMEDIATA:
                st.error(
                    f"🚨 **ATTENZIONE – USCITA IMMEDIATA DAL FORFETARIO!**\n\n"
                    f"Hai superato €{SOGLIA_USCITA_IMMEDIATA:,.0f}. La fuoriuscita dal regime "
                    f"forfetario si verifica **nell'anno stesso** (art. 1, co. 71, L. 190/2014):\n"
                    f"- Ai fini **IRPEF**: reddito rideterminato con criteri ordinari dall'inizio anno;\n"
                    f"- Ai fini **IVA**: applicazione dell'IVA a partire dall'operazione che ha "
                    f"determinato il superamento (emettere nota di variazione in aumento solo IVA "
                    f"per le fatture successive al superamento).\n\n"
                    f"**Contattare immediatamente lo Studio.**"
                )
            elif lordo_input > SOGLIA_FORFETTARIO:
                st.warning(
                    f"⚠️ **Attenzione: hai superato €{SOGLIA_FORFETTARIO:,.0f}.**\n\n"
                    f"Resti in regime forfetario per l'anno in corso, ma dal **1° gennaio "
                    f"dell'anno successivo** passerai al regime ordinario (IVA + IRPEF a scaglioni). "
                    f"Pianifica per tempo la transizione con lo Studio."
                )

            # ── Card netto ───────────────────────────────────────────────────
            st.markdown(f"""
            <div class="result-card">
                <h3>Netto Disponibile (per competenza):</h3>
                <h1 style="color: #002a52;">€ {risultati['netto']:,.2f}</h1>
                <div style="margin-top: 10px;">
                    <span style="color: #666; font-size: 0.9em;">Su un fatturato di € {lordo_input:,.2f}</span><br>
                    <span style="color: #D4AF37; font-weight: bold; font-size: 1.1em;">
                        Incidenza Cassa + Tasse: {incidenza_pct:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Tabella dettaglio ────────────────────────────────────────────
            st.write("#### 🔍 Dettaglio Fiscale (per competenza)")
            st.table(
                genera_tabella_avvocato(risultati, aliquota_tassa)
                .style.format({"Importo (€)": "€ {:,.2f}"})
            )
            st.info(
                "ℹ️ **Nota CPA:** In fattura aggiungi il **4% CPA** sugli onorari. "
                "Quella somma la incassi ma la versi integralmente a Cassa Forense (non è reddito tuo)."
            )

            # ── DISALLINEAMENTO COMPETENZA / CASSA ──────────────────────────
            st.markdown("---")
            st.markdown("### 🔄 Disallineamento Competenza / Cassa")
            st.markdown("""
> **Perché esiste questo disallineamento?**
>
> Il calcolo sopra è **per competenza**: attribuisce i contributi e le imposte
> all'anno in cui maturano, indipendentemente da quando vengono versati. Questo è
> lo standard per la pianificazione fiscale ed è corretto ai fini della
> determinazione del reddito imponibile.
>
> Tuttavia, il **principio di cassa** — che governa sia la deducibilità dei
> contributi previdenziali (art. 1, co. 64, L. 190/2014) sia i versamenti
> dell'imposta sostitutiva (saldo + acconti) — fa sì che le uscite monetarie
> effettive in un dato anno siano diverse da quanto mostrato nel calcolo di
> competenza.
>
> **In pratica:**
> - Il **conguaglio Cassa Forense** sull'anno corrente si paga entro il 30 settembre
>   dell'anno *successivo* (Mod. 5) → deducibile l'anno *prossimo*, non quello corrente.
> - L'**imposta sostitutiva** si versa come saldo dell'anno precedente (giugno) +
>   acconto dell'anno corrente (giugno + novembre, calcolato sull'anno precedente).
>   Per il **primo anno** non è dovuto alcun acconto.
""")

            # Input per il confronto
            with st.expander("⚙️ Configura e visualizza il confronto Competenza vs Cassa", expanded=True):
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    primo_anno_flag = st.checkbox(
                        "È il primo anno di attività?",
                        value=False,
                        help="Nel primo anno nessun acconto è dovuto e non esiste un conguaglio CFA dell'anno precedente."
                    )
                with col_c2:
                    if not primo_anno_flag:
                        lordo_prec = st.number_input(
                            "Fatturato anno precedente (€) – per il calcolo del conguaglio CFA e dell'acconto imposta",
                            min_value=0.0,
                            value=lordo_input,
                            step=1_000.0,
                            key="lordo_prec"
                        )
                    else:
                        lordo_prec = 0.0

                # Calcoli per cassa
                r_cassa = calcoli_cassa(
                    lordo_input, aliquota_tassa, anni_iscrizione,
                    primo_anno=primo_anno_flag, lordo_precedente=lordo_prec
                )
                r_comp = risultati  # già calcolato sopra

                diff_netto = r_cassa["netto_cassa"] - r_comp["netto"]
                diff_label = f"{'+'if diff_netto >= 0 else ''}{diff_netto:,.2f}"
                diff_color = "#27ae60" if diff_netto >= 0 else "#c0392b"

                # Tabella confronto affiancata
                st.markdown("#### 📊 Confronto Netto: Competenza vs Cassa")
                dati_cfr = pd.DataFrame({
                    "Voce": [
                        "Fatturato (Onorari)",
                        "── CFA: rate minime anno corrente",
                        "── CFA: conguaglio anno precedente (pagato a sett.)",
                        "── Contributo di Maternità CFA",
                        "= Totale CFA versato nell'anno",
                        "── Saldo imposta anno prec. (pagato a giugno)",
                        "── Acconto imposta anno corrente (giugno + nov.)",
                        "= Totale imposta versata nell'anno",
                        "✅ NETTO DISPONIBILE",
                    ],
                    "Per Competenza (€)": [
                        r_comp["lordo"],
                        -(r_comp["cassa"] if r_comp["cassa"] > 0 else 0),
                        "n/a (incluso sopra)",
                        -r_comp["maternita"],
                        -r_comp["cassa"] - r_comp["maternita"],
                        "n/a (incluso sotto)",
                        "n/a (incluso sotto)",
                        -r_comp["tasse"],
                        r_comp["netto"],
                    ],
                    "Per Cassa – Anno Corrente (€)": [
                        r_cassa["lordo"],
                        -r_cassa["cfa_rate_minime"],
                        -r_cassa["cfa_conguaglio_prec"],
                        -r_cassa["maternita"],
                        -r_cassa["cfa_versata_totale"],
                        -r_cassa["saldo_prec"],
                        -r_cassa["acconto_corrente"],
                        -r_cassa["imposta_versata"],
                        r_cassa["netto_cassa"],
                    ],
                })
                st.table(dati_cfr)

                # Riepilogo visivo
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("Netto per Competenza", f"€ {r_comp['netto']:,.2f}")
                with col_r2:
                    st.metric(
                        "Netto per Cassa (anno corrente)",
                        f"€ {r_cassa['netto_cassa']:,.2f}",
                        delta=f"{diff_label} €",
                        delta_color="normal"
                    )
                with col_r3:
                    st.metric(
                        "Uscite rinviate all'anno prossimo",
                        f"€ {r_cassa['totale_uscite_future']:,.2f}",
                        delta="da accantonare",
                        delta_color="inverse"
                    )

                # Spiegazione uscite future
                if r_cassa["totale_uscite_future"] > 0:
                    st.warning(
                        f"📅 **Pianificazione liquidità – Uscite rinviate all'anno prossimo:**\n\n"
                        f"- Conguaglio CFA anno corrente (Mod. 5, entro 30/9): "
                        f"**€ {r_cassa['cfa_conguaglio_futuro']:,.2f}**\n"
                        f"- Saldo imposta sostitutiva (entro 30/6): "
                        f"**€ {r_cassa['saldo_futuro']:,.2f}**\n\n"
                        f"**Totale da accantonare: € {r_cassa['totale_uscite_future']:,.2f}**\n\n"
                        f"Queste somme, pur non uscendo dal tuo conto nell'anno corrente, "
                        f"sono fiscalmente di competenza dell'anno corrente e ridurranno "
                        f"il tuo netto reale nell'anno prossimo. Metti da parte questa "
                        f"liquidità per evitare sorprese di cassa."
                    )

                # Nota metodologica
                if primo_anno_flag:
                    st.info(
                        "**Primo anno:** il netto per cassa è superiore perché non paghi "
                        "né l'acconto dell'imposta né il conguaglio CFA dell'anno precedente "
                        "(che non esiste). Attenzione: nell'**anno 2** dovrai versare sia "
                        "il conguaglio CFA del 1° anno sia il saldo + acconto sull'imposta "
                        "del 1° anno → picco di uscite nel secondo anno."
                    )
                else:
                    if abs(diff_netto) < 50:
                        st.info(
                            "**Anno a regime con reddito stabile:** netto per cassa ≈ netto per "
                            "competenza. Con reddito costante le uscite si compensano: il conguaglio "
                            "CFA che paghi è quello dell'anno scorso (pari a quello che pagherai "
                            "l'anno prossimo sul corrente), e l'acconto tasse eguaglia il dovuto. "
                            "Il disallineamento diventa rilevante quando il reddito varia "
                            "significativamente da un anno all'altro."
                        )
                    elif diff_netto > 0:
                        st.info(
                            "**Reddito in crescita rispetto all'anno scorso:** il conguaglio CFA "
                            "e l'acconto che paghi quest'anno sono calcolati sul reddito *precedente* "
                            "(più basso) → cash flow quest'anno migliore del dovuto per competenza. "
                            "Ma l'anno prossimo le uscite saranno più alte."
                        )
                    else:
                        st.info(
                            "**Reddito in calo rispetto all'anno scorso:** il conguaglio CFA "
                            "e l'acconto che paghi quest'anno sono calcolati sul reddito *precedente* "
                            "(più alto) → cash flow quest'anno peggiore del dovuto per competenza. "
                            "Valuta il metodo previsionale per l'acconto per ridurre le uscite."
                        )


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 2 – DAL NETTO AL LORDO
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🎯 Pianificazione Obiettivi – Dal Netto al Lordo")
    st.write("Inserisci quanto vuoi guadagnare 'pulito' in tasca (netto per competenza).")
    netto_input = st.number_input(
        "Netto Desiderato Annuo (€)", min_value=0.0, value=24_000.0, step=1_000.0
    )

    if st.button("CALCOLA FATTURATO NECESSARIO", key="btn_lordo"):
        if netto_input <= 0:
            st.warning("Inserisci un valore di netto maggiore di zero.")
        else:
            lordo_nec = calcola_lordo_da_netto_avvocato(netto_input, aliquota_tassa, anni_iscrizione)

            # ── Avvisi soglie ────────────────────────────────────────────────
            if lordo_nec >= SOGLIA_USCITA_IMMEDIATA:
                st.error(
                    f"🚨 Il fatturato necessario (€ {lordo_nec:,.2f}) **supera €{SOGLIA_USCITA_IMMEDIATA:,.0f}**: "
                    f"uscita immediata dal regime forfetario nell'anno stesso del superamento "
                    f"(art. 1, co. 71, L. 190/2014). Con il regime ordinario il calcolo cambia "
                    f"completamente. Contatta lo Studio per una pianificazione specifica."
                )
            elif lordo_nec > SOGLIA_FORFETTARIO:
                st.warning(
                    f"⚠️ Il fatturato necessario (€ {lordo_nec:,.2f}) **supera €{SOGLIA_FORFETTARIO:,.0f}**: "
                    f"resti forfetario nell'anno in corso, ma dal 1° gennaio dell'anno successivo "
                    f"passi al regime ordinario. Pianifica la transizione con lo Studio."
                )

            st.markdown(f"""
            <div class="result-card" style="border-color: #b8860b;">
                <h3>Devi Fatturare:</h3>
                <h1 style="color: #b8860b;">€ {lordo_nec:,.2f}</h1>
                <small>Per avere esattamente € {netto_input:,.2f} netti (per competenza)</small>
            </div>
            """, unsafe_allow_html=True)

            st.write("#### 🔢 Verifica del Calcolo Inverso")
            r_verifica = calcoli_avvocato(lordo_nec, aliquota_tassa, anni_iscrizione)
            st.table(
                genera_tabella_avvocato(r_verifica, aliquota_tassa)
                .style.format({"Importo (€)": "€ {:,.2f}"})
            )

            scarto = abs(r_verifica["netto"] - netto_input)
            if scarto < 1:
                st.success(f"✅ Verifica: netto calcolato € {r_verifica['netto']:,.2f} ≈ obiettivo € {netto_input:,.2f} (scarto < €1)")
            else:
                st.info(f"ℹ️ Scarto di verifica: € {scarto:.2f} (dovuto alla gestione del minimale CFA)")

            st.info(
                "ℹ️ Il netto mostrato è **per competenza**. Per il cash flow effettivo "
                "del primo anno, consulta la sezione 'Disallineamento Competenza/Cassa' nel tab precedente."
            )


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 3 – GENERA FATTURA
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📝 Generatore Nota di Onorari Pro-forma")

    st.error(
        "🔴 **OBBLIGO DI LEGGE – FATTURA ELETTRONICA:** Dal 01.01.2024 tutti i soggetti "
        "in regime forfetario sono obbligati alla fatturazione elettronica tramite SDI "
        "(D.Lgs. 5.02.2021, n. 36). Il PDF generato da questo strumento è una **nota "
        "pro-forma di supporto** per la comunicazione con il cliente. La fattura "
        "ufficiale deve essere emessa con: **Codice Regime RF19** | **Natura N2.2**. "
        "Sanzione per omessa e-fattura: dal 5% al 10% dell'imponibile (art. 6, D.Lgs. 471/1997)."
    )

    with st.form("form_fattura_avv"):
        c1, c2 = st.columns(2)
        with c1:
            mitt = st.text_area(
                "I tuoi Dati (Avv., Indirizzo, P.IVA, CF)",
                "Avv. Mario Rossi\nVia Legalità 1\n00100 Roma\nP.IVA 12345678901"
            )
            num = st.text_input("Numero Documento", f"{date.today().year}/001")
        with c2:
            dest = st.text_area("Dati Cliente", "Spett.le Cliente Srl\nVia Esempio 10\nMilano")
            data_doc = st.date_input("Data Documento", date.today())

        desc = st.text_input("Oggetto", "Attività di consulenza e assistenza legale...")
        onorari = st.number_input("Onorari (€) – esclusa CPA", min_value=0.0, value=1_000.0)

        if st.form_submit_button("📄 GENERA PDF PRO-FORMA"):
            cpa_val = onorari * 0.04
            tot_lordo = onorari + cpa_val
            bollo_val = 2.0 if tot_lordo > 77.47 else 0.0
            tot_pagare = tot_lordo + bollo_val

            dati_pdf = {
                "mittente": mitt, "destinatario": dest,
                "numero": num, "data": data_doc.strftime("%d/%m/%Y"),
                "descrizione": desc, "onorari": onorari,
                "cpa": cpa_val, "totale_lordo": tot_lordo,
                "bollo": bollo_val, "totale_pagare": tot_pagare,
            }

            st.info("**Anteprima importi:**")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            col_p1.metric("Onorari", f"€ {onorari:,.2f}")
            col_p2.metric("CPA 4%", f"€ {cpa_val:,.2f}")
            col_p3.metric("Totale Documento", f"€ {tot_lordo:,.2f}")
            col_p4.metric("Bollo", f"€ {bollo_val:,.2f}")
            st.markdown(f"### 💶 Totale a Pagare: € {tot_pagare:,.2f}")

            try:
                pdf_bytes = create_pdf_avvocato(dati_pdf)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = (
                    f'<a href="data:application/octet-stream;base64,{b64}" '
                    f'download="NotaOnorari_{num.replace("/","_")}.pdf" '
                    f'style="background-color: #D4AF37; color: #001529; padding: 10px 20px; '
                    f'text-decoration: none; border-radius: 5px; font-weight: bold;">'
                    f'📥 SCARICA PDF PRO-FORMA</a>'
                )
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Errore generazione PDF: {e}. Verifica requirements.txt (fpdf2).")


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 4 – INFO & ADEMPIMENTI
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### ℹ️ Regime Forfetario – Requisiti, Cause di Esclusione & Adempimenti")
    st.caption(f"Aggiornato al: 01.03.2026 | Riferimenti: L. 190/2014 s.m.i., L. 207/2024, Reg. Unico CFA vigente dal 01.01.2024")

    # ── Requisiti di accesso ──────────────────────────────────────────────────
    with st.expander("✅ Requisiti di Accesso al Regime Forfetario", expanded=True):
        st.markdown("""
**Può accedere (o rimanere) nel regime forfetario chi, nell'anno precedente, ha contemporaneamente:**

1. **Conseguito ricavi o compensi ≤ €85.000** (ragguagliati ad anno). Se si esercitano più attività
   con ATECO diversi, si considera la somma di tutti i compensi.

2. **Sostenuto spese per dipendenti/collaboratori ≤ €20.000** lordi (lavoro accessorio,
   dipendente, co.co.co., utili da partecipazione ad associati con apporto di solo lavoro).

*(Art. 1, co. 54, L. 190/2014 – come mod. dalla L. 197/2022 e L. 145/2018)*
""")

    # ── Cause di esclusione ───────────────────────────────────────────────────
    with st.expander("🚫 Cause di Esclusione (verificare ogni anno)", expanded=True):
        st.markdown("""
**Non possono applicare il regime forfetario:**

| Causa | Soglia / Condizione | Riferimento |
|-------|---------------------|-------------|
| Utilizzo di regimi IVA speciali o di regimi forfetari di determinazione del reddito | Qualsiasi | Art. 1, co. 57, lett. a) |
| Non residenza (salvo residenza UE/SEE con almeno 75% reddito prodotto in Italia) | — | Art. 1, co. 57, lett. b) |
| Attività esclusiva/prevalente: cessione fabbricati, terreni edificabili, mezzi di trasporto nuovi | — | Art. 1, co. 57, lett. c) |
| Partecipazione in società di persone, associazioni professionali, imprese familiari | — | Art. 1, co. 57, lett. d) |
| Controllo (diretto/indiretto) di SRL la cui attività è riconducibile a quella del contribuente | — | Art. 1, co. 57, lett. d) |
| **Redditi da lavoro dipendente/assimilati** (incl. pensioni) **> €35.000** nell'anno precedente | €35.000 (2025-2026) | Art. 1, co. 57, lett. d-ter); L. 207/2024, co. 13 |
| **Operatività prevalente con ex datore di lavoro** (ultimi 2 anni) che supera il 50% dei compensi | >50% dei compensi | Art. 1, co. 57, lett. d-bis) |

> ⚠️ **Nota soglia lavoro dipendente:** Il limite è stato elevato da €30.000 a **€35.000**
> dalla Legge di Bilancio 2025 (L. 207/2024, art. 1, co. 13) per il biennio **2025-2026**.
> L'esclusione **non si applica** se il rapporto di lavoro dipendente si è concluso entro
> il 31/12 dell'anno precedente (a condizione che in quell'anno non siano stati percepiti
> altri redditi da lavoro dipendente o pensione).

> ⚠️ **Nota ex datore di lavoro:** Se più del 50% dei tuoi compensi proviene da un soggetto
> che è stato tuo datore di lavoro o committente nei 2 anni precedenti, perdi il regime
> dall'anno successivo. È una causa ostativa fondamentale per gli avvocati che iniziano
> l'attività dopo una collaborazione.
""")

    # ── Superamento soglie ────────────────────────────────────────────────────
    with st.expander("📊 Cosa Succede se Superi i Limiti di Ricavi"):
        st.markdown("""
| Ricavi anno X | Conseguenza |
|---------------|-------------|
| **≤ €85.000** | Resti forfetario anche nell'anno X+1 ✅ |
| **€85.001 – €99.999** | Resti forfetario nell'anno X, **esci dal 1° gennaio X+1** ⚠️ |
| **≥ €100.000** | **Uscita immediata nell'anno X stesso** 🚨 |

**Dettaglio uscita immediata (>€100.000):**
- **IRPEF**: reddito rideterminato con criteri ordinari retroattivamente dall'**inizio dell'anno**;
- **IVA**: applicazione dell'IVA a partire dall'**operazione che ha determinato il superamento**;
  per le fatture già emesse senza IVA dopo il superamento: emettere nota di variazione
  in aumento di sola IVA (art. 26, DPR 633/1972).

*(Art. 1, co. 71, L. 190/2014; Circ. AE n. 32/E del 05.12.2023)*
""")

    # ── Scadenze e acconti ────────────────────────────────────────────────────
    with st.expander("📅 Scadenze Fiscali e Previdenziali"):
        st.markdown("""
**Imposta Sostitutiva (scadenze IRPEF – art. 17, DPR 435/2001):**

| Scadenza | Versamento |
|----------|-----------|
| 30 giugno (o 30 luglio +0,4%) | Saldo anno precedente + 1ª rata acconto 40% |
| 30 novembre | 2ª rata acconto 60% |

- **Acconto:** calcolato con metodo storico (100% imposta anno precedente) o previsionale.
- **Primo anno di attività:** nessun acconto dovuto.
- Codice tributo F24: **1792** (imposta sostitutiva persone fisiche regime forfetario).

**Contributi Cassa Forense – Minimali (rate fisse):**

| Rata | Scadenza 2025 |
|------|---------------|
| 1ª rata | 28 febbraio |
| 2ª rata | 31 maggio |
| 3ª rata | 31 luglio |
| 4ª rata + maternità | 30 settembre |

**Conguaglio CFA – Autoliquidazione (Mod. 5):** entro **30 settembre** dell'anno successivo.
""")

    # ── Fatturazione elettronica ──────────────────────────────────────────────
    with st.expander("🧾 Fatturazione Elettronica – Obblighi dal 01.01.2024"):
        st.markdown("""
**Dal 1° gennaio 2024 la fattura elettronica è obbligatoria per tutti i forfetari**
(D.Lgs. 5.02.2021, n. 36 – estensione dell'obbligo eliminando la soglia di ricavi).

**Dati obbligatori in fattura XML:**
- **Codice Regime Fiscale:** `RF19` (Regime Forfetario)
- **Natura Operazione:** `N2.2` (non soggetta – altri casi)
- **Ritenuta:** NON indicare (i forfetari sono esonerati)
- **Aliquota IVA:** non applicabile

**Termini di emissione:**
- Fattura immediata: entro **12 giorni** dall'operazione
- Fattura differita: entro il **15 del mese successivo**

**Sanzione per omessa/tardiva e-fattura:** dal **5% al 10%** dell'imponibile
(art. 6, D.Lgs. 471/1997).

*Eccezione: operatori sanitari che emettono fatture a persone fisiche restano esonerati
per preservare la privacy dei dati sanitari.*
""")

    # ── Note bollo ────────────────────────────────────────────────────────────
    with st.expander("📌 Imposta di Bollo e Nota CPA"):
        st.markdown("""
**Imposta di Bollo (DPR 26.10.1972, n. 642):**
- Si applica **€2,00** sulle fatture (anche elettroniche) per operazioni non soggette a IVA
  di importo **superiore a €77,47**.
- Base normativa: Tariffa Allegato A, art. 13, nota 2-ter, DPR 642/1972.
- Nelle fatture elettroniche: indicare il bollo con il tag `<BolloVirtuale>SI</BolloVirtuale>`
  e importo `2.00`. Il pagamento avviene tramite F24 entro il 20 del mese successivo
  al trimestre di riferimento (per importi totali > €250; sotto tale soglia: 31 gennaio
  dell'anno successivo).

**Contributo Integrativo CPA 4% (art. 11, L. 576/1980):**
- Va **addebitato al cliente** in aggiunta agli onorari ed è da questi pagato.
- Non è reddito del professionista: viene incassato e versato integralmente a Cassa Forense
  tramite il Modello 5 (autoliquidazione annuale).
- Nel regime forfetario la CPA incassata **non concorre al reddito imponibile**.
""")

# ==============================================================================
#  FOOTER
# ==============================================================================
st.markdown("""
<br>
<center style='color: #D4AF37; font-size: 0.8em;'>
Studio Gaetani © 2025 | 
<span style='color: #888;'>
Normativa di riferimento: L. 190/2014 s.m.i. · L. 207/2024 · Reg. Unico CFA vigente 01.01.2024 · D.Lgs. 36/2022
</span>
</center>
""", unsafe_allow_html=True)
