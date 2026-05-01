import numpy as np
from Bio.Seq import Seq
from collections import Counter

class BiyolojikBeyin:
    def __init__(self, crop_type='Domates'):
        self.crop_type = crop_type
        # BİYOLOJİK MARKÖRLER (Literatür bazlı amino asit motifleri)
        self.MARKERS = {
            "sugar_transport": ["STT", "TSS", "STS", "GGS"], # Tat (Brix)
            "defense_peptides": ["RRK", "KKR", "RKR", "HHK"], # Bağışıklık
            "biomass_growth": ["LIV", "VIL", "AAA", "GGG"],  # Verim
            "stress_response": ["PPP", "PPG", "APP"],        # Stres Toleransı
            "storage_proteins": ["EEN", "DDE", "QNE", "DNN"] # Çimlenme Enerjisi
        }
        
        # Ürün Bazlı Bilimsel Sınırlar (Fizyolojik Tavan Değerler)
        self.CROP_CONFIG = {
            "Domates": {"base_brix": 4.2, "base_cim": 65, "yield_mult": 12, "max_brix": 14.0},
            "Biber":   {"base_brix": 5.0, "base_cim": 60, "yield_mult": 8,  "max_brix": 11.0},
            "Hıyar":   {"base_brix": 3.5, "base_cim": 70, "yield_mult": 15, "max_brix": 7.0},
            "Kabak":   {"base_brix": 3.8, "base_cim": 75, "yield_mult": 18, "max_brix": 8.0},
            "Karpuz":  {"base_brix": 8.5, "base_cim": 55, "yield_mult": 25, "max_brix": 16.0},
            "Kavun":   {"base_brix": 9.0, "base_cim": 58, "yield_mult": 20, "max_brix": 17.0}
        }

    def dna_to_protein(self, dna):
        """DNA'yı proteine çevirir (Translation)"""
        try:
            dna = "".join(dna.split()).upper() # Boşlukları temizle
            dna = dna[:(len(dna)//3)*3] # 3'ün katı yap
            return str(Seq(dna).translate(to_stop=True))
        except: return ""

    def scan_markers(self, protein_seq):
        """Protein zincirinde fonksiyonel motifleri sayar."""
        counts = {key: 0 for key in self.MARKERS.keys()}
        if not protein_seq: return counts
        for category, motifs in self.MARKERS.items():
            for motif in motifs:
                counts[category] += protein_seq.count(motif)
        return counts

    def get_label(self, key, val):
        """Bilimsel sınıflandırma etiketleri."""
        thresholds = {
            "Brix": (5.0, 8.0), "Verim": (50, 80), "Cimlenme": (75, 90),
            "Bagisiklik": (30, 60)
        }
        low, high = thresholds.get(key, (30, 70))
        # Çimlenme gibi % içeren değerler için sayısal temizlik
        num_val = float(str(val).replace('%', '')) if isinstance(val, str) else val
        
        if num_val < low: return "Kritik (Düşük)"
        if num_val > high: return "Elite (Yüksek)"
        return "Ticari (Normal)"

    def predict(self, dna_seq):
        protein = self.dna_to_protein(dna_seq)
        if not protein: return {"Error": "Geçersiz DNA Dizisi!"}
            
        biomarks = self.scan_markers(protein)
        seq_len = max(len(protein), 1)
        conf = self.CROP_CONFIG.get(self.crop_type, self.CROP_CONFIG["Domates"])
        
        # 1. Çimlenme Gücü
        cim_artisi = (biomarks["storage_proteins"] / seq_len) * 150
        cim_val = min(conf["base_cim"] + cim_artisi, 99.5)

        # 2. Tat (Brix)
        brix_gain = (biomarks["sugar_transport"] / seq_len) * 60
        brix_val = min(conf["base_brix"] + brix_gain, conf["max_brix"])
        
        # 3. Verim
        yield_pot = (biomarks["biomass_growth"] / seq_len) * 120
        verim_val = yield_pot * conf["yield_mult"]
        
        # 4. Bağışıklık & Stres
        def_score = (biomarks["defense_peptides"] / seq_len) * 100
        str_score = (biomarks["stress_response"] / seq_len) * 100
        
        # Ceza Mekanizması: Stres toleransı düşükse verim ve çimlenme düşer
        if str_score < 0.4:
            verim_val *= 0.75
            cim_val -= 12
            notu = "Zayıf Genetik Kararlılık"
        else:
            notu = "Stabil Genetik Yapı"

        res = {
            'Brix': round(brix_val, 2),
            'Verim': round(verim_val, 2),
            'Cimlenme': round(max(cim_val, 0), 1),
            'Bagisiklik': round(min(def_score * 5, 100), 1),
            'Stres': round(min(str_score * 10, 100), 1),
            'Not': notu
        }
        
        # Sınıflandırmaları ekle
        final_res = {}
        for k, v in res.items():
            if k != 'Not':
                final_res[k] = {"val": v, "label": self.get_label(k, v)}
            else:
                final_res[k] = v
        return final_res
