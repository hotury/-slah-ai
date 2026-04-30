class BiovalentEngine:
    def __init__(self):
        # 🌿 BİTKİ ANAYASALARI VE KOMPLEKS PARAMETRELER
        self.PLANT_DB = {
            "Domates (Solanum lycopersicum)": {
                "base_stats": {
                    "Brix": 4.5, "Verim (Ton/Ha)": 80.0, "Raf Ömrü (Gün)": 10,
                    "Hastalık Toleransı (%)": 20.0, "Su İhtiyacı (L/Gün)": 5.0, "Hasat Süresi (Gün)": 110
                },
                "mutations": {
                    "LIN5 (Asn -> Asp)": {"Brix": 1.2, "Verim (Ton/Ha)": 5.0, "desc": "Meyve etinde şeker birikimini artırır."},
                    "ALMT9 (Glu -> Val)": {"Brix": 0.5, "Hastalık Toleransı (%)": 5.0, "desc": "Asidite dengesi üzerinden doku direncini artırır."},
                    "HSP70 (Pro -> Leu)": {"Hastalık Toleransı (%)": 25.0, "Su İhtiyacı (L/Gün)": -1.0, "desc": "Isı şoku proteini sayesinde kuraklık ve sıcaklık direnci sağlar."},
                    "PME (Cys -> Tyr)": {"Raf Ömrü (Gün)": 7, "Verim (Ton/Ha)": -2.0, "desc": "Pektin yapısını güçlendirerek meyveyi sertleştirir, raf ömrünü uzatır."},
                    "Ty-1 (Point Mut)": {"Hastalık Toleransı (%)": 40.0, "Hasat Süresi (Gün)": 5, "desc": "TYLCV virüsüne karşı yüksek direnç sağlar."}
                }
            },
            "Biber (Capsicum annuum)": {
                "base_stats": {
                    "Brix": 5.5, "Verim (Ton/Ha)": 35.0, "Raf Ömrü (Gün)": 12,
                    "Hastalık Toleransı (%)": 15.0, "Su İhtiyacı (L/Gün)": 4.0, "Hasat Süresi (Gün)": 90
                },
                "mutations": {
                    "Pun1 (Gln -> Stop)": {"Brix": 0.8, "desc": "Kapsaisin sentezini durdurur, tatlılık algısını artırır."},
                    "Lcyb (Ile -> Val)": {"Hastalık Toleransı (%)": 10.0, "desc": "Karotenoid birikimi ile doku stabilitesini artırır."},
                    "Bs2 (Genetik Mod)": {"Hastalık Toleransı (%)": 50.0, "desc": "Bakteriyel leke hastalığına (Xanthomonas) karşı tam koruma."}
                }
            }
        }

    def run_biochemical_analysis(self, plant_name, selected_mutations):
        plant_data = self.PLANT_DB.get(plant_name)
        if not plant_data: return None

        # Başlangıç değerlerini kopyala
        final_stats = plant_data["base_stats"].copy()
        analysis_reports = []
        
        # Seçilen her mutasyonun tüm parametreler üzerindeki etkisini topla
        for mut_name in selected_mutations:
            mut_info = plant_data["mutations"].get(mut_name)
            if mut_info:
                for param, value in mut_info.items():
                    if param != "desc":
                        final_stats[param] += value
                
                analysis_reports.append({
                    "name": mut_name,
                    "desc": mut_info["desc"]
                })

        return {"stats": final_stats, "reports": analysis_reports}
