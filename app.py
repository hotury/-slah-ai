import streamlit as st
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Genetik Harita Analiz Platformu")

# --- SOL PANEL: DOSYA GİRİŞİ ---
with st.sidebar:
    st.header("📂 Veri Kaynağı")
    # Dosya Yükleme Alanı
    uploaded_genome = st.file_uploader("Genetik Harita Yükle (FASTA/TXT)", type=["fasta", "txt"])
    
    st.markdown("---")
    plant_choice = st.selectbox("Bitki Türü:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    input_mode = st.radio("Veri Tipi:", ["DNA / Genetik Harita", "Protein / Amino Asit"])

# --- ANA PANEL: ANALİZ VE SONUÇLAR ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📝 Manuel Giriş veya Önizleme")
    
    # Eğer dosya yüklenmişse dosya içeriğini al, yoksa text_area'dan al
    if uploaded_genome is not None:
        raw_data = uploaded_genome.read().decode("utf-8")
        st.success("✅ Dosya başarıyla yüklendi!")
        st.text_area("Yüklenen Dosya İçeriği (İlk 500 Karakter):", value=raw_data[:500] + "...", height=150, disabled=True)
    else:
        raw_data = st.text_area("Sekansı Manuel Yapıştırın:", height=250, placeholder="ATGC... veya Protein dizisi")

    if st.button("🚀 Kapsamlı Analizi Başlat"):
        # Veriyi temizle
        clean_data = st.session_state.ai_engine.process_genome_file(raw_data)
        
        # Dönüştürme
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
            st.error("❌ Veri işlenemedi. Lütfen formatı kontrol edin.")

with col2:
    st.subheader("📊 Analiz Raporu")
    if 'results' in st.session_state:
        res = st.session_state.results
        
        # Metrikleri Göster
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix (Tat)", res["Brix"])
        c2.metric("Verim Potansiyeli", res["Verim"])
        c3.metric("Çimlenme Gücü", f"%{res['Cimlenme']}")
        
        st.markdown("---")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{res['Hastalik']}")
        c5.metric("Raf Ömrü", f"{res['RafOmru']} Gün")
        c6.metric("Vigor (Büyüme)", res["Vigor"])
        
        st.warning(f"🌡️ Stres Tolerans Skoru: {res['Stres']}/10")

        with st.expander("🔬 Amino Asit Kompozisyonu"):
            st.bar_chart(st.session_state.metrics)
            st.write(f"**Toplam İşlenen Uzunluk:** {len(st.session_state.active_seq)} Amino Asit")
