# Solution Design Principles

## Intent is the primary contract

Engineering quality starts with solving the requested problem completely and no larger problem accidentally.

A technically elegant change that misses the user's required outcome is still incorrect.

## Simple is not the same as minimal code

The simplest solution is the smallest design that satisfies the current requirement, known constraints, and reasonable failure behavior without creating unnecessary operational burden.

Fewer lines can still be a worse design if they collapse unrelated responsibilities into one place.

## Scalable is a measured property

Do not label an architecture scalable because it contains distributed infrastructure.

Identify:

- the expected workload
- the likely first bottleneck
- the current capacity model
- the trigger for changing the topology

Architectural complexity should arrive when a real constraint justifies it.

## Modularity is about ownership

Modularity means a change has a clear home.

Good boundaries reduce the number of unrelated reasons a module must change.

File count alone does not create modularity.

## Prefer reversible decisions early

When two approaches satisfy current requirements similarly, prefer the one that is easier to replace, extend, or migrate unless the reversible choice creates a material cost now.

## Scope is a correctness property

Unrequested changes increase review surface and make failures harder to attribute.

Supporting changes are acceptable when they are necessary for correctness. Unrelated improvement is separate work.

## Evidence beats confidence

Implementation claims should be backed by evidence that corresponds to the final candidate.

Useful evidence includes tests, builds, type checks, runtime behavior, diffs, and explicit requirement-to-behavior mapping.
