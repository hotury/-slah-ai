import streamlit as st
import pandas as pd
from BIYOLOJIK_BEYIN import BioValentBeyin

st.set_page_config(page_title="BioValent Elite", layout="wide")
st.title("🧬 BioValent")
st.markdown("*Bilimsel Veriyi Ticari Değere Dönüştüren Islah Platformu*")

if 'beyin' not in st.session_state:
    st.session_state.beyin = BioValentBeyin()

# ... (Yan panel ve veri girişi kısımları aynı kalıyor) ...
# Analiz butonuna basıldığında sonuç ekranı şu şekilde değişecek:

with col2:
    st.subheader("📊 Bilimsel & Ticari Analiz")
    if 'res' in st.session_state:
        r = st.session_state.res
        
        if "Error" in r["sci"]:
            st.error(r["sci"]["Error"])
        else:
            st.success(f"Format: {r['type']}")
            
            for param, data in r["sci"].items():
                with st.expander(f"🔹 {param}: {data['val']}", expanded=True):
                    st.write(f"**Açıklama:** {data['desc']}")
                    st.info(f"**Ticari Yorum:** {data['com']}")
            
            st.markdown("---")
            st.markdown("#### 🎯 Saha Tahminleri")
            c1, c2 = st.columns(2)
            c1.metric("Tahmini Brix", r["dummy"])
            c2.metric("Tahmini Verim", r["dummy"])
