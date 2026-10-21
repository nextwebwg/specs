---
title: Delivery protection and fallback
order: 12
blurb: encrypted delivery · ordinary copies · hosted access
sectionNav: true
navGroup: guide
---

# Delivery protection and fallback

The sender decides what should happen when someone cannot receive an encrypted contribution: send ordinary email, offer access through a hosted page, or hold delivery until a compatible endpoint is available. A client can remember that choice so routine sending does not require repeated dialogs.

> [!ex] Bob can decrypt; Carol cannot
> Alice sends one answer to Bob and Carol. If she permits ordinary email, Bob can receive an encrypted copy and Carol a readable ordinary copy. Alice's history shows that mixed protection. If Alice requires encrypted endpoints for both, Carol's delivery waits; Bob's ready copy may still be sent.
>
> A hosted link is a third choice with its own access rules. Failure to encrypt does not automatically authorize either fallback.

The policy applies to this contribution and its intended audience. An encrypted copy does not make every other copy confidential.

The [encryption journey](encryption-journey.md) applies these permissions to first contact, mixed recipients, device changes and recovery without requiring repeated routine decisions.

The [module framework](modules.md) also treats content encryption, sender masking, recipient masking and identity verification independently. Remembered address-privacy requirements can hold an otherwise encrypted copy; permitted automatic upgrades select newly available protection without asking the person to edit addresses. The [swap sequence](private-routing.md#when-the-addresses-change) defines the exact composition, encryption, outer origination and receive-display boundaries.

## Per-recipient outcomes

| Effective permission | Compatible authenticated endpoint available | No compatible endpoint available |
| --- | --- | --- |
| Require encrypted endpoint | Encrypt using the selected profile | Hold that delivery and show what capability or identity evidence is missing |
| Permit ordinary copy | Prefer protected delivery where supported | Send readable ordinary email under the remembered permission |
| Permit hosted access | Prefer protected delivery where supported | Use the approved hosted service and explicitly identified access model |

A permission to send an ordinary copy does not authorize publishing it at a new hosted service. A permission to use hosted access does not authorize a plaintext attachment after that service fails. The sender may explicitly permit more than one fallback; their order must be part of the effective policy.

The sender may deliver ready copies while another recipient remains pending. The sent record must distinguish that partial delivery from delivery to everyone. A later retry for the pending recipient retains the contribution's identity and authorization context; it does not resend successful copies or silently change their audience.

If a recipient's identity evidence changes after planning but before submission, re-evaluate that recipient. A transport failure does not by itself justify a weaker mode. Once a copy has been accepted for delivery, switching mode is an additional disclosure, not cancellation of the earlier copy.

## Contribution-wide exposure

A client must distinguish **“this copy was encrypted”** from **“every copy was encrypted.”** If Alice permits an ordinary copy for Carol, the contribution MUST NOT be labeled “end-to-end encrypted for everyone,” even though Bob's copy is encrypted.

The sender's history shows mixed protection and distinguishes protected copies, ordinary copies authorized, hosted access authorized and pending deliveries. An upgraded recipient's authenticated contribution metadata MUST indicate an intentional disclosure outside endpoint encryption, without revealing hidden recipient identities or counts. The exact encoding belongs in the message profile. A recipient reports only the evidence it possesses; successful decryption cannot prove that no other disclosure occurred.

Plaintext exposure is not reversed by later encryption. Removing someone from a later reply does not remove their earlier copies. Quoted history enters the new reply only when deliberately selected, with its exposure evaluated for the new audience.

A readable fallback can disclose more than the new operation itself. An answer may repeat a question and its selected label; a reaction may carry a reference to an earlier message. The sender's effective permission must cover those exact copied fields for the actual recipients. Prior access by the protected group does not authorize disclosure to someone outside it. The same rule applies to structured alternatives and metadata, including audience identifiers; hiding a field from the visible body does not make it private.

> [!ex] Answering does not automatically share the question
> Bob selects “Friday” in Alice's protected question. If his ordinary copy to Carol would include Alice's question text, his client must evaluate that text as part of the disclosure. Remembered permission can cover it; otherwise the copy waits. The client does not append the rest of Alice's conversation.

Readable alternatives of a protected copy belong inside its protection envelope. A plaintext alternative beside ciphertext in the same message would expose the content and MUST NOT be used as compatibility fallback. Hosted access must likewise identify who can read the content; a bearer link does not establish endpoint-only encryption.

:::: {.details summary="Why this differs from existing encrypted-email guidance"}

### Mixed delivery and the message's confidentiality status

[RFC9787 Section 3.2](https://www.rfc-editor.org/rfc/rfc9787.html#section-3.2) recommends avoiding copies of one message with different end-to-end protection. Email/2 deliberately permits sender-selected fallbacks for incremental adoption. This is a scoped departure from that recommendation, not a claim that mixed delivery provides uniform confidentiality.

[Section 9.6](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.6) explains the downstream problem: a recipient who receives an encrypted copy may assume that a reply to everyone can also be encrypted. Email/2 makes the fallback permission explicit and carries the contribution's broader disclosure status to upgraded recipients. It also composes replies as new contributions, without automatically quoting earlier content. This permits gradual adoption while retaining encryption on compatible deliveries. It does not recover confidentiality lost through an ordinary copy, and a legacy recipient may not understand the structured disclosure indication.

A reply therefore gets its own recipient plan. The original sender's fallback permission is not permission on behalf of the replying person. If that person's effective policy requires encryption, an unavailable recipient remains pending; receipt of a mixed-protection message does not weaken that policy. Deliberately including earlier protected content still requires evaluating its disclosure to the new audience.

Before sending, the interface MUST distinguish endpoint-encrypted delivery, provider-hosted access and ordinary plaintext delivery in the recipient plan. A local lock icon cannot replace the authenticated disclosure indication required above. If any copy is plaintext, the contribution MUST NOT be summarized as confidential to the encrypted recipients. The interface may describe that particular copy as encrypted alongside the broader disclosure status.

These permissions do not authorize weakening an enforced-encryption plan or disclosing an earlier protected message in a reply.

::::

## Choosing a sending account

A sender picker selects an account and its sending authority. It does not allow arbitrary From text. A compact address button may expose that choice without repeating it throughout the composer.

Before preparing a protected reply, resolve the selected account's cryptographic identity, authorized device and current conversation permissions. A mailbox alias does not establish a new identity or grant membership. If the selected identity cannot perform the operation, hold it and explain the missing authority. An edit still requires its original author's authority; selecting another account cannot bypass that rule.

Changing accounts also re-evaluates the recipient plan and the selected sender's fallback policy. Permission retained for another sender does not transfer automatically. Previously prepared or sent contributions retain their original identity and account binding: account switching must not rewrite signed events, queued retries or disclosure grants.

> [!ex] Personal and work accounts
> Carol opens a reply from her personal account, then chooses her work address. The thread can remain visible while the client checks the work account's authority and delivery policy. If it cannot send a protected reply there, the client holds that mode or offers an independently authorized alternative. It does not silently borrow the personal account's key.

## Remembered policy and the send plan

A client MAY remember a user's policy for a correspondent or conversation. It MUST expose the effective policy before sending and let the user change it. This specification does not require a confirmation dialog on every send or select a universal default.

Before submitting any copy, the client constructs a send plan containing:

- The immutable contribution and selected intended recipients, including private delivery recipients.
- The chosen route and protection mode for each recipient.
- The identity and capability evidence supporting that route, with its freshness and scope.
- Any hosted-access service and its access model.
- The effective fallback permissions and the scope in which the user set them.

The plan is local authorization state, not a public recipient manifest. It MUST NOT disclose Bcc recipients, private device lists or recipient-specific access credentials to other recipients.

Changes to audience, content, hosting service or protection mode require re-evaluation before the affected copy is submitted. A remembered policy may authorize a fallback without another prompt, but the composer and sent record must accurately reflect the resulting exposure. Failure to obtain capabilities MUST NOT silently amend a policy requiring encryption.

## Hosted-access models

A hosted fallback record identifies which of these models it implements. These names describe trust boundaries, not interchangeable security badges.

| Model | Who can gain access | Provider boundary |
| --- | --- | --- |
| Bearer access | Anyone possessing the access credential | Hosting service may hold plaintext or keys; email readers may obtain the credential |
| Account-bound access | An authenticated account satisfying the host's authorization policy | Host authentication and recovery are trusted; address ownership is not necessarily cryptographic identity continuity |
| Independently authorized cryptographic endpoint | An endpoint authorized under the selected end-to-end profile | Requires separately specified key authorization and browser-code trust; merely loading a web page does not establish this model |

The [hosted bearer-access candidate](hosted-access.md) defines credential generation, exact request/receipt objects, deliberate retrieval and revocation. Its credential profile uses 32 random octets encoded as unpadded base64url. The selected bearer model has a joined local implementation. Public management-credential issuance and production hosting integration remain unfinished; the other hosted models need separate contracts.

Each recipient receives a separate hosted grant. Shared links among recipients are outside this baseline because they prevent recipient-specific revocation and complicate disclosure accounting. Forwarding a bearer link still transfers its authority; a separate grant does not make a bearer link identity-bound.

The notification contains minimal invitation text and the access link. It MUST NOT include private answers, quoted history or the protected contribution as an email preview merely to make the notification look richer. An email subject may itself disclose information and must follow the selected metadata policy.

> [!ex] A forwarded link is still a bearer link
> Carol forwards her access email to Dave. If possession of the link is enough to open it, Dave can use it too. A separate link for each recipient helps revoke grants independently; it does not prove who opened the page or who wrote a reply.

## Link access, previews and replies

Fetching a link MUST NOT submit an answer, send a read receipt, accept an invitation, consume a one-time grant or change conversation state. Email scanners and preview services may follow links without user intent. Any state-changing operation requires explicit interaction after the access page has loaded and a fresh authorization check.

The access page MUST NOT send credentials or message content to third-party analytics, remote fonts, embedded resources or outbound-link referrers. Credentials must be excluded from routine application logs and error reports. This requirement does not make the hosting operator unable to inspect the delivered page or its content.

:::: {.details summary="Secret links and redirects"}

### Hosted credential navigation

A fragment-held credential is absent from the initial HTTP request target, but remains available to scripts in the loaded page. It is not automatically confined to the original origin. [RFC9110 Section 10.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.2) requires a redirect target without its own fragment to inherit the original fragment. A page reached through that redirect can therefore receive the secret in its URL even though the preceding server did not receive it as request content.

The initial hosted-access profile MUST use a direct HTTPS grant-entry URL and serve that entry page without an HTTP redirect. Do not put a URL shortener, tracking redirect or canonical-host redirect in front of a secret-bearing grant URL. This is a proposed deployment constraint to prevent credential transfer before the access application's code can run. It does not establish protection from the original hosting service or its page scripts.

After loading, any navigation to a login service or another origin MUST exclude the grant credential and protected content from the destination URL, including its fragment, and from redirect state and referrers. Preserve the grant only within the authorized access flow. A future redirect-capable profile must define its destination authorization and secret-removal behavior explicitly; an arbitrary Location response is not permission to disclose the credential.

Acceptance cases must exercise missing, empty and replacement redirect fragments, same-origin and cross-origin redirects, and login return paths. Test the browser's resulting URL and what destination scripts can read, not merely what appears in server access logs. This profile has not yet been verified in a hosted browser implementation.

::::

A bearer link alone MUST NOT authorize a reply attributed as a verified mailbox owner's act. The host must either authenticate the replying identity under its stated model or label the reply as originating from the holder of a particular grant, without upgrading that evidence to cryptographic authorship. Structured answers follow the same attribution rule.

Replying through the host creates a new contribution with its own audience and protection policy. The host MUST NOT expose earlier conversation history to new recipients automatically. It must not convert a recipient's response into an ordinary-email copy merely because the original invitation arrived through email.

## Expiry, revocation and failure

A hosted grant has an explicit expiry policy, either a timestamp or an explicit no-expiry setting. The sender can inspect it before disclosure. Revocation prevents future authorized retrieval through that grant after enforcement takes effect; it cannot erase downloads, screenshots, caches or previously obtained decryption material.

An expired, revoked or unavailable grant shows a clear access failure without automatically emailing the content or issuing a replacement grant. Renewal follows the sender's authorization policy and preserves an audit record. Reassigned accounts, changed identities and recovery require fresh authorization appropriate to the model.

The sender's record keeps separate facts for grant creation, notification submission, retrieval evidence, reply creation and revocation. None of these alone proves that the intended human read the contribution. A network request from a link scanner is not a read receipt.

## Scheduled submission and accepted holds

A locally scheduled draft remains subject to audience, identity and protection checks before submission. A message already accepted by a provider for future release has crossed that boundary. Show these states separately; do not present an accepted hold as a locally cancellable draft without a provider cancellation contract.

FUTURERELEASE does not define cancellation, ciphertext replacement or a fresh recipient-key check at release time. A sender requiring authorization to be rechecked at the scheduled instant must retain the contribution at an authorized endpoint capable of doing so. Do not delegate decryption to an ordinary relay to simulate that property. If the required scheduling mechanism is unavailable, hold or fail visibly rather than silently sending early.

A requested release time is not a guaranteed arrival time. Do not rewrite message history or trace fields to imply otherwise. The [future-release audit](audits/future-release.md) records existing timing rules and outstanding implementation dependencies.

## Replies and private recipients

A new reply has a new audience. Adding someone does not automatically share earlier history, confidential subjects or private recipient information. A blind-copy recipient must be able to see when replying would reveal their participation.

:::: {.details summary="Blind-copy generation and historical alternate addresses"}

### Blind-copy representations

For generated copies, do not include a Bcc field in copies intended for To or Cc recipients. A blind recipient's copy may omit Bcc, contain an empty Bcc field, or contain only that recipient's own address. Never expose the other blind recipients through shared structured metadata, control replies or encryption recipient descriptions. This proposed profile follows the clarified blind-copy handling in the pending emailcore message-format revision, while preserving legacy source messages for reading.

The absence of a Bcc field does not prove that no blind recipients existed. A client that knows the current user received a blind copy should make the disclosure consequence of replying to visible recipients apparent before sending. It must not infer a hidden recipient roster from missing header information.

### Why the managed-group model differs from RFC 9787

[RFC 9787 §9.4.1](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.4.1) offers a certificate-based construction: one main copy and a separate copy for each blind recipient, with that separate copy also decryptable by the named recipients. Its cryptographic payload contains no Bcc field, and blind-recipient certificates are not distributed with the message.

Email/2's managed MLS group has a member-visible roster. Adding a blind recipient to that group would disclose their membership, so this profile prohibits doing so. A private recipient instead needs a separately authorized delivery under the selected policy. This is a structural difference from the certificate-based construction, not evidence that MLS hides recipients. Creating a separate group with all named recipients would still reveal its membership to those members.

The ordinary-header alternatives above do not override the stricter no-Bcc-payload rule when implementing RFC 9787's certificate-based construction. Likewise, a hidden delivery must not leak through shared event audiences, device advertisements or history. A fresh reply needs its own audience and protection decision; a blind copy does not establish that its recipient can reply through the visible MLS group.

The [protected private-copy binding](private-copies.md) defines an experimental separate sender/recipient group, independent contribution identities and authenticated private-reply role. Its exact capability and disclosure versions must be supported before use; otherwise hold the protected delivery or use an explicitly permitted alternative. It never hides members inside the visible MLS group.

### Historical alternate addresses

A receiver MUST NOT transfer recipient identity, verified keys or capability history to an ASCII address merely because an RFC5335-era header presents it as an alternate. New delivery uses current SMTPUTF8 and internationalized-header rules. Any alternate destination requires its own identity and delivery-policy evaluation; it cannot silently receive content protected for the original recipient. Historical display recovery MUST NOT automatically add the recovered alternate to reply or reply-all targets. See the [historical internationalized-header audit](audits/internationalized-header-history.md).

::::

:::: {.details summary="Preserving confidential headers in replies"}

### Replies preserve protected header confidentiality

For an RFC9788 message, reply and reply-all recipients MUST be derived from the protected header fields. An outer Reply-To, Cc or other recipient hint MUST NOT add an audience member, even when the client knows an encryption key for that address. The From display exception for an unbound inner sender does not authorize replying to the outer address.

Confidential header values remain confidential when used to compose a reply or forward. This includes derived values such as a reply subject, references derived from a protected Message-ID, and addresses copied into a new destination field. Applying the client's default header policy alone is insufficient: the client must account for the referenced message's protected record of what its author exposed. It MUST NOT infer that record from mutable outer headers.

User editing does not automatically remove this provenance. Adding a reply prefix or changing part of a confidential subject must not cause the rest of that subject to appear in cleartext because an exact-value lookup no longer matches. A transition to plaintext delivery requires the existing explicit disclosure decision to cover the inherited confidential header values as well as the body. The draft must show the resulting audience and exposure before that decision is applied.

These requirements follow [RFC9788 Sections 6.1–6.2](https://www.rfc-editor.org/rfc/rfc9788.html#section-6). Its ReferenceHCP algorithm supplies a starting point for automatically generated fields; the implementation must also track derivation through subsequent edits. The [base audit and section ledger](audits/header-protection.md) are complete; dependency review remains in progress.


For the RFC9788 composition path, compute the final outer-header values, including inherited reply confidentiality, before constructing legacy display elements. Derive the decorative list from the final fields that were removed or obscured, and include it only in eligible main body parts inside encryption. This resolves the difference between RFC9788's local-policy-only list construction and its Appendix D.2.2.1 worked reply; the [audit evidence](audits/header-vector-checks.md) records that interpretation separately from the source text.

::::

## Delivery reports do not change permission

A refusal or missing receipt does not prove that someone lacks encryption support. It cannot authorize plaintext, hosted access or a different recipient. Keep each recipient's delivery result separate and apply the sender's existing policy.

:::: {.details summary="Rejections, retries and legacy receipt semantics"}

### Rejection is not downgrade authority

An SMTP/LMTP refusal, Sieve rejection, DSN or MDN MUST NOT by itself authorize changing an intended principal or sending previously protected content through plaintext or hosted fallback. Apply the sender's existing policy and its required visible transition rules. Diagnostic reason text MUST NOT be interpreted as an executable instruction or an authenticated capability advertisement. Temporary 4xx responses retain retry semantics and do not prove that an endpoint lacks encryption support. Track recipient-specific outcomes without converting mixed delivery into universal success or failure. See the [Sieve rejection audit](audits/sieve-rejection.md).

### Historical receipt semantics

A legacy disposition report MUST NOT establish reading comprehension, consent, structured-answer submission, device-key possession or irreversible deletion. Its absence MUST NOT trigger an encryption downgrade or be treated as proof of client incompatibility. Manual message action and manual permission to send a report are distinct report modes, not authorization for an Email/2 operation.

Use RFC8098 for current MDN generation rather than copying contradictory removed disposition values from RFC3798. Preserve unknown historical reports for inspection without synthesizing actions or error-response loops. See the [historical MDN audit](audits/mdn-history.md).

::::

## Required verification

Conformance fixtures must cover remembered policy, a stripped advertisement, mixed recipients, Bcc grants, partial transport acceptance, retries after key changes, host failure, link forwarding, scanner prefetch, expiry, revocation, account recovery, forged bearer replies and quoting old content into a new audience. Test evidence must identify which access model and security profile were exercised.

This chapter owns policy and disclosure behavior. The [security profile](security-profile.md), [hosted-access contract](hosted-access.md) and [protected private-copy contract](private-copies.md) own the selected algorithms, wire formats and access boundaries. Implementers must name the profiles they support and their tested limits; the policy alone is not a complete secure-delivery implementation.
