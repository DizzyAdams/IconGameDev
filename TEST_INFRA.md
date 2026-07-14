# E2E Test Infra: Minecraft Bedrock Marketplace Content

## Test Philosophy
- Opaque-box, requirement-driven.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Skin Pack Generation | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 2 | Texture Pack Generation | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 3 | Bulk Compilation | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 4 | Output Validation | ORIGINAL_REQUEST | 5 | 5 | ✓ |

## Test Architecture
- Test runner: pytest
- Invocation: `pytest` or `python -m pytest` run from `marketplace-content/`
- Directory layout:
  - marketplace-content/tests/conftest.py
  - marketplace-content/tests/test_skin_pack_gen.py
  - marketplace-content/tests/test_texture_pack_gen.py
  - marketplace-content/tests/test_bulk_compile.py
  - marketplace-content/tests/test_validation.py
  - marketplace-content/tests/test_cross_feature.py
  - marketplace-content/tests/test_workloads.py

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | 100 Skin Ingestion | Skin Pack Gen, Compilation, Validation | Medium |
| 2 | 500 Skin Ingestion | Skin Pack Gen, Compilation, Validation | High |
| 3 | Bulk Multi-Pack Submission | Skin & Texture Gen, Compile, Validate | High |
| 4 | Large Texture Pack Mod | Texture Pack Gen, Compile, Validate | Medium |
| 5 | Full Pipeline Run | All Features E2E | High |

## Coverage Thresholds
- Tier 1: 5 tests per feature (Total: 20)
- Tier 2: 5 tests per feature (Total: 20)
- Tier 3: Cross-feature combinations (Total: 4)
- Tier 4: Real-world workloads (Total: 5)
- Total E2E Tests: 49 tests
