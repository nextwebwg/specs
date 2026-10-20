// Semantic experiment only: records have already passed authentication and form validation.
// No wire parsing, cryptography, storage transaction, or external effects are implemented.
export function deriveAnswers(records) {
  const key = ({ author, id }) => JSON.stringify([author, id]);
  const groups = new Map();
  for (const record of records) {
    const k = key(record);
    if (!groups.has(k)) groups.set(k, new Map());
    // fixture identity represents equality of authenticated records; not wire canonicalization.
    groups.get(k).set(record.fixtureIdentity, record);
  }
  const status = new Map();
  const events = new Map();
  for (const [k, variants] of groups) {
    if (variants.size !== 1) status.set(k, 'conflict');
    else events.set(k, [...variants.values()][0]);
  }
  function validate(k, path = new Set()) {
    if (status.has(k)) return status.get(k);
    if (!events.has(k)) return 'pending';
    if (path.has(k)) return 'invalid';
    const event = events.get(k);
    const next = new Set(path).add(k);
    const references = event.targets ?? [];
    let pending = false;
    for (const ref of references) {
      if (ref.author !== event.author || key(ref) === k) return 'invalid';
      const targetKey = key(ref);
      const targetStatus = validate(targetKey, next);
      if (targetStatus === 'invalid' || targetStatus === 'conflict') return 'invalid';
      if (targetStatus === 'pending') { pending = true; continue; }
      const target = events.get(targetKey);
      if (target.kind !== 'answer' || target.form !== event.form || target.revision !== event.revision) return 'invalid';
    }
    if (!['answer', 'withdraw'].includes(event.kind)) return 'invalid';
    if (event.kind === 'withdraw' && references.length === 0) return 'invalid';
    return pending ? 'pending' : 'valid';
  }
  // Validate each root without caching recursion: cycle failure must not depend on traversal order.
  const results = new Map(status);
  for (const k of events.keys()) results.set(k, validate(k));
  const suppressed = new Set();
  for (const [k, event] of events) {
    if (results.get(k) === 'valid') for (const ref of event.targets ?? []) suppressed.add(key(ref));
  }
  const current = [...events].filter(([k,e]) => e.kind === 'answer' && results.get(k) === 'valid' && !suppressed.has(k)).map(([k])=>k).sort();
  return { current, status: Object.fromEntries([...results].sort(([a],[b])=>a.localeCompare(b))) };
}
