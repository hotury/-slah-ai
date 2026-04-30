import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Kapsamlı Genetik & Biyokimyasal Analiz")

with st.sidebar:
    st.header("📂 Veri Yükleme")
    genome_file = st.file_uploader("Genetik Harita (FASTA/TXT)", type=["fasta", "txt"])

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛠️ Girdi Analizi")
    plant_choice = st.selectbox("Ürün Türü:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    
    # Dosya veya text girişi kontrolü
    if genome_file:
        seq_input = genome_file.read().decode("utf-8")
    else:
        seq_input = st.text_area("Veya Sekansı Buraya Yapıştırın:", height=200)

    input_mode = st.radio("Veri Tipi:", ["DNA / FASTA", "Amino Asit (Protein)"])

    if st.button("Tam Kapsamlı Analiz Et"):
        if input_mode == "DNA / FASTA":
            final_seq = st.session_state.ai_engine.translate_dna(seq_input)
        else:
            final_seq = seq_input.strip().upper()
        
        if final_seq:
            res_stats, res_metrics = st.session_state.ai_engine.predict_all_parameters(final_seq, plant_choice)
            st.session_state.results = res_stats
            st.session_state.metrics = res_metrics
        else:
            st.error("Sekans okunamadı.")

with col2:
    st.subheader("📊 Analiz Sonuçları")
    if 'results' in st.session_state:
        data = st.session_state.results
        
        # Hata Çözümü: Anahtarların birebir eşleştiğinden emin oluyoruz
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix", data.get("Brix", 0))
        c2.metric("Verim", data.get("Verim", 0))
        c3.metric("Çimlenme Gücü", f"%{data.get('Cimlenme', 0)}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{data.get('Hastalik', 0)}")
        c5.metric("Raf Ömrü", f"{data.get('RafOmru', 0)} Gün")
        c6.metric("Vigor", data.get("Vigor", 0))
        
        st.warning(f"🌡️ Stres Tolerans Skoru: {data.get('Stres', 0)}/10")

        if 'metrics' in st.session_state:
            with st.expander("🔬 Amino Asit Frekans Dağılımı"):
                st.bar_chart(st.session_state.metrics)
