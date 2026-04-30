import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Genetik Haritadan Dijital Fenotip Analizi")

# --- SOL PANEL: DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📂 Veri Girişi")
    genome_file = st.file_uploader("Genetik Harita Yükle (FASTA/TXT)", type=["fasta", "txt"])
    st.info("Dosya yüklendiğinde metin alanı devre dışı kalır ve dosyadaki veri işlenir.")

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛠️ Girdi ve Çeviri")
    plant_choice = st.selectbox("Islah Edilecek Ürün:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    
    # Veri kaynağını belirle
    if genome_file:
        raw_input = genome_file.read().decode("utf-8")
        st.success("✅ Dosya başarıyla okundu.")
    else:
        raw_input = st.text_area("Veya Sekansı Manuel Yapıştırın:", height=200)

    input_mode = st.radio("Girdi Formatı:", ["DNA / Genetik Harita", "Protein / Amino Asit"])

    if st.button("🧬 Kapsamlı Analizi Başlat"):
        # 1. Veriyi temizle
        clean_data = st.session_state.ai_engine.process_genome_file(raw_input)
        
        # 2. Gerekirse Proteine çevir
        if input_mode == "DNA / Genetik Harita":
            final_seq = st.session_state.ai_engine.translate_dna(clean_data)
        else:
            final_seq = clean_data
        
        if final_seq:
            res_stats, res_metrics = st.session_state.ai_engine.predict_all_parameters(final_seq, plant_choice)
            st.session_state.results = res_stats
            st.session_state.metrics = res_metrics
            st.session_state.current_seq = final_seq
        else:
            st.error("❌ Veri işlenemedi. Lütfen formatı kontrol edin.")

with col2:
    st.subheader("📊 Dijital Fenotip Sonuçları")
    if 'results' in st.session_state:
        data = st.session_state.results
        
        # Metrik Kartları
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix (Tat)", data.get("Brix", 0))
        c2.metric("Verim Potansiyeli", data.get("Verim", 0))
        c3.metric("Çimlenme Gücü", f"%{data.get('Cimlenme', 0)}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{data.get('Hastalik', 0)}")
        c5.metric("Raf Ömrü", f"{data.get('RafOmru', 0)} Gün")
        c6.metric("Vigor (Büyüme)", data.get("Vigor", 0))
        
        st.warning(f"🌡️ Çevresel Stres Toleransı: {data.get('Stres', 0)}/10")

        with st.expander("🔬 Amino Asit Analiz Detayı"):
            st.write(f"**Analiz Edilen Dizi Uzunluğu:** {len(st.session_state.current_seq)} AA")
            st.bar_chart(st.session_state.metrics)
