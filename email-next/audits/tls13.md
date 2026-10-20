---
title: Current TLS 1.3 audit
sectionNav: true
---

# Current TLS 1.3 audit

RFC9846 preserves TLS1.3 wire compatibility while tightening implementation requirements. Email Next can retain its selected HTTPS minimum of TLS1.3 and disabled early data. This review does not establish that any chosen TLS library or deployment implements the new requirements.

## Service consequences

The application must specify service identity verification, not merely request encryption (§1). Validate the intended origin through the selected certificate/hostname policy; SNI is not independent authority. TLS termination creates two connections with separate security properties (§9.3). Neither certificate authentication nor handshake completion supplies the service's answering-principal authorization or business receipt.

Keep service requests out of early data. AppendixF.5 requires an application profile before0RTT use and requires explicit application opt-in for sending/accepting and retransmission. Application retry deduplication remains necessary even with1RTT (§8). TLS errors, transport EOF and close_notify do not prove a business operation was rejected or completed; HTTP framing and a complete matching receipt remain necessary.

For a selected library, check fresh generated key shares across connections (§4.3.8), key-update/close before key usage limits (§5.5), sender epoch bounds (§4.7.3), strict state/encoding/extension handling, and normal certificate/Finished verification. Receiving implementations must permit peer key-share reuse for8446 compatibility and must not enforce the sender epoch cap. Do not invent application-side rejection of peers contrary to those rules.

Resumption must preserve the original authenticated server identity constraints (§4.7.1), appropriate ticket lifetime and cumulative key lifetime policies. A ticket's wire maximum is seven days; this is separate from the proposed MLS package lifetime. PSK-only resumption lacks the asymmetric exchange's forward secrecy. Avoid tickets across deliberately isolated application contexts (AppendixC.4). Ordinary KeyUpdate does not recover after a traffic secret is compromised; a fresh asymmetric handshake is needed (AppendixF.2). Disabling static RSA on shared-key legacy endpoints also matters toTLS1.3 security (AppendixF.10).

TLS exposes length/timing and may expose connection identifiers. TLS1.3 does not itself promise anonymous contacts, mailbox verification, MLS admission, or post-compromise recovery of Email Next history. ECH, externalPSKs, rawpublickeys, clientcertificates and new exporters are not selected merely because the RFC describes them.

## Source issues and errata

Captured errata include verified9040 (obsolete-version negotiation example), reported9042/9043 (duplicateTLS1.1 wording issue), reported9157 (capitalization), and reported9161 (CertificateRequest syntax versus required extension). Only9040 is verified. Base§4.4.2 still requires signature_algorithms even though its vector syntax permits zero length. The official errata listing on 20 October 2026 matches all five captured records and statuses.

RFC9963's full review resolves the support-versus-use distinction. Its optional legacy client CertificateVerify algorithms do not remove general RSA-PSS implementation support in§9.1, and9963§4 explicitly retains PSS for TLS1.3 RSA servers. The broad§1.2 summary must not be interpreted as removing all PSS requirements. This is a limited client-key exception, not a defect finding or an accepted erratum. The configured bearer service does not select this client-certificate feature.

## Coverage and remaining scope

All7397 source lines/137pages, every structure, diagram, example, table, reference, appendix and end matter read in15 bounded chunks. Official metadata lists no later updates and obsoletes8446/5246/5077/6961/7627/8422, updating5705/6066. Dependencies, live registry reconciliation and deployed TLS acceptance evidence remain open. No TLS implementation or deployment tests were performed.

| Section | Disposition |
| --- | --- |
| front | Complete abstract/status/copyright/contents read. |
| 1 | Application must define handshake and identity verification; TLS channel is not mailbox or action authorization. |
| 1.1 | All terminology and BCP14 read. |
| 1.2 | All8446 changes read. RFC9963 review resolves PSSsummary as limited optional legacyclient signing exception, not removal of general support or RSAserverPSS requirements. |
| 1.3 | All TLS1.2 differences read; AEAD suites separate authentication/key exchange; no automatic privacy guarantee. |
| 1.4 | TLS1.2 changes conditional; no new1.2 support requirement. |
| 2 | Complete handshake flow and authentication phases read; server data before client Finished not client identity/liveness proof. |
| 2.1 | Retry diagram and unchanged initial transcript coverage read. |
| 2.2 | Both resumption diagrams read; PSK-only loses forward secrecy; external passwords unsafe. |
| 2.3 | Full0RTT diagram read; no assumed forward secrecy or cross-connection replay protection. |
| 3 | Complete presentation syntax introduction read. |
| 3.1 | Byte and network ordering read. |
| 3.2 | Opaque and alias syntax read. |
| 3.3 | Unsigned integer widths and numerical example read. |
| 3.4 | All fixed/variable vector examples read; byte lengths and divisibility distinct from element counts. |
| 3.5 | All enum examples/ranges read; extensible unknown values handling. |
| 3.6 | Constructed types and scoped fields read. |
| 3.7 | Fixed-value syntax read. |
| 3.8 | Full variant example read. |
| 4 | Handshake enum/union and mandatory ordering read; library responsibility. |
| 4.1 | Exact transcript and synthetic message_hash construction read; posthandshake context boundaries. |
| 4.2 | Key exchange scope read. |
| 4.2.1 | All four negotiation option sets read; PSK/certificate and supported group choices distinct. |
| 4.2.2 | All ClientHello fields and retry exceptions read; legacy_version not negotiatedTLS version; compression null. |
| 4.2.3 | Full ServerHello structure, HRR random and downgrade sentinel octets read; reported9042/9043 do not permitTLS1.1. |
| 4.2.4 | One retry, actual change, version/cipher consistency and PSK hash rules read. |
| 4.3 | Entire extensions enum/table and rules read; duplicates/trailing data/unsolicited responses rejected as specified; registry snapshot notlive audit. |
| 4.3.1 | Offered versions govern selection; service minimum1.3 remains application choice. |
| 4.3.2 | Cookie reflection and stateless CCS handling read; not browser cookies or service authorization. |
| 4.3.3 | Every signature scheme, encoding andcompatibility rule read; certificate signatures distinctfromCertificateVerify;9963optionallegacyclient exception separately reviewed. |
| 4.3.4 | CA distinguished-name selection hint read; no substitute for trust validation. |
| 4.3.5 | All OID matching rules read; optional client certificate selection notservice grant. |
| 4.3.6 | Posthandshake authentication must be offered; no ambient client certificate added to service baseline. |
| 4.3.7 | All named groups/preferences/duplicate rules read; unauthenticated preference cannot be used early. |
| 4.3.8 | All client/server/retry shares read; sender MUST NOT reuse across connections, receiver MUST permit peerreuse for8446 compatibility. |
| 4.3.8.1 | FFDH fixed-width padded public values and rangevalidation read. |
| 4.3.8.2 | Curve formats/coordinates and validation read; X25519/X448 lengths; no pointformat negotiation. |
| 4.3.9 | Both PSK modes read; offeredmode restriction and extension requirements. |
| 4.3.10 | Full early-data acceptance/rejection paths and ALPN/version/cipher matches read; client replay decision belongs to app. |
| 4.3.11 | All identity/binder fields and checks read; PSK last, hashcompatible, correctindex. |
| 4.3.11.1 | Ticket lifetime vs obfuscated millisecondage and modulo arithmetic read. |
| 4.3.11.2 | Exact truncated transcripts and HRR hash distinction read; cryptographic library scope. |
| 4.3.11.3 | Deadlock-preventing serverflight order read. |
| 4.4 | Encrypted server parameter context read. |
| 4.4.1 | Required order and forbidden extension handling read. |
| 4.4.2 | CertificateRequest structure and signature_algorithms requirement read; syntactic emptyvector not semanticpermission, reported9161. |
| 4.5 | Complete authentication input table read; context/keys differ for server/client/posthandshake. |
| 4.5.1 | Full certificate union, chain order, optional rawkey and OpenPGPreserved rules read; rawkey not selected. |
| 4.5.1.1 | Per-certificate OCSP/SCT carriage read; status_request_v2 deprecated; dependentvalidation open. |
| 4.5.1.2 | Certificate selection rules and fallback chain distinction read; SNI guidesselection notauthentication. |
| 4.5.1.3 | Chain validation external; emptyserverchain invalid; unauthenticatedclient allowed byTLS notautomatically serviceauthorized. |
| 4.5.2 | Complete signature context and hexexample read; proofpossession notapplicationgrant. |
| 4.5.3 | Finished calculation and exceptions read; verificationrequired; subsequentrecords appropriateapplicationkey. |
| 4.6 | Early-data endmessage ordering/keying read; earlydata disabled selectedprofile. |
| 4.7 | Posthandshake message context read. |
| 4.7.1 | All ticket fields/formula read;7daywiremaximum; validoriginalcertSNI; cumulativekeylifetime bounds recommended; noresumptionclients ignoretickets. |
| 4.7.2 | Optional posthandshake auth delayed/interleaved responses read; notbaselineclientauth. |
| 4.7.3 | KeyUpdate state/flags crossedflights read; sender epoch<=2^48−1, receiver mustnot enforce; no repeatedrequested beforepeerupdate. |
| 5 | All CCS acceptancewindow and recordtype checks read. |
| 5.1 | Fragmentation/alignment/alert/application rules read; records are notHTTPmessage boundaries; legacyrecordversion notnegotiation. |
| 5.2 | All AEAD structures/formulas/bounds read; authenticationfailure fatal. |
| 5.3 | Perdirection counters/XORnonce/rekeybeforewrap read. |
| 5.4 | Zero padding/scanning limits read; no claim traffic anonymity. |
| 5.5 | MUSTclose/keyupdate beforelimits; AESGCM2^24.5fullrecords; receivers SHOULDNOT enforce evolvinglimits. |
| 6 | Complete alert enum and fatal behavior read; discardfailedsecrets exceptconditionalPSKretention. |
| 6.1 | Halfclose/truncation/usercanceled read; EOFalone notcomplete receipt. |
| 6.2 | Every error meaning read,includinggeneral_error; notapplicationrejection evidence. |
| 7 | Keycomputation introduction read. |
| 7.1 | Complete keyschedule diagram/formulas read; renamedmain preserves wirelabels; secret erasure recommended. |
| 7.2 | Trafficsecret evolution/deleteold read; no postcompromise recovery byKeyUpdate alone. |
| 7.3 | All traffic key/IV derivation andtable read. |
| 7.4 | Sharedsecret chapter boundary read. |
| 7.4.1 | FFDH secret leftpadding differs fromTLS1.2. |
| 7.4.2 | ECDH leadingzeros and X25519/X448 allzerorejection read. |
| 7.5 | Exporter formula/context distinction read; normalexporter default,earlyseparate; no Email Next channelbinding invented. |
| 8 | Replayclasses and distributed-instance constraints read; application retrydedup required independently ofTLS. |
| 8.1 | Singleuseticket database tradeoff read; notMLSKeyPackage allocation. |
| 8.2 | Full ClientHello replaystore, validatedkey, Bloomfilter, zones/startup handling read. |
| 8.3 | Complete freshness arithmetic and examples read; clockwindowalone notantireplay; example10seconds notprofilequota. |
| 9 | Compliance chapter boundary read. |
| 9.1 | AES128GCM/P256/signature MTIs read; SHA384/ChaCha/X25519 recommendations. GeneralPSSsupport coexists with9963legacyclientkey exception; RSAserver stillPSS. |
| 9.2 | All MTI and conditionalextension rules read; librarycapabilities versus applicationusage distinct. |
| 9.3 | All endpoint/middlebox invariants read; terminatingproxy creates two separate securityconnections. |
| 10 | Security references read withall appendices. |
| 11 | All registry policies/assignments read; currentIANAstate notindependentlyreconciled. |
| 11.1 | Every new registrychange read; general_error117 andextended_main_secret naming. |
| 12 | Both fullreferencelists read. |
| 12.1 | Every normativecitation read; transitive contents notrecursively audited. |
| 12.2 | Every informativecitation read; includes9963/9849/9525; research notindependentlyvalidated. |
| A | Statemachine notation read. |
| A.1 | Complete clientdiagram andalertkey note read. |
| A.2 | Complete serverdiagram includingearlydata/emptyclientcertificate paths read. |
| B | Normativestructures introduction read; reservedvalues notsendable. |
| B.1 | All record structs reread. |
| B.2 | Entire alert enum includingreservedvalues read. |
| B.3 | Entire handshake enum/union read. |
| B.3.1 | All ClientHello/ServerHello/extensions/share/PSK structs read. |
| B.3.1.1 | Version extension union read. |
| B.3.1.2 | Cookie extension vector read. |
| B.3.1.3 | Entire signatureenumincludingreservedranges read. |
| B.3.1.4 | Entire groupenum/obsoletecurveprohibition read. |
| B.3.2 | All serverparameterstructs read includingemptyextensionbounds. |
| B.3.3 | Complete certificate/verify/finished structs read. |
| B.3.4 | Full ticketstruct read. |
| B.3.5 | Endearlydata andkeyupdate structs read. |
| B.4 | Both fulltables andfiveciphercodepoints read; suitesnotcrossversioninterchangeable. |
| C | Implementationnotes introduction/vectorreference read. |
| C.1 | CSPRNG/source-separation/randomnessaugmentation read; reuseestablishedlibrary. |
| C.2 | Trustanchor/revocation/keystrength/applicationroleambiguity read. |
| C.3 | Every protocolandcryptographicpitfall read; notanexecutedTLS test suite. |
| C.4 | Ticketreuse/crosspartitioncorrelation/externalidentity privacy read; avoidmailbox PSKlabels;ECHnotselectedbycitation. |
| C.5 | Uncheckedcert/rawkey unauthenticatedoperation risk read; no bearerHTTPS bypass. |
| D | AllTLS1.2termrenames read; PRFlabels unchanged. |
| E | Fullbackwardcompatibilityintro read; legacyrecordversion distinctfromTLSversion. |
| E.1 | Older-server negotiation andretrydowngraderisk read; service rejectsbelow1.3. |
| E.2 | Older-client example read withverified9040 correction; noTLS1.0/1.1permission; no requirement to add1.2support. |
| E.3 | 0RTT older-serverfailure andfleetuniformity read. |
| E.4 | Allmiddleboxcompatibilityrules read; dummyCCSnotTLS1.2downgrade. |
| E.5 | Allprohibitions read;SSL/TLS1.0/1.1/RC4/weakciphers forbidden; avoidstaleE.2example. |
| F | Securityanalysisscope read. |
| F.1 | Allproperties/compromisecases read; erasure prerequisite andPSK-only caveat; noMLSequivalence. |
| F.1.1 | HKDFordering/collisionlength rationale read. |
| F.1.2 | Clientcannot infer serverauthacceptance; applicationconfirmationrequired. |
| F.1.3 | Earlydatasecuritylimits read. |
| F.1.4 | Exporterindependence/erasure read. |
| F.1.5 | Longtermkeycompromise nothealedbyTLS alone. |
| F.1.6 | Allhandshakeanalysisreferences read, notreproved. |
| F.2 | Allrecordproperties read; newasymmetrichandshake needed aftertrafficsecretcompromise. |
| F.2.1 | Allrecordanalysisreferences read, notreproved. |
| F.3 | Length/timing/paddinglimitations read; noanonymityguarantee. |
| F.4 | Sidechannelresponsibilities extendaboveTLS. |
| F.5 | Every replayexample read; explicitapp0RTTprofile required; TLSmustnotenableorresend withoutapprequest. |
| F.5.1 | Earlyexporterreplay/channelbinding/keyreuse risks read. |
| F.6 | PSKidentityvalidityoracle read. |
| F.7 | CrossversionPSKdomainseparation caution read. |
| F.8 | MultipartyexternalPSKrerouting risks read; notselected. |
| F.9 | Rawkey/selfsignedidentitymisbinding read; notselectedHTTPSauthentication. |
| F.10 | StaticRSA elsewherewithsharedkey canimpersonateTLS1.3server; fleetkeyseparationreviewrequired. |
| Contributors | Complete contributor list read. |
| Author | Author record and end matter read. |

Sources: https://www.rfc-editor.org/rfc/rfc9846.txt ; https://www.rfc-editor.org/rfc/rfc9846.json ; https://www.rfc-editor.org/errata/rfc9846
