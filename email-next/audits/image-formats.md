---
title: Images, orientation and color
sectionNav: true
---

# Images, orientation and color

A photograph should appear upright, and a pale grey image should not become white because its samples were clipped. Supporting PNG and JPEG therefore means more than recognizing a filename or returning pixels. The [presentation profile](../presentation-profile.md) requires decoding, orientation and color interpretation inside the image-processing boundary. The authenticated resource remains unchanged.

> [!note] Specification and experiment
> The rules below define the proposed presentation behavior. The isolated decoder implements the selected static PNG and common JPEG path, including primary-image orientation and SDR color conversion. Its focused vectors establish local implementation behavior; they do not establish complete codec conformance or independent rendering agreement.

## Keep image interpretation inside the boundary

Authenticate the complete resource, check its declared type against its actual format, and decode it without network access. Apply limits to encoded data, dimensions, decoded pixels, metadata, working memory and processing time. A small compressed file can require substantial work. Metadata parsing and color transforms share those limits; they are not a second unrestricted processing path.

This profile deliberately uses explicit client-local resource budgets rather than one universal encoded-byte or pixel quota. Before accepting decoder work, the client configures positive finite bounds for encoded bytes, width, height, pixel count, output bytes, metadata expansion, working memory and processing time. Check cheap bounds before allocation; enforce expansion/work limits while processing; check dimensions and output again after orientation and color conversion. Failure produces the same readable fallback. A conformance report states the chosen budgets and demonstrates the required format cases within them. A resource rejection does not establish that the format is unsupported, and a receiver must not advertise complete image support while disabling a required format. No particular attachment size is guaranteed to render on every recipient device. This is an explicit resource-policy choice of the proposed profile.

Only the finished raster and client-owned diagnostics cross into the message renderer. Comments, GPS data, thumbnails, profile descriptions and embedded application data do not become HTML, external requests or conversation instructions. Retaining the original attachment is separate from returning its metadata to the display process. An original can contain location information or invisible pixels even when the preview shows neither.

A corrupt or unsupported image leaves its alternative text and an accessible explanation. A receiver MUST NOT silently substitute an unmanaged image for a color-managed result, clip high-depth samples, or fetch another representation. This failure behavior is an Email/2 restriction; image standards permit differing degrees of recovery.

## PNG

The selected format is the [PNG Third Edition Recommendation, 24 June 2025](https://www.w3.org/TR/2025/REC-png-3-20250624/). Static PNG support includes all defined color-type/bit-depth combinations, palette and transparent-color processing, filter method 0, and both noninterlaced and Adam7 images. These requirements come from §§11.2 and 15.3.3; they cannot be replaced by testing one RGB8 fixture. Animation remains outside this presentation profile, including an `acTL` image with only one frame. Rejecting that animation rather than showing its static image is a deliberate profile restriction.

::: {.details summary="PNG decoding and compressed data"}

| Source | Consequence |
| --- | --- |
| §§5.1–5.6, 11.2 | Validate signature, chunk bounds/order and integrity; require the critical image structure. Unknown critical chunks cannot be ignored as though the intended image were understood. Unknown ancillary chunks need not be interpreted. |
| §§6–9 | Preserve sample order, palette values and alpha; reverse filters byte by byte and reconstruct Adam7 passes. Empty passes have no scanline filter byte. |
| §§10, 11.2.3 | Concatenate IDAT contents into one zlib stream. Chunk, scanline and compressed-block boundaries are independent. PNG compression method 0 means zlib method 8 with at most a 32 KiB window and no preset dictionary. |
| §§11.3.1, 13.12, 15.3.3 | Compare transparent-color values at original precision before reducing sample depth. Rescale a 16-bit sample to the display range; clamping every value above 255 is not rescaling. Preserve straight alpha separately from color conversion. |
| §§13.1–13.5, 15 | Distinguish malformed input from unsupported critical semantics and from resource exhaustion. PNG CRC and zlib checksums detect corruption; neither authenticates the sender. |

[RFC1950 §§2.1–2.3](https://www.rfc-editor.org/rfc/rfc1950.html#section-2) defines the zlib header, Adler-32 check and rejection rules. [RFC1951 §§3.1–3.3](https://www.rfc-editor.org/rfc/rfc1951.html#section-3) supplies stored, fixed-Huffman and dynamic-Huffman blocks, bit packing and backward references. Output limits apply during decompression, including compressed metadata; waiting for a final image-size check is insufficient. These are selected decoding dependencies, not a new compressor implementation or a gzip container.

:::

## JPEG interchange

The required common JPEG paths are self-contained, eight-bit grayscale or three-component images using baseline sequential or progressive Huffman-coded DCT. Support both JFIF and Exif interchange; requiring JFIF APP0 immediately after SOI would incorrectly exclude Exif's APP1-first layout. Tables needed by the image must come from that image, not a previous correspondent's decoder state. Other JPEG processes and component models need an explicitly supported compatibility path; a generic `image/jpeg` label does not settle their interpretation.

[ITU-T T.81](https://www.itu.int/rec/T-REC-T.81/en) defines the coding processes, markers, table use, byte stuffing, restart behavior and reconstructed samples. The selected review covers §§5–7; Annex A's image/sample and DCT definitions; Annex B's nonhierarchical interchange structure; Annex C's Huffman representation; Annex E.2; Annex F.2.1–F.2.3; and Annex G's Huffman progression rules. Its algorithms are delegated to an established decoder. This is not review of the arithmetic, lossless or hierarchical processes, nor a T.83 conformance result.

[ITU-T T.871 §§6–10](https://www.itu.int/rec/T-REC-T.871/en) adds JFIF's one/three-component interpretation, full-range YCbCr conversion, component positioning, APP0 structure and top-down viewing convention. Chroma subsampling and lossy reconstruction mean that decoded JPEG values need not equal the source photograph's original RGB values. It is inappropriate to require a byte-exact JPEG round trip or infer color fidelity from opaque alpha bytes.

## Orientation

For Exif-bearing JPEG and PNG, the receiver MUST apply one well-formed primary-image Orientation value, 1–8, before layout. This includes reflections as well as quarter-turn rotations. Missing Orientation means 1. A malformed, duplicated or conflicting primary orientation produces the image fallback rather than a guessed rotation; a thumbnail's orientation never controls the primary raster. Recheck width and height limits after a quarter turn.

This uses [CIPA Exif 3.1 §4.6.5.1.6](https://www.cipa.jp/e/std/std-sec.html)'s row/column meanings. Reading the primary IFD requires bounded TIFF-header/entry processing under §§4.5.2, 4.6.2 and 4.7.2. Offsets and counts remain inside the containing metadata; cycles or out-of-range references cannot authorize another read. Full camera metadata, thumbnail decoding, XMP, Flashpix and annotation processing are not selected by this orientation rule.

PNG §11.3.4.5 cautions that Exif can be historical and stale. Applying a valid primary Orientation to the received raster is therefore an explicit Email/2 presentation decision, not a PNG requirement or proof that the metadata is truthful. New generators SHOULD normalize the intended raster orientation before authentication and omit Orientation or set it to 1. A receiver never rewrites authenticated bytes to make that normalization appear original.

## Color interpretation

Receivers MUST interpret supported source color information before delivering display pixels. For PNG, use the highest-precedence understood color description under §4.3: cICP, then iCCP, then sRGB, then cHRM/gAMA. Supporting iCCP requires a bounded color-management implementation; copying its bytes into a preview or dropping them is insufficient. PNG's alpha is linear opacity and receives no gamma/color transform.

The common color-management path must handle applicable embedded ICC v2/v4 RGB or grayscale profiles, including ordinary photographic display profiles, and PNG gamma/chromaticity descriptions. Convert into the declared output color space before returning pixels; the experimental RGBA8 host uses sRGB. Do not apply a second source transform in the browser after that conversion. For the SDR RGBA8 path, a receiver may reduce reconstructed samples to eight bits using the PNG rescaling rule before an eight-bit color-management transform, after exact source-precision transparency checks. Record that quantization in its implementation report: it can lose precision and introduce banding, and does not establish a sixteen-bit color-management or proofing path. An eight-bit output interface does not limit valid PNG inputs to eight bits.

For incomplete PNG color descriptions, this profile assumes sRGB primaries when only gAMA is available, and the sRGB transfer curve when only cHRM is available. With neither description it assumes sRGB. These fill missing display information; they do not prove which color space the author used. A present unsupported cICP declaration instead produces an unsupported-color fallback rather than silently choosing a lower-priority description. That is stricter than PNG's permission to use the highest-precedence understood description.

For JPEG, interpret JFIF/Exif component and color declarations before color management. Reassemble embedded ICC APP2 segments by their declared sequence/count and reject missing, repeated or inconsistent segments. A valid applicable ICC profile takes precedence over the generic Exif color-space label. Untagged images use the client's documented sRGB display assumption; `Uncalibrated` is not evidence that the photographer actually used sRGB. New generators SHOULD convert to sRGB with consistent metadata before authentication for predictable baseline display.

These color-management requirements are Email/2 choices for usable rich messages. PNG permits ancillary information to be ignored, and JFIF promises only basic color fidelity. Neither permission establishes that an unmanaged preview meets this profile. Unsupported newer color encodings, invalid profiles or contradictory declarations require an explicit image fallback; a client may separately offer a clearly identified approximate preview. Such a preview cannot establish renderer conformance. HDR tone mapping and printer/proofing fidelity are not promised by the sRGB output path.

::: {.details summary="Color-management source boundary"}

The selected [ICC.1:2022](https://www.color.org/specification/ICC.1-2022-05.pdf) review covers the RGB/grayscale transform definitions as well as their container. It retains both matrix/TRC and lookup-table profiles; support is not reduced to whichever model a fixture happens to exercise.

| Selected source ranges | Behavior inherited by image color processing |
| --- | --- |
| §§4.3–4.14, 6.1–6.5 and Annex A.3–A.4 | Numeric encodings, D50 connection-space interpretation, XYZ/Lab conversion, rendering intents and precision conversion. Device sample scaling and legacy Lab scaling are different operations. |
| §§7, 8.1–8.4, 8.10 and the selected transform tags in §9.2 | Profile bounds, input/display classes, RGB/grayscale channel agreement, matrix/curve and AToB/BToA or DToB/BToD selection. Profile metadata cannot choose another destination profile or execute code. |
| §§9.2.4–9.2.5, 9.2.15, 9.2.30–9.2.32, 9.2.36, 9.2.46–9.2.47; §§10.6, 10.18, 10.22, 10.31; Annexes E and F | Colorant/white-point matrices, sampled curves, gamma and piecewise parametric curves, chromatic adaptation, and monochrome/RGB computational models. A zero-entry curve means identity; a one-entry curve means a gamma exponent, not its inverse. |
| §§10.10–10.13 | `mft2`, `mft1`, `mAB ` and `mBA ` table layouts, channel order, grid dimensions, precision, process order and clipping. Stored element order is not necessarily evaluation order. LUT-based profiles remain part of the selected path. |
| §10.16 | `mpet` channel-connected processing chains, segmented curves, matrices and floating-point CLUTs. An unknown processing element invalidates that transform; it must not simply be skipped. The published §8.10 fallback to another complete supported transform remains permitted. |

For v2 compatibility, the selected historical definition is [ICC.1:2001-04](https://archive.color.org/files/ICC_Minor_Revision_for_Web.pdf), whose profile version is 2.4. The review covers numeric types (§5.3), headers/tag bounds (§§6.1–6.2), RGB/grayscale input/display models (§§6.3.1–6.3.2), their transform/colorant/curve/white-point tags (§6.4), curve/XYZ and `mft1`/`mft2` definitions (§§6.5.3, 6.5.7–6.5.8, 6.5.14, 6.5.26), and PCS/intent/precision rules (Annex A). This is a compatibility review of the latest v2 definition, not a new generation preference for obsolete profile versions. The [publisher's v2 guidance](https://www.color.org/v2profiles/) explains its remaining validity and recommends consistent white-point handling and avoidance of obsolete workflow tags.

One compatibility detail is particularly important: `mft2` uses the legacy Lab encoding, with L*=100 represented by `FF00`, even in a v4 profile. Other v4 Lab representations use the newer range. The color-management module must select the encoding from the actual tag and profile context; dividing every 16-bit value by the same constant would change colors. Profiles already express their connection to the D50 PCS. Applying chromatic adaptation again merely because a source image used D65 would duplicate a conversion.

The declared sRGB output is characterized by the [ICC sRGB registry](https://registry.color.org/rgb-registry/srgb) and its [profile interpretation note](https://registry.color.org/rgb-registry/files/sRGB.pdf): D65 primaries/white and the piecewise transfer function. The selected review includes its four pages, with the distinction between published sRGB encoding and the note's additional profile-making interpretation. This is not a full IEC61966-2-1 or physical-display measurement audit. Device calibration, observer measurements and proofing are not performed by this image adapter.

The local adapter uses the public Pillow ImageCms interface to an established color-management module: accepted RGB/grayscale input/display profiles are converted to a client-created sRGB destination, using the embedded profile's valid rendering intent. It does not request proofing or black-point compensation. Its input/output interface can quantize to eight bits without replacing the source profile's LUTs with a hand-written matrix. Profile acceptance, actual transform selection, malformed-input handling and interpolation accuracy still need implementation evidence; reading these source definitions does not certify LittleCMS or every accepted profile. The source review covers the standard transform families reached by this path, not unrelated printer, named-color, DeviceLink or iccMAX workflows.

The [ICC embedding technical note](https://www.color.org/technotes/ICC-Technote-ProfileEmbedding.pdf), JPEG section, defines the APP2 identifier and ordered segmentation. Its older PNG-version discussion does not replace PNG Third Edition. The selected [tag](https://registry.color.org/tag-signatures/) and [type](https://registry.color.org/type-signatures/) registry entries agree with the AToB/BToA, curve, XYZ and LUT identifiers used here; registration is not validation of a particular embedded profile.

Source cautions remain explicit. ICC.1:2022 contains outdated internal section references, and its Curve Set table prints a hexadecimal value inconsistent with the `cvst` label; neither supplies a new wire identifier. Its current parametric-curve equations supersede the different 2010 table. The sRGB interpretation note prints `12.02` for one blue-channel inverse expression, inconsistent with its own forward expression and the registry's shared `12.92` function. This audit does not adopt that isolated value as a channel-specific transfer rule.

The publisher's [current specification list](https://www.color.org/icc_specs2/) records the [April 2025 Adaptive Gain Curve amendment](https://archive.color.org/specification/ICC.1_Adaptive_Gain_Curve.pdf). Its header and Annexes 1–2 distinguish the adaptive transform from a backward-compatible AToB approximation at a declared target headroom; Annex 2.4 recommends SDR headroom 1.0 for that approximation. An ordinary complete SDR transform does not become invalid merely because an optional newer rendering method exists. A receiver must nevertheless establish a supported complete SDR path or use the unsupported-color fallback, rather than assume an ignored adaptive tag has been applied. ICC's own `cicp` tag (§§9.2.17, 10.3) must describe an encoding equivalent to the profile; it does not automatically replace its transform. This differs from choosing among PNG color-description chunks. HDR conversion through the adaptive function remains outside this adapter's selected SDR path. Profile descriptions, creator fields and profile IDs are not authorship or trust evidence.

:::

## Corrections and evidence limits

The PNG Third Edition's [published errata](https://www.w3.org/2025/06/REC-PNG-20250624-errata) lists a proposed correction to hexadecimal values in an mDCV example. It does not change the selected static-image decoding rules. T.871's March 2013 erratum corrects the ISO publication year in page headers. The T.81 publisher record lists a January 2004 patent-information corrigendum; no changed decoding rule is inferred from that title.

RFC1950's all-status listing has no errata. RFC1951 lists Reported records [7764](https://www.rfc-editor.org/errata/eid7764) and [8429](https://www.rfc-editor.org/errata/eid8429): extra-bit ordering wording and a zero-distance-code-length description. They remain unapproved reports. Use the operative bit-packing and code-length rules together, not a novel codec amendment derived from either report. Current Exif 3.1 follows the corrected 2024 Exif 3.0 publication; the selected primary orientation/header meanings were checked in the current edition.

The [isolated decoder](../evidence/README.md#isolated-image-decoding) returns sRGB RGBA8 with adjustable limits. Forty-two focused tests cover the existing decoder/resource boundary and selected fidelity cases: every valid PNG depth/type and interlace combination, source-precision transparency before sample reduction, Exif orientation, common JPEG interchange, ICC transforms, PNG gamma/chromaticity and malformed metadata. These are selected functional vectors. Comprehensive malformed-input and fuzz coverage, complete codec conformance, independent color-management agreement and hard memory isolation remain unproven. The [source fingerprints](image-format-sources.json) identify the consulted captures; the section ranges above delimit their review scope. No full PNG, JPEG, Exif, ICC or codec implementation certification is claimed.
