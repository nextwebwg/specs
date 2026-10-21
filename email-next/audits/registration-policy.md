---
title: Registration policy
sectionNav: true
---

# Registration policy

Email/2's draft names and local experiments do not allocate public identifiers. [RFC8126](https://www.rfc-editor.org/rfc/rfc8126.html) explains common registration policies and how to request IANA actions. Each registry's own definition determines which policy, template, review and change-control rules apply.

## What the draft needs

| Proposed use | Applicable boundary |
| --- | --- |
| Event media type | The [candidate registration](../media-type-registration.md) follows the media-type registry's vendor-tree rules. Its proposed contact and change controller are not appointments or submission authority. |
| Passive-discovery media type | The name remains unregistered; its separate registration template and experimental agreement remain required. An event-type proposal does not register another type. |
| MLS application-context extension | The experiment uses `0xff00` from the private-use range identified by RFC9420. Participants must prevent collisions within their deployment; it is not a globally unique Email/2 assignment. |
| Future DNS discovery | The exact binding and globally scoped underscored label remain unspecified. RFC8552's registry rules apply once that binding is chosen. |
| Future mail headers or transport extensions | Identify the exact registry and applicable policy before requesting an allocation. A name in this draft is not a reservation. |

These mappings preserve the registry-specific audits rather than replacing their procedures with a generic policy chosen by this project. The service-answer experiment uses existing JSON and HTTP fields; its application strings do not silently create new IANA registrations.

## What the policy names mean

**Expert Review** requires approval under the registry's documented review criteria. **Specification Required** also requires a stable, publicly retrievable specification detailed enough for independent implementations. It does not universally require an RFC. **RFC Required**, **IETF Review** and **Standards Action** impose different publication and process requirements; publication on this site satisfies none of them by itself.

Private-use and experimental ranges have the scope their registries define. They do not confer global uniqueness. Provisional registration is available only where the registry provides it, and does not endorse the underlying mechanism. An unassigned value is available through the applicable process; a reserved value is not. Prior deployment does not guarantee that an unregistered value can later be assigned.

## Preparing a submission

The registration section should enumerate the requested actions, exact registry names, required fields and references to the technical definitions. Keep the wire behavior in its normal technical chapter. Use distinct placeholders for unallocated numeric values; do not turn a test identifier into a permanent allocation by assumption.

The submission must identify who may maintain each registration. A contact person is not necessarily its owner or change controller. Subsequent changes must follow the registry's process and preserve compatibility; substantial changes after expert review may require another review. Registry entries should point to the current authoritative definition, including its section when useful.

This audit does not authorize a submission, appoint an expert, allocate an identifier or certify the security of a registered mechanism.

## Source review and remaining scope

The complete RFC8126 base was read: 2,635 lines covering every policy, example, review procedure, lifecycle rule, reference and backmatter section. Fifty-nine dispositions are retained with source hash `b8b5cc1e61e78352b5a12c4a92fa0573b3400d49522a448913455a478dd87401`.

The captured metadata identifies BCP26, published June 2017, obsoleting RFC5226 and updated by RFC9907. The RFC9907 update concerns IANA-maintained YANG modules. Its introduction, Section 3.8, complete Section 4.30 (including both templates) and Section 5 were reviewed for applicability. They require authoritative-registry changes to propagate into maintained YANG representations; they do not add requirements to this draft’s media, header, MLS or DNS registrations. No YANG module is selected by this registration mapping. This is a selected-section review, not a full RFC9907 audit. Its two Verified errata and one Reported erratum were read and reconciled with the live listing: 8880 restores the template’s registry-update note, 8872 corrects an example name, and 9134 proposes an unresolved enum-value clarification. Reopen the YANG requirements if a module is introduced. The RFC2026 process dependency and any future early-allocation procedure also remain distinct from this base-document review.

The live errata listing and captured set agreed on 20 October 2026: held record5772 corrects a historical acknowledgement reference; rejected record6522 proposed additional Internet-Draft guidance rather than correcting an error. Neither supplies a new allocation or permission. Current registry reconciliation at submission time remains necessary.
