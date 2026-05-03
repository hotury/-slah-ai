import streamlit as st
import pandas as pd
from BIYOLOJIK_BEYIN import BioValentBeyin

st.set_page_config(page_title="BioValent Elite", layout="wide")

st.title("🧬 BioValent")
st.markdown("*Bilimsel Veriyi Ticari Değere Dönüştüren Islah Platformu*")
st.markdown("---")

if 'beyin' not in st.session_state:
    st.session_state.beyin = BioValentBeyin()

with st.sidebar:
    st.header("🧠 Kendi AI'nı Eğit")
    st.write("Brix ve Verim tahminleri için saha verilerinizi (CSV) yükleyin.")
    
    training_file = st.file_uploader("Saha Verisi Yükle", type=['csv'])
    
    if training_file is not None:
        try:
            df = pd.read_csv(training_file)
            if st.button("🚀 Modeli Eğit"):
                with st.spinner("Yapay zeka öğreniyor..."):
                    sonuc = st.session_state.beyin.train_custom_model(df)
                    st.success(sonuc)
        except Exception as e:
            st.error(f"Dosya hatası: {e}")
    
    st.markdown("---")
    st.caption("BioValent v2.0")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📥 Veri Girişi")
    seq_input = st.text_area("Sekans Girin:", height=200, placeholder="ATGC... veya MVLS...")
    
    if st.button("🔍 Analizi Başlat", type="primary"):
        if len(seq_input) >= 10:
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
            st.error("Lütfen en az 10 karakterlik bir sekans girin.")

with col2:
    st.subheader("📊 Analiz Sonuçları")
    if 'res' in st.session_state:
        r = st.session_state.res
        
        if "Error" in r["sci"]:
            st.error(r["sci"]["Error"])
        else:
            st.success(f"Format: {r['type']}")
            
            # --- GÜVENLİ GÖSTERİM DÖNGÜSÜ ---
            for param, data in r["sci"].items():
                # data'nın bir sözlük olduğunu ve içinde 'val' anahtarı olduğunu kontrol et
                if isinstance(data, dict) and 'val' in data:
                    with st.expander(f"🔹 {param}: {data['val']}", expanded=True):
                        st.write(f"**Açıklama:** {data.get('desc', 'Bilgi yok.')}")
                        st.info(f"**Ticari Yorum:** {data.get('com', 'Yorum yok.')}")
            
            st.markdown("---")
            st.markdown("#### 🎯 Saha Tahminleri (Yapay Zeka)")
            
            if st.session_state.beyin.is_trained and r["pred"] is not None:
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix", r["pred"].get("Brix", "N/A"))
                c2.metric("Tahmini Verim", f"{r["pred"].get('Verim', 'N/A')} kg/ton")
            else:
                st.warning("⚠️ Tahminler için sol panelden model eğitimi yapmalısınız.")
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix", "Model Eğit")
                c2.metric("Tahmini Verim", "Model Eğit")
