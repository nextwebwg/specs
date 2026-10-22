import test from 'node:test';
import assert from 'node:assert/strict';
import {assemblePrimaryReplies} from './primary-reply-graph.mjs';

const conversation = 'c'.repeat(32), alice = 'enp0:' + 'a'.repeat(64), bob = 'enp0:' + 'b'.repeat(64);
const ref = (n, principal = alice, c = conversation) => ({principal, conversation: c, event: n.toString(16).padStart(32, '0')});
const row = (n, parent = null, kind = 'message', principal = alice) => ({reference: ref(n, principal), kind,
  replyTo: ['message', 'attachment-message', 'rich-message', 'reply-message'].includes(kind) ? (parent ? [parent] : []) : null});
const graph = (records, conflicts = () => false) => assemblePrimaryReplies(conversation, records, conflicts);
const at = (result, n, principal = alice) => result.find(r => r.reference.event === ref(n).event && r.reference.principal === principal);
function* permutations(values) {
  if (!values.length) { yield []; return; }
  for (let i = 0; i < values.length; i++) for (const rest of permutations(values.filter((_, j) => i !== j))) yield [values[i], ...rest];
}

test('all four primary message kinds preserve exact reply edges, including attachments', () => {
  const records = [row(1), ...['message', 'attachment-message', 'rich-message', 'reply-message'].map((kind, i) => row(i + 2, ref(1), kind))];
  const result = graph(records);
  assert.equal(at(result, 1).state, 'no-target');
  for (let n = 2; n <= 5; n++) assert.deepEqual(at(result, n).parent, ref(1));
});
test('late parent is pending, then resolves without changing the child or inventing a root', () => {
  const child = row(2, ref(1)), before = structuredClone(child);
  assert.equal(at(graph([child]), 2).state, 'pending');
  assert.deepEqual(at(graph([child, row(1)]), 2).parent, ref(1));
  assert.deepEqual(child, before);
});
test('every arrival order removes precisely cycle edges and retains an incoming tail', () => {
  const records = [row(1, ref(2)), row(2, ref(3)), row(3, ref(1)), row(4, ref(1)), row(5)];
  const expected = graph(records);
  for (const order of permutations(records)) assert.deepEqual(graph(order), expected);
  for (const n of [1, 2, 3]) {
    assert.equal(at(expected, n).reason, 'cycle');
    assert.equal(at(expected, n).parent, undefined);
  }
  assert.deepEqual(at(expected, 4).parent, ref(1));
  assert.equal(at(expected, 5).state, 'no-target');
  const earlier = graph(records.slice(0, 2));
  assert.equal(at(earlier, 2).state, 'pending');
  assert.deepEqual(at(earlier, 1).parent, ref(2));
});
test('self and cross-conversation references never produce edges', () => {
  const result = graph([row(1, ref(1)), row(2, ref(3, alice, 'd'.repeat(32)))]);
  assert.equal(at(result, 1).reason, 'self');
  assert.equal(at(result, 2).reason, 'conversation');
  assert.ok(result.every(r => !r.parent));
});
test('namespace conflict suppresses source and target edges without foreign content', () => {
  const records = [row(1), row(2, ref(1)), row(3, ref(9))];
  const result = graph(records, (principal, event) => principal === alice && [ref(1).event, ref(9).event].includes(event));
  assert.ok(result.every(r => r.state === 'conflict' && !r.parent));
  assert.ok(result.every(r => !Object.hasOwn(r, 'body')));
});
test('questions and observations can be targets; reactions do not invent primary parents', () => {
  for (const kind of ['question', 'service-question', 'hosted-holder-observation']) {
    const result = graph([row(1, null, kind), row(2, ref(1))]);
    assert.equal(at(result, 1).state, 'not-applicable');
    assert.deepEqual(at(result, 2).parent, ref(1));
  }
  const result = graph([row(1, null, 'reaction'), row(2, ref(1))]);
  assert.equal(at(result, 1).state, 'not-applicable');
  assert.equal(at(result, 2).reason, 'target-kind');
});
test('same event identifier under different principals stays independent', () => {
  const result = graph([row(1), row(1, null, 'message', bob), row(2, ref(1, bob))]);
  assert.deepEqual(at(result, 2).parent, ref(1, bob));
  assert.equal(at(result, 1).state, 'no-target');
  assert.equal(at(result, 1, bob).state, 'no-target');
});
test('long chains are traversed iteratively without a recursive stack limit', () => {
  const records = Array.from({length: 12000}, (_, i) => row(i + 1, i ? ref(i) : null));
  const result = graph(records.reverse());
  assert.equal(result.length, 12000);
  assert.equal(at(result, 1).state, 'no-target');
  assert.deepEqual(at(result, 12000).parent, ref(11999));
});
test('incomplete normalized input, duplicate nodes and implicit conflict results fail as a unit', () => {
  for (const records of [[row(1), row(1)], [{...row(1), extra: true}], [{...row(1), replyTo: null}]]) {
    assert.throws(() => graph(records), TypeError);
  }
  assert.throws(() => graph([row(1)], () => undefined), TypeError);
  assert.throws(() => assemblePrimaryReplies(conversation, [row(1)]), TypeError);
});


test('a forbidden reply edge is excluded before cycle detection', () => {
  const records = [row(1, ref(2)), row(2, ref(3)), row(3, ref(1))];
  const original = structuredClone(records);
  const expected = assemblePrimaryReplies(conversation, records, () => false,
    child => child.event === ref(1).event ? 'invalid' : 'allowed');
  assert.equal(at(expected, 1).reason, 'reply-permission');
  assert.equal(at(expected, 1).parent, undefined);
  assert.deepEqual(at(expected, 2).parent, ref(3));
  assert.deepEqual(at(expected, 3).parent, ref(1));
  for (const order of permutations(records)) {
    assert.deepEqual(assemblePrimaryReplies(conversation, order, () => false,
      child => child.event === ref(1).event ? 'invalid' : 'allowed'), expected);
  }
  assert.deepEqual(records, original);
});
test('unresolved or conflicted reply permission retains the requested edge without installing it', () => {
  for (const permission of ['pending', 'conflict']) {
    const result = assemblePrimaryReplies(conversation, [row(1), row(2, ref(1))],
      () => false, () => permission);
    assert.equal(at(result, 2).state, permission);
    assert.deepEqual(at(result, 2).requestedParent, ref(1));
    assert.equal(at(result, 2).parent, undefined);
  }
  for (const permission of [undefined, true, false, 'verified', {allowed: true}]) {
    assert.throws(() => assemblePrimaryReplies(conversation, [row(1), row(2, ref(1))],
      () => false, () => permission), /Explicit edge-permission/);
  }
});
