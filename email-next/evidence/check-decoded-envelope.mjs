import {isPrincipalId} from './principal-identifiers.mjs';
// Test adapter only. Input is JSON reserialized AFTER strict Python decoding.
// Its bytes are not the authenticated event bytes. Fixture principals are not keys.
import {readFileSync} from 'node:fs';
import {validateEnvelopeShape} from './event-envelope.mjs';
const value=JSON.parse(readFileSync(0,'utf8'));
const isPrincipal=isPrincipalId;
process.stdout.write(JSON.stringify({shapeValid:validateEnvelopeShape(value,isPrincipal)}));
