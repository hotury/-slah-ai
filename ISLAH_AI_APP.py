import streamlit as st
from BIYOLOJIK_BEYIN import BiyolojikBeyin

st.set_page_config(page_title="Islah AI Elite", layout="wide")

st.title("🧬 Islah AI: Atakan Tohumculuk Ar-Ge")
st.markdown("---")

# Sidebar - Ayarlar
with st.sidebar:
    st.header("🔬 Islah Parametreleri")
    crop = st.selectbox("Ürün Seçiniz:", ['Domates', 'Biber', 'Hıyar', 'Kabak', 'Karpuz', 'Kavun'])
    
    st.markdown("---")
    st.header("📂 Dosya Yükle")
    uploaded_file = st.file_uploader("DNA Dizisi (FASTA veya TXT):", type=['fasta', 'txt', 'dna'])
    st.info("Biyolojik Markör Modu Aktif.")

# Beyin Init
if 'beyin' not in st.session_state or st.session_state.current_crop != crop:
    st.session_state.beyin = BiyolojikBeyin(crop)
    st.session_state.current_crop = crop

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📥 Veri Girişi")
    
    # Dosya yüklendiyse içeriğini oku, yoksa boş bırak
    dna_content = ""
    if uploaded_file is not None:
        dna_content = uploaded_file.read().decode("utf-8")
        # FASTA başlıklarını (>) temizle
        dna_content = "\n".join([line for line in dna_content.splitlines() if not line.startswith(">")])
        st.success("Dosya başarıyla okundu!")

    # Metin alanı hem el girişine hem dosya içeriğini görmeye yarar
    dna_input = st.text_area("DNA Sekansı (Dosyadan yüklendi veya elle girin):", 
                             value=dna_content, height=300, 
                             placeholder="ATGC...")
    
    if st.button("🚀 Analizi Başlat", type="primary"):
        if len(dna_input) > 20:
            with st.spinner("Biyolojik motifler taranıyor..."):
                # DNA'yı temizle (boşlukları ve yeni satırları at)
                clean_dna = "".join(dna_input.split())
                st.session_state.result = st.session_state.beyin.predict(clean_dna)
        else:
            st.error("Lütfen geçerli bir DNA dizisi girin.")

with col2:
    st.subheader("📊 Dijital Fenotip Sonuçları")
    if 'result' in st.session_state:
        res = st.session_state.result
        
        # Hata kontrolü
        if "Error" in res:
            st.error(res["Error"])
        else:
            def show_card(title, key, unit=""):
                data = res[key]
                val = data['val']
                label = data['label']
                color = "green" if "Elite" in label else "orange" if "Ticari" in label else "red"
                
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid {color}">
                    <small style="color:gray">{title}</small><br>
                    <b style="font-size:24px">{val}{unit}</b><br>
                    <span style="color:{color}; font-size:12px">● {label}</span>
                </div>
                """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                show_card("Şeker Oranı (Brix)", "Brix")
                show_card("Toplam Verim Skoru", "Verim")
                show_card("Tohum Çıkış Gücü", "Cimlenme", "%")
            with c2:
                show_card("Bağışıklık Gücü", "Bagisiklik", "%")
                show_card("Stres Toleransı", "Stres", "%")
                st.success(f"Analiz Notu: {res['Not']}")

st.markdown("---")
st.caption("Atakan Tohumculuk - Dijital Islah Platformu v2.0")
