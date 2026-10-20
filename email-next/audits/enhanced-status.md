---
title: Enhanced status-code audit
sectionNav: true
---

# Enhanced status-code audit

Complete sixteen-page [RFC 3463](https://www.rfc-editor.org/rfc/rfc3463.html) reviewed, including every code, grammar, appendices and end matter. Held erratum4368 corrects an editorial word; it is not a wire change. Dependency closure remains open.

| Section | Disposition |
| --- | --- |
| 1 | Motivation and vocabulary reviewed. |
| 2 | Grammar, all classes and subjects reviewed; unknown detail retains recognized subject, unknown subject retains class. Registration policy updated by5248. |
| 3 | Detail scope reviewed. |
| 3.1 | Undefined fallback reviewed. |
| 3.2 | All nine address codes reviewed; none proves endpoint identity. |
| 3.3 | All five mailbox codes reviewed; delivery capacity is not capability withdrawal. |
| 3.4 | All six system codes reviewed; held4368 editorial correction recorded. |
| 3.5 | All eight routing codes reviewed; no authority to change recipients. |
| 3.6 | All six protocol codes reviewed; recipient splitting must preserve audience and protection. |
| 3.7 | All six media codes reviewed; conversion diagnostics do not authorize conversion. |
| 3.8 | All eight security codes reviewed; successful transport class does not establish integrity. |
| 4 | References read; dependency closure pending. |
| 5 | Diagnostic information disclosure reviewed. |
| A | Entire table compared with prose; omitsX.0.0 andX.3.5, so not exhaustive. |
| B | All revision changes read, including relaxedX.4.7 class restriction. |
| Author | Read. |
| Copyright | Copyright and acknowledgment read. |

The [transport contract](../transport.md) separates diagnostic interpretation from protection decisions. The [registry audit](status-registry.md) covers the newer registration policy. Neither a positive class nor a cryptographic diagnostic proves an endpoint's identity or successful content verification. Parser and UI fixtures remain required.
