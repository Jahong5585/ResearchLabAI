# ResearchLab AI

## Version

0.1

## Last completed stage

Stage 66

## Current stage

Stage 67

## Architecture

Director
↓
Planner
↓
Workflow
↓
Orchestrator
↓
Agent
↓
ResearchService
↓
Tools
↓
LLM

## Implemented Agents

- Planner
- Writer
- Programmer
- Translator
- Literature
- Researcher

## Implemented Tools

- HttpTool
- CrossrefTool
- CrossrefAbstractTool
- OpenAlexTool
- WebSearchTool (stub)
- TimeTool

## Core Modules

- Workflow
- Memory
- Prompt Loader
- Agent Registry
- Router
- ResearchService
- Tool Manager
- Paper Repository
- Citation Builder
- Query Optimizer
- Output Cleaner

## Models

- Paper
- Citation
- Task

## Current capabilities

- Multi-agent workflow
- Scientific search through Crossref
- OpenAlex API connected
- Paper repository
- Citation generation
- Query optimization
- Automatic output cleaning

## Next stage

Integrate OpenAlex into ResearchService.

Goals:

- Merge Crossref + OpenAlex
- Convert OpenAlex results into Paper objects
- Remove duplicates by DOI
- Sort by citations

## Known limitations

- Crossref rarely returns abstracts.
- OpenAlex is not yet converted to Paper objects.