---
title: TLS service identity audit
sectionNav: true
---

# TLS service identity audit

For the selected HTTPS button service, construct one DNS-ID reference from the already authorized service origin's host and match it against a dNSName subjectAltName in the server's leaf certificate. RFC9525 requires reference identities to be constructed independently of the server's certificate. Certificate matching is necessary, but does not establish certificate-path validity, service authorization or a mailbox identity.

## Service-profile mapping

Use the exact validated host in the authenticated descriptor and independently configured service binding. Do not replace it with a CNAME, resolved address, redirect destination, certificate-selected name, mailbox domain or provider brand. The selected no-redirect policy remains intact. A name match for an attacker-chosen destination does not authorize sending a bearer token there.

The current service grammar permits DNS hosts and excludes IP literals. The profile supports DNS-ID alone and excludes SRV-ID, URI-ID and IP-ID for this service. HTTPS URLs do not imply URI-ID certificate matching: RFC9525§4.2/6.1.2 use DNS-ID for ordinary HTTPS. The certificate does not validate the descriptor's path, port, action or token audience; those remain exact application bindings.

Compare domain labels using case-insensitive ASCII after proper IDNA processing. Certificates contain A-labels, not U-labels. The service's ASCII spelling requirement does not make an arbitrary xn-- string a valid A-label. Existing experimental A-label refusal remains an implementation gap; this review does not close IDNA5890/5891 or their character/context dependencies. Safe displayed origin text is also separate from certificate comparison.

The service selects RFC9525's default wildcard matching: exactly one wildcard, comprising the complete leftmost label, matching exactly one label. For example, *.service.example matches api.service.example but not service.example or x.api.service.example. Partial-label and multi-wildcard identifiers are invalid and ignored. Public-suffix wildcard defense is expressly outside this RFC; do not claim it follows from the syntax rule alone.

Do not use Common Name or any other subject RDN as a fallback. On mismatch, keep the service request unsent. RFC9525§6.6 allows carefully controlled advanced-user overrides; a fail-closed credentialed-service policy is a proposed application restriction, not a claim that the RFC universally forbids all overrides.

## Mail and identity boundaries

RFC7817 addresses mail submission/access certificate identity and its earlier6125-based rules; it is not the HTTPS action-service profile. Its SRV-aware account-domain/host relationships do not authorize accepting those alternative names for this HTTPS service. Its historical optional CN fallback must not be carried into a new9525-based profile. A future mail-provider adapter must reconcile its actual discovery and reference-name policy separately. Neither9525 nor7817 proves correspondent mailbox ownership, device authority, MLS membership or token-to-principal association.

RFC9525 explicitly leaves complete PKIX path validation, expiry, revocation, extended key usage and name constraints to5280 and applicable policy. That work remains open. ALPN/SNI and fleet deployment also remain separate dependencies; a shared certificate can expand the impact of a weaker sibling service.

## Coverage

All1440lines/25pages, every example, both reference lists, AppendixA and end matter read in three bounded chunks. Official metadata: obsoletes6125, no later updates/replacement listed. Live official errata search returned one held editorial erratum8173 correcting the SIP example reference from third to fourth; no new security rule follows. No certificate validator or live deployment was tested as part of this source review.

| Section | Disposition |
| --- | --- |
| front | Fullabstract/status/copyright/contents read. |
| 1 | Introduction boundary read. |
| 1.1 | Reference versus presented identity motivation; successor6125. |
| 1.2 | Leaf names only; fullpath/extensions/revocation governed byPKIX and not closed bythisreview. |
| 1.3 | SAN-only DNSidentity, completeleftmostwildcard, noCN; entire overviewread. |
| 1.4 | Scope boundary read. |
| 1.4.1 | TLSfamily/PKIX/derivedcredential scope read; no newQUIC/DANEfeature selected. |
| 1.4.2 | All exclusions read: clientidentity, paths/query, CApolicy,DNSresolution,UI remain external. |
| 1.5 | All terms andBCP14 read; DNS/IP/SRV/URI types distinct; TLSroles notapplicationroles. |
| 2 | Allidentifiercategories andSVCBdiscussion read. CN/otherRDN forbidden; DNSresolvedIP notreference; crossprotocolrisk. |
| 3 | Protocol mustselecttypes; noSRVwithoutdiscovery; URIuse≠URI-ID; explicitwildcardpolicy; IPclassification rules read. |
| 4 | Issuer instruction scope read. |
| 4.1 | Allsix cumulativeissuance rulesread; types scopedbyapplication. |
| 4.2 | Allwebsite/IP/IMAP/SIP/XMPP examplesread; HTTPS DNS-IDnotURI-ID. |
| 5 | AllCSR/minimalnames/crossprotocol/mailbundle guidance read; no certificateissuance implementationclaim. |
| 6 | Allverification steps read; namecheck distinctfromexpiry/revocation/pathchecks. |
| 6.1 | Reference construction scope read. |
| 6.1.1 | Independentreference list, trustedinputs, nointermediateDNSnames; no synthetic mix ofauthority; fullSIPexample read. |
| 6.1.2 | Allfiveexamples andnegativecasesread; held8173 corrects third→fourth SIP reference only. |
| 6.2 | Entire typedecomposition read; anymatchingpair, exactIP; domain/type jointlymatched. |
| 6.3 | ASCIIcaseinsensitive labels; U→A conversion; wildcardonecompleteleftmostlabel/one-labelmatch; invalidwildcardidentifier ignored. |
| 6.4 | FullIP comparison rulesread; IP-ID excludedbyselectedserviceorigin grammar. |
| 6.5 | Fullcombinedname/service example read; nevermix componentsacrossreferences; typecaseinsensitive. |
| 6.6 | Usematchedreference asidentity; defaultfailure andoptionaladvancedoverridesread. Servicebearerprofile shouldfailclosedwithout just-in-timeoverride. |
| 7 | Security chapter scope read. |
| 7.1 | Wildcardrisk/strictTLS/XSS/publicsuffixboundary read; no automaticpublicsuffixsafetyclaim. |
| 7.2 | URI-ID scheme/hostonly; othercomponentsignored; servicepath/portpermissions notcertified. |
| 7.3 | A-labelmatching only; visualhomograph safetyseparate. |
| 7.4 | SNI DNSnamesonly; exactIPclassification preventsconfusedcomponents; DNSresolvedIPnotauthority. |
| 7.5 | MultipleSANnames expandcompromisescope; consistentfleetcontrols required. |
| 7.6 | Nameconstraints applybyform; acceptingextraidentifierforms canexpandtrust. |
| 7.7 | TrustedCA/name match notendorsement ofservicebehavior oractionauthority. |
| 8 | NoIANAactions. |
| 9 | Bothreferencelists read. |
| 9.1 | Every normativecitationread;5280/IDNA/URI/DNS/SRV dependencies notrecursivelyclosed. |
| 9.2 | Every informativecitationread; optionaltechnologies andhistoricalreferencesnotselected. |
| A | Allchangesfrom6125read;CNremoval andIP-IDaddition distinguishedfrom7817historicalbehavior. |
| Acknowledgements | Complete text and author/endmatter records read. |
| Contributors | Complete text and author/endmatter records read. |
| Authors' Addresses | Complete text and author/endmatter records read. |

Sources: https://www.rfc-editor.org/rfc/rfc9525.txt ; https://www.rfc-editor.org/rfc/rfc9525.json ; https://errata.rfc-editor.org/search/?rfc_number=9525
