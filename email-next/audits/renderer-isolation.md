---
title: Renderer DOM and isolation audit
sectionNav: true
---

# Renderer DOM and isolation audit

The experimental renderer builds message content as DOM nodes inside a sandboxed frame. It does not insert sender HTML into that frame's source document. This review checks the selected browser rules behind that boundary; it does not certify the renderer or establish cross-browser security.

## Constructing the view

The runtime uses `createElement`, `createTextNode`, restricted `setAttribute`, `append` and `replaceChildren`. Text-node construction preserves text as data; it does not parse markup. Element and attribute setters still have browser semantics, so their use alone is not sanitization. The client-owned vocabulary excludes script elements, event-handler attributes and message-controlled resource URLs. Images arrive as decoded pixels; link destinations stay in the parent client. The trusted runtime creates canvas and accessibility attributes itself. [DOM construction and mutation](https://dom.spec.whatwg.org/#interface-document), [text content](https://dom.spec.whatwg.org/#dom-node-textcontent).

## Separating the frame

The iframe sets `sandbox="allow-scripts"` without `allow-same-origin`. That permits the fixed client runtime while retaining the opaque-origin restriction and restrictions on forms, auxiliary windows and top-level navigation. It is not a claim that all script execution is disabled. Removing the frame destroys its child navigable; the host also closes its message ports and clears retained link selections. [HTML sandboxing](https://html.spec.whatwg.org/multipage/browsers.html#sandboxing), [iframe processing](https://html.spec.whatwg.org/multipage/iframe-embed-object.html#the-iframe-element).

The trusted child runtime creates the channel and transfers the parent's endpoint in its ready message. The parent installs its listener before frame insertion and requires the exact frame window, opaque origin, per-mount token, message shape and one port. It accepts one handshake; rejected renderer handshakes close their transferred ports. Plaintext is sent only through the accepted channel. A later frame load disposes the view and port. The child uses a wildcard when addressing its parent because the enclosing client origin is not a sender-controlled configuration value; this relies on that parent being trusted. It does not protect against a compromised embedding application. [Cross-document messaging security](https://html.spec.whatwg.org/multipage/web-messaging.html#security-10).

The browser checks include wrong source/origin/token, extra fields, excess ports, repeated and stale handshakes, navigation before and after readiness, timeout and disposal. Some invalid events are injected by the trusted test harness to exercise the validation branches; they do not demonstrate a remote attack. These checks strengthen the lifecycle evidence without proving a complete navigation or channel security model.

## Content and referrer policies

The generated document places its CSP meta element before its stylesheet and runtime script. The policy blocks resource loads by default, permits the nonce-bearing runtime and permits inline styling for the filtered presentation. `base-uri` and `form-action` are explicit restrictions; they must not be inferred from the fetch default. Attribute and CSS filtering remain essential. The selected CSP draft itself leaves CSSOM initialization behavior unfinished. [CSP3, 16 September 2026](https://www.w3.org/TR/2026/WD-CSP3-20260916/).

Meta-delivered policy does not cover preceding content and cannot deliver `sandbox`, `frame-ancestors` or report-only policy. Other applicable policies are enforced alongside it; this meta element cannot relax an embedding application's policy. The iframe attribute supplies this experiment's sandbox. [CSP meta delivery](https://www.w3.org/TR/2026/WD-CSP3-20260916/#meta-element).

> [!note] A nonce is client configuration, not sender data
> The default now encodes all 128 bits from `crypto.getRandomValues` into 32 hexadecimal characters. A supplied `sandboxNonce` remains a trusted embedding/test override: syntax and length checks do not establish entropy or freshness. An embedding application that transmits nonce policies owns their unique-generation lifecycle. Focused tests check byte-preserving encoding and override behavior; they do not prove a browser's random generator or complete CSP enforcement. [CSP nonce reuse](https://www.w3.org/TR/2026/WD-CSP3-20260916/#security-nonces).


The iframe's `referrerPolicy` governs its loading behavior. Deliberate external navigation occurs in the parent with `noopener,noreferrer`; HTML defines the latter as also selecting no-referrer. This suppresses the referrer header, not all destination-visible information or tracking. [Window opening](https://html.spec.whatwg.org/multipage/nav-history-apis.html#window-open-steps), [Referrer Policy](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer).

## Passing data and decoded pixels

The channel transfers a fresh pixel buffer owned by this render request. Transfer detaches that buffer from the sender; it does not transfer the original retained message or image resource. Plain objects and arrays are reconstructed in the receiving realm. Structured cloning is not schema validation: it preserves object graphs and can read properties during serialization. The host therefore bounds and constructs its input before transfer, and the runtime checks its permitted vocabulary again. This interface accepts client-produced data, not arbitrary sender JavaScript objects. [Structured data](https://html.spec.whatwg.org/multipage/structured-data.html#structuredserializewithtransfer).

A transferred port carries its queued tasks to the receiving endpoint. Setting `onmessage` or calling `start()` enables delivery; `close()` detaches and disentangles the endpoint. Closing is not an acknowledgment that the other side processed a message. Deserialization can fail with `messageerror`, and allocation can fail. The renderer's timeout and disposal remain necessary failure paths. [Channel messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#message-ports).

Pixels use `Uint8ClampedArray`, `ImageData` and the default sRGB, eight-bit 2D context. The dimensions must match the RGBA array. `putImageData` writes pixels without applying the current transform, clipping, compositing or shadow settings. Canvas dimensions are set before painting because changing them resets the bitmap and rendering state. Color conversion, alpha representation and subsequent display scaling mean that identical decoded bytes do not promise identical screen pixels or byte-identical readback. No sender URL is passed to Canvas. [Pixel manipulation](https://html.spec.whatwg.org/multipage/canvas.html#pixel-manipulation), [ImageData](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#imagedata).

## Applying filtered styles

The runtime calls `style.setProperty` for each accepted declaration. CSSOM parses the value against the property's grammar; unsupported properties or invalid values are ignored. The priority argument is separate, so a value containing `!important` is not a way to set priority. Setting a declaration updates the element's style attribute; shorthand expansion and logical-property ordering still follow CSSOM. These browser checks supplement the finite profile filter and do not replace it. [CSSOM §§6.6.1, 6.7.1 and 7.1](https://www.w3.org/TR/2021/WD-cssom-1-20210826/#dom-cssstyledeclaration-setproperty).

## Inherited embedding policies

An `about:srcdoc` document receives a clone of its parent's policy container on fresh navigation; a history navigation uses its retained policy container. The sandboxed-origin flag takes precedence over the ordinary srcdoc origin inheritance. These are separate rules: an opaque origin does not erase inherited CSP restrictions. A stricter embedding policy can prevent the trusted runtime from starting, and the renderer must fail visibly rather than relax that policy. [Policy containers](https://html.spec.whatwg.org/multipage/browsers.html#policy-containers), [srcdoc navigation](https://html.spec.whatwg.org/multipage/browsing-the-web.html#create-navigation-params-from-a-srcdoc-resource).

## Review boundary

The HTML review uses commit `e8393694edd92117cfb4886e2fe5dd2897374136`; CSP uses the dated working draft above. CSSOM uses its dated 26 August 2021 Working Draft, still the published `/TR/cssom-1/` version at this review; DOM and Referrer Policy are captured snapshots from 20 October 2026. Private evidence records exact hashes and reviewed line ranges. This is a selected-range review, not complete review of those specifications. The selected srcdoc policy inheritance, plain-data and transferable-buffer algorithms, port lifecycle, inline CSSOM setters and pixel-only Canvas path are covered here. Other navigation modes, platform-object serialization and Canvas drawing APIs are outside this renderer path. Trusted Types enforcement by an embedding application remains a conditional integration dependency; this experiment has not established a Trusted Types policy. This review does not audit the complete JavaScript engine, Web IDL conversion machinery or operating-system graphics stack. Existing [browser experiments](../evidence/README.md#isolated-browser-rendering) remain execution evidence with their stated limits; the associated 21-group Chromium run adds local lifecycle evidence, not independent assurance.

::: {.details summary="Selected platform algorithms"}

### Exact applicable scope

| Source | Reviewed selection | Boundary |
| --- | --- | --- |
| Pinned WHATWG HTML source | StructuredSerializeInternal and StructuredDeserialize branches for primitives, arrays, ordinary objects and ArrayBuffer; transfer variants | No use of shared buffers, resizable buffers or arbitrary serializable platform objects is required by this host. |
| Pinned WHATWG HTML source | MessageChannel construction; MessagePort entanglement, transfer, receiving, posting, start, close and garbage collection | Task delivery does not establish application acceptance. Explicit disposal is separate from eventual garbage collection. |
| Pinned WHATWG HTML source | Canvas dimensions and 2D context initialization; ImageData initialization; putImageData common steps | Pixel insertion only; no sender drawing commands, text painting, drawImage or external image decoding in the frame. |
| Pinned WHATWG HTML source | Policy-container cloning, navigation policy selection, srcdoc navigation parameters and origin determination | Selected local frame path, not complete navigation/history or Fetch review. |
| CSSOM §§6.6.1, 6.7, 7.1 | Inline declaration update, setter, grammar parsing and declaration/value serialization | Serialization is a browser representation, not retained authenticated CSS. The draft records serialization latitude; the client does not use serialized style text as an authenticity check. |

### Evidence boundary

Private evidence fingerprints the HTML commit, CSSOM publication and the runtime files inspected. ECMAScript allocation/property operations and Web IDL bindings are trusted platform dependencies; this selected audit does not claim to have independently reimplemented or fully reviewed them. The published CSSOM draft's unresolved details and CSP's CSSOM integration issue remain visible rather than being treated as completed standards text.

:::
