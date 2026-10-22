import {isEventReference, isObjectId} from './event-identifiers.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';

const primaryKinds = new Set(['message', 'attachment-message', 'rich-message', 'reply-message']);
const targetKinds = new Set([...primaryKinds, 'question', 'service-question', 'hosted-holder-observation']);
const keyOf = reference => JSON.stringify([reference.principal, reference.conversation, reference.event]);

// Input is a complete authorized projection of already accepted/deduplicated
// events, not wire data. The caller owns authentication, module/target authority,
// processing budgets and a current namespace snapshot token for installation.
// An optional trusted permission query runs before topology. Without it this is
// only structural topology, not enforcement of the current reply-intent contract.
export function assemblePrimaryReplies(conversation, records, hasNamespaceConflict, authorizeEdge = null) {
  if (!isObjectId(conversation) || !Array.isArray(records) || typeof hasNamespaceConflict !== 'function') {
    throw new TypeError('Complete projection and namespace-conflict query required');
  }
  if (authorizeEdge !== null && typeof authorizeEdge !== 'function') {
    throw new TypeError('Trusted edge-permission query required');
  }
  const conflicts = new Map();
  const conflicted = (principal, event) => {
    const key = JSON.stringify([principal, event]);
    if (!conflicts.has(key)) {
      const value = hasNamespaceConflict(principal, event);
      if (typeof value !== 'boolean') throw new TypeError('Explicit namespace-conflict result required');
      conflicts.set(key, value);
    }
    return conflicts.get(key);
  };
  const nodes = new Map();
  for (const record of records) {
    if (!record || Object.keys(record).length !== 3 ||
        !['reference', 'kind', 'replyTo'].every(k => Object.hasOwn(record, k)) ||
        !isEventReference(record.reference, isPrincipalId) || record.reference.conversation !== conversation ||
        typeof record.kind !== 'string' ||
        (primaryKinds.has(record.kind)
          ? !Array.isArray(record.replyTo) || record.replyTo.length > 1 || !record.replyTo.every(r => isEventReference(r, isPrincipalId))
          : record.replyTo !== null)) {
      throw new TypeError('Exact normalized relationship record required');
    }
    const key = keyOf(record.reference);
    if (nodes.has(key)) throw new TypeError('Caller must deduplicate before topology');
    nodes.set(key, record);
  }
  const edges = new Map(), results = new Map();
  for (const [key, record] of nodes) {
    const result = {reference: {...record.reference}, state: 'not-applicable'};
    results.set(key, result);
    if (conflicted(record.reference.principal, record.reference.event)) {
      result.state = 'conflict';
      continue;
    }
    if (!primaryKinds.has(record.kind)) continue;
    if (!record.replyTo.length) { result.state = 'no-target'; continue; }
    const parent = record.replyTo[0], parentKey = keyOf(parent);
    result.requestedParent = {...parent};
    if (parent.conversation !== conversation) { result.state = 'invalid'; result.reason = 'conversation'; continue; }
    if (parentKey === key) { result.state = 'invalid'; result.reason = 'self'; continue; }
    if (conflicted(parent.principal, parent.event)) { result.state = 'conflict'; continue; }
    const target = nodes.get(parentKey);
    if (!target) { result.state = 'pending'; continue; }
    if (!targetKinds.has(target.kind)) { result.state = 'invalid'; result.reason = 'target-kind'; continue; }
    if (authorizeEdge !== null) {
      const permission = authorizeEdge({...record.reference}, {...target.reference});
      if (!['allowed', 'pending', 'conflict', 'invalid'].includes(permission)) {
        throw new TypeError('Explicit edge-permission result required');
      }
      if (permission !== 'allowed') {
        result.state = permission;
        result.reason = 'reply-permission';
        continue;
      }
    }
    result.state = 'target-matched';
    edges.set(key, parentKey);
  }
  // Iterative functional-graph traversal: only members of a cycle lose edges.
  // A tail leading into the cycle still replies to an available exact message.
  const done = new Set(), cyclic = new Set();
  for (const start of nodes.keys()) {
    const path = [], positions = new Map();
    let cursor = start;
    while (cursor !== undefined && !done.has(cursor)) {
      if (positions.has(cursor)) {
        for (let i = positions.get(cursor); i < path.length; i++) cyclic.add(path[i]);
        break;
      }
      positions.set(cursor, path.length);
      path.push(cursor);
      cursor = edges.get(cursor);
    }
    for (const key of path) done.add(key);
  }
  for (const key of cyclic) {
    edges.delete(key);
    Object.assign(results.get(key), {state: 'invalid', reason: 'cycle'});
  }
  for (const [key, parent] of edges) results.get(key).parent = {...nodes.get(parent).reference};
  return [...results.entries()].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([, value]) => value);
}
