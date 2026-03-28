# ADR-004: Campaign Instances as Full Copies of Templates

## Status
Accepted

## Context
Campaigns have a template (story skeleton with Acts, Beats, NPCs, locations) and runtime instances (active playthroughs). The relationship between template and instance could be handled via references/symlinks (instance reads from template at runtime) or full copies (instance gets its own files at creation).

## Decision
`create_campaign_instance` copies the entire template directory to `campaigns/[instance]/`. Instances are fully independent from the moment of creation.

Campaign story content follows an Acts/Beats structure:
- **Acts** are major story phases
- **Beats** are scene-level milestones with explicit accomplishment conditions
- Progress is tracked in `campaign_progress.md` against this structure

## Consequences
- **Instances can diverge freely.** NPCs can be killed, locations can change, story branches can be added — none of this affects the template or other instances.
- **Instances are archivable.** A completed campaign is a self-contained directory with full history in git.
- **No runtime template dependency.** The agent never needs to read from `available_campaigns/` during active play.
- **Beats provide pacing structure.** Clear accomplishment conditions (e.g., "solve the rat problem") tell the DM when to advance the story, preventing both railroading and aimless drift.
- **Constraint:** Do not make instances reference template files at runtime. The copy-on-create model is intentional — modifying a template should never affect an active instance.
