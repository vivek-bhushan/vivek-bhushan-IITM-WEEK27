import re
from dataclasses import dataclass,field
from .tools import PolicyNotFoundError
@dataclass
class AgentResult:
    answer:str; citations:list[str]; quotes:list[str]; trace:list[dict]=field(default_factory=list); steps:int=0; stopped_reason:str="completed"
class PolicyAgent:
    def __init__(self,tools,max_steps=4):self.tools,self.max_steps=tools,max_steps
    @staticmethod
    def _tokens(text):
        stop={"what","when","where","which","does","must","with","from","have","about","policy","employee","employees","company","will","would","could","should","into","only","than","that","this","your","their","they","them","under","after","before","more","much","many","long"}
        return {x for x in re.findall(r"[a-z0-9]+",text.lower()) if len(x)>2 and x not in stop}
    def _select(self,q,d):
        s=[x.strip() for x in re.split(r"(?<=[.!?])\s+",d.text.split(":",1)[-1].strip()) if x.strip()]; qt=self._tokens(q)
        ranked=sorted(((len(qt&self._tokens(x)),-i,x) for i,x in enumerate(s)),reverse=True)
        return [x for n,_,x in ranked if n>0][:2] or ([ranked[0][2]] if ranked else [])
    def answer(self,q,hint=None,forced_doc_id=None):
        trace=[];docs=[];steps=0;match=re.search(r"(?:doc(?:ument)?[_ -]?id|policy id)\s*[:=]?\s*([a-z0-9_]+)",q,re.I);requested=forced_doc_id or (match.group(1) if match else None)
        if requested and steps<self.max_steps:
            steps+=1
            try:d=self.tools.read_policy(requested);docs.append(d);trace.append({"thought":"Read supplied ID first.","action":f"read_policy({requested})","observation":d.text})
            except PolicyNotFoundError as e:trace.append({"thought":"Fail softly, then search.","action":f"read_policy({requested})","observation":{"error":type(e).__name__,"message":str(e)}})
        if not docs and hint and hint.get("doc_ids") and steps<self.max_steps:
            steps+=1
            try:d=self.tools.read_policy(hint["doc_ids"][0]);docs.append(d);trace.append({"thought":"Validate cheapest verified memory hint.","action":f"read_policy({d.doc_id})","observation":d.text})
            except PolicyNotFoundError:pass
        if not docs and steps<self.max_steps:
            steps+=1;hits=self.tools.policy_search(q,3);trace.append({"thought":"Search local corpus.","action":f"policy_search({q!r}, k=3)","observation":[h.__dict__ for h in hits]})
            for h in hits[:2]:
                if steps>=self.max_steps:break
                steps+=1;d=self.tools.read_policy(h.doc_id);docs.append(d);trace.append({"thought":"Read a top candidate.","action":f"read_policy({h.doc_id})","observation":d.text})
        latest=[];seen=set()
        for d in sorted(docs,key=lambda x:x.date,reverse=True):
            family=re.sub(r"_v\d+$","",d.doc_id)
            if "superseded" in d.text.lower() or family in seen:continue
            latest.append(d);seen.add(family)
        if not latest:return AgentResult("I could not find supporting policy in the local corpus.",[],[],trace,steps,"no_evidence")
        parts=[];ids=[];quotes=[]
        for d in latest:
            selected=self._select(q,d)
            if not selected:continue
            words=selected[0].rstrip(".").split();quote=" ".join(words[:18])+("..." if len(words)>18 else "")
            parts.append(f"{' '.join(selected)} [{d.doc_id}] Supporting text: \"{quote}\" [{d.doc_id}]");ids.append(d.doc_id);quotes.append(quote)
        return AgentResult(" ".join(parts),ids,quotes,trace,steps)
