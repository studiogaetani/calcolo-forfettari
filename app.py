import streamlit as st
from datetime import date

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Studio Legale - Area Clienti", page_icon="⚖️")

# --- CSS PER STILE PROFESSIONALE ---
st.markdown("""
<style>
    .main {background-color: #f5f5f5;}
    h1 {color: #2c3e50;}
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px;
        width: 100%;
    }
    .info-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU LATERALE) ---
st.sidebar.title("Navigazione")
scelta = st.sidebar.radio("Vai a:", ["Home", "Calcola Preventivo", "Prenota Appuntamento", "Contatti"])

# --- PAGINA HOME ---
if scelta == "Home":
    st.title("⚖️ Studio Legale [Tuo Nome]")
    st.write("### Assistenza legale trasparente e professionale")
    
    st.image("https://images.unsplash.com/photo-1589829085413-56de8ae18c73?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True)
    
    st.markdown("""
    <div class="info-box">
    Benvenuto nell'area digitale dello studio. Qui puoi:
    <ul>
        <li>Ottenere una stima dei costi per la tua pratica.</li>
        <li>Richiedere un appuntamento senza attese telefoniche.</li>
        <li>Accedere ai documenti utili (fac-simile).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# --- PAGINA CALCOLA PREVENTIVO ---
elif scelta == "Calcola Preventivo":
    st.title("💰 Stima Costi e Compensi")
    st.info("Questa è una simulazione non vincolante basata sui parametri forensi medi.")
    
    tipo_pratica = st.selectbox("Seleziona il tipo di attività", 
                                ["Consulenza Stragiudiziale", "Recupero Crediti", "Separazione/Divorzio", "Causa Civile Ordinaria"])
    
    valore_controversia = st.number_input("Valore della controversia (€)", min_value=0.0, value=5000.0, step=500.0)
    
    # Logica di calcolo semplificata (Parametri DM 55/2014 indicativi)
    onorario_base = 0.0
    
    if tipo_pratica == "Consulenza Stragiudiziale":
        onorario_base = max(300, valore_controversia * 0.05)
    elif tipo_pratica == "Recupero Crediti":
        onorario_base = max(400, valore_controversia * 0.08)
    elif tipo_pratica == "Separazione/Divorzio":
        onorario_base = 1500 # Forfettario medio base
    elif tipo_pratica == "Causa Civile Ordinaria":
        onorario_base = max(1200, valore_controversia * 0.10)
        
    cpa = onorario_base * 0.04
    iva = onorario_base * 0.22 # Se fossi in ordinario, ma tu sei forfettario quindi IVA è 0
    
    # Checkbox regime forfettario
    regime = st.radio("Regime Fiscale Avvocato", ["Regime Forfettario (No IVA)", "Regime Ordinario (+IVA 22%)"])
    
    if "Forfettario" in regime:
        iva = 0
        bollo = 2.0 if onorario_base > 77.47 else 0.0
    else:
        bollo = 0.0

    totale = onorario_base + cpa + iva + bollo
    
    if st.button("Calcola Preventivo"):
        st.markdown(f"""
        <div class="info-box">
        <h4>Dettaglio Stima:</h4>
        <p><b>Onorario:</b> € {onorario_base:,.2f}</p>
        <p><b>Cassa Forense (4%):</b> € {cpa:,.2f}</p>
        <p><b>IVA:</b> € {iva:,.2f}</p>
        <p><b>Bollo:</b> € {bollo:,.2f}</p>
        <hr>
        <h3>Totale Stimato: € {totale:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)

# --- PAGINA PRENOTA APPUNTAMENTO ---
elif scelta == "Prenota Appuntamento":
    st.title("📅 Richiedi un Appuntamento")
    
    with st.form("form_appuntamento"):
        nome = st.text_input("Nome e Cognome")
        email = st.text_input("Email")
        data = st.date_input("Data preferita", min_value=date.today())
        motivo = st.text_area("Breve descrizione del problema")
        
        submitted = st.form_submit_button("Invia Richiesta")
        
        if submitted:
            st.success(f"Grazie {nome}. La richiesta per il {data} è stata inviata. Ti contatterò a breve alla mail {email}.")
            # Qui si potrebbe integrare l'invio reale di una mail

# --- PAGINA CONTATTI ---
elif scelta == "Contatti":
    st.title("📍 Dove siamo")
    st.markdown("""
    **Studio Legale Avv. Rossi**
    Via della Giustizia, 1 - Roma
    
    📞 Telefono: 06.12345678
    📧 Email: studio@esempio.com
    """)
    
    st.map() # Mostra una mappa generica (personalizzabile con lat/lon)
