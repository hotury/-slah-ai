import numpy as np
from Bio.Seq import Seq

class IslahAI:
    def __init__(self):
        self.PLANT_CONFIG = {
            "Domates": {"brix": 0.45, "yield": 12.0, "germination": 0.8, "disease": 1.2},
            "Biber": {"brix": 0.35, "yield": 8.0, "germination": 0.7, "disease": 1.5},
            "Hıyar": {"brix": 0.20, "yield": 15.0, "germination": 0.9, "disease": 1.0},
            "Kabak": {"brix": 0.25, "yield": 14.0, "germination": 0.85, "disease": 1.1},
            "Karpuz": {"brix": 0.50, "yield": 18.0, "germination": 0.75, "disease": 0.9},
            "Kavun": {"brix": 0.55, "yield": 13.0, "germination": 0.80, "disease": 1.0},
            "Patlıcan": {"brix": 0.30, "yield": 10.0, "germination": 0.70, "disease": 1.3}
        }

    def process_genome_file(self, file_content):
        """FASTA/TXT içeriğini temizler ve saf sekansı döndürür."""
        lines = file_content.splitlines()
        # FASTA başlıklarını (>) ayıkla ve satırları birleştir
        clean_seq = "".join([line.strip() for line in lines if not line.startswith(">")])
        return clean_seq.upper().replace(" ", "")

    def translate_dna(self, dna_sequence):
        try:
            coding_dna = Seq(dna_sequence)
            return str(coding_dna.translate(to_stop=True))
        except:
            return None

    def calculate_aa_metrics(self, protein_seq):
        if not protein_seq: return None
        seq_len = len(protein_seq)
        return {
            "sugar_index": sum(protein_seq.count(x) for x in "ST") / seq_len,
            "growth_index": sum(protein_seq.count(x) for x in "LIV") / seq_len,
            "stress_index": sum(protein_seq.count(x) for x in "P") / seq_len,
            "defense_index": sum(protein_seq.count(x) for x in "RK") / seq_len,
            "energy_index": sum(protein_seq.count(x) for x in "AG") / seq_len,
            "stability_index": sum(protein_seq.count(x) for x in "YF") / seq_len
        }

    def predict_all_parameters(self, protein_seq, plant_type):
        m = self.calculate_aa_metrics(protein_seq)
        if not m: return None, None
        cfg = self.PLANT_CONFIG.get(plant_type, self.PLANT_CONFIG["Domates"])
        
        results = {
            "Brix": round(4.0 + (m["sugar_index"] * 25 * cfg["brix"]), 2),
            "Verim": round(50 + (m["growth_index"] * 120 * cfg["yield"] / 10), 2),
            "Cimlenme": round(70 + (m["energy_index"] * 30 * cfg["germination"]), 2),
            "Hastalik": round(20 + (m["defense_index"] * 60 * cfg["disease"]), 2),
            "Stres": round(m["stress_index"] * 50, 2),
            "RafOmru": round(5 + (m["stability_index"] * 40), 2),
            "Vigor": round(1 + (m["growth_index"] * 9), 2)
        }
        return results, m
