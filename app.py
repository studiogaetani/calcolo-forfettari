import streamlit as st
import pandas as pd
import time
from datetime import date
from fpdf import FPDF
import base64

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Gaetani | Avvocati", page_icon="⚖️", layout="centered")

# --- 2. GESTIONE LOGIN ---
def check_password():
    """Gestisce il login."""
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # GRAFICA LOGIN
        st.markdown("""
        <style>
        .stApp {background: linear-gradient(180deg, #001529 0%, #001e3c 100%);}
        h1, h3, p {color: white; text-align: center; font-family: 'Helvetica Neue', sans-serif;}
        .stTextInput > label {color: #D4AF37 !important; font-weight: bold;}
        .stButton > button {background-color: #D4AF37; color: #001529; width: 100%; font-weight: bold; border: none;}
        #MainMenu, header, footer {visibility: hidden;}
        
        /* FIX INPUT LOGIN */
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
        st.markdown("<br><center style='color: #888;'>Software riservato ai Clienti dello Studio.</center>", unsafe_allow_html=True)
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
#                 INIZIO APP REALE
# ==============================================================================

# --- CSS LUXURY & HIGH CONTRAST INPUTS ---
st.markdown("""
    <style>
    /* SFONDO GENERALE */
    .stApp { background: linear-gradient(180deg, #001529 0%, #001e3c 100%); }

    /* WHITE LABEL */
    #MainMenu, header, footer, [data-testid="stToolbar"] {visibility: hidden; display: none;}

    /* TESTI GLOBALI */
    h1, h2, h3, h4, h5, h6, p, li, div, label, span {
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* LINK ORO */
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    a:hover { color: #ffffff !important; text-decoration: underline; }

    /* === INPUT AD ALTA VISIBILITÀ (BIANCO SU BLU) === */
    input, textarea, .stNumberInput input, .stTextInput input, .stTextArea textarea {
        color: #ffffff !important; 
        caret-color: #D4AF37 !important;
        font-weight: 500;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="base-input"], textarea {
        background-color: #002a52 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 5px;
    }

    /* ETICHETTE ORO */
    .stSelectbox > label, .stNumberInput > label, .stRadio > label, .stCheckbox > label, 
    .stTextInput > label, .stDateInput > label, .stTextArea > label {
        color: #D4AF37 !important;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    
    /* MENU A TENDINA */
    div[data-baseweb="select"] > div {
        background-color: #002a52 !important;
        border: 2px solid #D4AF37 !important;
        color: white !important;
    }
    div[data-baseweb="select"] span { color: white !important; }
    div[data-baseweb="select"] svg { fill: white !important; }
    div[data-baseweb="popover"] div, ul[data-baseweb="menu"] {
        background-color: #001529 !important;
        border: 1px solid #D4AF37 !important;
    }
    li[data-baseweb="option"] { color: white !important; }
    li[data-baseweb="option"]:hover, li[aria-selected="true"] {
        background-color: #D4AF37 !important;
        color: #001529 !important;
    }

    /* PULSANTI */
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
    }
    
    /* CARD RISULTATI */
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
