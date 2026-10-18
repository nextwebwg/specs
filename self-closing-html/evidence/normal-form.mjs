import fs from 'node:fs';
import {audit} from './audit.mjs';
import {run,contextElement} from './model.mjs';
const parts=['<div/>','</div>','<x-box/>','</x-box>','<svg>','</svg>','<math>','</math>','<mtext>','</mtext>','<mglyph>','</mglyph>','<style>','</style>','<textarea>','</textarea>','<table>','</table>','<form>','</form>','<template>','</template>','<noscript>','</noscript>','<img src onerror="probe()">','<!--','-->','text','<div a=x/>','<x-box a="/>"/>'];
let state=0x4e4f524d;const rand=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
const report={seed:'0x4e4f524d',inputs:20000,contexts:['div','table','template','select'],scripting:[true,false],audits:0,eligibleFree:0,identical:0,failures:[]};
for(let i=0;i<report.inputs;i++){let source='';for(let j=0,n=1+rand()%16;j<n;j++)source+=parts[rand()%parts.length];
 for(const context of report.contexts)for(const scripting of report.scripting){report.audits++;if(audit(source,contextElement(context),scripting).length)continue;report.eligibleFree++;
 const legacy=run(source,'legacy',contextElement(context),scripting);const next=run(source,'all',contextElement(context),scripting);
 if(legacy.serialized===next.serialized&&next.activations.length===0)report.identical++;else if(report.failures.length<20)report.failures.push({source,context,scripting,legacy:legacy.serialized,next:next.serialized,activations:next.activations});
 }
}
fs.writeFileSync('normal-form-results.json',JSON.stringify(report,null,2)+'\n');console.log(report);if(report.failures.length)process.exitCode=1;
