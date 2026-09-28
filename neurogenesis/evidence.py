"""Versioned, append-only semantic evidence events with dependency invalidation.

Truth is not inferred from a valid graph. Source, event, interpretation and goal
are kept separate; a local event-chain digest requires an external trust anchor.
"""
from __future__ import annotations
from collections import deque
from copy import deepcopy
from .core import ValidationError, keys, canonical, digest
ROLES = {'D','I','K','W','P'}
KINDS = {'observation','synthetic','formal','book','hypothesis','interpretation','goal'}


def evaluate(nodes: dict[str,dict]) -> dict:
    counts={i:0 for i in nodes}; children={i:[] for i in nodes}
    for i,n in nodes.items():
        for parent in n['parents']:
            if parent not in nodes: raise ValidationError(f'Missing dependency: {parent}')
            counts[i]+=1; children[parent].append(i)
    todo=deque(sorted(i for i,n in counts.items() if n==0)); order=[]; valid={}; reasons={}
    while todo:
        i=todo.popleft(); order.append(i); n=nodes[i]; why=[]
        if n['status']!='active': why.append(n['status'])
        if any(not valid[p] for p in n['parents']): why.append('invalid_upstream')
        available=set().union(*(set(nodes[p].get('provides',[])) for p in n['parents'])) if n['parents'] else set()
        if set(n.get('requires',[]))-available: why.append('unsatisfied_contract')
        valid[i]=not why; reasons[i]=why
        for child in children[i]:
            counts[child]-=1
            if counts[child]==0: todo.append(child)
    if len(order)!=len(nodes): raise ValidationError('Dependency cycle')
    return {'valid':valid,'reasons':reasons,'order':order,
            'scope':'Declared structural validity, not independent validation of scientific truth.'}


class EvidenceStore:
    """Each accepted operation preserves the prior event and resulting state."""
    def __init__(self):
        self.nodes:dict[str,dict]={}; self.events:list[dict]=[]; self.goal=None

    def _commit(self, operation:dict, nodes:dict, goal:str|None):
        check=evaluate(nodes)
        prior=self.events[-1]['hash'] if self.events else '0'*64
        event={'sequence':len(self.events),'previous':prior,'operation':deepcopy(operation),
               'state_digest':digest({'nodes':nodes,'goal':goal})}
        self.events.append({**event,'hash':digest(event)})
        self.nodes=nodes; self.goal=goal
        return check

    def put(self,node:dict) -> dict:
        keys(node,{'id','kind','role','text','parents','source','requires','provides'},
             {'id','kind','role','text','parents'})
        if not isinstance(node['id'],str) or not 1<=len(node['id'])<=80: raise ValidationError('Invalid node id')
        if node['id'] in self.nodes: raise ValidationError('Use revise for an existing id')
        if node['kind'] not in KINDS or node['role'] not in ROLES: raise ValidationError('Invalid kind or role')
        if not isinstance(node['text'],str) or len(node['text'])>4000: raise ValidationError('Invalid text')
        for field in ['parents','requires','provides']:
            if not isinstance(node.get(field,[]),list) or any(not isinstance(x,str) for x in node.get(field,[])):
                raise ValidationError('Dependency and contract lists must contain strings')
            if len(set(node.get(field,[])))!=len(node.get(field,[])): raise ValidationError('Duplicate dependency/contract item')
        if node['kind'] in {'observation','formal','book'} and not isinstance(node.get('source'),str):
            raise ValidationError('A source locator is required')
        if len(self.nodes)>=500: raise ValidationError('At most 500 nodes supported')
        if node['kind']=='observation' and node['parents']:
            raise ValidationError('Observations are source records, not computed descendants; use interpretation')
        n=deepcopy(node); n['version']=1; n['status']='active'
        nodes=deepcopy(self.nodes); nodes[n['id']]=n
        return self._commit({'action':'put','node':node},nodes,self.goal)

    def withdraw(self, identifier:str, reason:str) -> dict:
        if identifier not in self.nodes or not isinstance(reason,str) or not reason:
            raise ValidationError('Withdrawal requires an existing id and reason')
        nodes=deepcopy(self.nodes); nodes[identifier]['status']='withdrawn'
        return self._commit({'action':'withdraw','id':identifier,'reason':reason},nodes,self.goal)

    def revise(self, identifier:str, text:str, parents:list[str]) -> dict:
        if identifier not in self.nodes or not isinstance(text,str) or not text or len(text)>4000:
            raise ValidationError('Invalid revision')
        if self.nodes[identifier]['kind'] in {'observation','synthetic','formal','book'}:
            raise ValidationError('Raw/source records are immutable; withdraw and add a new source record')
        if not isinstance(parents,list) or any(not isinstance(x,str) for x in parents) or len(set(parents))!=len(parents):
            raise ValidationError('Invalid parents')
        nodes=deepcopy(self.nodes); n=nodes[identifier]; n.update(text=text,parents=parents,status='active',version=n['version']+1)
        return self._commit({'action':'revise','id':identifier,'text':text,'parents':parents},nodes,self.goal)

    def set_goal(self,goal:str) -> dict:
        if not isinstance(goal,str) or not goal or len(goal)>400: raise ValidationError('Invalid goal')
        return self._commit({'action':'goal','goal':goal},deepcopy(self.nodes),goal)

    def snapshot(self) -> dict:
        return {'nodes':deepcopy(self.nodes),'goal':self.goal,'evaluation':evaluate(self.nodes),
                'head':self.events[-1]['hash'] if self.events else '0'*64}

    @classmethod
    def replay(cls,events:list[dict]):
        if not isinstance(events,list) or len(events)>2000: raise ValidationError('Invalid event list')
        store=cls()
        for event in events:
            if not isinstance(event,dict) or 'operation' not in event: raise ValidationError('Malformed evidence event')
            op=event['operation']; action=op.get('action')
            if action=='put': store.put(op['node'])
            elif action=='withdraw': store.withdraw(op['id'],op['reason'])
            elif action=='revise': store.revise(op['id'],op['text'],op['parents'])
            elif action=='goal': store.set_goal(op['goal'])
            else: raise ValidationError('Unknown event operation')
            if canonical(store.events[-1])!=canonical(event): raise ValidationError('Evidence history mismatch')
        return store


def revision_trial(budget_bytes:int=16000) -> dict:
    s=EvidenceStore(); s.set_goal('Explain a recorded increase without changing the raw event')
    s.put({'id':'raw','kind':'synthetic','role':'D','text':'Recorded response amplitude 2.0; acquisition unit mV.', 'parents':[], 'provides':['raw_voltage']})
    s.put({'id':'cal-v1','kind':'hypothesis','role':'I','text':'Acquisition gain is 1.0.', 'parents':[], 'provides':['calibration']})
    s.put({'id':'mechanism','kind':'interpretation','role':'K','text':'Increased synaptic drive is the initial interpretation.', 'parents':['raw','cal-v1'],'requires':['raw_voltage','calibration']})
    before=s.snapshot(); summary={'answer':s.nodes['mechanism']['text'],'goal':s.goal}
    s.withdraw('cal-v1','A gain change was found; old calibration is invalid')
    after_withdraw=s.snapshot()
    s.put({'id':'cal-v2','kind':'synthetic','role':'D','text':'Calibration record: gain was 2.0.', 'parents':[], 'provides':['calibration']})
    s.revise('mechanism','Gain drift explains the recorded increase under the corrected calibration.',['raw','cal-v2'])
    s.set_goal('Test whether a new independent recording supports the corrected interpretation')
    after=s.snapshot(); restored=EvidenceStore.replay(s.events[:4]).snapshot()
    # Execute all event prefixes into deliberately reduced representations.
    # Queries return retained values or None; scores are equality checks against
    # this public fixture, not hand-assigned architecture ratings.
    views={'summary_only':None,'current_dag':None,'versioned_dag':None}
    withdrawals={}
    for prefix in range(1,len(s.events)+1):
        state=EvidenceStore.replay(s.events[:prefix]).snapshot()
        views['summary_only']={'answer':state['nodes'].get('mechanism',{}).get('text'),'goal':state['goal']}
        views['current_dag']={'nodes':deepcopy(state['nodes']),'goal':state['goal']}
        views['versioned_dag']={'events':deepcopy(s.events[:prefix])}
        if prefix==5:
            withdrawals['summary_only']=None
            withdrawals['current_dag']=evaluate(views['current_dag']['nodes'])['valid']['mechanism']
            withdrawals['versioned_dag']=EvidenceStore.replay(views['versioned_dag']['events']).snapshot()['evaluation']['valid']['mechanism']
    answers={}
    for name,view in views.items():
        current=EvidenceStore.replay(view['events']).snapshot() if 'events' in view else view
        nodes=current.get('nodes',{})
        old_goal=EvidenceStore.replay(view['events'][:4]).snapshot()['goal'] if 'events' in view else None
        answers[name]={'raw_event_retained':nodes.get('raw'),
                      'withdrawal_identified':withdrawals[name],
                      'current_interpretation_updated':nodes.get('mechanism',{}).get('text',current.get('answer')),
                      'past_goal_recoverable':old_goal}
    expected={'raw_event_retained':before['nodes']['raw'],'withdrawal_identified':False,
              'current_interpretation_updated':after['nodes']['mechanism']['text'],'past_goal_recoverable':before['goal']}
    checks={name:{task:answer[task]==expected[task] for task in expected} for name,answer in answers.items()}
    sizes={name:len(canonical(view).encode()) for name,view in views.items()}
    rows=[{'architecture':name,'passed_tasks':sum(t.values()),'tasks':len(t),'serialized_bytes':sizes[name],
           'within_shared_budget':sizes[name]<=budget_bytes,**t} for name,t in checks.items()]
    return {'rows':rows,'metrics':{'shared_budget_bytes':budget_bytes,'versioned_task_passes':sum(checks['versioned_dag'].values()),'stale_descendants_after_retraction':sum(not v for v in after_withdraw['evaluation']['valid'].values())},
            'evidence_events':s.events,'query_answers':answers,'fixture_expected_answers':expected,'limitations':['Four constructed regression tasks, not an independent benchmark of human memory or DIKWP superiority.',
            'All architectures see the same events and budget cap, but they consume different serialized storage; cap failures are reported rather than prevented. These are not runtime-RAM measurements.',
            'Goal changes are software records, not an assertion that a biological brain contains DIKWP labels.']}
