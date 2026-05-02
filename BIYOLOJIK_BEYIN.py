import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils.ProtParam import ProteinAnalysis

class BioValentBeyin:
    def __init__(self):
        self.is_trained = False
        # Şirket özel modelleri burada saklanacak, şuan boş.

    def preprocess_sequence(self, seq_input):
        """DNA veya Protein ayrımını yapar."""
        seq = "".join(seq_input.split()).upper()
        valid_dna = set("ATGCUN")
        if set(seq).issubset(valid_dna):
            seq = seq[:(len(seq)//3)*3]
            protein = str(Seq(seq).translate(to_stop=True))
            seq_type = "DNA Dizisi (Proteine Çevrildi)"
        else:
            protein = seq
            seq_type = "Amino Asit Dizisi"
        return protein, seq_type

    def calculate_science(self, protein_seq):
        """%100 Bilimsel Veriler (Eğitim gerektirmez, değişmez gerçeklerdir)"""
        valid_protein = "".join([aa for aa in protein_seq if aa in "ACDEFGHIKLMNPQRSTVWY"])
        if len(valid_protein) < 10: 
            return {"Error": "Analiz için dizi çok kısa (Min. 10 AA)."}

        analysis = ProteinAnalysis(valid_protein)
        
        # Bilimsel Parametreler
        mw = analysis.molecular_weight()
        pi = analysis.isoelectric_point()
        instability = analysis.instability_index()
        gravy = analysis.gravy()
        
        # Çimlenme Gücü (Azot Rezervi Hesabı)
        aa_percent = analysis.get_amino_acids_percent()
        n_pool = (aa_percent.get('N', 0) + aa_percent.get('Q', 0) + aa_percent.get('R', 0)) * 100

        return {
            "Moleküler Kütle": f"{round(mw, 1)} Da",
            "İzoelektrik Nokta (pI)": round(pi, 2),
            "Kararlılık İndeksi": f"{round(instability, 2)}",
            "Su Stresi Toleransı (GRAVY)": f"{round(gravy, 3)}",
            "Çimlenme Enerjisi (Azot)": f"%{round(n_pool, 1)}",
            "Protein Uzunluğu": f"{len(valid_protein)} AA"
        }

    def predict_dummy(self):
        """Eğitilmeyen alanlar için sabit uyarı döner."""
        return "Model Eğit"
