# ISLAH_AI_APP.py - Clean & Full Feature
import streamlit as st
from BIYOLOJIK_BEYIN import BiyolojikBeyin, beyin

st.set_page_config(page_title="IslahAI Elite", layout="wide")

st.title("🧬 IslahAI Elite")
st.markdown("**DNA Phenotyping Platform**")

# Sidebar
st.sidebar.header("Bitki")
crop = st.sidebar.selectbox("Seç:", ['Domates', 'Biber', 'Hıyar', 'Kabak', 'Karpuz', 'Kavun'])

# Lazy beyin init
if 'beyin_instance' not in st.session_state:
    st.session_state.beyin_instance = BiyolojikBeyin(crop)

beyin = st.session_state.beyin_instance
beyin.crop_type = crop

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("DNA")
    dna_file = st.file_uploader("FASTA/DNA")
    dna = ""
    if dna_file:
        dna = dna_file.read().decode()
    else:
        dna = st.text_area("DNA:", height=200, 
            value="ATGGAAGAAGAACCGCTTTTGGTGGCGCTCTGCTGCTGCTGCC" * 20)
    
    if st.button("🔍 Full Phenotype", type="primary"):
        if len(dna) > 100:
            result = beyin.predict_full(dna)
            st.session_state.result = result
            st.rerun()

with col2:
    if 'result' in st.session_state:
        res = st.session_state.result
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Brix", res['Brix'])
            st.metric("Verim", res['Verim'])
            st.metric("Çimlenme", res['Cimlenme'])
        with c2:
            st.metric("Bağışıklık", res['Bagisiklik'])
            st.metric("Raf Ömrü", res['RafOmru'])
        
        st.metric("Glu AA", res['Glu'])
        st.metric("SNP Hit", res['SNP_Hit'])
        
        with st.expander("Tam Rapor"):
            st.json(res)

st.caption("Multi-Crop DNA Analysis")
