import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash, createPrivateKey, createPublicKey, sign, verify} from 'node:crypto';

// Public test material from RFC 8463 Appendix A, not deployment credentials.
// This fixed canonical input does not implement DKIM header selection or parsing.
const seed = Buffer.from('nWGxne/9WmC6hEr0kuwsxERJxWl7MmkZcDusAxyuf2A=', 'base64');
const rawPublic = Buffer.from('11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo=', 'base64');
const privateKey = createPrivateKey({
  key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), seed]),
  format: 'der', type: 'pkcs8',
});
const publicKey = createPublicKey({
  key: Buffer.concat([Buffer.from('302a300506032b6570032100', 'hex'), rawPublic]),
  format: 'der', type: 'spki',
});
const canonicalHeaders = Buffer.from([
  'from:Joe SixPack <joe@football.example.com>',
  'to:Suzie Q <suzie@shopping.example.net>',
  'subject:Is dinner ready?',
  'date:Fri, 11 Jul 2003 21:00:37 -0700 (PDT)',
  'message-id:<20030712040037.46341.5F8J@football.example.com>',
  'dkim-signature:v=1; a=ed25519-sha256; c=relaxed/relaxed; d=football.example.com; i=@football.example.com; q=dns/txt; s=brisbane; t=1528637909; h=from : to : subject : date : message-id : from : subject : date; bh=2jUSOH9NhtVGCQWNr9BrIAPreKQjO6Sn7XIkfJVOzv8=; b=',
].join('\r\n'));
const expectedSignature = Buffer.from('/gCrinpcQOoIfuHNQIbq4pgh9kyIK3AQUdt9OdqQehSwhEIug4D11BusFa3bT3FY5OsU7ZbnKELq+eXdp1Q1Dw==', 'base64');
const digest = createHash('sha256').update(canonicalHeaders).digest();

test('published body digest matches the fixed relaxed body representation', () => {
  const body = Buffer.from('Hi.\r\n\r\nWe lost the game.  Are you hungry yet?\r\n\r\nJoe.\r\n');
  // Relaxed body canonicalization reduces the interior double space.
  const canonicalBody = Buffer.from(body.toString().replace('game.  Are', 'game. Are'));
  assert.equal(createHash('sha256').update(canonicalBody).digest('base64'),
    '2jUSOH9NhtVGCQWNr9BrIAPreKQjO6Sn7XIkfJVOzv8=');
});

test('Ed25519 over the DKIM SHA256 digest reproduces the published signature', () => {
  assert.deepEqual(sign(null, digest, privateKey), expectedSignature);
  assert.equal(verify(null, digest, publicKey, expectedSignature), true);
});

test('direct signing of canonical headers does not implement this DKIM algorithm', () => {
  const directSignature = sign(null, canonicalHeaders, privateKey);
  assert.notDeepEqual(directSignature, expectedSignature);
  assert.equal(verify(null, canonicalHeaders, publicKey, expectedSignature), false);
  assert.equal(verify(null, digest, publicKey, directSignature), false);
});

test('a changed covered field fails the published signature', () => {
  const changed = Buffer.from(canonicalHeaders.toString().replace('Is dinner ready?', 'Dinner is cancelled'));
  const changedDigest = createHash('sha256').update(changed).digest();
  assert.equal(verify(null, changedDigest, publicKey, expectedSignature), false);
});
