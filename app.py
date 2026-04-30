import streamlit as st
from biovalent_algo import BiovalentEngine

st.set_page_config(page_title="Biovalent AI | Biyokimyasal Analiz", layout="wide")

if 'engine' not in st.session_state:
    st.session_state.engine = BiovalentEngine()

st.title("🛡️ Biovalent AI: Biyokimyasal Islah ve Hücre Analizi")
st.markdown("Bitki genetiğindeki amino asit değişimlerinin fenotip üzerindeki tüm etkilerini hesaplayın.")

# 1. BİTKİ SEÇİMİ
selected_plant = st.selectbox("Çalışılacak Bitki Türünü Seçin:", list(st.session_state.engine.PLANT_DB.keys()))
plant_info = st.session_state.engine.PLANT_DB[selected_plant]

# 2. AMİNO ASİT DEĞİŞİMLERİ GİRDİSİ
st.subheader("🧬 Amino Asit ve Protein Değişimleri")
possible_mutations = list(plant_info["mutations"].keys())
selected_mutations = st.multiselect("Tohumda Tespit Edilen Değişimler:", possible_mutations)

if st.button("Tam Analizi Başlat"):
    result = st.session_state.engine.run_biochemical_analysis(selected_plant, selected_mutations)
    
    if result:
        # 3. TÜM VERİLERİN ÇIKARTILMASI (METRİKLER)
        st.subheader("📊 Tahmini Tohum Performans Kartı")
        cols = st.columns(len(result['stats']))
        
        for i, (param, val) in enumerate(result['stats'].items()):
            cols[i].metric(label=param, value=f"{round(val, 2)}")

        # 4. PROTEİN VE HÜCRE ANALİZ RAPORU
        st.markdown("---")
        st.subheader("🔬 Amino Asit Birleşimlerinden Doğan Yapısal Analiz")
        
        if not result['reports']:
            st.info("Standart genetik yapı (Varyasyon tespit edilmedi).")
        
        for rep in result['reports']:
            with st.expander(f"📌 {rep['name']}"):
                st.write(f"**Biyokimyasal Karşılık:** {rep['desc']}")
                st.write("---")
                # Mutasyonun hangi parametreyi değiştirdiğini görselleştir
                impacts = [f"{k}: {v}" for k, v in plant_info["mutations"][rep['name']].items() if k != "desc"]
                st.code(f"Etki Alanları: {', '.join(impacts)}")

        st.success("Analiz Tamamlandı. Bu veriler laboratuvar teorik tavanını temsil etmektedir.")
