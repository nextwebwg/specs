---
title: Experimental form operation schemas
order: 5
blurb: revisions · typed values · exact targets
sectionNav: true
---

# Experimental form operation schemas

> [!note] Deferred exploration
> General-purpose forms are outside the first-version scope. Version one targets predefined answer buttons that send a response in one action. These broader schemas preserve experimental work; first-version clients are not required to implement them.

These schemas define the operation object carried by an experimental event. They use the strict JSON rules in [Event encoding](event-encoding.md). They do not replace the event envelope, audience binding or cryptographic authorization. Every member listed for an object is required unless explicitly marked optional; additional members are invalid. The discriminator is `kind`.

## Shared types

`ObjectId` follows the [identifier grammar](event-identifiers.md). `EventReference` is the exact three-member reference defined there. Arrays described as sets MUST contain no duplicate values; their order has no semantic meaning. Duplicate references are detected using all three decoded string values, not object member order. Ordered arrays retain the order supplied by the author.

Labels and descriptive text are strings of Unicode scalar values, interpreted as plain text. They MUST NOT be parsed as HTML or command syntax. Empty strings are allowed; clients must provide accessible generic labels where an empty label would otherwise make a control unusable. This does not alter the stored field label.

## Form definition

| Member | Type and meaning |
| --- | --- |
| `kind` | Exactly `form` |
| `form` | ObjectId, scoped to the authenticated author of the initial definition |
| `title` | Plain-text string |
| `fields` | Ordered array of field objects; field identifiers must be unique |
| `supersedes` | Set of EventReference values naming earlier revisions of this form |

An initial definition has an empty `supersedes` array. A later revision names at least one prior revision and contains the complete new definition. The enclosing event is the revision identity. The receiver validates authority, form scope and acyclic revision relationships separately. An empty array does not authorize a second initial definition for an already established form identity.

A text field has exactly `field`, `label`, `type` and `required`. A choice field additionally has `choices`.

| Member | Type and meaning |
| --- | --- |
| `field` | ObjectId |
| `label` | Plain-text string |
| `type` | Exactly `text`, `single-choice` or `multiple-choice` |
| `required` | Boolean |
| `choices` | For choice fields only: nonempty ordered array of choice objects |

A choice object has exactly `choice` (ObjectId) and `label` (plain-text string). Choice identifiers must be unique within the field. A text field MUST NOT contain `choices`, even as an empty array. A form may have zero fields; submitting it is still an explicit user action, not consent inferred from opening it.

## Submission

| Member | Type and meaning |
| --- | --- |
| `kind` | Exactly `submit` |
| `form` | ObjectId |
| `revision` | EventReference naming the exact form definition |
| `answers` | Set of answer objects, with unique field identifiers |
| `supersedes` | Set of EventReference values naming this author's submissions to replace |

Each answer object has exactly `field` and `value`. The field identifier must occur in the referenced revision. The value type depends on that revision's field definition:

| Field type | Value |
| --- | --- |
| `text` | String, including an intentionally empty string |
| `single-choice` | One ObjectId occurring among that field's choices |
| `multiple-choice` | Array of distinct ObjectIds occurring among that field's choices; empty is permitted |

An omitted answer is unanswered. Required fields must occur in `answers`; this requirement does not forbid an empty text or multiple-choice value. Unknown fields, wrong types, duplicate answers or unknown choices invalidate the whole submission. No valid-looking subset may be applied.

The referenced revision must have the named form identifier. All superseded submissions must have the same authenticated author, form and exact revision. Missing dependencies leave validation pending. A later form revision cannot substitute for the requested revision.

## Withdrawal

| Member | Type and meaning |
| --- | --- |
| `kind` | Exactly `withdraw` |
| `form` | ObjectId |
| `revision` | EventReference naming the exact form definition |
| `submissions` | Nonempty set of EventReference values naming submissions to withdraw |

Withdrawal has no answer values. Every target must be a submission by the withdrawal's authenticated author to the named form and revision. The receiver resolves all targets before applying the operation. The operation does not delete historical content or reverse an external action already taken.

## Validation stages

First reject invalid encoding and object shapes. Then resolve references, validate the target schema, and check authenticated authority and graph relationships. Only after all stages succeed may the receiver update the derived answer view atomically. A shape validator cannot establish authorization. A missing reference is pending, while a resolved reference of the wrong kind is invalid.

The accompanying value-validation experiment checks submissions against an explicitly supplied form definition. It assumes that definition has already passed shape and authority validation. The operation-shape experiment additionally validates forms, submissions and withdrawals, including duplicate reference sets and scalar-value labels. The [submission-target experiment](evidence/README.md#exact-submission-target-resolution) checks exact resolver output and answer membership while keeping pending, conflicted and invalid states distinct. It assumes prior authentication and revision-graph results; generating those results, validating supersession authority and integrating the selected contribution envelope with its cryptographic context remain required work.


## Withdrawal target resolution

Resolve the exact form revision and every named submission before deriving withdrawal effects. Each target must match all three reference components, have the same form and exact revision, and belong to the withdrawal's authenticated author. Submission authority and answer validity must already be established by the target-validation pipeline; matching an object shape alone is insufficient.

When dependencies have mixed outcomes, invalid takes precedence over conflict, and conflict over pending. The result must not depend on the order of the submission reference set. All targets remain available for diagnostics, and no subset is withdrawn while another target is unresolved. A successful target check is not a storage commit or permission to reverse an external action.

The [withdrawal target experiment](evidence/README.md#withdrawal-targets) exercises these reference constraints with a trusted resolver. Its resolver records use the existing internal `id` property for an event identifier; the wire envelope's member remains `event`.
