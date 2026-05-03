import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from sklearn.ensemble import RandomForestRegressor

class BioValentBeyin:
    def __init__(self):
        self.is_trained = False
        self.model_brix = None
        self.model_verim = None

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

    def train_custom_model(self, df):
        """Kullanıcının yüklediği CSV ile AI'yı eğitir."""
        try:
            X, y_brix, y_verim = [], [], []
            for _, row in df.iterrows():
                prot, _ = self.preprocess_sequence(str(row['Sekans']))
                valid_prot = "".join([aa for aa in prot if aa in "ACDEFGHIKLMNPQRSTVWY"])
                if len(valid_prot) >= 10:
                    analysis = ProteinAnalysis(valid_prot)
                    X.append([analysis.molecular_weight(), analysis.isoelectric_point(), analysis.gravy(), analysis.instability_index()])
                    y_brix.append(float(row['Brix']))
                    y_verim.append(float(row['Verim']))
            
            self.model_brix = RandomForestRegressor(n_estimators=100).fit(X, y_brix)
            self.model_verim = RandomForestRegressor(n_estimators=100).fit(X, y_verim)
            self.is_trained = True
            return "Başarılı: Yapay zeka firmanıza özel verilerle eğitildi!"
        except Exception as e:
            return f"Hata: CSV formatı hatalı. (Sütunlar: Sekans, Brix, Verim olmalı). Detay: {e}"

    def predict_phenotype(self, protein_seq):
        """Eğitilmiş modelle tahmin yapar."""
        if not self.is_trained:
            return None
        analysis = ProteinAnalysis(protein_seq)
        feats = [[analysis.molecular_weight(), analysis.isoelectric_point(), analysis.gravy(), analysis.instability_index()]]
        return {
            "Brix": round(self.model_brix.predict(feats)[0], 2),
            "Verim": round(self.model_verim.predict(feats)[0], 2)
        }
