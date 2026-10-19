/-
HTML Next's static containment construction, independent of HTML tokenization.
A payload represents an immutable recognized node identity and all its data.
A barrier represents a protected container. Only non-barriers can be lifted.
This theorem concerns this model, not browser scheduling or sanitizer policies.
-/
import Std

namespace HTMLNext

inductive Forest (α : Type) where
  | nil
  | cons (payload : α) (eligible barrier : Bool) (children rest : Forest α)
  deriving Repr

namespace Forest

def append : Forest α → Forest α → Forest α
  | .nil, ys => ys
  | .cons p e b children rest, ys => .cons p e b children (append rest ys)

def preorder : Forest α → List α
  | .nil => []
  | .cons p _ _ children rest => p :: (preorder children ++ preorder rest)

def project : Forest α → Forest α
  | .nil => .nil
  | .cons p e b children rest =>
    if e && !b then
      .cons p e b .nil (append (project children) (project rest))
    else
      .cons p e b (project children) (project rest)

-- For each node, retain its immutable payload and ordered protected ancestors.
def protectedPaths (ancestors : List α) : Forest α → List (α × List α)
  | .nil => []
  | .cons p _ b children rest =>
    let inside := if b then ancestors ++ [p] else ancestors
    (p, ancestors) :: (protectedPaths inside children ++ protectedPaths ancestors rest)

theorem preorder_append (xs ys : Forest α) :
    preorder (append xs ys) = preorder xs ++ preorder ys := by
  induction xs with
  | nil => rfl
  | cons p e b children rest ihc ihr =>
    simp [append, preorder, ihr, List.append_assoc]

theorem preorder_project (xs : Forest α) : preorder (project xs) = preorder xs := by
  induction xs with
  | nil => rfl
  | cons p e b children rest ihc ihr =>
    cases e <;> cases b <;> simp [project, preorder, preorder_append, ihc, ihr]

theorem protectedPaths_append (xs ys : Forest α) (ancestors : List α) :
    protectedPaths ancestors (append xs ys) =
      protectedPaths ancestors xs ++ protectedPaths ancestors ys := by
  induction xs generalizing ancestors with
  | nil => rfl
  | cons p e b children rest ihc ihr =>
    simp [append, protectedPaths, ihr, List.append_assoc]

theorem protectedPaths_project (xs : Forest α) (ancestors : List α) :
    protectedPaths ancestors (project xs) = protectedPaths ancestors xs := by
  induction xs generalizing ancestors with
  | nil => rfl
  | cons p e b children rest ihc ihr =>
    cases e <;> cases b <;> simp [project, protectedPaths, protectedPaths_append, ihc, ihr]

-- The payload can contain node identity, namespace, attributes, and text. Equality
-- of the entire ordered payload sequence rules out additions, loss, substitution,
-- or reclassification within this pure projection model.
#print axioms preorder_project
#print axioms protectedPaths_project

end Forest
end HTMLNext
