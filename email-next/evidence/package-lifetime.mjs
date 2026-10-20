const MAX_UINT64=(1n<<64n)-1n;
export const MAX_PACKAGE_LIFETIME=604800n;
const uint64=value=>typeof value==='bigint'&&value>=0n&&value<=MAX_UINT64;
// Inputs come from authenticated MLS fields and an independently established clock interval.
export function packageLifetime({notBefore,notAfter,earliestNow,latestNow}) {
 if(!uint64(notBefore)||!uint64(notAfter)||notAfter<notBefore||notAfter-notBefore>MAX_PACKAGE_LIFETIME)return 'invalid-lifetime';
 if(!uint64(earliestNow)||!uint64(latestNow)||latestNow<earliestNow)return 'time-unresolved';
 if(latestNow<notBefore)return 'not-yet-valid';
 if(earliestNow>notAfter)return 'expired';
 if(earliestNow<notBefore||latestNow>notAfter)return 'time-unresolved';
 return 'valid';
}
