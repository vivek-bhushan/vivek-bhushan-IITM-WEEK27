import re
class GroundingCritic:
    def __init__(self,tools):self.tools=tools
    def evaluate(self,result):
        issues=[];ids=re.findall(r"\[([a-z0-9_]+)\]",result.answer)
        if not ids:issues.append("missing_doc_id")
        if not result.quotes or '"' not in result.answer:issues.append("missing_quote")
        for doc_id in dict.fromkeys(ids):
            try:source=" ".join(self.tools.read_policy(doc_id).text.lower().split())
            except Exception:issues.append(f"unknown_doc_id:{doc_id}");continue
            if not any(q.lower().replace("...","") in source for q in result.quotes):issues.append(f"quote_not_supported:{doc_id}")
        return {"valid":not issues,"issues":issues}
