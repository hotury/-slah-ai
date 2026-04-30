import streamlit as st
from biovalent_algo import BiovalentEngine

st.set_page_config(page_title="Biovalent AI | Biochemical Labs", layout="wide")

if 'engine' not in st.session_state:
    st.session_state.engine = BiovalentEngine()

st.title("🛡️ Biovalent AI: Biyokimyasal Islah Karar Destek")
st.markdown("---")

# 1. BİTKİ SEÇİMİ
selected_plant = st.selectbox("Çalışılacak Bitki Türünü Seçin:", list(st.session_state.engine.PLANT_DB.keys()))
plant_info = st.session_state.engine.PLANT_DB[selected_plant]

# 2. AMİNO ASİT / MUTASYON SEÇİMİ
st.subheader(f"🧬 {selected_plant} İçin Tanımlı Protein Değişimleri")
st.write("Aday tohumun sahip olduğu genetik/amino asit değişimlerini işaretleyin:")

possible_mutations = list(plant_info["mutations"].keys())
selected_mutations = st.multiselect("Protein & Amino Asit Değişimleri:", possible_mutations)

if st.button("Hücre ve Verim Analizini Başlat"):
    result = st.session_state.engine.analyze_biochemical_profile(selected_plant, selected_mutations)
    
    if result:
        # ÖZET SKORLAR
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Tahmini Kalite (Brix/Protein)", f"{result['final_brix']}")
        with c2:
            st.metric("Tahmini Verim Potansiyeli", f"{result['final_yield']}")

        # BURSA GEN YORUMLAMA RAPORU
        st.markdown("---")
        st.subheader("📋 Bursa Gen Yorumlama / Teknik Rapor")
        
        if not result['reports']:
            st.warning("Herhangi bir spesifik mutasyon seçilmedi. Bitki standart potansiyelinde görünüyor.")
        
        for rep in result['reports']:
            with st.chat_message("assistant"):
                st.write(f"**Mutasyon:** {rep['name']}")
                st.write(f"**Biyokimyasal Analiz:** {rep['desc']}")
                st.write(f"**Etki Katsayısı:** `{'+' if rep['impact'] > 0 else ''}{rep['impact']}`")
                
                # Biyolojik derinlik yorumu ekle
                if "brix" in rep['name'].lower() or "Asn" in rep['name']:
                    st.info("Hücre çeperindeki invertaz aktivitesi arttığı için şeker taşıma kapasitesi optimize edildi.")
                elif "tolerance" in rep['name'].lower():
                    st.success("Protein katlanma hızı (chaperone activity) arttığı için bitki strese karşı daha dirençli.")
