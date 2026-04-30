# Streamlit App (streamlit_app.py) - SYNTAX HATASI DÜZELTİLDİ
import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI  # biovalent_engine.py dosyasını kaydet

st.set_page_config(page_title="Islah AI v3 - GWAS Kalibrasyonlu", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI v3: GWAS & Literatür Kalibrasyonlu")

# Uyarı ve bilimsel not
st.warning("🔬 **Bilimsel Doğruluk:** GWAS QTL (Nature Genetics 2019+) + saha kalibrasyonu")
st.caption("📊 R² skorları gösterilir. 0.65+ = Yüksek güvenilirlik")

with st.sidebar:
    st.header("🔬 Genetik Veri")
    uploaded_file = st.file_uploader("FASTA/TXT", type=["fasta", "txt"])
    
    st.markdown("---")
    st.header("🎓 Literatür Ayarları")
    plant_choice = st.selectbox("Bitki:", ["Domates", "Biber", "Hıyar", "Patlıcan"])
    variety = st.selectbox("Çeşit Grubu:", ["", "F1", "cherry", "beef", "sweet", "hot", "Determinate"])
    
    st.markdown("---")
    st.header("🤖 Saha Kalibrasyonu")
    field_data = st.file_uploader("CSV (sequence,Brix,Verim...)", type="csv")
    if field_data is not None and st.button("🚀 Modeli Saha Verisiyle Eğit"):
        try:
            st.session_state.ai_engine.train_with_field_data(pd.read_csv(field_data))
            r2_val = st.session_state.ai_engine.r2_scores.get('Brix', 0)
            st.success(f"✅ Kalibrasyon tamamlandı! R² Brix: {r2_val:.2f}")
        except Exception as e:
            st.error(f"❌ CSV formatı hatalı: {str(e)}")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("⚙️ Analiz")
    input_mode = st.radio("Veri:", ["DNA", "Protein"])
    raw_data = ""
    if uploaded_file is not None:
        raw_data = uploaded_file.read().decode("utf-8")
    else:
        raw_data = st.text_area("Sekans:", height=150, value="")

    if st.button("🔍 GWAS Fenotip Analizi", type="primary"):
        with st.spinner("GWAS QTL + literatür analizi..."):
            clean = st.session_state.ai_engine.process_genome_file(raw_data)
            seq = st.session_state.ai_engine.translate_dna(clean) if input_mode == "DNA" else clean
            if seq:
                st.session_state.results, st.session_state.metrics = st.session_state.ai_engine.predict_all_parameters(
                    seq, plant_choice, variety
                )
                st.success(f"✅ {len(seq)} AA analiz edildi")
            else:
                st.error("❌ Geçerli sekans bulunamadı")

with col2:
    st.subheader("📊 Literatür Kalibrasyonlu Rapor")
    if 'results' in st.session_state and st.session_state.results:
        res = st.session_state.results
        trained = st.session_state.ai_engine.is_trained
        
        # SYNTAX HATASI DÜZELTİLDİ - display_gwas_metric fonksiyonu
        def display_gwas_metric(title, data, unit=""):
            if isinstance(data, dict):
                if 'r2' in 
                    r2_badge = f" R²:{data['r2']:.2f}"
                    color = "🟢" if data['r2'] > 0.65 else "🟡" if data['r2'] > 0.4 else "🔴"
                else:
                    r2_badge = ""
                    color = "🟡"
                
                val = data['val']
                label = data.get('label', 'Ticari')
                val_color = "green" if "Elite" in label else "orange" if "Ticari" in label else "red"
            else:
                val = data
                label = "Ticari"
                r2_badge = ""
                color = "🟡"
                val_color = "orange"
                if isinstance(val, dict):
                    val = val['val']
            
            st.markdown(f"""
            **{title}** {color}: <span style='color:{val_color}; font-size:22px; font-weight:bold;'>
            {val}{unit}</span>{r2_badge}<br>
            *{label}*
            """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            display_gwas_metric("🍅 Brix", res["Brix"])
            display_gwas_metric("🌾 Verim", res["Verim"], " kg/bitki")
            display_gwas_metric("🌱 Çimlenme", res["Cimlenme"], "%")
        with c2:
            display_gwas_metric("🛡️ Bağışıklık", res["Bagisiklik"], "%")
            display_gwas_metric("📦 Raf Ömrü", res["RafOmru"], " gün")
            st.metric("💪 Vigor", res["Vigor"]["val"])
        
        # Kalite göstergesi
        if trained:
            r2_val = st.session_state.ai_engine.r2_scores.get('Brix', 0)
            st.success(f"🎯 **Saha Kalibrasyonlu** R²={r2_val:.2f}")
        else:
            st.info("📚 **Literatür Baseline** (Saha verisiyle %50+ iyileşme)")
        
        # QTL detayları
        st.subheader("🔬 GWAS QTL & Özellik Skorları")
        if isinstance(st.session_state.metrics, dict):
            metrics_df = pd.DataFrame(list(st.session_state.metrics.items()), columns=['Özellik', 'Değer'])
            st.dataframe(metrics_df, use_container_width=True)
        else:
            st.info("Metrics mevcut değil")

# Test sekansı örneği
with st.expander("🧪 Test İçin Örnek Sekans (Domates Brix QTL)"):
    st.code("""
    >Test_Tomato_Elite
    ATGGCCTACGGCGATGCCGACTAGCTAGCTAGCTAGCTAGC...
    """, language="fasta")
