import {isObjectId} from './event-identifiers.mjs';

// Shape only: the enclosing event must be authenticated separately.
export function validateResourceManifest(value) {
  if (!Array.isArray(value)) return {state:'invalid'};
  const ids=new Set();
  for (const entry of value) {
    if (!entry || typeof entry!=='object' || Array.isArray(entry) ||
        Object.keys(entry).sort().join(',')!=='id,sha256,size' ||
        !isObjectId(entry.id) || ids.has(entry.id) ||
        typeof entry.size!=='string' || !/^(0|[1-9][0-9]{0,19})$/.test(entry.size) ||
        BigInt(entry.size)>18446744073709551615n ||
        typeof entry.sha256!=='string' || !/^[0-9a-f]{64}$/.test(entry.sha256)) return {state:'invalid'};
    ids.add(entry.id);
  }
  return {state:'shape-valid'};
}

// Convert only after local limits; never round a wire length into a JS number.
export function resourceExpectation(manifest, id, maxBytes) {
  if(validateResourceManifest(manifest).state!=='shape-valid' || !isObjectId(id) ||
     !Number.isSafeInteger(maxBytes) || maxBytes<0) return {state:'invalid'};
  const entry=manifest.find(item=>item.id===id);
  if(!entry) return {state:'missing'};
  const size=BigInt(entry.size);
  if(size>BigInt(maxBytes)) return {state:'limit-exceeded'};
  return {state:'bounded',expected:{size:Number(size),sha256:entry.sha256}};
}
