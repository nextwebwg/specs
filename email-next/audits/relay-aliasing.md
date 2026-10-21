---
title: Apple email relay prior art
sectionNav: true
---

# Apple email relay prior art

Apple's email relay features combine ordinary email aliases and forwarding with service-specific account and sender controls. The public documents below identify standard email-authentication mechanisms, but do not identify an interoperable protocol for providers to issue, exchange and revoke one another's aliases. That is a finding about these documents, not proof that no related standard exists.

## Documented mechanisms

**Sign in with Apple private email relay.** Developers register permitted sending domains or addresses. Apple requires SPF and/or DKIM authentication and checks the authenticated source against that registration; unregistered sources are rejected. This is standard sender authentication combined with Apple's registration policy. It does not by itself authorize an individual end-user peer of a shared provider. [Apple developer configuration guide](https://developer.apple.com/help/account/capabilities/configure-private-email-relay-service/)

Apple's November 2019 white paper describes a distinct alias for each user/developer pair, forwarding to a verified inbox, masked replies and user-controlled disabling. It names SPF, DKIM and DMARC as authentication mechanisms. This historical description supplies prior art; it is not evidence of current implementation internals or independently verified retention. [Sign in with Apple white paper, pages 5–6](https://www.apple.com/co/privacy/docs/Sign_in_with_Apple_White_Paper_Nov_2019.pdf)

**iCloud+ Hide My Email in Mail.** Apple documents generated aliases for sending, forwarding replies to the real account, replying from the same alias and managing or deactivating aliases. These user-facing operations demonstrate address masking without requiring correspondents to adopt a new mail protocol. [Apple Mail user guide](https://support.apple.com/guide/iphone/use-hide-my-email-iphf277f837e/ios)

The cited relay descriptions do not specify end-to-end message encryption or an authenticated encrypted inner-address package. Masking an address must not be presented as providing those properties. Apple retains the forwarding role and knows the alias-to-inbox mapping. Forwarding to a personal destination also leaves that destination necessary to the onward delivery service.

## Application to Email/2

The [private-addressing contract](../private-routing.md) adopts scoped, revocable routing and explicit sender authorization as design requirements. Its additional work is a provider-independent contract for authenticated alias issuance, peer-scoped route use, renewal/revocation and migration, plus personal addresses inside the authenticated encrypted conversation package.

Normal SMTP delivery and provider SPF/DKIM/DMARC authentication remain useful for the outer relay identity. They do not prove inner authorship, authorize conversation membership or hide a personal recipient used on a later forwarding hop. The client must accept the encrypted contribution and its address bindings before displaying a personal author in place of a relay.

## Review scope

Selected Apple public documentation, reviewed 20 October 2026. This is a feature/mechanism comparison, not a section-by-section RFC audit, an Apple implementation audit or a claim that Apple's relay service supports Email/2. No published cross-provider provisioning protocol was identified in these sources; the Email/2 binding remains proposed and unfinished.
