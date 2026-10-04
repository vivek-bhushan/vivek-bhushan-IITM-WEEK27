import faiss,numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
class VerifiedFactMemory:
    def __init__(self,dimension=512):self.vectorizer=HashingVectorizer(n_features=dimension,alternate_sign=False,norm="l2");self.index=faiss.IndexFlatIP(dimension);self.entries=[]
    def _v(self,t):return np.ascontiguousarray(self.vectorizer.transform([t]).toarray().astype("float32"))
    def write(self,q,r,valid):
        if not valid or not r.citations:return False
        self.index.add(self._v(q));self.entries.append({"question":q,"answer":r.answer,"doc_ids":list(r.citations)});return True
    def read(self,q,threshold=.65):
        if not self.entries:return None
        scores,indices=self.index.search(self._v(q),1)
        if indices[0][0]<0 or scores[0][0]<threshold:return None
        e=dict(self.entries[int(indices[0][0])]);e["score"]=float(scores[0][0]);return e
