import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
import base64

# ─────────────────────────────────────────────────────────────────────────────
#  1. CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Studio Gaetani | Avvocati", page_icon="⚖️", layout="centered")

# ─────────────────────────────────────────────────────────────────────────────
#  2. LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    def password_entered():
        if (st.session_state["username"] in st.secrets["passwords"] and
                st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <style>
        .stApp{background:linear-gradient(180deg,#001529 0%,#001e3c 100%);}
        h1,h3,p{color:white;text-align:center;font-family:'Helvetica Neue',sans-serif;}
        .stTextInput>label{color:#D4AF37!important;font-weight:bold;}
        .stButton>button{background-color:#D4AF37;color:#001529;width:100%;border:none;}
        #MainMenu,header,footer{visibility:hidden;}
        input{color:white!important;}
        div[data-baseweb="input"]>div{background-color:#002a52!important;border-color:#D4AF37!important;}
        </style>""", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;margin-bottom:20px'><span style='font-size:60px'>⚖️</span></div>", unsafe_allow_html=True)
        st.markdown("<h1>STUDIO GAETANI</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#D4AF37;margin-top:-20px;font-style:italic'>Partner Fiscale dell'Avvocatura</h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<p style='color:white'>Accesso Area Riservata</p>", unsafe_allow_html=True)
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
    return True

if not check_password():
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  3. COSTANTI FISCALI E PREVIDENZIALI  ← aggiornare ogni anno
# ─────────────────────────────────────────────────────────────────────────────
ANNO_IMPOSTA = 2025

# Aliquota soggettiva CFA – Reg. Unico Previdenza Forense, art. 16, vigente 01.01.2024
# 16% per 2024-2025 → 17% dal 2026
ALIQUOTE_CFA   = {2024: 0.16, 2025: 0.16, 2026: 0.17}
ALIQUOTA_CFA   = ALIQUOTE_CFA.get(ANNO_IMPOSTA, 0.16)

# Minimali soggettivi 2025 (art. 21 Reg. Unico CFA)
MINIMO_PIENO   = 2_750.0   # Dal 9° anno di iscrizione
MINIMO_RIDOTTO = 1_375.0   # Dal 5° all'8° anno (50%)
# Anni 1-4: nessun minimo soggettivo (solo proporzionale)

# Contributo di maternità – art. 30 Reg. Unico CFA (fisso annuo, deducibile)
MATERNITA_CFA  = 96.76     # 2024; aggiornare per 2025 quando comunicato da CFA

# Soglie regime forfetario – art. 1, co. 54 e 71, L. 190/2014
SOGLIA_RF       = 85_000.0
SOGLIA_IMMEDIATA = 100_000.0

# Coefficiente di redditività ATECO 69.10.10 – Allegato 2, L. 145/2018
COEFF = 0.78

# ─────────────────────────────────────────────────────────────────────────────
#  4. CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#001529 0%,#001e3c 100%);}
#MainMenu,header,footer,[data-testid="stToolbar"]{visibility:hidden;display:none;}
h1,h2,h3,h4,h5,h6,p,li,div,label,span{color:#fff;font-family:'Helvetica Neue',sans-serif;}
a{color:#D4AF37!important;text-decoration:none;font-weight:bold;}
a:hover{color:#fff!important;text-decoration:underline;}
[data-testid="stSidebar"]{background-color:#000f1f;border-right:1px solid #D4AF37;}
hr{border-color:#D4AF37;opacity:.5;}
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
input,textarea,.stNumberInput input,.stTextInput input,.stTextArea textarea{
    color:#fff!important;caret-color:#D4AF37!important;font-weight:500;}
div[data-baseweb="input"]>div,div[data-baseweb="base-input"],textarea{
    background-color:#002a52!important;border:2px solid #D4AF37!important;border-radius:5px;}
.stSelectbox>label,.stNumberInput>label,.stRadio>label,.stCheckbox>label,
.stTextInput>label,.stDateInput>label,.stTextArea>label{
    color:#D4AF37!important;font-weight:bold;font-size:1.1em;margin-bottom:5px;}
div[data-baseweb="select"]>div{background-color:#002a52!important;border:2px solid #D4AF37!important;color:#fff!important;}
div[data-baseweb="select"] span{color:#fff!important;}
div[data-baseweb="select"] svg{fill:#fff!important;}
div[data-baseweb="popover"] div,ul[data-baseweb="menu"]{background-color:#001529!important;border:1px solid #D4AF37!important;}
li[data-baseweb="option"]{color:#fff!important;}
li[data-baseweb="option"]:hover,li[aria-selected="true"]{background-color:#D4AF37!important;color:#001529!important;}
.stButton>button{background-color:#001529;color:#D4AF37!important;font-weight:bold;
    border:2px solid #D4AF37;border-radius:8px;padding:.8rem 1rem;width:100%;text-transform:uppercase;}
.stButton>button:hover{background-color:#D4AF37;color:#001529!important;border-color:#fff;}
.result-card{background-color:#fff;padding:25px;border-radius:12px;border:3px solid #D4AF37;
    box-shadow:0 10px 30px rgba(0,0,0,.5);margin-bottom:25px;text-align:center;}
.result-card h1,.result-card h3,.result-card span,.result-card small,.result-card div{color:#001529!important;}
.result-card h1{font-size:2.8em!important;margin:10px 0!important;}
.dataframe{background-color:white;color:#333!important;border-radius:5px;}
.dataframe th{background-color:#D4AF37!important;color:#001529!important;}
.dataframe td{color:#333!important;}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  5. HEADER
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<div style='display:flex;justify-content:center;align-items:center;height:100%'><span style='font-size:3.5em'>⚖️</span></div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin-bottom:0'>STUDIO GAETANI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;margin-top:-10px;font-style:italic;font-weight:300'>Partner Fiscale dell'Avvocatura</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:#ccc;font-size:.9em;letter-spacing:1px;margin-bottom:10px'>CONTABILITÀ • PIANIFICAZIONE FISCALE • CONSULENZA TRIBUTARIA</div>", unsafe_allow_html=True)
    try:
        user_name = st.secrets["passwords"].get("user_display_name", "Gentile Cliente")
        st.markdown(f"<div style='background-color:#002a52;padding:5px 10px;border-radius:5px;display:inline-block;border:1px solid #D4AF37'><small>Area Riservata Clienti | 👤 <b>{user_name}</b></small></div>", unsafe_allow_html=True)
    except:
        st.markdown("<div style='background-color:#002a52;padding:5px 10px;border-radius:5px;display:inline-block;border:1px solid #D4AF37'><small>Area Riservata Clienti</small></div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
#  6. SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Parametri Fiscali")

regime_scelta = st.sidebar.radio(
    "Aliquota Imposta Sostitutiva:",
    ["Start-up (5%)", "Ordinario (15%)"],
    index=1
)
aliquota_tassa = 0.05 if "Start-up" in regime_scelta else 0.15

if "Start-up" in regime_scelta:
    st.sidebar.warning(
        "⚠️ **Requisiti aliquota 5%** (art. 1, co. 65, L. 190/2014):\n\n"
        "1. Nessuna attività professionale/d'impresa nei **3 anni precedenti**;\n"
        "2. L'attività non è continuazione di lavoro dipendente (salvo pratica forense);\n"
        "3. Attività eventualmente rilevata: ricavi ≤ €85.000 nell'anno prec.\n\n"
        "**Durata massima: 5 anni.**"
    )

anni_iscrizione = st.sidebar.selectbox(
    "Anni di iscrizione a Cassa Forense:",
    ["1° – 4° anno (nessun minimo sogg.)", "5° – 8° anno (minimo ridotto 50%)", "Dal 9° anno (minimo pieno)"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Dati Fiscali e Previdenziali")
st.sidebar.info(f"""
**Attività:** Studio Legale  
**Codice ATECO:** 69.10.10  
**Coeff. Redditività:** 78%

**Cassa Forense – Soggettivo:**  
• 2024-2025: **16%** (Reg. Unico CFA, art. 16)  
• Dal 2026: **17%**  
• Anno in uso: **{int(ALIQUOTA_CFA * 100)}%**

**CPA (Contributo Integrativo):** 4%  
*(addebitato al cliente in fattura)*  
**Minimo sogg. 2025:** €2.750 pieno / €1.375 ridotto  
**Contributo maternità 2024:** €96,76
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Risorse Ufficiali")
st.sidebar.markdown("""<div style="margin-left:5px;font-size:.9em">
<a href="https://www.cassaforense.it/" target="_blank">▪️ Cassa Forense</a><br>
<a href="https://www.agenziaentrate.gov.it/" target="_blank">▪️ Agenzia delle Entrate</a><br>
<a href="https://www.consiglionazionaleforense.it/" target="_blank">▪️ CNF</a>
</div>""", unsafe_allow_html=True)

if st.sidebar.button("Esci / Logout"):
    del st.session_state["password_correct"]
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  7. FUNZIONI DI CALCOLO
# ─────────────────────────────────────────────────────────────────────────────

def _minimo_cfa(anni_str: str) -> float:
    """Restituisce il minimo soggettivo CFA in base agli anni di iscrizione."""
    if "1°" in anni_str:
        return 0.0            # Anni 1-4: solo proporzionale (art. 21 Reg. Unico CFA)
    elif "5°" in anni_str:
        return MINIMO_RIDOTTO  # Anni 5-8: 50%
    return MINIMO_PIENO        # Dal 9° anno: pieno


def calcoli_avvocato(lordo: float, al_tassa: float, anni_str: str) -> dict:
    """
    CALCOLO PER COMPETENZA.

    Attribuisce contributi e imposte all'anno di maturazione (anno X).
    Usato per la pianificazione fiscale e la determinazione del reddito imponibile.

    Nota: i contributi CFA sono deducibili per cassa (art. 1, co. 64, L. 190/2014),
    cioè nell'anno in cui vengono effettivamente versati. Il conguaglio relativo
    all'anno X viene versato a settembre dell'anno X+1 e sarà deducibile in X+1.
    Questo genera un disallineamento rispetto al cash flow reale: vedi sezione
    'Disallineamento Competenza / Cassa'.
    """
    min_cfa = _minimo_cfa(anni_str)
    reddito        = lordo * COEFF
    cassa          = max(reddito * ALIQUOTA_CFA, min_cfa)
    maternita      = MATERNITA_CFA
    deduzioni      = cassa + maternita
    imponibile     = max(reddito - deduzioni, 0.0)
    tasse          = imponibile * al_tassa
    netto          = lordo - cassa - maternita - tasse
    return {
        "lordo":           lordo,
        "costi_forfettari": lordo * (1.0 - COEFF),
        "reddito":         reddito,
        "cassa":           cassa,
        "maternita":       maternita,
        "deduzioni":       deduzioni,
        "imponibile":      imponibile,
        "tasse":           tasse,
        "netto":           netto,
        "peso_totale":     cassa + maternita + tasse,
    }


def calcola_lordo_da_netto(netto_target: float, al_tassa: float, anni_str: str) -> float:
    """
    CALCOLO INVERSO: lordo necessario per ottenere un netto target (per competenza).

    Derivazione algebrica:
        netto = L - L·R·α_CFA - MAT - (L·R - L·R·α_CFA - MAT)·al
        netto = L·(1 - R·α_CFA - R·(1-α_CFA)·al) - MAT·(1-al)
        L = (netto + MAT·(1-al)) / (1 - R·α_CFA - R·(1-α_CFA)·al)

    Caso minimo (proporzionale < minimo CFA):
        netto = L - MIN - MAT - (L·R - MIN - MAT)·al
        netto = L·(1 - R·al) - (MIN+MAT)·(1-al)
        L = (netto + (MIN+MAT)·(1-al)) / (1 - R·al)
    """
    min_cfa = _minimo_cfa(anni_str)

    # ── Formula regime proporzionale ─────────────────────────────────────────
    fc  = COEFF * ALIQUOTA_CFA
    ft  = COEFF * (1.0 - ALIQUOTA_CFA) * al_tassa
    den = 1.0 - fc - ft
    if den <= 0:
        return 0.0
    lordo = (netto_target + MATERNITA_CFA * (1.0 - al_tassa)) / den

    # ── Se il proporzionale è sotto il minimo: usa formula a minimo ───────────
    if min_cfa > 0 and lordo * COEFF * ALIQUOTA_CFA < min_cfa:
        den2 = 1.0 - COEFF * al_tassa
        if den2 <= 0:
            return 0.0
        lordo = (netto_target + (min_cfa + MATERNITA_CFA) * (1.0 - al_tassa)) / den2

    return lordo


def calcoli_cassa(lordo_corrente: float, al_tassa: float, anni_str: str,
                  primo_anno: bool, lordo_precedente: float = 0.0) -> dict:
    """
    CALCOLO PER CASSA: uscite monetarie effettive nell'anno corrente.

    Schema versamenti Cassa Forense:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ Anno N – rate minime (4 rate: feb/mag/lug/set)                          │
    │ Anno N – conguaglio su reddito N-1 (Mod. 5, entro 30/9)   ← esce ora   │
    │ Anno N+1 – conguaglio su reddito N (Mod. 5, entro 30/9)   ← rinviato   │
    └─────────────────────────────────────────────────────────────────────────┘

    Schema versamenti Imposta Sostitutiva:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ Anno N, giugno  – saldo imposta N-1 + 1ª acconto 40% su N-1            │
    │ Anno N, novembre – 2ª acconto 60% su N-1                               │
    │ Anno N+1, giugno – saldo imposta N                         ← rinviato  │
    └─────────────────────────────────────────────────────────────────────────┘

    Primo anno: nessun acconto imposta; nessun conguaglio CFA precedente.
    """
    min_cfa = _minimo_cfa(anni_str)

    # ── CFA in uscita nell'anno corrente ─────────────────────────────────────
    cfa_rate_minime = min_cfa
    maternita       = MATERNITA_CFA

    if primo_anno or lordo_precedente <= 0:
        cfa_conguaglio_prec = 0.0
    else:
        reddito_prec        = lordo_precedente * COEFF
        cfa_totale_prec     = max(reddito_prec * ALIQUOTA_CFA, min_cfa)
        cfa_conguaglio_prec = max(cfa_totale_prec - min_cfa, 0.0)

    cfa_versata = cfa_rate_minime + cfa_conguaglio_prec + maternita

    # ── Imposta in uscita nell'anno corrente ──────────────────────────────────
    if primo_anno or lordo_precedente <= 0:
        saldo_prec       = 0.0
        acconto_corrente = 0.0
        imposta_versata  = 0.0
    else:
        # Imposta dovuta sull'anno precedente (base per metodo storico)
        r_prec       = calcoli_avvocato(lordo_precedente, al_tassa, anni_str)
        imposta_prec = r_prec["tasse"]
        # Saldo anno N-1: imposta N-1 meno acconto versato in N-1.
        # Con reddito stabile, acconto pagato in N-1 ≈ imposta N-1 → saldo ≈ 0.
        # Se il reddito è cambiato il saldo sarà diverso; il calcolo esatto
        # richiede la dichiarazione dell'anno precedente.
        acconto_versato_in_prec = imposta_prec  # ipotesi reddito stabile N-2 ≈ N-1
        saldo_prec       = max(imposta_prec - acconto_versato_in_prec, 0.0)
        acconto_corrente = imposta_prec          # 100% metodo storico
        imposta_versata  = saldo_prec + acconto_corrente

    netto_cassa = lordo_corrente - cfa_versata - imposta_versata

    # ── Uscite rinviate all'anno prossimo (da accantonare) ───────────────────
    reddito_corrente    = lordo_corrente * COEFF
    cfa_totale_corrente = max(reddito_corrente * ALIQUOTA_CFA, min_cfa)
    cfa_futuro          = max(cfa_totale_corrente - min_cfa, 0.0)

    r_corr        = calcoli_avvocato(lordo_corrente, al_tassa, anni_str)
    imposta_corr  = r_corr["tasse"]
    if primo_anno or lordo_precedente <= 0:
        saldo_futuro = imposta_corr          # Tutto il saldo è rinviato
    else:
        saldo_futuro = max(imposta_corr - acconto_corrente, 0.0)

    return {
        "lordo":               lordo_corrente,
        "cfa_rate_minime":     cfa_rate_minime,
        "cfa_conguaglio_prec": cfa_conguaglio_prec,
        "maternita":           maternita,
        "cfa_versata":         cfa_versata,
        "saldo_prec":          saldo_prec,
        "acconto_corrente":    acconto_corrente,
        "imposta_versata":     imposta_versata,
        "netto_cassa":         netto_cassa,
        # rinviato all'anno prossimo
        "cfa_futuro":          cfa_futuro,
        "saldo_futuro":        saldo_futuro,
        "totale_futuro":       cfa_futuro + saldo_futuro,
    }


def genera_tabella(r: dict, al_tassa: float) -> pd.DataFrame:
    """Tabella riepilogativa per competenza."""
    pct_cfa  = int(ALIQUOTA_CFA * 100)
    pct_cost = round((1.0 - COEFF) * 100)   # ← round() per evitare 21.99…%
    pct_tax  = int(al_tassa * 100)
    return pd.DataFrame({
        "Voce": [
            "1. Fatturato (Onorari)",
            f"2. Abbattimento Forfetario ({pct_cost}% costi)",
            f"3. Reddito Professionale ({int(COEFF*100)}%)",
            f"4. Cassa Forense – Soggettivo ({pct_cfa}%, deducibile per cassa)",
            "5. Contributo di Maternità CFA (deducibile per cassa)",
            "6. Base Imponibile Fiscale",
            f"7. Imposta Sostitutiva ({pct_tax}%)",
            "👉 NETTO (per competenza)",
        ],
        "Importo (€)": [
            r["lordo"],
            -r["costi_forfettari"],
            r["reddito"],
            -r["cassa"],
            -r["maternita"],
            r["imponibile"],
            -r["tasse"],
            r["netto"],
        ],
    })


# ─────────────────────────────────────────────────────────────────────────────
#  8. PDF
# ─────────────────────────────────────────────────────────────────────────────
def create_pdf(dati: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="NOTA DI ONORARI / AVVISO DI PARCELLA", ln=1, align="C")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 10, txt="AVVOCATO (Emittente):", border=0)
    pdf.cell(95, 10, txt="CLIENTE (Destinatario):", border=0, ln=1)
    pdf.set_font("Arial", "", 10)
    y0 = pdf.get_y()
    pdf.multi_cell(95, 5, txt=dati["mittente"])
    yl = pdf.get_y()
    pdf.set_xy(105, y0)
    pdf.multi_cell(95, 5, txt=dati["destinatario"])
    yr = pdf.get_y()
    pdf.set_xy(10, max(yl, yr) + 10)

    pdf.set_fill_color(240, 240, 240)
    pdf.cell(200, 8, txt=f"Documento n. {dati['numero']} del {dati['data']}", ln=1, fill=True)
    pdf.ln(5)

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
        pdf.cell(130, 8, txt="Imposta di bollo (DPR 26.10.1972, n. 642 – All. A, art. 13)", border=0, align="R")
        pdf.cell(60, 8, txt=f"EUR {dati['bollo']:,.2f}", border=0, align="R", ln=1)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(130, 8, txt="TOTALE A PAGARE", border=0, align="R")
        pdf.cell(60, 8, txt=f"EUR {dati['totale_pagare']:,.2f}", border=0, align="R", ln=1)

    pdf.ln(15)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(80, 80, 80)
    note_base = (
        "Operazione effettuata ai sensi dell'art. 1, commi 54-89, L. 23.12.2014, n. 190 e s.m.i. "
        "(Regime Forfetario) – Operazione non soggetta ad IVA.\n"
        "Operazione non soggetta a ritenuta alla fonte a titolo di acconto "
        "ai sensi dell'art. 1, co. 67, L. 23.12.2014, n. 190.\n"
        "Contributo Integrativo CPA 4% ex art. 11, L. 20.09.1980, n. 576."
    )
    if dati["bollo"] > 0:
        note_base += ("\nImposta di bollo assolta sull'originale ai sensi del DPR 26.10.1972, n. 642, "
                      "Tariffa All. A, art. 13 – Euro 2,00.")
    pdf.multi_cell(0, 4, txt=note_base)
    pdf.ln(6)
    pdf.set_font("Arial", "BI", 7)
    pdf.set_text_color(180, 80, 0)
    pdf.multi_cell(0, 4, txt=(
        "AVVISO: Dal 01.01.2024 la fattura elettronica e' OBBLIGATORIA per tutti i forfetari "
        "(D.Lgs. 36/2022). Questo e' un documento pro-forma. La fattura ufficiale va emessa "
        "tramite SDI con: Codice Regime RF19 | Natura Operazione N2.2."
    ))
    return pdf.output(dest="S").encode("latin-1")


# ─────────────────────────────────────────────────────────────────────────────
#  9. TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📉 Dal Lordo al Netto",
    "🎯 Dal Netto al Lordo",
    "📝 Genera Fattura",
    "ℹ️ Info & Adempimenti",
])

# ═════════════════════════════════════════════════════════════════════════════
#  TAB 1 – DAL LORDO AL NETTO
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📉 Calcolo Redditività – Dal Lordo al Netto")
    st.write("Inserisci gli onorari annui incassati (esclusa CPA 4%).")

    lordo_input = st.number_input(
        "Compensi Lordi Annuo (€)",
        min_value=0.0, value=30_000.0, step=1_000.0, key="lordo_t1"
    )

    if st.button("CALCOLA NETTO", key="btn_netto"):
        # Salvo lordo in session_state: la sezione risultati/disallineamento
        # rimane visibile e reattiva anche quando l'utente interagisce
        # con checkbox/number_input senza ricliccare il bottone.
        st.session_state["lordo1_saved"] = lordo_input

    # ── Tutto ciò che segue si renderizza ogni volta che lordo1_saved esiste ─
    if "lordo1_saved" in st.session_state:
        L = st.session_state["lordo1_saved"]

        # Ricalcolo sempre con i parametri sidebar correnti (si aggiorna
        # automaticamente se l'utente cambia aliquota o anni in sidebar)
        r = calcoli_avvocato(L, aliquota_tassa, anni_iscrizione)
        incidenza_pct = r["peso_totale"] / L * 100 if L > 0 else 0

        # ── Avvisi soglie ────────────────────────────────────────────────────
        if L >= SOGLIA_IMMEDIATA:
            st.error(
                f"🚨 **USCITA IMMEDIATA DAL FORFETARIO** – Superato €{SOGLIA_IMMEDIATA:,.0f}\n\n"
                f"**IRPEF:** reddito rideterminato con criteri ordinari retroattivamente dall'1/1.\n"
                f"**IVA:** applicata a partire dall'operazione che ha causato il superamento "
                f"(emettere nota di variazione in aumento di sola IVA sulle fatture successive).\n\n"
                f"*(Art. 1, co. 71, L. 190/2014 – Circ. AE 32/E del 05.12.2023)*\n\n"
                f"**Contattare immediatamente lo Studio.**"
            )
        elif L > SOGLIA_RF:
            st.warning(
                f"⚠️ **Superato €{SOGLIA_RF:,.0f}** – Regime forfetario mantenuto per l'anno corrente, "
                f"ma **uscita obbligatoria dal 1° gennaio dell'anno successivo** "
                f"(regime ordinario: IVA + IRPEF a scaglioni). Pianifica la transizione."
            )

        # ── Card netto ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="result-card">
            <h3>Netto Disponibile (per competenza):</h3>
            <h1 style="color:#002a52">€ {r['netto']:,.2f}</h1>
            <div style="margin-top:10px">
                <span style="color:#666;font-size:.9em">Su un fatturato di € {L:,.2f}</span><br>
                <span style="color:#D4AF37;font-weight:bold;font-size:1.1em">
                    Incidenza Cassa + Tasse: {incidenza_pct:.1f}%
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabella per competenza ────────────────────────────────────────────
        st.write("#### 🔍 Dettaglio Fiscale (per competenza)")
        st.table(genera_tabella(r, aliquota_tassa).style.format({"Importo (€)": "€ {:,.2f}"}))
        st.info(
            "ℹ️ **Nota CPA:** In fattura aggiungi il **4% CPA** sugli onorari. "
            "Incassi quella somma ma la versi integralmente a Cassa Forense – non è reddito tuo."
        )

        # ════════════════════════════════════════════════════════════════════
        #  SEZIONE DISALLINEAMENTO COMPETENZA / CASSA
        #  Questa sezione è FUORI dal blocco if st.button, quindi i widget
        #  interni (checkbox, number_input) sono sempre interattivi e
        #  Streamlit riesegue il confronto ad ogni loro modifica.
        # ════════════════════════════════════════════════════════════════════
        st.markdown("---")
        st.markdown("### 🔄 Disallineamento Competenza / Cassa")

        st.markdown("""
> **Perché esiste questo disallineamento?**
>
> Il calcolo sopra è **per competenza**: attribuisce contributi e imposte
> all'anno in cui maturano, indipendentemente da quando vengono versati.
> Questo è lo standard per la pianificazione fiscale ed è corretto ai fini
> della determinazione del reddito imponibile (art. 1, co. 64, L. 190/2014).
>
> Tuttavia, le uscite monetarie *effettive* nell'anno seguono il **principio
> di cassa**:
> - Il **conguaglio CFA** dell'anno corrente si versa a settembre dell'anno
>   *prossimo* (Mod. 5) → le rate versate ora sono quelle sull'anno *precedente*.
> - L'**imposta sostitutiva** si paga come saldo dell'anno scorso (giugno) +
>   acconto calcolato sull'anno scorso (giugno + novembre). Il saldo
>   dell'anno corrente uscirà a giugno dell'anno *prossimo*.
> - Nel **primo anno** non è dovuto alcun acconto imposta e non esiste
>   conguaglio CFA precedente → cassa molto più alta, ma il "conto" arriva
>   tutto nel secondo anno.
""")

        # ── Configuratore ────────────────────────────────────────────────────
        st.markdown("#### ⚙️ Configura il confronto")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            primo_anno = st.checkbox(
                "Primo anno di attività",
                value=False,
                key="primo_anno_t1",
                help="Se spuntato: nessun acconto imposta, nessun conguaglio CFA precedente."
            )
        with col_c2:
            lordo_prec = 0.0
            if not primo_anno:
                lordo_prec = st.number_input(
                    "Fatturato anno precedente (€)",
                    min_value=0.0,
                    value=L,
                    step=1_000.0,
                    key="lordo_prec_t1",
                    help="Usato per calcolare conguaglio CFA e acconto imposta dell'anno corrente."
                )

        # ── Calcoli per cassa ────────────────────────────────────────────────
        rc = calcoli_cassa(L, aliquota_tassa, anni_iscrizione, primo_anno, lordo_prec)

        diff        = rc["netto_cassa"] - r["netto"]
        diff_str    = f"{'+'if diff >= 0 else ''}{diff:,.2f}"
        diff_color  = "#27ae60" if diff >= 0 else "#c0392b"

        # ── Tabella confronto ─────────────────────────────────────────────────
        st.markdown("#### 📊 Confronto Netto: Per Competenza vs Per Cassa")
        cfr = pd.DataFrame({
            "Voce": [
                "Fatturato (Onorari)",
                "  ├ CFA – rate minime anno corrente",
                "  ├ CFA – conguaglio anno prec. (set.)",
                "  ├ Contributo di maternità",
                "  └ Totale CFA versata nell'anno",
                "  ├ Saldo imposta anno prec. (giugno)",
                "  ├ Acconto imposta anno corr. (giu.+nov.)",
                "  └ Totale imposta versata nell'anno",
                "✅ NETTO DISPONIBILE",
            ],
            "Per Competenza (€)": [
                f"€ {r['lordo']:,.2f}",
                "– (incluso nel proporzionale)",
                "– (incluso nel proporzionale)",
                f"€ {-r['maternita']:,.2f}",
                f"€ {-(r['cassa'] + r['maternita']):,.2f}",
                "– (incluso nel totale)",
                "– (incluso nel totale)",
                f"€ {-r['tasse']:,.2f}",
                f"€ {r['netto']:,.2f}",
            ],
            "Per Cassa – Anno Corrente (€)": [
                f"€ {rc['lordo']:,.2f}",
                f"€ {-rc['cfa_rate_minime']:,.2f}",
                f"€ {-rc['cfa_conguaglio_prec']:,.2f}",
                f"€ {-rc['maternita']:,.2f}",
                f"€ {-rc['cfa_versata']:,.2f}",
                f"€ {-rc['saldo_prec']:,.2f}",
                f"€ {-rc['acconto_corrente']:,.2f}",
                f"€ {-rc['imposta_versata']:,.2f}",
                f"€ {rc['netto_cassa']:,.2f}",
            ],
        })
        st.table(cfr)

        # ── Metriche riepilogative ────────────────────────────────────────────
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Netto per competenza",   f"€ {r['netto']:,.2f}")
        col_m2.metric(
            "Netto per cassa (anno corr.)",
            f"€ {rc['netto_cassa']:,.2f}",
            delta=f"{diff_str} €",
            delta_color="normal"
        )
        col_m3.metric(
            "Da accantonare (anno pross.)",
            f"€ {rc['totale_futuro']:,.2f}",
            delta="uscita futura",
            delta_color="inverse"
        )

        # ── Box uscite future ─────────────────────────────────────────────────
        if rc["totale_futuro"] > 0:
            st.warning(
                f"📅 **Uscite rinviate all'anno prossimo – da accantonare subito:**\n\n"
                f"- Conguaglio CFA anno corrente (Mod. 5, entro 30/9 anno pross.): "
                f"**€ {rc['cfa_futuro']:,.2f}**\n"
                f"- Saldo imposta sostitutiva anno corrente (giugno anno pross.): "
                f"**€ {rc['saldo_futuro']:,.2f}**\n\n"
                f"**Totale da accantonare: € {rc['totale_futuro']:,.2f}**\n\n"
                f"Queste somme non escono dal conto nell'anno corrente, ma sono di competenza "
                f"fiscale di quest'anno e peseranno sulla liquidità dell'anno prossimo. "
                f"Mettile da parte fin da ora."
            )

        # ── Commento contestuale ──────────────────────────────────────────────
        if primo_anno:
            st.info(
                "**Primo anno:** il netto per cassa è significativamente più alto perché non "
                "paghi né acconto imposta né conguaglio CFA dell'anno precedente. "
                "Attenzione: nell'**anno 2** arriveranno insieme conguaglio CFA del 1° anno "
                "e saldo + acconto sull'imposta del 1° anno → picco di uscite da pianificare."
            )
        elif abs(diff) < 100:
            st.info(
                "**Reddito stabile anno su anno:** il disallineamento è minimo. "
                "Quello che versi quest'anno come conguaglio CFA e acconto "
                "è circa uguale a quello che verrà rinviato all'anno prossimo. "
                "Il disallineamento diventa rilevante quando il reddito varia "
                "significativamente da un anno all'altro."
            )
        elif diff > 0:
            st.info(
                "**Reddito in crescita rispetto all'anno scorso:** conguaglio CFA e acconto "
                "imposta che versi ora sono calcolati sul reddito *precedente* (più basso). "
                "Il cash flow di quest'anno è migliore del dovuto per competenza, "
                "ma l'anno prossimo le uscite saranno più alte."
            )
        else:
            st.info(
                "**Reddito in calo rispetto all'anno scorso:** conguaglio CFA e acconto "
                "imposta sono calcolati sul reddito *precedente* (più alto). "
                "Il cash flow di quest'anno è peggiore del dovuto per competenza. "
                "Considera il metodo previsionale per ridurre gli acconti."
            )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 2 – DAL NETTO AL LORDO
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🎯 Pianificazione Obiettivi – Dal Netto al Lordo")
    st.write("Inserisci quanto vuoi guadagnare netto (per competenza).")

    netto_input = st.number_input(
        "Netto Desiderato Annuo (€)",
        min_value=0.0, value=24_000.0, step=1_000.0
    )

    if st.button("CALCOLA FATTURATO NECESSARIO", key="btn_lordo"):
        st.session_state["netto2_saved"] = netto_input

    if "netto2_saved" in st.session_state:
        N = st.session_state["netto2_saved"]
        lordo_nec = calcola_lordo_da_netto(N, aliquota_tassa, anni_iscrizione)

        # ── Avvisi soglie ────────────────────────────────────────────────────
        if lordo_nec >= SOGLIA_IMMEDIATA:
            st.error(
                f"🚨 Il fatturato necessario (€ {lordo_nec:,.2f}) supera €{SOGLIA_IMMEDIATA:,.0f}: "
                f"uscita immediata dal forfetario nell'anno stesso del superamento. "
                f"Con regime ordinario il calcolo cambia completamente. Contatta lo Studio."
            )
        elif lordo_nec > SOGLIA_RF:
            st.warning(
                f"⚠️ Il fatturato necessario (€ {lordo_nec:,.2f}) supera €{SOGLIA_RF:,.0f}: "
                f"resti forfetario nell'anno in corso, ma dal 1° gennaio dell'anno successivo "
                f"passi al regime ordinario. Pianifica con lo Studio."
            )

        st.markdown(f"""
        <div class="result-card" style="border-color:#b8860b">
            <h3>Devi Fatturare:</h3>
            <h1 style="color:#b8860b">€ {lordo_nec:,.2f}</h1>
            <small>Per avere esattamente € {N:,.2f} netti (per competenza)</small>
        </div>
        """, unsafe_allow_html=True)

        st.write("#### 🔢 Verifica del Calcolo Inverso")
        r_v = calcoli_avvocato(lordo_nec, aliquota_tassa, anni_iscrizione)
        st.table(genera_tabella(r_v, aliquota_tassa).style.format({"Importo (€)": "€ {:,.2f}"}))

        scarto = abs(r_v["netto"] - N)
        if scarto < 1.0:
            st.success(f"✅ Verifica: netto calcolato € {r_v['netto']:,.2f} ≈ obiettivo € {N:,.2f} (scarto < €1)")
        else:
            st.info(
                f"ℹ️ Scarto di verifica: € {scarto:.2f} "
                f"(dovuto alla gestione del minimale CFA o arrotondamenti)."
            )

        st.info(
            "ℹ️ Il netto è calcolato **per competenza**. Per il cash flow effettivo "
            "dell'anno (specialmente il primo), consulta la sezione "
            "'🔄 Disallineamento Competenza / Cassa' nel tab **📉 Dal Lordo al Netto**."
        )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 3 – GENERA FATTURA
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📝 Generatore Nota di Onorari Pro-forma")
    st.error(
        "🔴 **OBBLIGO DI LEGGE – FATTURA ELETTRONICA**\n\n"
        "Dal 01.01.2024 tutti i soggetti in regime forfetario sono obbligati alla "
        "fatturazione elettronica tramite SDI (D.Lgs. 5.02.2021, n. 36). "
        "Il PDF generato qui è una **nota pro-forma di supporto** per il cliente. "
        "La fattura ufficiale deve essere emessa con: "
        "**Codice Regime RF19** | **Natura N2.2**. "
        "Sanzione per omessa e-fattura: dal 5% al 10% dell'imponibile "
        "(art. 6, D.Lgs. 471/1997)."
    )

    with st.form("form_fattura"):
        c1, c2 = st.columns(2)
        with c1:
            mitt    = st.text_area("I tuoi Dati (Avv., Indirizzo, P.IVA, CF)",
                                   "Avv. Mario Rossi\nVia Legalità 1\n00100 Roma\nP.IVA 12345678901")
            num     = st.text_input("Numero Documento", f"{date.today().year}/001")
        with c2:
            dest    = st.text_area("Dati Cliente", "Spett.le Cliente Srl\nVia Esempio 10\nMilano")
            data_doc = st.date_input("Data Documento", date.today())
        desc    = st.text_input("Oggetto", "Attività di consulenza e assistenza legale...")
        onorari = st.number_input("Onorari (€) – esclusa CPA 4%", min_value=0.0, value=1_000.0)

        if st.form_submit_button("📄 GENERA PDF PRO-FORMA"):
            cpa_val    = onorari * 0.04
            tot_lordo  = onorari + cpa_val
            bollo_val  = 2.0 if tot_lordo > 77.47 else 0.0
            tot_pagare = tot_lordo + bollo_val

            dati_pdf = {
                "mittente": mitt, "destinatario": dest,
                "numero": num,    "data": data_doc.strftime("%d/%m/%Y"),
                "descrizione": desc, "onorari": onorari,
                "cpa": cpa_val,   "totale_lordo": tot_lordo,
                "bollo": bollo_val, "totale_pagare": tot_pagare,
            }

            st.info("**Anteprima importi:**")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            col_p1.metric("Onorari",          f"€ {onorari:,.2f}")
            col_p2.metric("CPA 4%",           f"€ {cpa_val:,.2f}")
            col_p3.metric("Totale Documento", f"€ {tot_lordo:,.2f}")
            col_p4.metric("Bollo",            f"€ {bollo_val:,.2f}")
            st.markdown(f"### 💶 Totale a Pagare: € {tot_pagare:,.2f}")

            try:
                pdf_bytes = create_pdf(dati_pdf)
                b64  = base64.b64encode(pdf_bytes).decode()
                href = (
                    f'<a href="data:application/octet-stream;base64,{b64}" '
                    f'download="NotaOnorari_{num.replace("/","_")}.pdf" '
                    f'style="background-color:#D4AF37;color:#001529;padding:10px 20px;'
                    f'text-decoration:none;border-radius:5px;font-weight:bold">'
                    f'📥 SCARICA PDF PRO-FORMA</a>'
                )
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Errore generazione PDF: {e}. Verifica requirements.txt (fpdf2).")


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 4 – INFO & ADEMPIMENTI
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ℹ️ Regime Forfetario – Requisiti, Cause di Esclusione & Adempimenti")
    st.caption("Aggiornato al 01.03.2026 | L. 190/2014 s.m.i. · L. 207/2024 · Reg. Unico CFA dal 01.01.2024 · D.Lgs. 36/2022")

    with st.expander("✅ Requisiti di Accesso", expanded=True):
        st.markdown("""
**Può accedere (o rimanere) nel regime forfetario chi, nell'anno precedente, ha contemporaneamente:**

1. **Conseguito ricavi o compensi ≤ €85.000** (ragguagliati ad anno). Se si esercitano più attività
   con codici ATECO diversi, si considera la somma di tutti i compensi.
2. **Sostenuto spese per dipendenti/collaboratori ≤ €20.000** lordi (lavoro accessorio,
   dipendente, co.co.co., utili da partecipazione ad associati con apporto di solo lavoro).

*(Art. 1, co. 54, L. 190/2014 – come modificato da L. 197/2022 e L. 145/2018)*
""")

    with st.expander("🚫 Cause di Esclusione (verificare ogni anno)"):
        st.markdown("""
| Causa | Soglia / Condizione | Riferimento |
|-------|---------------------|-------------|
| Regimi IVA speciali o regimi forfetari di determinazione del reddito | Qualsiasi | Art. 1, co. 57, lett. a) |
| Non residenza (salvo UE/SEE con ≥75% reddito in Italia) | — | Art. 1, co. 57, lett. b) |
| Attività escl./prev.: cessione fabbricati, terreni edificabili, mezzi di trasporto nuovi | — | Art. 1, co. 57, lett. c) |
| Partecipazione in soc. persone, associazioni professionali, imprese familiari | — | Art. 1, co. 57, lett. d) |
| Controllo (diretto/indiretto) di SRL con attività riconducibile a quella individuale | — | Art. 1, co. 57, lett. d) |
| **Redditi da lav. dip./assimilati (incl. pensioni) > €35.000** nell'anno precedente | **€35.000** (2025-2026) | Art. 1, co. 57, lett. d-ter); **L. 207/2024, co. 13** |
| **Prevalenza operatività con ex datore di lavoro** (ultimi 2 anni) > 50% compensi | >50% dei compensi | Art. 1, co. 57, lett. d-bis) |

> ⚠️ **Soglia lavoro dipendente 2025-2026:** elevata da €30.000 a **€35.000** dalla Legge di
> Bilancio 2025 (L. 207/2024, art. 1, co. 13), confermata per il 2026. L'esclusione
> **non si applica** se il rapporto dipendente è cessato entro il 31/12 dell'anno precedente
> (senza altri redditi da lavoro o pensione nello stesso anno).

> ⚠️ **Causa ostativa ex datore:** se più del 50% dei tuoi compensi proviene da un soggetto
> che è stato tuo datore di lavoro o committente nei 2 anni precedenti, perdi il regime
> dall'anno successivo (art. 1, co. 57, lett. d-bis, L. 190/2014). Cruciale per chi
> avvia l'attività forense dopo una collaborazione o rapporto dipendente.
""")

    with st.expander("📊 Cosa Succede se Superi i Limiti di Ricavi"):
        st.markdown("""
| Ricavi anno X | Conseguenza |
|---------------|-------------|
| **≤ €85.000** | Resti forfetario anche nell'anno X+1 ✅ |
| **€85.001 – €99.999** | Resti forfetario nell'anno X, **esci dal 1° gennaio X+1** ⚠️ |
| **≥ €100.000** | **Uscita immediata nell'anno X stesso** 🚨 |

**Dettaglio uscita immediata (≥ €100.000):**
- **IRPEF**: reddito rideterminato con criteri ordinari retroattivamente dall'**1° gennaio**;
- **IVA**: si applica a partire dall'**operazione che ha determinato il superamento**;
  per le fatture già emesse senza IVA dopo il superamento: nota di variazione in aumento
  di sola IVA (art. 26, DPR 633/1972).

*(Art. 1, co. 71, L. 190/2014; Circ. AE n. 32/E del 05.12.2023; Risposta AE n. 149/2025)*
""")

    with st.expander("📅 Scadenze Fiscali e Previdenziali"):
        st.markdown("""
**Imposta Sostitutiva** (art. 17, DPR 435/2001):

| Scadenza | Versamento | Codice F24 |
|----------|-----------|------------|
| 30 giugno (o 30 luglio + 0,4%) | Saldo anno prec. + 1ª rata acconto 40% | **1792** |
| 30 novembre | 2ª rata acconto 60% | **1792** |
| Primo anno di attività | Nessun acconto dovuto | — |

Acconto: metodo storico (100% imposta anno prec.) o previsionale (se reddito atteso inferiore).

**Cassa Forense – Rate Minimali 2025:**

| Rata | Scadenza |
|------|----------|
| 1ª (sogg. + integr.) | 28 febbraio |
| 2ª | 31 maggio |
| 3ª | 31 luglio |
| 4ª + maternità | 30 settembre |

**Conguaglio CFA (Mod. 5 / autoliquidazione):** entro **30 settembre** dell'anno successivo.
""")

    with st.expander("🧾 Fatturazione Elettronica – Obblighi dal 01.01.2024"):
        st.markdown("""
**Obbligo universale dal 1° gennaio 2024** per tutti i forfetari
(D.Lgs. 5.02.2021, n. 36 – eliminata la soglia di ricavi previgente).

**Dati obbligatori nel file XML:**
- **Codice Regime Fiscale:** `RF19`
- **Natura Operazione:** `N2.2` (non soggetta – altri casi)
- Ritenuta: non indicare (i forfetari sono esonerati)
- Aliquota IVA: non applicabile

**Termini di emissione:**
- Fattura immediata: entro **12 giorni** dall'effettuazione dell'operazione
- Fattura differita: entro il **15 del mese successivo**

**Sanzione:** dal **5% al 10%** dell'imponibile (art. 6, D.Lgs. 471/1997).

*Eccezione: operatori sanitari che emettono fatture a persone fisiche.*
""")

    with st.expander("📌 Bollo Virtuale e Contributo CPA"):
        st.markdown("""
**Imposta di Bollo** (DPR 26.10.1972, n. 642):
- **€2,00** su fatture non soggette a IVA per importi **> €77,47**
- Nelle e-fatture: tag `<BolloVirtuale>SI</BolloVirtuale>` con importo `2.00`
- Versamento tramite F24: entro il **20 del mese** successivo al trimestre di riferimento
  (se totale trimestrale > €250; altrimenti entro il 31 gennaio dell'anno successivo)

**Contributo Integrativo CPA 4%** (art. 11, L. 576/1980):
- Addebitato al cliente in aggiunta agli onorari
- Non è reddito del professionista: incassato e versato interamente a CFA tramite Mod. 5
- Nel regime forfetario la CPA incassata **non concorre al reddito imponibile**
""")

# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<br>
<center style='color:#D4AF37;font-size:.8em'>
Studio Gaetani © 2025 |
<span style='color:#888'>
L. 190/2014 s.m.i. · L. 207/2024 · Reg. Unico CFA 01.01.2024 · D.Lgs. 36/2022
</span>
</center>
""", unsafe_allow_html=True)
