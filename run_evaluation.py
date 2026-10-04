import csv,json,re,time
from pathlib import Path
from policy_assistant import *
QUESTIONS=[("Q1","How many days per week may an eligible employee work remotely?","remote_work_v3"),("Q2","How many annual leave days do full-time employees receive, and what can be carried over?","leave_policy_v2"),("Q3","What is the meal allowance for approved travel within India?","travel_expense_v4"),("Q4","When is MFA mandatory and how quickly must a new employee enroll?","security_mfa_v1"),("Q5","What are the password length and rotation requirements?","password_policy_v2"),("Q6","Can a fully remote employee claim home-office equipment support?","laptop_equipment_v1"),("Q7","How long are customer personal data and internal HR records retained?","data_retention_v2"),("Q8","What approval is needed for an expense above INR 25000?","expense_approval_v1"),("Q9","How is VPN access approved, and when does an inactive session time out?","vpn_access_v2")]
def build_graph(budget=8):
 t=PolicyTools("policies.jsonl");return PolicyGraph(PolicyAgent(t),GroundingCritic(t),VerifiedFactMemory(),budget)
def evaluate():
 Path("logs").mkdir(exist_ok=True);g=build_graph();rows=[];traces=[]
 for qid,q,expected in QUESTIONS:
  t=time.perf_counter();r=g.run(q);ms=round((time.perf_counter()-t)*1000,3);row={"id":qid,"question":q,"expected_doc_id":expected,"latency_ms":ms,"agent_steps":r.agent_steps,"graph_steps":r.graph_steps,"has_docid":bool(re.search(r"\[[a-z0-9_]+\]",r.answer)),"critic_valid":r.critic["valid"],"pass":r.critic["valid"] and f"[{expected}]" in r.answer,"memory_hit":r.memory_hit,"stopped_reason":r.stopped_reason,"answer":r.answer};rows.append(row);traces.append({"result":r.__dict__,"evaluation":row});print(f"{qid}: latency={ms:.3f} ms | steps={r.agent_steps} | has_docid={row['has_docid']} | pass={row['pass']}")
 with open("logs/evaluation_results.csv","w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 with open("logs/evaluation_traces.jsonl","w",encoding="utf-8") as f:
  for x in traces:f.write(json.dumps(x)+"\n")
 s={"questions":len(rows),"passed":sum(x["pass"] for x in rows),"pass_rate":sum(x["pass"] for x in rows)/len(rows),"average_latency_ms":sum(x["latency_ms"] for x in rows)/len(rows)};Path("logs/evaluation_summary.json").write_text(json.dumps(s,indent=2));return s
if __name__=="__main__":print(json.dumps(evaluate(),indent=2))
