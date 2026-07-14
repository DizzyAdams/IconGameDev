# Original User Request

## Initial Request — 2026-06-27T07:24:55-03:00

# Teamwork Project Prompt

O projeto consiste na criação de um sistema massivo e automatizado para geração e compilação em larga escala de pacotes de skin e texturas (.mcpack) para o Marketplace do Minecraft Bedrock, focado em alta monetização e seguindo rigorosamente a documentação oficial.

Working directory: ~/teamwork_projects/bedrock_mass_automation
Integrity mode: development

## Requirements

### R1. Mass Compilation Engine
The system must process bulk inputs of skins and textures to automatically generate valid Bedrock `.mcpack` files. The architecture and technology choice is up to the team, but it must adhere strictly to the official Minecraft Bedrock packaging structure and manifest schemas.

### R2. Output Validation & Verification
The system must include an automated validation mechanism to ensure all generated packages are structurally sound, have valid JSON files, feature unique UUIDs across modules/headers, and enforce correct texture dimensions (e.g., 64x64 for skins).

## Acceptance Criteria

### Execution and Performance
- [ ] The system can ingest a mock batch of 500 skin inputs and successfully generate all corresponding `.mcpack` files programmatically without manual intervention.

### Schema and Validity
- [ ] A programmatic validation test confirms that 100% of the generated `manifest.json` and `skins.json` files parse as valid JSON.
- [ ] The validator proves that no two generated `.mcpack` files share the same header or module UUIDs.
