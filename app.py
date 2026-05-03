import streamlit as st
import pandas as pd
from BIYOLOJIK_BEYIN import BioValentBeyin

# Sayfa Ayarları
st.set_page_config(page_title="BioValent Elite", layout="wide", page_icon="🧬")

# Stil ve Başlık
st.title("🧬 BioValent")
st.markdown("*Bilimsel Veriyi Ticari Değere Dönüştüren Dijital Islah Platformu*")
st.markdown("---")

# Uygulama hafızasında beyin objesini tut
if 'beyin' not in st.session_state:
    st.session_state.beyin = BioValentBeyin()

# --- YAN PANEL: AI EĞİTİM MERKEZİ ---
with st.sidebar:
    st.header("🧠 Kurumsal AI Eğitimi")
    st.write("Brix ve Verim tahminlerini aktifleştirmek için CSV dosyanızı yükleyin.")
    
    training_file = st.file_uploader("Saha Verisi (CSV)", type=['csv'])
    
    if training_file is not None:
        try:
            df = pd.read_csv(training_file)
            if st.button("🚀 Modeli Şimdi Eğit"):
                with st.spinner("Yapay zeka verileri işliyor..."):
                    sonuc = st.session_state.beyin.train_custom_model(df)
                    st.success(sonuc)
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")
    
    st.markdown("---")
    st.caption("BioValent Intelligence © 2026")

# --- ANA EKRAN TASARIMI ---
col1, col2 = st.columns([1, 1.4])

with col1:
    st.subheader("📥 Genetik Veri Girişi")
    seq_input = st.text_area("Analiz edilecek sekans (DNA veya AA):", height=250, placeholder="ATGC... veya MVLS...")
    
    if st.button("🔍 Analizi Başlat", type="primary"):
        if len(seq_input.strip()) >= 10:
            protein, s_type = st.session_state.beyin.preprocess_sequence(seq_input)
            
            # Bilimsel verileri hesapla
            sci_results = st.session_state.beyin.calculate_science(protein)
            
            # Tahminleri al (Eğitilmemişse None döner)
            predictions = st.session_state.beyin.predict_phenotype(protein)
            
            st.session_state.res = {
                "type": s_type,
                "sci": sci_results,
                "pred": predictions
            }
        else:
            st.error("Lütfen geçerli bir sekans girin (Min. 10 karakter).")

with col2:
    st.subheader("📊 Analiz ve Ticari Öngörüler")
    if 'res' in st.session_state:
        r = st.session_state.res
        
        if isinstance(r["sci"], dict) and "Error" in r["sci"]:
            st.error(r["sci"]["Error"])
        else:
            st.success(f"Tespit Edilen Veri Tipi: **{r['type']}**")
            
            # Bilimsel ve Ticari Verileri Listele
            for param, data in r["sci"].items():
                if isinstance(data, dict) and "val" in data:
                    with st.expander(f"🔹 {param}: {data['val']}", expanded=True):
                        st.write(f"**Bilimsel Tanım:** {data.get('desc', '')}")
                        st.info(f"**Ticari Değer:** {data.get('com', '')}")
            
            st.markdown("---")
            st.markdown("#### 🎯 Yapay Zeka Saha Tahminleri")
            
            # Tahmin bloğu kontrolü
            if st.session_state.beyin.is_trained and r["pred"] is not None:
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix Skoru", r["pred"].get("Brix", "N/A"))
                c2.metric("Tahmini Verim Potansiyeli", f"{r['pred'].get('Verim', 'N/A')} kg/ton")
            else:
                st.warning("⚠️ Tahminleri görmek için sol menüden firmanıza özel model eğitimi yapmalısınız.")
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix", "Model Eğit")
                c2.metric("Tahmini Verim", "Model Eğit")

st.markdown("---")
