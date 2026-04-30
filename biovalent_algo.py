import pandas as pd

class BiovalentEngine:
    def __init__(self):
        # 🌿 BİTKİ ÇEŞİTLİLİĞİ VE BİYOLOJİK KÜTÜPHANE
        # Burası bitki bazlı "Anayasa" kütüphanesidir.
        self.PLANT_DB = {
            "Domates (Solanum lycopersicum)": {
                "base_brix": 4.5, "base_yield": 80.0,
                "mutations": {
                    "LIN5 (Asn -> Asp)": {"effect": "brix", "impact": 0.8, "desc": "Meyve etinde şeker birikimini hızlandırır."},
                    "ALMT9 (Glu -> Val)": {"effect": "acidity", "impact": -0.12, "desc": "Malik asit taşımasını azaltarak lezzeti yumuşatır."},
                    "HSP70 (Pro -> Leu)": {"effect": "tolerance", "impact": 0.3, "desc": "Isı şoku protein stabilitesini artırır."}
                }
            },
            "Biber (Capsicum annuum)": {
                "base_brix": 6.0, "base_yield": 40.0,
                "mutations": {
                    "Pun1 (Gln -> Stop)": {"effect": "pungency", "impact": -1.0, "desc": "Kapsaisin sentezini durdurarak biberi tatlılaştırır."},
                    "Lcyb (Ile -> Val)": {"effect": "color", "impact": 0.5, "desc": "Likopen döngüsünü hızlandırarak rengi koyulaştırır."}
                }
            },
            "Buğday (Triticum aestivum)": {
                "base_brix": 0, "base_yield": 350.0, # Kg/Dekar
                "mutations": {
                    "Gpc-B1 (Trp -> Arg)": {"effect": "protein", "impact": 0.15, "desc": "Tanedeki protein ve demir içeriğini artırır."},
                    "Rht-B1 (Point Mut)": {"effect": "height", "impact": -0.3, "desc": "Yarı bodur yapı oluşturarak yatmayı engeller."}
                }
            },
            "Mısır (Zea mays)": {
                "base_brix": 3.0, "base_yield": 1200.0,
                "mutations": {
                    "Opaque-2 (Lys+ Gen)": {"effect": "protein", "impact": 0.25, "desc": "Lizin ve Triptofan amino asit miktarını ikiye katlar."},
                    "Bt-Cry1Ab": {"effect": "resistance", "impact": 0.9, "desc": "Mısır kurduna karşı biyolojik toksin sentezler."}
                }
            }
        }

    def analyze_biochemical_profile(self, plant_name, selected_mutations):
        """Amino Asit değişimlerini alıp bitkiyi yorumlayan motor."""
        plant_data = self.PLANT_DB.get(plant_name)
        if not plant_data:
            return None

        # Temel Değerler
        current_brix = plant_data["base_brix"]
        current_yield = plant_data["base_yield"]
        reports = []
        
        # Seçilen Amino Asit Değişimlerini İşle
        for mut_name in selected_mutations:
            mut_info = plant_data["mutations"].get(mut_name)
            if mut_info:
                impact = mut_info["impact"]
                
                if mut_info["effect"] == "brix":
                    current_brix += impact
                elif mut_info["effect"] == "yield":
                    current_yield *= (1 + impact)
                elif mut_info["effect"] == "acidity":
                    current_brix *= (1 + impact)
                
                reports.append({
                    "name": mut_name,
                    "desc": mut_info["desc"],
                    "impact": impact
                })

        return {
            "final_brix": round(current_brix, 2),
            "final_yield": round(current_yield, 2),
            "reports": reports
        }
