from dataclasses import dataclass
@dataclass
class GraphResult:question:str;answer:str;critic:dict;trace:list;graph_steps:int;agent_steps:int;retries:int;memory_hit:bool;stopped_reason:str
class PolicyGraph:
    def __init__(self,agent,critic,memory,max_graph_steps=8,max_retries=1):self.agent,self.critic,self.memory=agent,critic,memory;self.max_graph_steps,self.max_retries=max_graph_steps,max_retries
    def run(self,q,forced_doc_id=None):
        trace=[];steps=0;retries=0;result=None;verdict=None
        def visit(n,d):
            nonlocal steps
            if steps>=self.max_graph_steps:return False
            steps+=1;trace.append({"node":n,"details":d});return True
        if not visit("plan",{"route":"memory_read -> agent_answer -> critic"}):return self._budget(q,trace,steps)
        if not visit("memory_read",{}):return self._budget(q,trace,steps)
        hint=self.memory.read(q);memory_hit=hint is not None;trace[-1]["details"]={"hit":memory_hit,"hint":hint}
        while True:
            if not visit("agent_answer",{"retry":retries}):return self._budget(q,trace,steps,result)
            result=self.agent.answer(q,hint,forced_doc_id if retries==0 else None);trace.extend({"node":"agent_trace","details":x} for x in result.trace)
            if not visit("critic",{}):return self._budget(q,trace,steps,result)
            verdict=self.critic.evaluate(result);trace[-1]["details"]=verdict
            if verdict["valid"] or retries>=self.max_retries:break
            retries+=1;hint=None;forced_doc_id=None
        if not visit("memory_write",{}):return self._budget(q,trace,steps,result)
        trace[-1]["details"]={"written":self.memory.write(q,result,verdict["valid"])};reason="completed" if verdict["valid"] else "critic_failed_after_retry";visit("stop",{"reason":reason})
        return GraphResult(q,result.answer,verdict,trace,steps,result.steps,retries,memory_hit,reason)
    @staticmethod
    def _budget(q,trace,steps,result=None):trace.append({"node":"stop","details":{"reason":"budget_exhausted"}});return GraphResult(q,result.answer if result else "Stopped: graph budget exhausted.",{"valid":False,"issues":["graph_budget_exhausted"]},trace,steps,result.steps if result else 0,0,False,"budget_exhausted")
