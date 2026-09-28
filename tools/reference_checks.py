"""Optional release-time numerical comparison (requires SciPy, not a runtime dependency).

An independently written relative-voltage HH RHS is integrated with DOP853.
This cross-check detects implementation/integration discrepancies; it is not
an independent experimental validation or an actual run of Brian2.
"""
from pathlib import Path
import sys,math,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scipy
from scipy.integrate import solve_ivp
from neurogenesis.experiments import run,catalog
from neurogenesis.core import write_json

def relative_rates(u):
    # Reparameterized relative-to-rest convention, deliberately not using rates().
    def quotient(a,b):return b if abs(a)<1e-10 else a/(-math.expm1(-a/b))
    return .1*quotient(u-25,10),4*math.exp(-u/18),.07*math.exp(-u/20),1/(1+math.exp((30-u)/10)),.01*quotient(u-10,10),.125*math.exp(-u/80)

def compare():
    settings={k:v['default'] for k,v in catalog()['hh']['parameters'].items()}
    a,b,c,d,e,f=relative_rates(0); y=[0,a/(a+b),c/(c+d),e/(e+f)]
    endpoints=[0,settings['pulse_start_ms'],settings['pulse_end_ms'],settings['duration_ms']];parts=[]
    for left,right in zip(endpoints,endpoints[1:]):
        current=settings['current_uA_cm2'] if settings['pulse_start_ms']<=.5*(left+right)<settings['pulse_end_ms'] else 0.
        def rhs(t,z):
            u,m,h,n=z;am,bm,ah,bh,an,bn=relative_rates(u)
            dv=(current-120*m**3*h*(u-115)-36*n**4*(u+12)-.3*(u-10.613))/settings['capacitance_uF_cm2']
            return [dv,am*(1-m)-bm*m,ah*(1-h)-bh*h,an*(1-n)-bn*n]
        sol=solve_ivp(rhs,(left,right),y,method='DOP853',rtol=1e-10,atol=1e-12,dense_output=True,max_step=.025)
        if not sol.success:raise RuntimeError(sol.message)
        parts.append((left,right,sol));y=sol.y[:,-1]
    checks=[]
    for dt in [.025,.0125,.00625]:
        r=run('hh',{'dt_ms':dt});errors=[]
        for row in r['rows']:
            t=row['time_ms'];segment=next((s for l,h,s in parts if l-1e-8<=t<=h+1e-8),parts[-1][2]);errors.append(abs(row['voltage_mV']-(float(segment.sol(t)[0])-65)))
        checks.append({'dt_ms':dt,'max_voltage_error_mV':max(errors),'rms_voltage_error_mV':math.sqrt(sum(x*x for x in errors)/len(errors)), 'charge_residual_nC_cm2':r['metrics']['charge_residual_nC_cm2'],'spike_count':r['metrics']['spike_count']})
    accepted=checks[0]['max_voltage_error_mV']<.02 and all(b['max_voltage_error_mV']<a['max_voltage_error_mV'] for a,b in zip(checks,checks[1:]))
    out={'method':'Independent relative-voltage RHS + SciPy DOP853 versus release absolute-voltage RK4','scipy_version':scipy.__version__,'reference_rtol':1e-10,'reference_atol':1e-12,'checks':checks,'passed':accepted,'external_biological_validation':False,'brian2_executed':False}
    return out

if __name__=='__main__':
    out=compare();dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path('validation/reference_solver.json');dest.parent.mkdir(parents=True,exist_ok=True);write_json(dest,out);print(json.dumps(out,indent=2));raise SystemExit(0 if out['passed'] else 1)
