import {JSDOM} from 'jsdom';
import {createDOMSafeParser} from './safe-dom.mjs';
export function createSafeParser(options){const window=new JSDOM('').window;return {...createDOMSafeParser(window,options),close:()=>window.close()};}
