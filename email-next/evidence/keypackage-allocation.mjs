// In-memory transition experiment. Caller supplies authenticated identities and validated packages.
export class PackageAllocator {
  #available;
  #device;
  #profile;
  #results=new Map();
  #published=new Set();
  constructor(packages, {device,profile}) {
    if(![device,profile].every(v=>typeof v==='string'&&v.length))throw new TypeError('Pool scope required');
    this.#device=device;this.#profile=profile;
    this.#available=[];
    for(const reference of packages)this.publish(reference);
  }
  publish(reference) {
    if(typeof reference!=='string'||!reference||this.#published.has(reference))throw new TypeError('Package reference must be new');
    this.#published.add(reference);this.#available.push(reference);
  }
  allocate({principal,device,profile,request}) {
    if(![principal,device,profile,request].every(v=>typeof v==='string'&&v.length))throw new TypeError('Request scope required');
    if(device!==this.#device||profile!==this.#profile)throw new TypeError('Wrong pool scope');
    const key=JSON.stringify([principal,device,profile,request]);
    if(this.#results.has(key))return {...this.#results.get(key)};
    const packageReference=this.#available.shift();
    const result=packageReference===undefined?{state:'depleted'}:{state:'allocated',packageReference};
    this.#results.set(key,result);
    return {...result};
  }
}
