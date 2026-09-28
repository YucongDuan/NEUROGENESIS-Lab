import unittest,math,json,csv,io,copy
from pathlib import Path
from neurogenesis.core import *
from neurogenesis.experiments import run,catalog,validate
from neurogenesis.membrane import rates,nernst,vtrap
from neurogenesis.calibration import fit_csv
ROOT=Path(__file__).resolve().parents[1]

class Contracts(unittest.TestCase):
    def test_bool_not_number(self):
        with self.assertRaises(ValidationError):number(True,'x')
    def test_nan_rejected(self):
        with self.assertRaises(ValidationError):number(float('nan'),'x')
    def test_infinity_rejected(self):
        with self.assertRaises(ValidationError):loads('{"x":1e999}')
    def test_duplicate_key_rejected(self):
        with self.assertRaises(ValidationError):loads('{"x":1,"x":2}')
    def test_fractional_integer_rejected(self):
        with self.assertRaises(ValidationError):integer(3.1,'x',0,9)
    def test_unit_conversion(self):self.assertAlmostEqual(convert(1,'nA','pA'),1000)
    def test_energy_not_molar_energy(self):
        with self.assertRaises(ValidationError):convert(5,'J/mol','J')
    def test_amount_not_concentration(self):
        with self.assertRaises(ValidationError):convert(5,'mol','mol/L')
    def test_unknown_unit(self):
        with self.assertRaises(ValidationError):convert(5,'neurobits','bit')
    def test_invalid_unit_type(self):
        with self.assertRaises(ValidationError):convert(5,[],'bit')
    def test_tagged_quantity(self):self.assertEqual(validate('energy',{'voltage_mV':{'value':.065,'unit':'V'}})['voltage_mV'],65)
    def test_wrong_tagged_dimension(self):
        with self.assertRaises(ValidationError):validate('energy',{'voltage_mV':{'value':.065,'unit':'J'}})
    def test_unknown_experiment(self):
        with self.assertRaises(ValidationError):run('__import__')
    def test_singular_solver(self):
        with self.assertRaises(ValidationError):solve([[1,2],[2,4]],[1,2])
    def test_solver_known(self):self.assertTrue(numerical_equal(solve([[2,1],[1,3]],[5,7]),[1.6,1.8]))
    def test_rk4_exponential(self):self.assertAlmostEqual(rk4([1.],.01,lambda y:[-y[0]])[0],math.exp(-.01),places=10)
    def test_bool_equality_not_integer(self):self.assertFalse(numerical_equal(True,1))
    def test_catalog_has_all_chapters(self):
        b=load_json(ROOT/'neurogenesis/data/book_map.json');self.assertEqual([r['chapter'] for r in b['chapters']],list(range(1,19)))
    def test_references_resolve(self):
        refs={r['id'] for r in load_json(ROOT/'neurogenesis/data/references.json')}
        for v in catalog().values():self.assertTrue(set(v['references'])<=refs)

class Physics(unittest.TestCase):
    def test_nernst_equal_concentration(self):self.assertEqual(nernst(10,10,1,310),0)
    def test_nernst_valence_sign(self):self.assertAlmostEqual(nernst(140,5,1,310),-nernst(140,5,-1,310))
    def test_nernst_zero_valence(self):
        with self.assertRaises(ValidationError):run('nernst',{'valence':0})
    def test_nernst_concentration_ratio(self):self.assertAlmostEqual(nernst(140,5,1,310),nernst(280,10,1,310))
    def test_rate_singularity_minus40(self):self.assertAlmostEqual(rates(-40)[0],1)
    def test_rate_singularity_minus55(self):self.assertAlmostEqual(rates(-55)[4],.1)
    def test_vtrap_continuity(self):self.assertAlmostEqual(vtrap(1e-9,10),10,places=8)
    def test_hh_charge_and_gates(self):
        r=run('hh');self.assertLess(r['metrics']['charge_residual_nC_cm2'],1e-7)
        self.assertGreaterEqual(r['metrics']['min_gate'],0);self.assertLessEqual(r['metrics']['max_gate'],1)
    def test_hh_no_drive_no_spikes(self):self.assertEqual(run('hh',{'current_uA_cm2':0})['metrics']['spike_count'],0)
    def test_hh_no_sodium_no_spikes(self):self.assertEqual(run('hh',{'g_na_mS_cm2':0})['metrics']['spike_count'],0)
    def test_hh_pulse_boundary_rejected(self):
        with self.assertRaises(ValidationError):run('hh',{'pulse_start_ms':40,'pulse_end_ms':30})
    def test_hh_step_refinement(self):
        a=run('hh');b=run('hh',{'dt_ms':.0125})
        self.assertEqual(a['metrics']['spike_count'],b['metrics']['spike_count'])
        self.assertLess(max(abs(x-y) for x,y in zip(a['spike_times_ms'],b['spike_times_ms'])),.01)
        self.assertLess(abs(a['metrics']['ideal_Na_pump_energy_J_cm2']/b['metrics']['ideal_Na_pump_energy_J_cm2']-1),.001)
    def test_cable_balance(self):self.assertLess(run('cable')['metrics']['charge_residual_fC'],1e-7)
    def test_cable_no_axial_no_distal(self):self.assertEqual(run('cable',{'axial_nS':0})['metrics']['distal_to_proximal_ratio'],0)
    def test_cable_no_current(self):self.assertEqual(run('cable',{'current_pA':0})['metrics']['distal_to_proximal_ratio'],0)
    def test_cable_stiff_step_rejected(self):
        with self.assertRaises(ValidationError):run('cable',{'capacitance_pF':100,'axial_nS':300,'dt_ms':.1})
    def test_energy_two_routes(self):
        m=run('energy')['metrics'];self.assertAlmostEqual(m['dimensionless_ratio'],m['ratio_via_RT'])
    def test_network_same_wiring_different_dynamics(self):
        m=run('network')['metrics'];self.assertGreater(m['excitatory_max_real_eigenvalue_per_ms'],0);self.assertLess(m['opponent_max_real_eigenvalue_per_ms'],0)
    def test_alias(self):
        m=run('alias')['metrics'];self.assertEqual(m['aliased_frequency_Hz'],10);self.assertLess(m['max_equal_sample_error'],1e-10)
    def test_homeostat_conservation(self):self.assertLess(run('body')['metrics']['balance_residual'],1e-8)
    def test_resource_failure_not_clipped(self):
        with self.assertRaises(ValidationError):run('body',{'initial_resource':1,'max_intake':0,'basal_cost':1})

class Learning(unittest.TestCase):
    def test_binomial_zero(self):self.assertEqual(run('release',{'probability':0})['metrics']['sample_mean'],0)
    def test_binomial_one(self):self.assertEqual(run('release',{'probability':1})['metrics']['sample_mean'],8)
    def test_binomial_pmf(self):self.assertAlmostEqual(sum(r['binomial_probability'] for r in run('release')['rows']),1)
    def test_release_sample_matches_expectation(self):self.assertLess(abs(run('release')['metrics']['sample_mean']-2),.15)
    def test_zero_sensitivity_chance(self):self.assertAlmostEqual(run('detection',{'d_prime':0})['metrics']['balanced_accuracy'],.5)
    def test_criterion_shift(self):
        a=run('detection',{'criterion':-1})['metrics'];b=run('detection',{'criterion':1})['metrics']
        self.assertEqual(a['d_prime'],b['d_prime']);self.assertGreater(a['false_alarm_rate'],b['false_alarm_rate'])
    def test_hopfield_energy(self):self.assertLessEqual(run('attractor')['metrics']['largest_energy_increase'],1e-10)
    def test_normalized_development(self):self.assertLess(run('development')['metrics']['max_normalization_error'],1e-12)
    def test_td_no_learning(self):self.assertEqual(run('td',{'learning_rate':0})['metrics']['final_value'],0)
    def test_social_independence(self):self.assertEqual(run('social',{'shared_fraction':0})['metrics']['effective_sample_size'],30)
    def test_social_perfect_correlation(self):self.assertEqual(run('social',{'shared_fraction':1})['metrics']['effective_sample_size'],1)
    def test_report_channel_zero(self):
        m=run('access',{'report_gate':0})['metrics'];self.assertEqual(m['report_rate'],0);self.assertIsNone(m['accuracy_among_reports']);self.assertGreater(m['first_order_accuracy'],.7)
    def test_report_not_consciousness_metric(self):self.assertNotIn('consciousness',run('access')['metrics'])
    def test_output_equivalence(self):self.assertLess(run('identify')['metrics']['observation_max_difference'],1e-12)
    def test_sensor_adds_rank(self):self.assertEqual(run('identify')['metrics']['observability_rank_two_selective_sensors'],2)
    def test_mapping_action_counts_match(self):
        r=run('mapping');self.assertEqual(len({x['actions_per_seed'] for x in r['policies']}),1)
        self.assertGreater(r['policies'][3]['conditional_cost_nJ'],r['policies'][0]['conditional_cost_nJ'])
    def test_mapping_independent_pairs(self):
        r=run('mapping')['metrics'];self.assertGreater(r['paired_post_shift_accuracy_delta'],.5);self.assertLess(r['normal_approx_95_low'],r['normal_approx_95_high'])
    def test_tournament_test_not_selection(self):self.assertFalse(run('tournament')['metrics']['test_used_for_selection'])
    def test_tournament_history_default(self):self.assertEqual(run('tournament')['metrics']['selected_by_validation'],'history')
    def test_candidate_zero_psi(self):self.assertLess(abs(run('candidate',{'psi_nJ_bit':0})['metrics']['fitted_psi_nJ_bit']),.1)
    def test_candidate_known_psi(self):self.assertAlmostEqual(run('candidate',{'noise_nJ':0})['metrics']['fitted_psi_nJ_bit'],.7,places=8)

class Calibration(unittest.TestCase):
    def setUp(self):
        self.text=(ROOT/'examples/passive_step.csv').read_text();self.meta=load_json(ROOT/'examples/passive_source.json')
    def test_fit_known(self):
        m=fit_csv(self.text,self.meta)['metrics'];self.assertEqual(m['tau_ms'],20);self.assertAlmostEqual(m['resistance_MOhm'],100,delta=1)
    def test_heldout_mutation_does_not_change_fit(self):
        rows=list(csv.DictReader(io.StringIO(self.text)));out=io.StringIO();w=csv.DictWriter(out,fieldnames=['time','voltage','split']);w.writeheader()
        for r in rows:
            if r['split']=='test':r['voltage']=str(float(r['voltage'])+5)
            w.writerow(r)
        a=fit_csv(self.text,self.meta)['metrics'];b=fit_csv(out.getvalue(),self.meta)['metrics']
        self.assertEqual(a['tau_ms'],b['tau_ms']);self.assertEqual(a['resistance_MOhm'],b['resistance_MOhm']);self.assertNotEqual(a['test_rmse_mV'],b['test_rmse_mV'])
    def test_conversion_invariance(self):
        rows=list(csv.DictReader(io.StringIO(self.text)));out=io.StringIO();w=csv.DictWriter(out,fieldnames=['time','voltage','split']);w.writeheader()
        for r in rows:r['time']=float(r['time'])/1000;r['voltage']=float(r['voltage'])/1000;w.writerow(r)
        m=dict(self.meta,time_unit='s',voltage_unit='V');self.assertAlmostEqual(fit_csv(out.getvalue(),m)['metrics']['resistance_MOhm'],fit_csv(self.text,self.meta)['metrics']['resistance_MOhm'])
    def test_bad_header(self):
        with self.assertRaises(ValidationError):fit_csv(self.text.replace('time,voltage,split','time,voltage,name'),self.meta)
    def test_no_test_data(self):
        with self.assertRaises(ValidationError):fit_csv(self.text.replace('test','train'),self.meta)
    def test_no_source(self):
        m=dict(self.meta);del m['source_locator']
        with self.assertRaises(ValidationError):fit_csv(self.text,m)
    def test_private_data_contract(self):
        with self.assertRaises(ValidationError):fit_csv(self.text,dict(self.meta,source_kind='patient'))
    def test_duplicate_times(self):
        lines=self.text.splitlines();lines[2]=lines[1]
        with self.assertRaises(ValidationError):fit_csv('\n'.join(lines),self.meta)
    def test_nonfinite(self):
        with self.assertRaises(ValidationError):fit_csv(self.text.replace('-65.0349107137','nan'),self.meta) if '-65.0349107137' in self.text else fit_csv('time,voltage,split\n0,nan,train',self.meta)

class ExperimentContracts(unittest.TestCase):pass
# One independent method per named experiment makes failures attributable rather than burying them in one loop.
for name in catalog():
    def deterministic(self,n=name):self.assertEqual(canonical(run(n)),canonical(run(n)))
    def unknown(self,n=name):
        with self.assertRaises(ValidationError):run(n,{'unexpected_parameter':1})
    def nonfinite(self,n=name):
        key=next(iter(catalog()[n]['parameters']))
        with self.assertRaises(ValidationError):run(n,{key:float('nan')})
    def boundary(self,n=name):
        key=next(iter(catalog()[n]['parameters']));p=catalog()[n]['parameters'][key]
        with self.assertRaises(ValidationError):run(n,{key:p['min']-1})
    setattr(ExperimentContracts,f'test_{name}_deterministic',deterministic)
    setattr(ExperimentContracts,f'test_{name}_unknown_key',unknown)
    setattr(ExperimentContracts,f'test_{name}_nonfinite',nonfinite)
    setattr(ExperimentContracts,f'test_{name}_lower_bound',boundary)
