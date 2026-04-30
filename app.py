import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Islah AI v2", layout="wide")

# Engine başlatma
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Genetik Analiz ve Saha Adaptasyonu")

# --- SOL PANEL: GENETİK GİRİŞ VE AI EĞİTİMİ ---
with st.sidebar:
    st.header("🔬 Genetik Veri Girişi")
    # DNA veya Amino Asit dosya yükleme alanı
    uploaded_file = st.file_uploader("Genetik/Protein Dosyası (.fasta, .txt)", type=["fasta", "txt"])
    
    st.markdown("---")
    st.header("🚜 Saha Verisi & AI Eğitimi")
    # AI Eğitme Kısmı
    field_data = st.file_uploader("Saha Performans Verisi (CSV)", type="csv")
    if field_data is not None:
        df_field = pd.read_csv(field_data)
        if st.button("🚀 AI Modeli Eğit"):
            success = st.session_state.ai_engine.train_with_field_data(df_field)
            if success:
                st.success("AI Modeli Başarıyla Eğitildi!")
            else:
                st.error("Hata: CSV sütun isimlerini kontrol edin (Protein_Seq, Saha_Sonuc).")

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ Analiz Parametreleri")
    plant_choice = st.selectbox("Bitki Türü Seçimi:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    input_mode = st.radio("Yüklenen Dosya/Veri İçeriği:", ["DNA / Genetik Harita", "Amino Asit (Protein)"])
    
    # Veri Okuma Mantığı
    raw_data = ""
    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
        st.info("📂 Dosya başarıyla okundu.")
    else:
        raw_data = st.text_area("Veya Sekansı Manuel Yapıştırın:", height=200)

    if st.button("🔍 Dijital Fenotipi Analiz Et"):
        # Veriyi temizle
        clean_data = st.session_state.ai_engine.process_genome_file(raw_data)
        
        # Seçime göre işle
        if input_mode == "DNA / Genetik Harita":
            final_seq = st.session_state.ai_engine.translate_dna(clean_data)
        else:
            final_seq = clean_data
            
        if final_seq:
            res_stats, res_metrics = st.session_state.ai_engine.predict_all_parameters(final_seq, plant_choice)
            st.session_state.results = res_stats
            st.session_state.metrics = res_metrics
            st.session_state.active_seq = final_seq
        else:
            st.error("Veri işleme hatası! Lütfen girdiyi kontrol edin.")

with col2:
    st.subheader("📊 Tahmini Performans Raporu")
    if 'results' in st.session_state:
        res = st.session_state.results
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix (Tat)", res.get("Brix", 0))
        c2.metric("Verim", res.get("Verim", 0))
        c3.metric("Çimlenme", f"%{res.get('Cimlenme', 0)}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{res.get('Hastalik', 0)}")
        c5.metric("Raf Ömrü", f"{res.get('RafOmru', 0)} Gün")
        c6.metric("Vigor (Büyüme)", res.get("Vigor", 0))

        st.warning(f"🌡️ Stres Toleransı: {res.get('Stres', 0)}/10")
        
        # Hata veren kısım getattr ile güvenli hale getirildi
        if getattr(st.session_state.ai_engine, 'is_trained', False):
            st.success("🎯 Bu sonuçlar AI tarafından saha verilerinizle kalibre edilmiştir.")
        
        if 'metrics' in st.session_state:
            with st.expander("🔬 Amino Asit Dağılım Grafiği"):
                st.bar_chart(st.session_state.metrics)
