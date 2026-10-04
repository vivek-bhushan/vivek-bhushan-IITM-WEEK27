import json
from dataclasses import dataclass
from pathlib import Path
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class PolicyNotFoundError(Exception):
    def __init__(self, doc_id):
        self.doc_id=doc_id; super().__init__(f"Policy document not found: {doc_id}")

@dataclass(frozen=True)
class PolicyDocument: doc_id:str; text:str; date:str
@dataclass(frozen=True)
class SearchHit: doc_id:str; score:float; date:str; preview:str

class PolicyTools:
    def __init__(self,dataset_path="policies.jsonl"):
        rows=[json.loads(x) for x in Path(dataset_path).read_text(encoding="utf-8").splitlines() if x.strip()]
        required={"doc_id","text","date"}
        if not rows or any(not required.issubset(r) for r in rows): raise ValueError("Each policy row requires doc_id, text and date")
        self.documents=[PolicyDocument(r["doc_id"],r["text"],r["date"]) for r in rows]
        self.by_id={d.doc_id:d for d in self.documents}
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words="english",sublinear_tf=True)
        vectors=np.ascontiguousarray(self.vectorizer.fit_transform(d.text for d in self.documents).toarray().astype("float32"))
        faiss.normalize_L2(vectors); self.index=faiss.IndexFlatIP(vectors.shape[1]); self.index.add(vectors)
    def policy_search(self,query,k=3):
        if not query.strip() or k<1:return []
        vector=np.ascontiguousarray(self.vectorizer.transform([query]).toarray().astype("float32"))
        if not np.any(vector):return []
        faiss.normalize_L2(vector); scores,indices=self.index.search(vector,len(self.documents)); hits=[]
        for score,index in zip(scores[0],indices[0]):
            if index<0 or score<=0:continue
            d=self.documents[int(index)]; adjusted=float(score)*(0.25 if "superseded" in d.text.lower() else 1)
            hits.append(SearchHit(d.doc_id,adjusted,d.date,d.text[:180]))
        hits.sort(key=lambda h:(h.score,h.date,h.doc_id),reverse=True); return hits[:k]
    def read_policy(self,doc_id):
        if doc_id not in self.by_id:raise PolicyNotFoundError(doc_id)
        return self.by_id[doc_id]
    @staticmethod
    def safe_divide(a,b):
        if b==0:raise ZeroDivisionError("Cannot divide by zero")
        return a/b
