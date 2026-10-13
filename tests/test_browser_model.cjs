const test = require('node:test');
const assert = require('node:assert/strict');
const {calculate} = require('../web/calculator.js');
const p={age:60,sex:'male',nyha_class:2,ischemic:false,ejection_fraction:30,systolic_bp:120,sodium:140,hemoglobin:14,lymphocyte_percent:25,uric_acid:6,total_cholesterol:180,weight_kg:80,loop_diuretic_mg_day:0,ace_inhibitor:true,arb:false,beta_blocker:true,statin:false,allopurinol:false,potassium_sparing_diuretic:false,device:'none'};
test('published reference',()=>{const r=calculate(p);assert.ok(Math.abs(r.score+0.10894930686)<1e-8);assert.ok(Math.abs(r.survival[1]-0.96433221439)<1e-8);});
test('invalid inputs',()=>{assert.throws(()=>calculate({...p,ejection_fraction:0}));assert.throws(()=>calculate({...p,age:NaN}));});
