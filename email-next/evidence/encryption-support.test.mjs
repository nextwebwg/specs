// Documentation fixture checks only: no HTTP endpoint, strict raw JSON decoder,
// accepted identity store, network privacy or actual setup implementation.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const example = JSON.parse(readFileSync(new URL('../examples/encryption-support.json', import.meta.url), 'utf8'));

test('support-hint example has exactly the selected string field inventories', () => {
  assert.deepEqual(Object.keys(example.request).sort(), ['recipient', 'version']);
  assert.equal(example.request.version, '0');
  assert.equal(example.request.recipient, 'bob@example.org');
  for (const [name, expected] of [['advertisedResponse', 'advertised'], ['uniformNegativeResponse', 'not-advertised']]) {
    assert.deepEqual(Object.keys(example[name]).sort(), ['support', 'version']);
    assert.equal(example[name].version, '0');
    assert.equal(example[name].support, expected);
  }
});
