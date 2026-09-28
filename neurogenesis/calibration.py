"""Train-only passive-membrane step-response fitting from a narrow CSV contract."""
from __future__ import annotations
import csv
import io
import math
from .core import ValidationError, keys, number, convert, ols, rmse, digest


def fit_csv(text:str, metadata:dict) -> dict:
    required={'source_kind','source_locator','license','time_unit','voltage_unit','current_pA','rest_mV','onset_ms'}
    keys(metadata,required,required)
    if metadata['source_kind'] not in {'synthetic','public_research'}:
        raise ValidationError('Only synthetic or explicitly public research recordings are supported')
    for k in ['source_locator','license']:
        if not isinstance(metadata[k],str) or not 1<=len(metadata[k])<=500:
            raise ValidationError(f'{k} must be declared')
    current=number(metadata['current_pA'],'current_pA',1,1000)
    rest=number(metadata['rest_mV'],'rest_mV',-100,0)
    onset=number(metadata['onset_ms'],'onset_ms',0,100000)
    if not isinstance(text,str) or len(text.encode('utf-8'))>500000:
        raise ValidationError('CSV must be UTF-8 text within 500 kB')
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames!=['time','voltage','split']:
        raise ValidationError('CSV header must be exactly time,voltage,split')
    rows=[]
    try:
        for row in reader:
            if len(rows)>=2000 or set(row)!={'time','voltage','split'}: raise ValidationError('Invalid CSV row or too many rows')
            t=convert(float(row['time']),metadata['time_unit'],'ms')
            v=convert(float(row['voltage']),metadata['voltage_unit'],'mV')
            number(t,'time_ms',onset,100000); number(v,'voltage_mV',-150,150)
            if row['split'] not in {'train','test'}: raise ValidationError('split must be train or test')
            if rows and t<=rows[-1]['time_ms']: raise ValidationError('Times must be strictly increasing, without duplicates')
            rows.append({'time_ms':t,'voltage_mV':v,'split':row['split']})
    except (ValueError,TypeError,KeyError) as exc:
        raise ValidationError(f'Invalid numeric CSV: {exc}') from exc
    train=[r for r in rows if r['split']=='train']; test=[r for r in rows if r['split']=='test']
    if len(train)<8 or len(test)<4: raise ValidationError('At least 8 training and 4 held-out rows are required')
    train_digest=digest(train)  # Bind acquisition rows, not the later fitted predictions.
    grid=[1.+i for i in range(200)]; profile=[]
    observed=[r['voltage_mV'] for r in train]
    for tau in grid:
        # Voltage displacement per MOhm: pA * MOhm = 0.001 mV.
        basis=[current*.001*(-math.expm1(-(r['time_ms']-onset)/tau)) for r in train]
        denominator=math.fsum(v*v for v in basis)
        if denominator<1e-12: raise ValidationError('No post-onset information identifies a time constant')
        resistance=math.fsum(x*(y-rest) for x,y in zip(basis,observed))/denominator
        if resistance<=0: continue
        pred=[rest+resistance*x for x in basis]
        profile.append({'tau_ms':tau,'resistance_MOhm':resistance,'train_rmse_mV':rmse(observed,pred)})
    if not profile: raise ValidationError('No positive-resistance fit in the declared model family')
    best=min(profile,key=lambda x:x['train_rmse_mV']); tau=best['tau_ms']; resistance=best['resistance_MOhm']
    for r in rows:
        r['predicted_mV']=rest+current*.001*resistance*(-math.expm1(-(r['time_ms']-onset)/tau))
        r['residual_mV']=r['voltage_mV']-r['predicted_mV']
    test=[r for r in rows if r['split']=='test']
    return {'experiment':'fit-passive','model_version':'1.0.0','title':'Recorded passive step-response fit',
       'question':'Does a train-fitted passive RC model predict the held-out voltages?',
       'method':'Profile over tau = 1..200 ms at 1 ms spacing; positive resistance fit analytically from training data only.',
       'source_kind':metadata['source_kind'],'parameters':metadata,'book_sections':['6.4','17.7','17.10'],
       'references':['BOOK'],'rows':rows,'profile':profile,'series':{'x':'time_ms','y':['voltage_mV','predicted_mV']},
       'metrics':{**best,'capacitance_pF':1000*tau/resistance,
           'test_rmse_mV':rmse([r['voltage_mV'] for r in test],[r['predicted_mV'] for r in test]),
           'train_rows':len(train),'test_rows':len(test),'at_grid_boundary':tau in {grid[0],grid[-1]},'test_used_for_fitting':False},
       'training_selection':{'train_digest':train_digest,'tau_grid_ms':{'start':1,'stop':200,'step':1}},
       'limitations':['Assumes known rest, onset and a maintained positive current step; no spikes, offset drift or current variation.',
       'Grid-profile fit is not a confidence interval, nor independent biological validation.',
       'The source declaration is user supplied; the program cannot verify licensing, de-identification or ethical approval.',
       'Public-research CSV import is supported; NWB/ABF, electrodes, stimulation and clinical use are not.']}
