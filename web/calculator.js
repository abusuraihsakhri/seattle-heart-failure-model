/* Original 2006 Levy SHFM research equation. No data leaves the browser. */
(function (root) {
  'use strict';
  const log = Math.log;
  const hr = { age: 1.090, male: 1.089, nyha: 1.600, ef: 1.030, ischemic: 1.354,
    sbp: 0.877, loop: 1.178, allopurinol: 1.571, sodium: 1.050, cholesterol: 2.206,
    hbLow: 1.124, hbHigh: 1.336, lymph: 0.897, urate: 1.064,
    ace: 0.77, arb: 0.85, bb: 0.66, k: 0.74, statin: 0.63,
    icd: 0.73, biv_pacemaker: 1, biv_icd: 0.79 };
  const ranges = {age:[18,120], nyha_class:[1,4], ejection_fraction:[0.000001,100],
    systolic_bp:[0.000001,300], sodium:[0.000001,200], hemoglobin:[0.000001,25],
    lymphocyte_percent:[0,100], uric_acid:[0,30], total_cholesterol:[0.000001,1000],
    weight_kg:[0.000001,500], loop_diuretic_mg_day:[0,1000]};
  function calculate(x) {
    for (const [key, [lo, hi]] of Object.entries(ranges)) {
      if (typeof x[key] !== 'number' || !Number.isFinite(x[key]) || x[key] < lo || x[key] > hi) {
        throw new Error('Invalid or missing ' + key);
      }
    }
    if (!Number.isInteger(x.nyha_class)) throw new Error('NYHA must be an integer');
    if (!['male', 'female'].includes(x.sex)) throw new Error('Invalid sex');
    if (!['none', 'icd', 'biv_pacemaker', 'biv_icd'].includes(x.device)) throw new Error('Invalid device');
    const bool = (name) => {
      if (typeof x[name] !== 'boolean') throw new Error('Invalid ' + name);
      return Number(x[name]);
    };
    const score = (x.age / 10) * log(hr.age) + Number(x.sex === 'male') * log(hr.male)
      + x.nyha_class * log(hr.nyha) + (100 / x.ejection_fraction) * log(hr.ef)
      + bool('ischemic') * log(hr.ischemic) + (Math.min(x.systolic_bp, 160) / 10) * log(hr.sbp)
      + (x.loop_diuretic_mg_day / x.weight_kg) * log(hr.loop)
      + bool('allopurinol') * log(hr.allopurinol) + Math.max(138 - x.sodium, 0) * log(hr.sodium)
      + (100 / x.total_cholesterol) * log(hr.cholesterol)
      + (x.hemoglobin < 16 ? (16 - x.hemoglobin) * log(hr.hbLow) : (x.hemoglobin - 16) * log(hr.hbHigh))
      + (Math.min(x.lymphocyte_percent, 47) / 5) * log(hr.lymph)
      + Math.max(x.uric_acid, 3.4) * log(hr.urate)
      + bool('ace_inhibitor') * log(hr.ace) + bool('arb') * log(hr.arb)
      + bool('beta_blocker') * log(hr.bb) + bool('potassium_sparing_diuretic') * log(hr.k)
      + bool('statin') * log(hr.statin)
      + (x.device === 'none' ? 0 : log(hr[x.device]));
    const survival = {};
    for (const year of [1,2,3,5]) survival[year] = Math.exp(-0.0405 * year * Math.exp(Math.min(score,700)));
    return {score, survival, model: 'Original Levy 2006, unvalidated educational implementation'};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {calculate};
  else root.SHFMCalculator = {calculate};
})(typeof window === 'undefined' ? {} : window);
