import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils.ProtParam import ProteinAnalysis

class BioValentBeyin:
    def __init__(self):
        self.is_trained = False

    def preprocess_sequence(self, seq_input):
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
        valid_protein = "".join([aa for aa in protein_seq if aa in "ACDEFGHIKLMNPQRSTVWY"])
        if len(valid_protein) < 10: 
            return {"Error": "Analiz için dizi çok kısa."}

        analysis = ProteinAnalysis(valid_protein)
        mw = analysis.molecular_weight()
        pi = analysis.isoelectric_point()
        instability = analysis.instability_index()
        gravy = analysis.gravy()
        aa_percent = analysis.amino_acids_percent 
        n_pool = (aa_percent.get('N', 0) + aa_percent.get('Q', 0) + aa_percent.get('R', 0)) * 100

        # Bilimsel verileri ve ticari karşılıklarını eşleştiriyoruz
        return {
            "Moleküler Kütle": {
                "val": f"{round(mw, 1)} Da",
                "desc": "Proteinin yapısal büyüklüğünü ifade eder.",
                "com": "Yüksek kütle, meyve dolgunluğu ve biyokütle artışı potansiyeline işarettir."
            },
            "İzoelektrik Nokta (pI)": {
                "val": round(pi, 2),
                "desc": f"Proteinin yüksüz olduğu pH değeri {round(pi, 2)}'dir.",
                "com": "Düşük pH'lı topraklarda besin alım verimliliği ve aroma kalitesini belirler."
            },
            "Kararlılık İndeksi": {
                "val": round(instability, 2),
                "desc": "Hücre yapısının bozulmaya karşı direncini ölçer.",
                "com": "40 altı değerler çok stabildir; uzun raf ömrü ve dayanıklı lojistik imkanı sağlar."
            },
            "Su Stresi (GRAVY)": {
                "val": round(gravy, 3),
                "desc": "Proteinin hidrofobik (su itici) dengesidir.",
                "com": "Pozitif değerler kuraklığa ve aşırı sıcaklara karşı genetik zırh anlamına gelir."
            },
            "Çimlenme Enerjisi": {
                "val": f"%{round(n_pool, 1)}",
                "desc": "Amino asit bazlı azot rezerv oranını gösterir.",
                "com": "Tohumun topraktan fırlama gücünü (Vigor) ve fide homojenliğini artırır."
            }
        }

    def predict_dummy(self):
        return "Model Eğit"
