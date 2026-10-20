---
title: Rich messages and resources
order: 1.5
blurb: readable text · selected HTML · embedded images
sectionNav: true
---

# Rich messages and resources

A rich message carries a readable text version, an HTML presentation and an explicit inventory of its resources. An image placed in the message and a file offered for download have different roles. Neither may fetch bytes from an arbitrary URL or become active content because of its filename.

> [!ex] A diagram and a document
> Alice sends a diagram with the description “The entrance is on the north side” and attaches a PDF. The text version includes that description. The HTML references the diagram by its scoped resource identifier. The PDF remains a deliberate download; it is not rendered as another part of the message body. If the diagram is unavailable, its alternative text remains useful.

This chapter defines the existing experimental `rich-message` operation and `mime-rich-v0` carriage. Authentication, recipient authority and exact-byte event identity still come from the enclosing [security profile](security-profile.md), not from HTML, MIME filenames or resource hashes.

## Two presentations of one contribution

The author supplies both `text` and `html`. The HTML uses the defined [HTML/CSS presentation profile](presentation-profile.md); it is not permission to embed an unrestricted web page. The client can show the text version by preference or when safe rich presentation is unavailable.

Authoring must account for the readable content of the HTML, including meaningful image descriptions, in the text version. The experiment checks whether projected text fragments and nonempty alternative text occur in whitespace-normalized plain text. This detects some omissions; it does not prove equivalent meaning, order, emphasis or accessibility. A composer should support reviewing both presentations without imposing a new confirmation dialog on every send.

The authenticated event fields are authoritative. MIME text/HTML alternatives are projections for carriage and compatibility. A mismatch is reported per received carrier; it does not rewrite the event or confer authority on the alternative. Rich rendering uses the accepted event's HTML. Retries preserve the original event bytes, including whitespace and escape spellings.

## Embedded images and download-only files

Every resource belongs to exactly one declared role. Embedded resources are PNG or JPEG images eligible for the scoped decoder. Attachments are opaque files described for deliberate retrieval. A declaration or MIME header cannot make a resource available: the selected bytes must match the authenticated size and SHA-256 digest.

An HTML image reference has this form:

```text
cid:<resource-id>.<event-id>@resources.email-next.invalid
```

Both identifiers use the existing nonzero 32-character lowercase hexadecimal ObjectId grammar. Resolution is confined to the exact selected carrier for that event. The receiver does not search another message, an outer attachment, a forwarded subtree or the network for a replacement. Supported URI decoding does not enlarge that scope.

Every `img` needs an `alt` attribute. Empty alternative text explicitly marks a decorative image; omission is not equivalent. Missing, ambiguous, corrupt, unsupported or over-budget image bytes produce an inert alternative-text result. Validated images become pixels in the isolated renderer, not sender-controlled HTML image elements. Attachments remain explicit downloads, including HTML and message/rfc822 files. Opening a message never automatically opens an attachment or activates nested MIME.

:::: {.details summary="Complete operation schema"}

### Required members

The operation is a JSON object with exactly these eight members. None may be omitted; additional members and null values are invalid. The common strict event decoder rejects duplicate decoded member names and invalid Unicode before operation validation.

| Member | Exact type and meaning |
| --- | --- |
| `kind` | Exactly `"rich-message"` |
| `text` | Unicode scalar-value string; empty is structurally permitted |
| `html` | Unicode scalar-value string; empty is structurally permitted, but safe authoring/presentation is a separate gate |
| `presentation` | Exactly `"html-css-v0"` |
| `replyTo` | Array containing zero or one exact EventReference, using the ordinary message reply rules |
| `manifest` | Array of unique resource records described below; empty is allowed |
| `embedded` | Array of embedded-image role records; empty is allowed |
| `attachments` | Array of independent attachment descriptions; empty is allowed |

A minimal operation with no resources is:

```json
{
  "kind": "rich-message",
  "text": "Meet at noon.",
  "html": "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><p>Meet at <strong>noon</strong>.</p></body></html>",
  "presentation": "html-css-v0",
  "replyTo": [],
  "manifest": [],
  "embedded": [],
  "attachments": []
}
```

An EventReference has exactly `principal`, `conversation` and `event`, with their existing identifier grammars. A reference is not an access credential or proof that its target exists. Missing context can remain visibly unavailable; a relationship must satisfy the ordinary exact-target and conversation rules before the client treats it as established. No transcript is inserted to satisfy a missing reference.

### Manifest records

Each manifest record has exactly `id`, `size` and `sha256`:

- `id` is a resource ObjectId, unique within the manifest.
- `size` is a canonical decimal string from `"0"` through `"18446744073709551615"`. No signs, leading zeros, fractions or JSON numbers are admitted.
- `sha256` is exactly 64 lowercase hexadecimal characters describing the resource bytes after MIME transfer decoding.

Manifest order is not constrained by this schema. It remains part of the exact event bytes and cannot be reordered during a retry. Local byte limits apply before allocating the declared size; accepting the wire grammar is not permission to allocate a uint64-sized resource.

### Role records and complete coverage

Each embedded record has exactly `resource` and `mediaType`. `resource` names a manifest entry; `mediaType` is exactly `image/png` or `image/jpeg`. Embedded records must be in strictly ascending resource-identifier order.

Each attachment record has exactly `resource`, `name`, `mediaType` and `description`. `name` and `description` are Unicode scalar-value strings, structurally allowed to be empty. `mediaType` is a lowercase token/token media type with no parameters. Each token matches the following character class, repeated one or more times:

```text
[a-z0-9!#$%&'*+.^_`{|}~-]+
```

This grammar describes metadata; it does not authorize a decoder. Attachment order is not constrained by this schema.

Each role names an existing manifest entry once. The two role lists are disjoint and together cover every manifest entry. A resource cannot be both an embedded image and a download-only attachment. HTML may reference the same declared embedded resource more than once; the role inventory still contains it once. Shape validation does not establish that every declared image is visibly used.

::::

:::: {.details summary="Protected MIME layout and selection"}

### Exact direct structure

With no download-only attachments, the root is `multipart/alternative` with exactly three children, in this order:

1. `text/plain; charset=utf-8`.
2. `text/html; charset=utf-8`, or the related structure below when there are embedded images.
3. The exact event bytes as the candidate `application/vnd.threadlabs.email-next-event+json` type, with no media-type parameters.

For embedded images, the second child is `multipart/related; type=text/html`. Its first child is the HTML alternative; the remaining direct children are the embedded image resources. There is no `start` parameter. For download-only attachments, the root is `multipart/mixed`: first the complete alternative structure, then the independent attachment parts. Empty related/mixed wrappers are not generated or selected. No recursive search selects a nested alternative or forwarded message as the contribution.

The root has one `MIME-Version: 1.0`. Multipart parameters are only the required boundary and, for related, `type=text/html`; preambles and epilogues are absent. Each part has one Content-Type. Duplicate or defective headers fail selection. Only Content-Type, MIME-Version and leaf Content-Transfer-Encoding are allowed, with Content-ID and Content-Disposition additionally allowed on resource parts. Protected From/Subject and similar presentation headers are not smuggled into this body structure.

The three alternatives use canonical base64, allowing MIME whitespace around its encoded symbols. Text alternatives decode as strict UTF-8. Generated readable alternatives use the existing MIME text serialization, including line-ending projection; the event alternative preserves the exact JSON bytes. Resource parts also use canonical base64 with MIME whitespace allowed, under the [resource binding](messages.md#bundled-resource-binding) rules. CRLF wire framing is required.

### Resource projections

Each resource part has Content-ID `<resource-id.event-id@resources.email-next.invalid>`. An embedded part is image/png or image/jpeg with `Content-Disposition: inline` and no disposition parameters. An independent attachment has `Content-Disposition: attachment` and one filename parameter.

Authenticated attachment descriptions remain authoritative when MIME filename or type projections differ. Generated filenames replace control characters with underscores and use `attachment` when the resulting name is empty; this is not a filesystem-safety guarantee. Composite declared media types (`message/*` or `multipart/*`) project as `application/octet-stream`, preserving opaque bytes. Other metadata discrepancies are diagnostics, not permission to reinterpret the file or replace the authenticated description.

### Failure boundaries

Carrier selection precedes structured effects and uses the authenticated payload choice; there is no MIME/raw sniff fallback. Invalid framing, unsupported structure, encoding or resource limits makes carriage unavailable for activation. It does not authorize truncation, partial structured effects or a switch to ordinary delivery.

A valid event can remain readable while individual resources are missing, ambiguous or fail integrity checks. Unbound parts do not become additional declared resources. Bytes found only in an embedded-image slot cannot satisfy a download-only attachment, even when their Content-ID and digest match. Unexpected resource identifiers do not shift another attachment’s metadata association. Rich HTML diagnostics or parser isolation failure select the authored plain presentation; an image-specific binding/decoder failure retains alternative text. Actual bytes are released for download only through accepted-event and exact-carrier selection.

Wire, decoded-byte, part-count, parser, image and output budgets are explicit local implementation limits. Post-parse part counting is not a claim that the MIME parser never allocates before counting. The separate process enforcement and platform limitations are described in the [presentation profile](presentation-profile.md).

::::

## Negotiate the whole payload profile

The initial selected binding is context4, envelope1 and payload `mime-rich-v0`, supported through signed assertion3 tuples. The exact operation set must include `rich-message` on every admitted device. Implementing the operation parser or advertising a different payload does not imply support. Initial invitation version 3 uses common roster version 0; established invitations use version 3. Both bind that agreement as specified in their owning chapters.

The [private-copy profile](private-copies.md) independently versions its envelope/context/assertion while reusing this operation and payload. Later profiles must explicitly select their own exact tuple and preserve the operation's rules; no inferred cross-product or silent upgrade is permitted. Existing raw-event/body-only contexts do not accept a rich payload merely because it contains recognizable MIME.

## Evidence and remaining limits

The [joined rich experiment](evidence/README.md#protected-rich-body-and-scoped-images) combines signed discovery and admission, SMTP, durable protected receive, isolated HTML presentation, exact embedded pixels and deliberate attachment retrieval. Source/schema checks and local browser examples do not establish semantic equivalence of the two presentations, complete decoder fidelity, every browser or native accessibility conformance, or independent-provider interoperability.
