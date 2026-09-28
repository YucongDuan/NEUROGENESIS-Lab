"""Explicit neural biophysics: HH membrane and a sealed passive cable.

HH voltages use an absolute convention with resting voltage near -65 mV.
Canonical squid-axon rates correspond to 6.3 C. No human-neuron calibration.
"""
from __future__ import annotations
import math
from .core import ValidationError, rk4
FARADAY = 96485.33212
GAS_R = 8.31446261815324
BOLTZMANN = 1.380649e-23
AVOGADRO = 6.02214076e23


def nernst(inside: float, outside: float, charge: int, temperature_K: float) -> float:
    if inside <= 0 or outside <= 0 or charge == 0 or temperature_K <= 0:
        raise ValidationError("Nernst equation requires positive concentrations/temperature and nonzero valence")
    return GAS_R*temperature_K/(charge*FARADAY)*math.log(outside/inside)*1000


def vtrap(x: float, scale: float) -> float:
    """x/(1-exp(-x/scale)), with its removable singularity evaluated stably."""
    u = x/scale
    if abs(u) < 1e-6:
        return scale*(1+u/2+u*u/12)
    return x/(-math.expm1(-u))


def rates(v: float) -> tuple[float, ...]:
    if not math.isfinite(v) or not -150 <= v <= 150:
        raise ValidationError("HH voltage outside [-150,150] mV; reduce dt or change input")
    return (.1*vtrap(v+40,10), 4*math.exp(-(v+65)/18),
            .07*math.exp(-(v+65)/20), 1/(1+math.exp(-(v+35)/10)),
            .01*vtrap(v+55,10), .125*math.exp(-(v+65)/80))


def hh(p: dict) -> dict:
    h0 = p['dt_ms']; duration = p['duration_ms']
    if p['pulse_start_ms'] >= p['pulse_end_ms'] or p['pulse_end_ms'] > duration:
        raise ValidationError("Pulse interval must be ordered and inside the simulation")
    if duration/h0 > 40000 or h0 > .025:
        raise ValidationError("HH permits dt <= 0.025 ms and at most 40000 steps")
    a,b,c,d,e,f = rates(-65.)
    # V,m,h,n; signed Na,K,leak,external charge; inward Na; ionic dissipation
    y = [-65.,a/(a+b),c/(c+d),e/(e+f)]+[0.]*6
    t=0.; rows=[]; spikes=[]; max_res=0.; low=1.; high=0.
    edges=sorted(set([p['pulse_start_ms'],p['pulse_end_ms'],duration]))
    def record():
        nonlocal max_res, low, high
        residual = p['capacitance_uF_cm2']*(y[0]+65)-(y[7]-y[4]-y[5]-y[6])
        max_res=max(max_res,abs(residual)); low=min(low,*y[1:4]); high=max(high,*y[1:4])
        rows.append({'time_ms':t,'voltage_mV':y[0],'m':y[1],'h':y[2],'n':y[3],
                     'charge_balance_nC_cm2':residual})
    record()
    while t < duration-1e-10:
        future=[b for b in edges if b>t+1e-10]
        step=min(h0, duration-t, future[0]-t if future else h0)
        midpoint=t+step/2
        inj=p['current_uA_cm2'] if p['pulse_start_ms'] <= midpoint < p['pulse_end_ms'] else 0.
        def rhs(z):
            v,m,h,n=z[:4]; am,bm,ah,bh,an,bn=rates(v)
            if any(q < -1e-5 or q>1.00001 for q in (m,h,n)):
                raise ValidationError("Gate left [0,1]; no clipping is applied")
            gna=p['g_na_mS_cm2']*m**3*h; gk=p['g_k_mS_cm2']*n**4; gl=.3
            ina=gna*(v-50); ik=gk*(v+77); il=gl*(v+54.387)
            heat=gna*(v-50)**2+gk*(v+77)**2+gl*(v+54.387)**2
            return [(inj-ina-ik-il)/p['capacitance_uF_cm2'],am*(1-m)-bm*m,ah*(1-h)-bh*h,an*(1-n)-bn*n,
                    ina,ik,il,inj,max(0.,-ina),heat]
        old=y[0]; y=rk4(y,step,rhs)
        if old < 0 <= y[0]: spikes.append(t+step*(-old)/(y[0]-old))
        t+=step; record()
    return {'rows':rows,'metrics':{'spike_count':len(spikes),'peak_mV':max(r['voltage_mV'] for r in rows),
        'charge_residual_nC_cm2':max_res,'min_gate':low,'max_gate':high,
        'inward_sodium_C_cm2':y[8]*1e-9,
        'ideal_Na_pump_energy_J_cm2':y[8]*1e-9/FARADAY/3*50000,
        'ionic_dissipation_J_cm2':y[9]*1e-12},'spike_times_ms':spikes,
        'series':{'x':'time_ms','y':['voltage_mV']},
        'limitations':['Space-clamped HH membrane, not an axonal propagation or human whole-brain model.',
        'Fixed reversal potentials; 6.3 C kinetic convention; no dynamic ion reservoirs.',
        'Inward Na/3 and 50 kJ/mol estimate only an ideal Na-restoration budget, including resting influx over this interval.',
        'Conductance dissipation and ATP restoration are different ledgers; they are not added or equated to total metabolism.']}


def cable(p: dict) -> dict:
    n=p['compartments']; c=p['capacitance_pF']; gl=p['leak_nS']; ga=p['axial_nS']
    if p['dt_ms']*(gl+4*ga)/c > .5:
        raise ValidationError("Cable step exceeds the conservative stiffness guard")
    v=[0.]*n; y=v+[0.,0.]; rows=[]; t=0.; max_res=0.
    while True:
        residual=c*math.fsum(y[:n])-y[n]+y[n+1]
        max_res=max(max_res,abs(residual))
        row={'time_ms':t,'proximal_mV':y[0],'middle_mV':y[n//2],'distal_mV':y[n-1],
             'charge_residual_fC':residual}; rows.append(row)
        if t>=p['duration_ms']-1e-10: break
        step=min(p['dt_ms'],p['duration_ms']-t)
        def rhs(z):
            flux=[]
            for i in range(n):
                axial=ga*((z[i-1]-z[i]) if i else 0)+ga*((z[i+1]-z[i]) if i<n-1 else 0)
                flux.append(((p['current_pA'] if i==0 else 0)-gl*z[i]+axial)/c)
            return flux+[p['current_pA'], gl*math.fsum(z[:n])]
        y=rk4(y,step,rhs); t+=step
    return {'rows':rows,'metrics':{'distal_to_proximal_ratio':y[n-1]/y[0] if y[0] else 0.,
        'charge_residual_fC':max_res},'series':{'x':'time_ms','y':['proximal_mV','middle_mV','distal_mV']},
        'limitations':['Sealed, identical passive compartments; voltage is displacement from rest.',
        'Changing axial conductance is a model lesion, not a clinical disease classifier.',
        'No active channels, morphology reconstruction, myelin geometry or conduction velocity estimate.']}
