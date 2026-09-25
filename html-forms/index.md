---
title: HTML Forms
eyebrow: HTML Next · independent proposal
status: Unofficial Editor's Draft · Stage 0
pager: false
---

# HTML Forms Level 1

A form is an **author-owned submission scope**: it gathers named controls, validates them, and turns a deliberate submit into a request or dialog action. This proposal extends that durable model with the HTTP methods applications use, an explicit hierarchy for composing focused submissions into a larger workflow, and constraint validation for any element that has a value.

## The proposal

HTML forms already combine four useful platform concepts: **control ownership**, **constraint validation**, an explicit **commit event**, and **request construction**. This proposal develops that model in four focused areas:

1. **Expanded request methods.** Forms accept `query`, `put`, `patch`, and `delete` alongside `get`, `post`, and the non-network `dialog` action.
2. **Submitter-selected operations.** One set of controls can serve multiple endpoints and methods through the existing `formaction` and `formmethod` attributes.
3. **Composable submission scopes.** An outer form may opt into containing focused inner forms. Each submitter selects one scope, while the outer scope represents the complete workflow.
4. **Constraint validation on any element.** Validity, its reasons, and its author-facing surface extend from form controls to any element that has a value.
{.algo}

> [!warn] Open for review
> Review is requested on the method vocabulary, QUERY navigation behavior, the `composable` opt-in, aggregate validation and entry-list construction, implicit submission, reset behavior, accessibility exposure, the parser compatibility boundary, and which elements beyond form controls take part in a form's validation.

## Expanded request methods

The `method` attribute is an **ASCII-case-insensitive enumerated attribute** with lowercase canonical keywords. HTML source writes `method="patch"`, while request construction maps the selected keyword to the uppercase HTTP method. `patch` and `PATCH` both produce HTTP `PATCH`; the authored spelling is never passed through as the wire method.

```html
<form action="/api/posts/42" method="patch">
  <label>Title <input name="title" required></label>
  <button>Save draft</button>

  <!-- One control set can expose more than one operation. -->
  <button formaction="/api/posts/42/publish" formmethod="post">
    Publish
  </button>
</form>
```

| Keyword | Request semantics | Form data |
| --- | --- | --- |
| `get` | safe, idempotent retrieval | encoded into the action URL |
| `query` | safe, idempotent retrieval with request content | encoded as the request body with an explicit media type |
| `post` | resource-specific processing | encoded as the request body |
| `put` | replace resource state | encoded as the request body |
| `patch` | apply a partial modification | encoded as the request body |
| `delete` | remove the selected resource | encoded into the action URL, following the current WHATWG proposal |
| `dialog` | close the owning dialog | no network request |

The existing submitter overrides remain the operation-selection mechanism: `formaction`, `formmethod`, `formenctype`, `formtarget`, and `formnovalidate` let one button choose a different endpoint or operation while reusing the form's controls. The new network keywords apply to `formmethod` as well as `method`.

> [!norm] Lowercase authoring, uppercase HTTP
> The supported network keywords are `get`, `query`, `post`, `put`, `patch`, and `delete`. Parsing is ASCII-case-insensitive; the corresponding HTTP methods are `GET`, `QUERY`, `POST`, `PUT`, `PATCH`, and `DELETE`. A missing or invalid value retains HTML's existing `get` default. `dialog` remains a form action rather than an HTTP method.

## QUERY forms

RFC&nbsp;10008 defines `QUERY` for safe, idempotent requests whose query is too structured or large for a URL. Advanced search, report builders, map queries, and similar read operations can therefore carry form data as request content without adopting POST semantics.

```html
<form action="/api/reports" method="query"
      enctype="application/x-www-form-urlencoded">
  <label>Regions <select name="region" multiple>…</select></label>
  <label>From <input name="from" type="date"></label>
  <label>To <input name="to" type="date"></label>
  <button>Run report</button>
</form>
```

A QUERY submission constructs the successful-controls entry list, encodes it using the selected `enctype`, and places it in the request content. The request carries the matching `Content-Type`. History, reload, and retry behavior follow a safe, idempotent retrieval.

> [!warn] QUERY requires end-to-end support
> HTTP QUERY was standardized in June&nbsp;2026. HTML support is proposed in WHATWG HTML issue&nbsp;#12594 and is not yet part of the HTML Living Standard. Servers, proxies, caches, and security products also need to recognize the method. Implementations must surface an unsupported-method failure instead of silently changing QUERY into GET.

## Composable submission scopes

A complex workflow may need both a complete submission and smaller submissions within it: a shipping quote inside checkout, an address lookup inside account setup, or row-level actions inside a larger editor. A `composable` outer form declares one hierarchy containing those focused scopes.

```html
<form composable action="/checkout" method="post">
  <label>Postal code <input name="postalCode" required></label>

  <form action="/shipping/quote" method="query">
    <label>Delivery speed <select name="speed">…</select></label>
    <button>Update shipping quote</button>
  </form>

  <button>Place order</button>
</form>
```

The candidate ownership and submission rules are:

1. A control's nearest ancestor `<form>` remains its form owner. An explicit `form="id"` association overrides ancestry, as it does today.
2. Activating a submitter submits exactly its form owner. An inner submit validates and collects that inner scope.
3. Submitting the outer form collects the successful controls of its descendant form scopes in tree order. It performs one validation pass, one `formdata` construction, and one request to the outer action.
4. `requestSubmit(submitter)`, implicit Enter-key submission, reset, `form.elements`, and validity resolve against the selected scope. Operations on the composable outer scope include its composed descendants; operations on an inner scope remain local.
5. The `submit` event is dispatched for the selected form and bubbles normally through the DOM. Bubbling does not initiate another submission.
{.algo}

The `composable` opt-in belongs to the outer form because that author controls the aggregate request. Inner forms remain ordinary, focused submission scopes with their own action, method, validation, and submitters.

> [!warn] Parser compatibility requires incubation
> The HTML parser currently keeps one **form element pointer** and ignores a nested `<form>` start tag while another form is open. Changing every nested form would reinterpret existing malformed pages. The `composable` marker provides an explicit compatibility boundary: only an opted-in outer form admits nested form tokens, using a stack of active form scopes. Native support requires parser, submission, history, accessibility, and web-compat work with browser tests and implementation interest.

::: {#constraint-validation-on-any-element}

## Constraint validation on any element

HTML already has a real validation system, the **Constraint Validation API**. Each piece of it works; each stops at form controls. This proposal keeps every piece and extends it:

| Today | Where it stops | This proposal |
| --- | --- | --- |
| **Declarative constraints**: `required`, `pattern`, `min`/`max`, `step`, `minlength`/`maxlength`, `type`. | Only on `<input>`, `<select>`, and `<textarea>`. | Any element with a value can have validity. Other specifications can define where its constraints come from; [Declarative HTML Components](/html-next/validation) derives them from declared types. |
| **`ValidityState`**: `element.validity`, with flags such as `valueMissing`, `typeMismatch`, and `rangeOverflow`. | The set of flags is fixed. Every other failure goes into one catch-all flag, `customError`, with a single message. | An open list of reasons, each with a message and optionally a path to the failing part of the value. The native flags stay available for compatibility. |
| **The validity surface**: `checkValidity()`, `reportValidity()`, `validationMessage`, the `invalid` event, and `:valid`, `:invalid`, and `:user-invalid`. | Only on form controls and form-associated custom elements. | The same surface on any element that has validity, with its invalid state exposed to assistive technology as `aria-invalid` is today. |
| **Script-set errors**: `setCustomValidity(message)` on form controls, and `ElementInternals.setValidity(flags, message, anchor)` for form-associated custom elements. | An ARIA widget, a `contenteditable` region, or any element that is not a form control cannot set an error at all. | `el.setValidity(errors)` on any element with a value, for failures only the page knows about, such as a server reporting that a name is taken. |

```html
<!-- An ARIA widget has a value, so it can have validity -->
<div role="combobox" aria-required="true" id="assignee">…</div>

<script>
  const assignee = document.getElementById("assignee");
  // A failure the page knows about: a server answer, a business rule.
  assignee.setValidity([{ reason: "unavailable", message: "Ada is on leave." }]);
  assignee.validity;          // { valid: false, errors: [{ reason: "unavailable", … }] }
  assignee.validationMessage; // "Ada is on leave."
  assignee.setValidity();     // clear it
</script>

<style>
  [role="combobox"]:user-invalid { border-color: var(--danger); }
</style>
```

### Valid or invalid, with reasons

Validity is binary: a value satisfies its constraints or it does not. When it does not, it carries a list of reasons, because a value can fail more than one way. The vocabulary is open, so no failure needs a catch-all bucket.

```ts
el.validity            // { valid: boolean, errors: ValidityError[] }
el.validationMessage   // the first error's message, or ""
el.validate()          // recompute now → { valid, errors }; fires `invalid` if invalid
el.setValidity(errors) // add failures the element cannot derive itself
el.setValidity()       // clear them

interface ValidityError { reason: string; message: string; path?: string }
```

`validate()` generalizes `checkValidity()`: it returns the full result rather than a boolean. `setValidity(errors)` keeps the name `ElementInternals` already uses. Failures an element derives from its own constraints and failures set by script are reported together.

| Reason | When | Native flag |
| --- | --- | --- |
| `missing` | required, but empty | `valueMissing` |
| `type` | the wrong kind of value | `typeMismatch` |
| `range` | below the minimum or above the maximum | `rangeUnderflow` / `rangeOverflow` |
| `length` | shorter or longer than allowed | `tooShort` / `tooLong` |
| `pattern` | does not match a pattern | `patternMismatch` |
| `step` | off the step grid | `stepMismatch` |
| `unparseable` | cannot be parsed as a value at all | `badInput` |
| *any other reason* | a failure with no native flag | `customError`, for compatibility only |

### Computing validity, and showing it

These are different questions. **Computing** validity happens whenever the value changes, so `el.validity` is always current. **Showing** an error waits for interaction: CSS `:user-invalid` already means “invalid, and the user has interacted with it,” and it now applies to every element with validity. Submitting a form validates the form's controls and marks them interacted, as today.

> [!warn] Open: which elements a form validates
> A form owns its listed controls. Whether an ARIA widget or a `contenteditable` region inside a form also blocks its submission, and how such an element contributes an entry to the form data, is open for review.

> [!note] Used by Declarative HTML Components
> [Declarative HTML Components](/html-next/validation) builds on this model: a component's declared prop types and a `<data>` source's schema become constraints, and their failures are reported through this validity surface.

:::

## Relationship to current platform work

The proposal brings two active platform efforts together and adds a focused composition model:

- **PUT, PATCH, and DELETE:** WHATWG HTML PR&nbsp;#11347 specifies the form and navigation changes, paired with a Fetch change for CORS-preflighted navigation requests.
- **QUERY:** RFC&nbsp;10008 standardizes the HTTP method; WHATWG HTML issue&nbsp;#12594 proposes adding it to `method` and `formmethod`.
- **Composable scopes:** the ownership hierarchy above is new in this proposal. Its syntax and aggregate submission semantics need focused review and web-platform incubation.
- **Validity on any element:** also new. It builds on the Constraint Validation API and `ElementInternals.setValidity()`, and on the invalid state ARIA already defines for any element.

## Element reference

::: {.entry name="<form composable>" role="an explicit hierarchy of native submission scopes"}
Methods
: `get`, `query`, `post`, `put`, `patch`, `delete`, and form action `dialog`; parsed ASCII-case-insensitively.

Ownership
: Nearest form by default; explicit `form` association overrides ancestry.

Inner submit
: Validates, collects, and submits the selected inner scope.

Outer submit
: Collects its own and composed descendant scopes into one entry list and submits once.

Stage
: [Stage 0 · incubation]{.pill .inc}
:::

## References

[^1]: WHATWG HTML, [the form element](https://html.spec.whatwg.org/multipage/forms.html#the-form-element), [form ownership](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms), and [submitter overrides](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#attr-fs-formmethod).
[^2]: WHATWG HTML [PR&nbsp;#11347](https://github.com/whatwg/html/pull/11347), adding `put`, `patch`, and `delete` to forms, with WHATWG Fetch [PR&nbsp;#1785](https://github.com/whatwg/fetch/pull/1785) for CORS-preflighted navigations.
[^3]: IETF [RFC&nbsp;10008: The HTTP QUERY Method](https://www.rfc-editor.org/rfc/rfc10008), and WHATWG HTML [issue&nbsp;#12594](https://github.com/whatwg/html/issues/12594) proposing `method="query"`.
[^4]: WHATWG HTML, [the Constraint Validation API](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-constraint-validation-api), [ValidityState](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-validitystate-interface), and [ElementInternals.setValidity()](https://html.spec.whatwg.org/multipage/custom-elements.html#dom-elementinternals-setvalidity).
[^5]: WAI-ARIA, [aria-invalid](https://www.w3.org/TR/wai-aria-1.2/#aria-invalid), and CSS Selectors Level 4, [validity pseudo-classes](https://www.w3.org/TR/selectors-4/#validity-pseudos).
[^6]: WHATWG HTML, [the form element pointer](https://html.spec.whatwg.org/multipage/parsing.html#the-form-element-pointer): the parser currently ignores a nested `<form>` start tag while another form is open.
