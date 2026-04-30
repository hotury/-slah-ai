# ISLAH_AI_APP.py - Clean Professional Interface
import streamlit as st
from BIYOLOJIK_BEYIN import BiyolojikBeyin

st.set_page_config(page_title="IslahAI Elite", layout="wide")

# Header (temiz)
st.title("🧬 IslahAI Elite")
st.markdown("*Multi-Crop DNA Phenotyping*")

# Sidebar
with st.sidebar:
    st.header("Bitki Seç")
    crop = st.selectbox("Ürün:", ['Domates', 'Biber', 'Hıyar', 'Kabak', 'Karpuz', 'Kavun'])
    
    st.header("Custom Train")
    csv_file = st.file_uploader("CSV Eğit (snp_profile,Brix,Verim)", type='csv')
    if csv_file and st.button("Şirket Modeli Eğit"):
        result = beyin.train_custom(csv_file)
        st.success(result)
    
    st.markdown("---")
    st.caption("DNA → SNP → Phenotype")

# Global beyin init
if 'beyin' not in st.session_state:
    st.session_state.beyin = BiyolojikBeyin(crop)

beyin = st.session_state.beyin
beyin.crop_type = crop  # Dynamic crop

col1, col2 = st.columns([1, 1.4])

with col1:
    st.header("DNA Analizi")
    dna_file = st.file_uploader("DNA/FASTA", type=['fasta','txt'])
    
    dna = ""
    if dna_file:
        dna = dna_file.read().decode()
    else:
        dna = st.text_area("DNA:", height=250, 
            value="ATGGAAGAAGAACCGCTTTTGGTGGCGCTCTGCTGCTGCTGCC" * 25)
    
    if st.button("🔍 Phenotype Tahmin", type="primary"):
        if len(dna) > 50:
            with st.spinner("SNP extraction..."):
                result = beyin.predict(dna)
                st.session_state.result = result

with col2:
    if 'result' in st.session_state:
        res = st.session_state.result
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("🍅 Brix", res['Brix'])
            st.metric("🌾 Verim", f"{res['Verim']} kg")
        with c2:
            st.metric("🔬 Glu %", res['Glu'])
            st.metric("🎯 SNP Hit", res['SNPHit'])
        
        st.info(f"Model: {res['Model']}")
        
        with st.expander("Detay"):
            st.json(res)

st.markdown("---")
st.caption("Professional DNA Phenotyping Platform")
