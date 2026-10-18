import { run } from './model.mjs';
const cases = [
 ['style','<style/><img data-probe onerror="probe()"><style></style>'],
 ['textarea','<textarea/><img data-probe onerror="probe()"><textarea></textarea>'],
 ['mtext','<math><mtext><x-box/><mglyph><style><img data-probe onerror="probe()"></style></mglyph></mtext></math>'],
 ['ancestor','<x-box/><svg></x-box><style><img data-probe onerror="probe()"></style></svg>'],
 ['div-ancestor','<div/><svg></div><style><img data-probe onerror="probe()"></style></svg>']
];
for(const [name,input] of cases) console.log(JSON.stringify({name,profiles:Object.fromEntries(['legacy','all','text-excluded','text-and-foreign-excluded'].map(p=>{const r=run('<!doctype html><body>'+input,p);return [p,{signals:r.signals,activations:r.activations,html:r.serialized}]}))}));
