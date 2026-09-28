"""Matched-input experiments, versioned-memory comparison, and locked holdouts."""
from __future__ import annotations
import math
import random
from .core import mean, variance, rmse, ols, predict, digest


def mapping(p:dict) -> dict:
    """All policies get the same cue; truth is delivered only after committing an action."""
    modes=['frozen','delayed','permuted','adaptive']; totals={m:[] for m in modes}; cost={m:[] for m in modes}
    rows=[]; n=p['trials']; shift=n//2
    for seed in range(p['seeds']):
        rng=random.Random(p['seed']+seed); truth=[rng.choice([-1,1]) for _ in range(n)]
        cue=[v*(1 if i<shift else -1)*(-1 if rng.random()<p['noise'] else 1) for i,v in enumerate(truth)]
        perm=list(cue); rng.shuffle(perm) # offline marginal-preserving negative control; not causal online sensing
        score=1.; correct={m:0 for m in modes}; running={m:0 for m in modes}
        for t in range(n):
            action={'frozen':cue[t],'delayed':cue[max(0,t-p['delay_trials'])],
                    'permuted':perm[t],'adaptive':cue[t]*(1 if score>=0 else -1)}
            for m in modes:
                ok=int(action[m]==truth[t]); running[m]+=ok
                if t>=shift: correct[m]+=ok
            # Same feedback available to every policy; only adaptive uses it for updates.
            score=(1-p['learning_rate'])*score+p['learning_rate']*cue[t]*truth[t]
            if seed==0 and (t%max(1,n//300)==0 or t==n-1):
                rows.append({'trial':t+1,**{m:running[m]/(t+1) for m in modes},'phase':0 if t<shift else 1,'mapping_estimate':score})
        for m in modes:
            totals[m].append(correct[m]/(n-shift))
            cost[m].append(n*(p['sensor_nJ']+p['action_nJ'])+(n*p['update_nJ'] if m=='adaptive' else 0))
    delta=[a-b for a,b in zip(totals['adaptive'],totals['frozen'])]
    se=math.sqrt(variance(delta)/len(delta)); effect=mean(delta)
    policies=[{'policy':m,'mean_post_shift_accuracy':mean(totals[m]),'conditional_cost_nJ':mean(cost[m]),
               'actions_per_seed':n,'observations_per_seed':n} for m in modes]
    return {'rows':rows,'policies':policies,'metrics':{'paired_post_shift_accuracy_delta':effect,
       'normal_approx_95_low':effect-1.96*se,'normal_approx_95_high':effect+1.96*se,'seeds':p['seeds']},
       'series':{'x':'trial','y':modes},'limitations':['Synthetic binary reversal task; no neural or clinical validation.',
        'Action and sensing counts/cost coefficients match; adaptive update cost is additional and reported.',
        'The permuted arm is an offline shuffle control, not a deployable causal sensor.',
        'Intervals use a normal approximation across paired seeds, not population-level biological inference.',
        'Frozen and adaptive receive the same noisy cue and post-action feedback; neither sees current truth before acting.']}


def tournament(p:dict) -> dict:
    rng=random.Random(p['seed']); n=p['samples']; m=0.; data=[]
    for i in range(n):
        x=math.sin(i*.19)+rng.gauss(0,.3); structural=math.cos(i*.071)+rng.gauss(0,.2)
        m=.95*m+.05*x
        y=.5*x+.7*structural+p['history_gain']*m+rng.gauss(0,p['noise'])
        data.append((x,structural,m,y))
    ntrain=int(n*.6); nval=int(n*.8)
    specs={'activity':[0], 'structure':[0,1], 'history':[0,1,2]}; results=[]; predictions={}
    for name,cols in specs.items():
        x=[[1.]+[row[c] for c in cols] for row in data]; y=[row[3] for row in data]
        w=ols(x[:ntrain],y[:ntrain]); pred=predict(x,w); predictions[name]=pred
        results.append({'model':name,'parameters':len(w),'weights':w,'train_rmse':rmse(y[:ntrain],pred[:ntrain]),
            'validation_rmse':rmse(y[ntrain:nval],pred[ntrain:nval]),'test_rmse':rmse(y[nval:],pred[nval:])})
    selected=min(results,key=lambda x:(x['validation_rmse'],x['parameters']))['model']
    rows=[{'sample':i,'observed':row[3],**{k:v[i] for k,v in predictions.items()},'split':'train' if i<ntrain else 'validation' if i<nval else 'test'} for i,row in enumerate(data)]
    return {'rows':rows,'models':results,'metrics':{'selected_by_validation':selected,'train_samples':ntrain,
      'validation_samples':nval-ntrain,'test_samples':n-nval,'test_used_for_selection':False},
      'selection_record':{'training_digest':digest(data[:ntrain]),'validation_digest':digest(data[ntrain:nval]),'selected_model':selected},
      'series':{'x':'sample','y':['observed',selected]},'limitations':['Known synthetic generating mechanism; richer models are not guaranteed to win when history_gain is zero.',
      'The history variable is observed in the synthetic data; applying this model to research recordings requires a justified measurement or independently validated estimator.',
      'Nested models use different feature subsets of the same table. Their measurement costs are not assumed equal.',
      'Normal-equation OLS is limited to small well-conditioned designs; a pivot guard rejects singular cases.']}


def candidate(p:dict) -> dict:
    rng=random.Random(p['seed']); n=p['samples']; data=[]
    for i in range(n):
        spikes=rng.uniform(1,8); duration=rng.uniform(1,5); bits=rng.uniform(.2,3)
        compression=rng.uniform(.2,1); coupling=rng.uniform(.2,1); term=bits*compression*coupling
        energy=.4*spikes+.2*duration+p['psi_nJ_bit']*term+rng.gauss(0,p['noise_nJ'])
        data.append((spikes,duration,term,energy))
    cut=int(n*.7); results=[]; rows=[]
    for name,cols in [('resource_only',[0,1]),('candidate_term',[0,1,2])]:
        x=[[1.]+[r[c] for c in cols] for r in data]; y=[r[3] for r in data]
        w=ols(x[:cut],y[:cut]); fitted=predict(x,w)
        results.append({'model':name,'weights':w,'train_rmse_nJ':rmse(y[:cut],fitted[:cut]),'holdout_rmse_nJ':rmse(y[cut:],fitted[cut:])})
        for i in range(cut,n): rows.append({'sample':i,'model':name,'observed_nJ':y[i],'predicted_nJ':fitted[i]})
    return {'rows':rows,'models':results,'metrics':{'candidate_holdout_rmse_nJ':results[1]['holdout_rmse_nJ'],
         'baseline_holdout_rmse_nJ':results[0]['holdout_rmse_nJ'],'fitted_psi_nJ_bit':results[1]['weights'][-1]},
         'limitations':['E = Psi * I * C * A is evaluated here only as a declared phenomenological feature.',
         'I is in bits, C and A are dimensionless, so Psi has energy/bit units; data are synthetic.',
         'This regression cannot distinguish an independent information field from omitted conventional mechanisms.',
         'The holdout is evaluated but not used for feature or parameter selection; preregistration requires an external timestamp, not just a local digest.']}
