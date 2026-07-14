# Scale to ~5k Marketplace Products Plan

> For Hermes: plan only. No code changes besides this file until execution is explicitly started.

## Goal
Grow the Bedrock marketplace catalog from 871 products to approximately 5,000, reorganize directories for Microsoft Partner submission, and align content generation with Microsoft-preferred languages/stacks/libs for Bedrock/Minecraft Marketplace assets.

## Current Context
- `marketplace-content/` holds current packs: 780 skin-packs, 38 texture-packs, 32 world-templates, 22 mashup-packs.
- `dist/` has 171 `.mcpack` files prepared for submission.
- `catalog/PACK_CATALOG.json` centralizes metadata and is already consumed by the generated site.
- Website is generated from `scripts/generate-site.py` and outputs to `website/`.
- CAVMan monetization subagents exist but are not yet looped to mass generate assets.

## Proposed Approach
1. Ground stack decisions in Microsoft/Bedrock tooling reality (Blockbench, bridge., Minecraft Bedrock Editor, command blocks/addons, scripting).
2. Restructure marketplace-content into submission-ready folders: generated source, curated/dist-ready, assets, descriptions, behavior, behavior.
3. Run a controlled content expansion path that keeps manifests, descriptions, and assets in sync.
4. Stop near 5k products and produce a Partner submission bundle.

## Step-by-step Plan

### Task 1: Map Microsoft-supported Bedrock creation stack
Objective: Record preferred languages, tools, and libraries for Bedrock marketplace content.

Files:
- Create: `.hermes/plans/microsoft-bedrock-stack/microsoft-bedrock-stack.md`

Step 1: Write preferred tools list.
Step 2: Determine minimum viable product format for each category.
Step 3: Save findings as reference for generation scripts.

### Task 2: Reorganize marketplace-content
Objective: Restructure for Partner deliverable + CI-friendly layout.

Files:
- Modify: `marketplace-content/` directories
- Create: new layout docs in repo root

Target layout:
- `marketplace-content/source/` -> generated pack directories
- `marketplace-content/curated/` -> final approved packs for packaging/submission
- `marketplace-content/assets/` -> prints, images, 3d models, thumbnails (already created)
- `marketplace-content/descriptions/` -> existing description store
- `marketplace-content/behavior-packs/` -> existing items and entities
- `marketplace-content/world-templates/` -> existing worlds/mazes/minigames
- `marketplace-content/dist/` -> submission `.mcpack` output

### Task 3: Create mass content generator with stop condition
Objective: Add a script that expands packs in controlled batches, maintaining catalog + descriptions + compliance metadata.

Files:
- Create: `scripts/scale-products.py`

Step 1: Add target count (`TARGET_PRODUCTS = 5000`).
Step 2: Read current catalog from `catalog/PACK_CATALOG.json`.
Step 3: Generate missing products by category quotas based on Microsoft highselling ratios:
- 60-70% skins
- 15-20% textures
- 10-15% worlds/minigames
- 5-10% mashups/behavior
Step 4: Write new pack directories, manifests, and descriptions.
Step 5: Stop when total >= target.
Step 6: Rewrite `catalog/PACK_CATALOG.json`.
Step 7: Regenerate site from catalog.

### Task 4: Add asset pipeline hooks
Objective: Ensure every new pack also gets placeholder assets and pricing records so site/storefront stays consistent.

Files:
- Modify: `agents/` entries
- Create: `scripts/sync-assets.py`

Step 1: For each new pack, create placeholder PNGs/OBJs.
Step 2: Update catalog references for asset paths.

### Task 5: Validation + Partner bundle
Objective: Produce final Partner submittable package.

Files:
- Target: `submission_bundle.zip` refresh and output manifest.

Step 1: Re-run validator and compliance QA in green.
Step 2: Repackage `dist/` contents into `submission_bundle.zip`.
Step 3: Write partner submission checklist output to `.hermes/plans/partner-submission-checklist.md`.

## Tests / Validation
- `PYTHONPATH=. python scripts/upgrade-manifests.py` should report total counts matching catalog.
- `PYTHONPATH=. python scripts/generate-site.py` completes without error.
- `PYTHONPATH=. python agents/compliance_qa_agent.py --pack-dir <sample>` returns no REJECTED.
- Final `catalog/PACK_CATALOG.json` count should approximate 5000.

## Risks, Tradeoffs, and Open Questions
- Risk: Reorganizing folders breaks existing scripts that use hardcoded paths.
  Mitigation: Add path constants in one place (`src/paths.py`) and update callers.
- Risk: 5k products inflates packaging and Partner review time.
  Mitigation: Keep categories curated and pre-vetted.
- Risk: Microsoft stack preference may shift seasonally.
  Mitigation: Keep reference doc updated and prefer official Minecraft Bedrock formats.
