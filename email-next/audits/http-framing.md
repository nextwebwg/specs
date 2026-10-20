---
title: HTTP framing and caching
sectionNav: true
---

# HTTP framing and caching

A server must identify one complete request before treating its body as an authorized action. A client must receive one complete response before recording its receipt. Conflicting lengths, truncated bodies and ambiguous authority cannot establish either fact.

## Framing precedes application authorization

The configured service and hosted-access experiments reject duplicate authority or framing fields, malformed field names, folded fields, transfer coding, unsupported expectations and invalid lengths before dispatch. They require one exact configured Host value. The provider experiment has its own bounded parser with corresponding authority and framing checks. These checks support the existing exact endpoint binding; they do not create a different authorization mechanism. [RFC 9112 §§2–3, 5–6](https://www.rfc-editor.org/rfc/rfc9112.html#section-2)

The direct service and management clients require a bounded Content-Length response and compare that length with the bytes actually received. An incomplete response cannot become a receipt. They request connection closure and do not reuse a connection for another exchange. A lost response can still leave the application outcome uncertain; reconciliation uses the retained operation and exact request. [RFC 9112 §§6.3, 8–9](https://www.rfc-editor.org/rfc/rfc9112.html#section-6.3)

The fixture handler restores the original validated request target before dispatch because its underlying Python handler otherwise collapses leading slashes. `/submit`, `//submit` and `///submit` remain distinct configured paths. Socket-level regression checks exercise that boundary.

## These fixtures implement a restricted transport

The Python fixtures accept origin-form requests with fixed-length bodies. They reject chunked transfer coding and absolute-form targets. General HTTP/1.1 recipients must support chunked decoding, and general origin servers must accept absolute-form targets. The fixtures therefore provide bounded local evidence, **not full HTTP/1.1 server conformance**. A production HTTP stack needs those capabilities and equivalent checks at every proxy boundary. [RFC 9112 §§3.2.2 and 6.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2.2)

RFC 9931 updates HTTP/1.1 CONNECT behavior to prevent optimistic tunnel bytes from becoming another request after rejection. These adapters do not offer CONNECT, protocol upgrades or proxy tunnels. Deployments adding those features must review that update before enabling them. [RFC 9931 §8](https://www.rfc-editor.org/rfc/rfc9931.html#section-8)

## No-store does not mean no retained application evidence

Sensitive responses carry `Cache-Control: no-store`. The direct clients have no HTTP response cache; the hosted browser requests also select no-store behavior. A request directive alone does not remove an already stored response, and no-store is not a confidentiality guarantee against a malicious cache. Authenticated responses also have specific shared-cache restrictions. [RFC 9111 §§3.5, 5.2.1.5 and 5.2.2.5](https://www.rfc-editor.org/rfc/rfc9111.html#section-3.5)

An encrypted request vault, durable decision or historical management receipt is application state, not an HTTP cache. Its retention and access rules remain those of the owning service contract. These experiments do not implement cache revalidation, shared-cache freshness calculations or an intermediary deployment.

## Reviewed scope and corrections

This is a selected review of message framing, connection closure, cache storage restrictions and sensitive-response handling. It is not a complete base review of RFC 9111, RFC 9112 or RFC 9931. Exact source hashes and reviewed ranges are retained privately.

All listed errata were examined for this scope: four for RFC 9111 and four for RFC 9112; none were listed for RFC 9931. RFC 9112's verified corrections repair an `obs-text` reference and document absolute-form precedence. Its rejected proposals do not authorize relaxed chunk framing. RFC 9111's reported revalidation changes and held cache-extension clarification are not adopted as new requirements. These adapters have no shared cache or conditional revalidation implementation. [RFC 9111 errata](https://errata.rfc-editor.org/search/?rfc_number=9111), [RFC 9112 errata](https://errata.rfc-editor.org/search/?rfc_number=9112)
