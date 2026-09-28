"""Twenty-four bounded, executable experiments for the eighteen-chapter book.

A chapter mapping is an educational link, not a claim that the chapter's full
biology has been simulated. Every experiment declares its own omissions.
"""
from __future__ import annotations
import math
import random
from pathlib import Path
from statistics import NormalDist
from .core import ValidationError, number, integer, keys, mean, variance, rmse, load_json, canonical, convert
from .membrane import hh, cable, rates, nernst, GAS_R, BOLTZMANN, AVOGADRO
from .learning import mapping, tournament, candidate
from .evidence import revision_trial


def catalog() -> dict:
    return load_json(Path(__file__).parent/'data'/'experiments.json')


def validate(name:str, overrides:dict|None=None) -> dict:
    labs=catalog()
    if name not in labs: raise ValidationError(f'Unknown experiment: {name}')
    spec=labs[name]['parameters']; overrides={} if overrides is None else overrides
    keys(overrides,set(spec)); p={}
    for k,v in spec.items():
        value=overrides.get(k,v['default'])
        if isinstance(value,dict):
            keys(value,{'value','unit'},{'value','unit'})
            value=convert(value['value'],value['unit'],v['unit'])
        if v['type']=='integer': value=integer(value,k,v['min'],v['max'])
        else: value=number(value,k,v['min'],v['max'])
        p[k]=value
    return p


def loop(p):
    rows=[]; states={'feedback':p['initial'],'open_loop':p['initial']}
    for t in range(p['steps']):
        disturbance=.12 if p['steps']//3<=t<2*p['steps']//3 else 0.
        for key in states:
            action=-p['gain']*states[key] if key=='feedback' else 0.
            states[key]=.95*states[key]+action+disturbance
        rows.append({'step':t,**states})
    return {'rows':rows,'metrics':{'feedback_squared_error':mean([r['feedback']**2 for r in rows]),
      'open_loop_squared_error':mean([r['open_loop']**2 for r in rows])},'series':{'x':'step','y':['feedback','open_loop']},
      'limitations':['Dimensionless scalar control example; no anatomy, consciousness or physiological survival threshold.']}


def ionic(p):
    v=nernst(p['inside_mmol_L'],p['outside_mmol_L'],p['valence'],p['temperature_K'])
    rows=[{'outside_mmol_L':x,'equilibrium_mV':nernst(p['inside_mmol_L'],x,p['valence'],p['temperature_K'])} for x in [1.,2.,5.,10.,20.,50.,100.,140.]]
    return {'rows':rows,'metrics':{'equilibrium_mV':v},'series':{'x':'outside_mmol_L','y':['equilibrium_mV']},
      'limitations':['Single-ion equilibrium with ideal activities. Not the resting potential of a multi-ion membrane.']}


def delay(p):
    rows=[]
    for factor in [.1,.2,.5,1.,2.,5.,10.]:
        length=p['distance_mm']*factor; meters=length*.001
        rows.append({'distance_mm':length,'diffusion_s':meters**2/(2*p['diffusivity_m2_s']),
                     'conduction_s':meters/p['velocity_m_s']+p['synaptic_delay_ms']*.001})
    return {'rows':rows,'metrics':{'comparison':'1D diffusion time versus assigned conduction speed'},
      'series':{'x':'distance_mm','y':['diffusion_s','conduction_s']},
      'limitations':['Conditional scaling comparison, not a reconstruction of ancestral nervous systems.',
                     'Assigned conduction velocity omits diameter, temperature and myelination mechanisms.']}


def network(p):
    rows=[]; gain=p['gain']; tau=p['tau_ms']
    for i in range(201):
        t=p['duration_ms']*i/200; a=t/tau
        rows.append({'time_ms':t,'excitatory_x1':math.exp(-a)*math.cosh(gain*a),
                     'opponent_x1':math.exp(-a)*math.cos(gain*a)})
    return {'rows':rows,'metrics':{'same_unsigned_adjacency':True,'excitatory_max_real_eigenvalue_per_ms':(-1+gain)/tau,
      'opponent_max_real_eigenvalue_per_ms':-1/tau},'series':{'x':'time_ms','y':['excitatory_x1','opponent_x1']},
      'limitations':['Two linear states with the same unsigned adjacency but different signed connections.',
      'Exact solutions isolate signs and gains; no connectome is claimed to have been biologically reconstructed.']}


def development(p):
    rng=random.Random(p['seed']); weights=[.5,.5]; rows=[]
    for i in range(p['steps']):
        sample=[1. if rng.random()<p['preference'] else 0.,1. if rng.random()<1-p['preference'] else 0.]
        weights=[w+p['learning_rate']*s for w,s in zip(weights,sample)]
        total=sum(weights); weights=[w/total for w in weights]
        rows.append({'step':i,'input_1_weight':weights[0],'input_2_weight':weights[1],'total_weight':sum(weights)})
    return {'rows':rows,'metrics':{'final_input_1_weight':weights[0],'max_normalization_error':max(abs(r['total_weight']-1) for r in rows)},
       'series':{'x':'step','y':['input_1_weight','input_2_weight']},
       'limitations':['Normalized competition rule is a synthetic developmental analogy, not a cell-fate or synaptogenesis model.']}


def release(p):
    rng=random.Random(p['seed']); counts=[sum(rng.random()<p['probability'] for _ in range(p['sites'])) for _ in range(p['trials'])]
    theoretical=p['sites']*p['probability']; rows=[]
    for k in range(p['sites']+1):
        prob=math.comb(p['sites'],k)*p['probability']**k*(1-p['probability'])**(p['sites']-k)
        rows.append({'released_vesicles':k,'empirical_probability':counts.count(k)/len(counts),'binomial_probability':prob})
    return {'rows':rows,'metrics':{'sample_mean':mean(counts),'expected_mean':theoretical,'sample_variance':variance(counts),
      'expected_variance':theoretical*(1-p['probability']),'failure_probability':(1-p['probability'])**p['sites']},
      'series':{'x':'released_vesicles','y':['empirical_probability','binomial_probability']},
      'limitations':['Independent identical release sites, no depletion, facilitation or quantal-size variation.']}


def detection(p):
    normal=NormalDist(); d=p['d_prime']; criterion=p['criterion']; rows=[]
    for k in range(-40,41):
        c=k/10; hit=1-normal.cdf(c-d/2); false=1-normal.cdf(c+d/2)
        rows.append({'criterion':c,'hit_rate':hit,'false_alarm_rate':false})
    hit=1-normal.cdf(criterion-d/2); false=1-normal.cdf(criterion+d/2)
    return {'rows':rows,'metrics':{'hit_rate':hit,'false_alarm_rate':false,'balanced_accuracy':(hit+1-false)/2,'d_prime':d},
      'series':{'x':'criterion','y':['hit_rate','false_alarm_rate']},
      'limitations':['Equal-variance Gaussian signal detection. Criterion and sensitivity are distinct; neither measures subjective experience.']}


def motor(p):
    rng=random.Random(p['seed']); noise=[rng.gauss(0,p['noise']) for _ in range(p['steps'])]; out={}; rows=[]
    for lag in [0,p['delay_steps']]:
        x=0.; hist=[x]; series=[]
        for i in range(p['steps']):
            desired=1. if i>=20 else 0.; observation=hist[max(0,len(hist)-1-lag)]+noise[i]
            action=p['gain']*(desired-observation)
            x=.9*x+.1*action; hist.append(x); series.append(x)
        out[lag]=series
    rows=[{'step':i,'target':1. if i>=20 else 0.,'immediate':out[0][i],'delayed':out[p['delay_steps']][i]} for i in range(p['steps'])]
    target=[r['target'] for r in rows]
    return {'rows':rows,'metrics':{'immediate_rmse':rmse(target,out[0]),'delayed_rmse':rmse(target,out[p['delay_steps']])},
       'series':{'x':'step','y':['target','immediate','delayed']},
       'limitations':['Discrete linear motor-control analogy; common measurement noise across arms. No patient or device controller.']}


def body(p):
    # Resource pool is changed by input and expenditure; a neural-like controller reacts to a delayed estimate.
    resource=p['initial_resource']; hist=[resource]; inputs=spent=0.; rows=[]; maxres=0.
    for i in range(p['steps']):
        perceived=hist[max(0,len(hist)-1-p['delay_steps'])]
        demand=p['basal_cost']+(p['extra_cost'] if p['steps']//3<=i<2*p['steps']//3 else 0.)
        acquisition=max(0,min(p['max_intake'],p['basal_cost']+p['gain']*(p['target']-perceived)))
        resource+=acquisition-demand; inputs+=acquisition; spent+=demand
        residual=resource-p['initial_resource']-inputs+spent; maxres=max(maxres,abs(residual)); hist.append(resource)
        rows.append({'step':i,'resource':resource,'perceived':perceived,'acquisition':acquisition,'expenditure':demand,'balance_residual':residual})
        if resource<0: raise ValidationError('Resource exhausted in the declared toy system; no floor clipping applied')
    return {'rows':rows,'metrics':{'balance_residual':maxres,'lowest_resource':min(r['resource'] for r in rows)},
       'series':{'x':'step','y':['resource','perceived']},'limitations':['Resource units are explicitly arbitrary, not blood glucose, hydration, pain or survival predictions.',
        'Actuator saturation is part of the model; negative resource states raise failure instead of being clipped.']}


def attractor(p):
    rng=random.Random(p['seed']); n=p['neurons']; pattern=[rng.choice([-1,1]) for _ in range(n)]
    patterns=[pattern]+[[rng.choice([-1,1]) for _ in range(n)] for _ in range(p['patterns']-1)]
    w=[[0. if i==j else sum(v[i]*v[j] for v in patterns)/n for j in range(n)] for i in range(n)]
    state=[-v if rng.random()<p['corruption'] else v for v in pattern]; rows=[]
    def energy(): return -.5*sum(w[i][j]*state[i]*state[j] for i in range(n) for j in range(n))
    rows.append({'update':0,'energy':energy(),'overlap':sum(x*y for x,y in zip(pattern,state))/n})
    for t in range(p['updates']):
        i=rng.randrange(n); field=sum(w[i][j]*state[j] for j in range(n))
        if field!=0: state[i]=1 if field>0 else -1
        rows.append({'update':t+1,'energy':energy(),'overlap':sum(x*y for x,y in zip(pattern,state))/n})
    return {'rows':rows,'metrics':{'final_overlap':rows[-1]['overlap'],'largest_energy_increase':max(b['energy']-a['energy'] for a,b in zip(rows,rows[1:]))},
       'series':{'x':'update','y':['overlap']},'limitations':['Symmetric asynchronous Hopfield model. Its Lyapunov energy is not measured thermodynamic energy.',
       'Attractor completion is not a claim to reproduce autobiographical memory or subjective recollection.']}


def td(p):
    value=0.; rows=[]
    for t in range(p['trials']):
        reward=1. if t<p['trials']//2 else 0.; error=reward-value
        value+=p['learning_rate']*error
        rows.append({'trial':t,'reward':reward,'value':value,'prediction_error':error})
    return {'rows':rows,'metrics':{'final_value':value},'series':{'x':'trial','y':['reward','value','prediction_error']},
       'limitations':['One-state reward prediction update. Not a dopamine assay, pleasure measure or moral-value metric.']}


def sleep(p):
    pressure=p['initial_pressure']; rows=[]
    for i in range(p['hours']*4+1):
        t=i*.25; phase=t%24; awake=phase<16
        rows.append({'hour':t,'homeostatic_pressure':pressure,'circadian':.5+.5*math.cos(2*math.pi*(t-16)/24),'awake':awake})
        equilibrium=1. if awake else 0.; tau=p['wake_tau_h'] if awake else p['sleep_tau_h']
        pressure=equilibrium+(pressure-equilibrium)*math.exp(-.25/tau)
    return {'rows':rows,'metrics':{'minimum_pressure':min(r['homeostatic_pressure'] for r in rows),'maximum_pressure':max(r['homeostatic_pressure'] for r in rows)},
      'series':{'x':'hour','y':['homeostatic_pressure','circadian']},'limitations':['Assigned 16/8-hour schedule and two-process illustration; not a sleep prescription, diagnosis or individual clock estimate.']}


def social(p):
    n=p['reports']; rho=p['shared_fraction']; effective=n/(1+(n-1)*rho)
    rows=[{'reports':k,'independent_effective_n':float(k),'correlated_effective_n':k/(1+(k-1)*rho)} for k in range(1,n+1)]
    return {'rows':rows,'metrics':{'effective_sample_size':effective,'nominal_sample_size':n,'naive_to_actual_standard_error_ratio':math.sqrt(effective/n)},
      'series':{'x':'reports','y':['independent_effective_n','correlated_effective_n']},
      'limitations':['Exchangeable equal-variance correlated observations; repeated reports are not independent sources.',
      'This is a sampling model, not a judgment about a person, community or cultural value.']}


def access(p):
    rng=random.Random(p['seed']); rows=[]; total_correct=reports=reported_correct=0
    for t in range(p['trials']):
        target=rng.randrange(2); decision=target if rng.random()<p['sensitivity'] else 1-target
        available=rng.random()<p['report_gate']; ok=decision==target
        total_correct+=ok; reports+=available; reported_correct+=ok and available
        rows.append({'trial':t,'target':target,'decision':decision,'reported':decision if available else None})
    return {'rows':rows,'metrics':{'first_order_accuracy':total_correct/p['trials'],'report_rate':reports/p['trials'],
      'accuracy_among_reports':reported_correct/reports if reports else None},
      'limitations':['Independent report gate creates a functional dissociation by construction.',
       'No consciousness score, clinical consciousness diagnosis, IIT Phi or PCI is computed. Absence of report is not taken as absence of experience.']}


def identify(p):
    # Observation y=x1+x2, both decay with tau. Hidden split is unobservable without a selective measurement/intervention.
    rows=[]; maxdifference=0.
    for i in range(101):
        t=p['duration_ms']*i/100; decay=math.exp(-t/p['tau_ms'])
        a=p['split_a']*decay+(1-p['split_a'])*decay
        b=p['split_b']*decay+(1-p['split_b'])*decay
        maxdifference=max(maxdifference,abs(a-b))
        rows.append({'time_ms':t,'observed_a':a,'observed_b':b,'selective_a':p['split_a']*decay,'selective_b':p['split_b']*decay})
    return {'rows':rows,'metrics':{'observation_max_difference':maxdifference,'hidden_split_difference':abs(p['split_a']-p['split_b']),
      'observability_rank_sum_sensor':1,'observability_rank_two_selective_sensors':2},
      'series':{'x':'time_ms','y':['observed_a','observed_b','selective_a','selective_b']},
      'limitations':['Two identical decay modes and an explicit observation map. A selective sensor adds information; it is not free.',
      'A perfect output fit alone cannot identify the hidden split in this constructed model.']}


def energy(p):
    per_event=p['molar_energy_J_mol']/AVOGADRO; bit_floor=BOLTZMANN*p['temperature_K']*math.log(2)
    membrane=.5*(p['capacitance_pF']*1e-12)*(p['voltage_mV']*.001)**2
    return {'rows':[{'quantity':'molar energy converted to one event','value_J':per_event},
                    {'quantity':'ideal one-bit erasure floor','value_J':bit_floor},
                    {'quantity':'capacitor energy relative to zero volts','value_J':membrane}],
       'metrics':{'event_energy_J':per_event,'landauer_floor_J_bit':bit_floor,
        'dimensionless_ratio':per_event/bit_floor,'ratio_via_RT':p['molar_energy_J_mol']/(GAS_R*p['temperature_K']*math.log(2)),
        'capacitor_energy_J':membrane},
       'limitations':['Landauer comparison is an ideal logically irreversible erasure bound, not measured energy of a neural bit.',
       'J/mol is converted to J/event using Avogadro constant before forming the dimensionless ratio.',
       'Capacitor energy, restoration cost, variational free energy and life value are not interchangeable.']}


def clamp(p):
    rows=[]
    for v in range(-100,51,2):
        am,bm,ah,bh,an,bn=rates(float(v))
        rows.append({'voltage_mV':v,'m_inf':am/(am+bm),'h_inf':ah/(ah+bh),'n_inf':an/(an+bn),
          'tau_m_ms':1/(am+bm),'tau_h_ms':1/(ah+bh),'tau_n_ms':1/(an+bn)})
    am,bm,ah,bh,an,bn=rates(p['voltage_mV'])
    return {'rows':rows,'metrics':{'m_inf':am/(am+bm),'h_inf':ah/(ah+bh),'n_inf':an/(an+bn)},
      'series':{'x':'voltage_mV','y':['m_inf','h_inf','n_inf']},'limitations':['Canonical HH steady-state rate curves; not a laboratory voltage-clamp protocol.']}


def alias(p):
    f=p['frequency_Hz']; fs=p['sample_Hz']; alias_f=abs((f+fs/2)%fs-fs/2)
    rows=[{'time_s':i/fs,'sample':math.cos(2*math.pi*f*i/fs),'alias':math.cos(2*math.pi*alias_f*i/fs)} for i in range(p['samples'])]
    return {'rows':rows,'metrics':{'aliased_frequency_Hz':alias_f,'nyquist_Hz':fs/2,
       'max_equal_sample_error':max(abs(r['sample']-r['alias']) for r in rows)},
       'series':{'x':'time_s','y':['sample','alias']},'limitations':['Cosine sampling equivalence; phase/noise/filter dynamics are not estimated. Recovering the original frequency needs additional constraints.']}


def revision(p): return revision_trial(p['budget_bytes'])

FUNCTIONS={'loop':loop,'nernst':ionic,'delay':delay,'network':network,'development':development,'hh':hh,
'release':release,'detection':detection,'motor':motor,'body':body,'attractor':attractor,'td':td,'sleep':sleep,
'cable':cable,'social':social,'access':access,'identify':identify,'energy':energy,'clamp':clamp,'alias':alias,
'mapping':mapping,'revision':revision,'tournament':tournament,'candidate':candidate}


def run(name:str,overrides:dict|None=None) -> dict:
    p=validate(name,overrides); spec=catalog()[name]
    try: result=FUNCTIONS[name](p)
    except (OverflowError, ZeroDivisionError) as exc: raise ValidationError(f'Model arithmetic failed: {exc}; no clipping or default success') from exc
    result.update(experiment=name,model_version='1.0.0',title=spec['title'],parameters=p,
                  book_sections=spec['book_sections'],source_kind='synthetic_or_conditional',
                  question=spec['question'],method=spec['method'],references=spec['references'])
    result.setdefault('limitations',[]); result.setdefault('rows',[]); result.setdefault('metrics',{})
    canonical(result)
    return result
