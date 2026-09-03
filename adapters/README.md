# Adapters

Adapters contain runtime-specific wiring that should not pollute canonical artifacts.

Examples include:

- model IDs
- proprietary agent configuration
- installation paths
- product-specific discovery metadata
- runtime permission settings
- generated target formats

Do not create an adapter merely to copy a canonical skill into another folder.

Add an adapter only when the target assistant needs behavior or configuration that cannot live portably in the canonical artifact.
