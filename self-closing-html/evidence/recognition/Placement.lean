/-
Static authorization boundary for a placement plan. A receipt carries origin,
namespace/attributes (payload), protected ancestry, and exact owned code/text.
Literal text nodes are inserted as text, never retokenized by this model.
This is not a verification of JavaScript, HTML recognition, or native scheduling.
-/
import Std

namespace HTMLPlacement

structure Receipt (Payload : Type) where
  origin : Nat
  payload : Payload
  protectedAncestors : List Nat
  ownedCode : Option String
  deriving DecidableEq, Repr

inductive Output (Payload : Type) where
  | literalText (value : String)
  | element (receipt : Receipt Payload)
  deriving DecidableEq, Repr

variable {Payload : Type} [DecidableEq Payload]

def Authorized (source : List (Receipt Payload)) : List (Output Payload) → Prop
  | [] => True
  | .literalText _ :: rest => Authorized source rest
  | .element receipt :: rest => receipt ∈ source ∧ Authorized source rest

def check (source : List (Receipt Payload)) : List (Output Payload) → Bool
  | [] => true
  | .literalText _ :: rest => check source rest
  | .element receipt :: rest => decide (receipt ∈ source) && check source rest

theorem check_sound (source : List (Receipt Payload)) :
    ∀ output, check source output = true → Authorized source output := by
  intro output
  induction output with
  | nil => simp [check, Authorized]
  | cons head rest ih =>
    cases head with
    | literalText value => simpa [check, Authorized] using ih
    | element receipt =>
      intro h
      simp [check] at h
      exact ⟨h.1, ih h.2⟩

def origins : List (Output Payload) → List Nat
  | [] => []
  | .literalText _ :: rest => origins rest
  | .element receipt :: rest => receipt.origin :: origins rest

def admissible (source : List (Receipt Payload)) (output : List (Output Payload)) : Bool :=
  check source output && decide (origins output |>.Nodup)

omit [DecidableEq Payload] in
theorem source_map_safe (source receipts : List (Receipt Payload))
    (included : ∀ receipt, receipt ∈ receipts → receipt ∈ source) :
    Authorized source (receipts.map Output.element) := by
  induction receipts with
  | nil => simp [Authorized]
  | cons first rest ih =>
    simp only [List.map_cons, Authorized]
    constructor
    · exact included first (by simp)
    · exact ih (fun receipt present => included receipt (by simp [present]))

omit [DecidableEq Payload] in
theorem source_map_origins (source : List (Receipt Payload)) :
    origins (source.map Output.element) = source.map Receipt.origin := by
  induction source with
  | nil => rfl
  | cons first rest ih => simp [origins, ih]

def choose (source : List (Receipt Payload))
    (recovery proposed : List (Output Payload)) : List (Output Payload) :=
  if admissible source proposed = true then proposed
  else if admissible source recovery = true then recovery
  else source.map Output.element

theorem admissible_authorized (source : List (Receipt Payload))
    (output : List (Output Payload)) (h : admissible source output = true) :
    Authorized source output := by
  simp [admissible] at h
  exact check_sound source output h.1

theorem admissible_unique (source : List (Receipt Payload))
    (output : List (Output Payload)) (h : admissible source output = true) :
    (origins output).Nodup := by
  simp [admissible] at h
  exact h.2

theorem choose_authorized (source : List (Receipt Payload))
    (recovery proposed : List (Output Payload)) :
    Authorized source (choose source recovery proposed) := by
  unfold choose
  split
  · next h => exact admissible_authorized source proposed h
  · split
    · next h => exact admissible_authorized source recovery h
    · exact source_map_safe source source (fun _ h => h)

theorem choose_unique (source : List (Receipt Payload))
    (recovery proposed : List (Output Payload))
    (source_unique : (source.map Receipt.origin).Nodup) :
    (origins (choose source recovery proposed)).Nodup := by
  unfold choose
  split
  · next h => exact admissible_unique source proposed h
  · split
    · next h => exact admissible_unique source recovery h
    · simpa [source_map_origins] using source_unique

omit [DecidableEq Payload] in
theorem receipt_from_source (source : List (Receipt Payload)) (receipt : Receipt Payload) :
    ∀ output, Authorized source output → Output.element receipt ∈ output → receipt ∈ source := by
  intro output
  induction output with
  | nil => simp
  | cons head rest ih =>
    cases head with
    | literalText value => simpa [Authorized] using ih
    | element first =>
      intro safe present
      rcases List.mem_cons.mp present with same | remaining
      · cases same
        exact safe.1
      · exact ih safe.2 remaining

theorem selected_receipt_from_source (source : List (Receipt Payload))
    (recovery proposed : List (Output Payload)) (receipt : Receipt Payload)
    (present : Output.element receipt ∈ choose source recovery proposed) :
    receipt ∈ source :=
  receipt_from_source source receipt _ (choose_authorized source recovery proposed) present

#print axioms check_sound
#print axioms choose_authorized
#print axioms choose_unique
#print axioms receipt_from_source
#print axioms selected_receipt_from_source

end HTMLPlacement
