import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Genetik Haritadan Saha Performansına")

# --- YAN PANEL: AI EĞİTİM ---
with st.sidebar:
    st.header("🏢 Şirket Özel AI Eğitimi")
    st.write("Kendi saha verilerinizi yükleyerek AI'yı kalibre edin.")
    uploaded_file = st.file_uploader("Saha Verisi (CSV)", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if st.button("Modeli Eğit"):
            st.session_state.ai_engine.train_field_model(df)
            st.success("AI Sizin Sahanız İçin Eğitildi!")

# --- ANA PANEL: ANALİZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛠️ Genetik Girdi")
    plant_choice = st.selectbox("Ürün Seçimi:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    input_type = st.radio("Girdi Tipi:", ["DNA / FASTA", "Amino Asit Dizisi"])
    raw_data = st.text_area("Sekans Verisini Yapıştırın:", height=200)

    if st.button("Analiz Et"):
        if input_type == "DNA / FASTA":
            protein_seq = st.session_state.ai_engine.translate_dna(raw_data)
        else:
            protein_seq = raw_data.strip().upper()

        if protein_seq:
            results = st.session_state.ai_engine.predict_performance(protein_seq, plant_choice)
            st.session_state.results = results
            st.session_state.active_seq = protein_seq
        else:
            st.error("Geçersiz sekans formatı!")

with col2:
    st.subheader("📊 Analiz Sonuçları")
    if 'results' in st.session_state:
        res = st.session_state.results
        
        # Metrik Kartları
        m1, m2 = st.columns(2)
        m1.metric("Laboratuvar Potansiyeli (Brix)", f"{res['theory']['Brix']}")
        m2.metric("Laboratuvar Potansiyeli (Verim)", f"{res['theory']['Verim']}")
        
        if res['field_ai']:
            st.warning(f"🎯 Saha Performans Tahmini (AI): {res['field_ai']}")
        else:
            st.info("💡 Saha tahmini için sol taraftan modelinizi eğitin.")

        # Detaylı Amino Asit Raporu
        with st.expander("🔬 Amino Asit Kompozisyon Analizi"):
            st.write(f"**İşlenen Protein Dizisi:** {st.session_state.active_seq[:50]}...")
            st.json(res['metrics'])
            st.write("Bu frekanslar, bitkinin şeker taşıma (Brix) ve yapısal büyüme (Vigor) kapasitesini belirler.")
