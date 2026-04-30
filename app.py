import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Kapsamlı Genetik & Biyokimyasal Analiz")

# --- YAN PANEL: DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📂 Veri Yükleme")
    # Genetik Harita / Sekans Dosyası
    genome_file = st.file_uploader("Genetik Harita (FASTA/TXT)", type=["fasta", "txt"])
    
    st.markdown("---")
    st.header("🏢 AI Saha Eğitimi")
    field_file = st.file_uploader("Saha Verisi (CSV)", type="csv")
    if field_file and st.button("AI'yı Sahaya Göre Eğit"):
        st.session_state.ai_engine.train_field_model(pd.read_csv(field_file))
        st.success("Saha Eğitimi Tamam!")

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛠️ Girdi Analizi")
    plant_choice = st.selectbox("Ürün Türü:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    
    # Dosyadan veri okuma
    if genome_file:
        seq_input = genome_file.read().decode("utf-8")
        st.info("Dosya başarıyla yüklendi.")
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
            st.error("Sekans okunamadı. Lütfen formatı kontrol edin.")

with col2:
    st.subheader("📊 Analiz Sonuçları (Fenotipik Tahmin)")
    if 'results' in st.session_state:
        # Metrikleri görselleştir
        data = st.session_state.results
        
        # Grid sistemi ile metrikleri göster
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix", data["Brix (Şeker Değeri)"])
        c2.metric("Verim", data["Verim Potansiyeli"])
        c3.metric("Çimlenme Gücü", f"%{data['Çimlenme Gücü (%)']}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{data['Hastalık Dayanımı (%)']}")
        c5.metric("Raf Ömrü", f"{data['Raf Ömrü (Gün)']} Gün")
        c6.metric("Vigor", data["Vigor (Gelişim Hızı)"])
        
        st.warning(f"🌡️ Stres Tolerans Skoru: {data['Stres Toleransı (0-10)']}/10")

        with st.expander("🔬 Amino Asit Frekans Dağılımı"):
            st.bar_chart(st.session_state.metrics)
