---
title: Authentication status codes audit
sectionNav: true
---

# Authentication status codes audit

**Coverage:** complete eight-page [RFC 7372](https://www.rfc-editor.org/rfc/rfc7372.html), including registrations and end matter. No entries occur in the retrieved errata dataset. The [IANA registry](https://www.iana.org/assignments/smtp-enhanced-status-codes/) entries X.7.20 through X.7.26 agree with the recorded assignments, checked 19 October 2026. General status-code and authentication dependencies remain open.

## Finding

Authentication rejection is not evidence that a recipient address is invalid. Distinguish an evaluated failure, an evaluation error and a passing signature rejected by local policy. A single diagnostic may omit other causes, and a generic response may intentionally conceal policy details.

| Section | Disposition |
| --- | --- |
| 1 | Adds diagnostic codes for authentication-related local policy rejection/deferral; updates7208 reporting, not the underlying authorization result. |
| 2 | Requirement vocabulary reviewed. |
| 3 | Registers seven distinct enhanced status details, not new SMTP commands. |
| 3.1 | Distinguishes no passing DKIM signature(X.7.20), passing but locally unacceptable(X.7.21), and author-match policy failure(X.7.22). All associate550. Registration does not endorse rejecting all unsigned mail. |
| 3.2 | SPF fail X.7.23 associates550; evaluation error X.7.24 associates451/550. Error is distinct from an evaluated fail and can be temporary or permanent. |
| 3.3 | Reverse DNS policy failure X.7.25 associates550; not a mailbox-invalid result. |
| 3.4 | Multiple authentication failures X.7.26 associates550 without identifying which checks failed. |
| 4 | One returned detail need not be the only or principal failure. Prefer multiple-failure code when appropriate. Do not remove list recipients as invalid solely for authentication failures. Future technologies should register distinct codes. |
| 5 | Detailed diagnostics disclose local policy; generic codes remain permitted. Absence of a detailed code does not prove absence of a check. |
| 6 | Registers codes from section3; live IANA X.7.20–26 checked and consistent. |
| 7 | 3463,5248,baseDKIM,SPF and Authentication-Results successors remain dependencies. |
| Appendix A | Acknowledgements and author address reviewed. |

| Front matter | Abstract, status and copyright reviewed. |

## Email/2 consequence

Keep the SMTP outcome, enhanced diagnostic and application security state separate. Explain an authentication-policy rejection as a reported delivery condition. Do not label the recipient nonexistent, delete a group member, revoke a correspondent key, or resend plaintext because of that condition.

A temporary SPF evaluation error can remain retryable under the transport contract. A permanent failure requires its applicable handling; it does not grant authority to weaken content protection. Do not invent a list of failed mechanisms from the aggregate multiple-failure code.

Required cases include passing-but-unacceptable DKIM, missing signatures, SPF fail versus evaluation error, temporary versus permanent error, generic diagnostics, multiple failures and mailing-list bounce processing. No SMTP diagnostic parser or live delivery behavior has been tested here.
