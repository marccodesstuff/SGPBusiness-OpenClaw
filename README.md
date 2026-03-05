# OpenClaw SGPBusiness Research Pipeline

A Python-based orchestration system that researches brands via Perplexica and extracts Singapore legal entity information from SGPBusiness.

## Architecture

The pipeline consists of:

1. **Orchestrator** (`orchestrator.py`) - Core framework managing skills and agents
2. **Skills** - Modular components:
   - `research-brand` - Queries Perplexica API for entity information
   - `scrape-sgpbusiness` - Scrapes SGPBusiness for UEN and legal details
3. **Agents** - Orchestration workflows combining multiple skills
4. **Configuration** - JSON-based configs in `~/.openclaw/`

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                          │
│              (run-pipeline.py)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
      ┌──────────────────────────────────────────┐
      │    OpenClaw Orchestrator Framework       │
      │  - Loads agents & skills                 │
      │  - Manages LLM (Ollama) connection       │
      │  - Executes skill pipeline               │
      └─────────────────┬──────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
  ┌──────────────────┐         ┌──────────────────┐
  │  Perplexica API  │         │  SGPBusiness Web │
  │  (localhost:3000)│         │  (sgbizfile...)  │
  │                  │         │                  │
  │ research-brand   │         │ scrape-sgpbusiness│
  │ Skill            │         │ Skill            │
  └────────┬─────────┘         └──────────────────┘
           │                          ▲
           │ Returns entity_name      │
           └──────────────────────────┘

Input: Brand name → Output: {entity_name, UEN, business_type, ...}
```

## Directory Structure

```
~/.openclaw/                          # OpenClaw home directory
├── config.json                       # Global configuration
├── skills/                           # All available skills
│   ├── research-brand/
│   │   ├── skill.py                 # Perplexica integration
│   │   └── skill.json               # Skill definition
│   ├── scrape-sgpbusiness/
│   │   ├── skill.py                 # SGPBusiness scraper
│   │   └── skill.json               # Skill definition
│   └── extract-business-info/
│       ├── skill.py                 # Orchestrator placeholder
│       └── skill.json               # Skill definition
└── agents/                           # Agent definitions
    └── sgp-entity-finder.json       # Main agent

/home/beakthor0301/Code/openclaw-playground/
├── package.json                      # Project metadata
├── requirements.txt                  # Python dependencies
├── config.json                       # Default config (copy to ~/.openclaw/)
├── orchestrator.py                   # Core orchestration framework
├── skills/                           # Skill implementations (copy to ~/.openclaw/skills/)
│   ├── research-brand/
│   │   ├── skill.py
│   │   └── skill.json
│   ├── scrape-sgpbusiness/
│   │   ├── skill.py
│   │   └── skill.json
│   └── extract-business-info/
│       ├── skill.py
│       └── skill.json
├── agents/                           # Agent configs (copy to ~/.openclaw/agents/)
│   └── sgp-entity-finder.json
└── scripts/
    └── run-pipeline.py              # CLI entry point
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Ollama running with qwen3.5:9b model at `http://localhost:11434`
- Perplexica running at `http://localhost:3000`
- SGPBusiness website accessible (https://www.sgbizfile.gov.sg)

### Installation

1. **Set up Python environment:**
```bash
cd /home/beakthor0301/Code/openclaw-playground/
python3 -m venv venv
source venv/bin/activate  # On WSL/Linux/Mac
# or on Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Deploy skills, agents, and config to ~/.openclaw:**
```bash
mkdir -p ~/.openclaw/skills ~/.openclaw/agents
cp config.json ~/.openclaw/
cp -r skills/research-brand ~/.openclaw/skills/
cp -r skills/scrape-sgpbusiness ~/.openclaw/skills/
cp -r skills/extract-business-info ~/.openclaw/skills/
cp -r agents/* ~/.openclaw/agents/
```

4. **Verify OpenClaw configuration:**
```bash
ls -la ~/.openclaw/
# Should show: config.json, skills/, agents/
```

## Usage

### Basic Usage

```bash
cd /home/beakthor0301/Code/openclaw-playground/
python3 scripts/run-pipeline.py "Grab Technologies"
```

### Command Options

```bash
# JSON output (default)
python3 scripts/run-pipeline.py "Brand Name" --output json

# Pretty-printed JSON
python3 scripts/run-pipeline.py "Brand Name" --pretty

# Text format output
python3 scripts/run-pipeline.py "Brand Name" --output text

# Specify custom config directory
python3 scripts/run-pipeline.py "Brand Name" --config /custom/path/.openclaw

# Specify different agent
python3 scripts/run-pipeline.py "Brand Name" --agent sgp-entity-finder
```

## Output Example

```json
{
  "status": "success",
  "input": {
    "brand": "Grab Technologies"
  },
  "timestamp": "2026-03-05T15:30:45.123456",
  "agent": "sgp-entity-finder",
  "research-brand_entity_name": "Grab Technologies Pte Ltd",
  "research-brand_research_summary": "Grab is a Southeast Asian ride-hailing and logistics platform...",
  "scrape-sgpbusiness_entity_name": "Grab Technologies Pte Ltd",
  "scrape-sgpbusiness_uen": "201520234K",
  "scrape-sgpbusiness_business_type": "Private Company Limited by Shares",
  "scrape-sgpbusiness_registration_date": "2015-03-20",
  "scrape-sgpbusiness_business_address": "112 Robinson Road, #13-06, Singapore 068902",
  "scrape-sgpbusiness_website_url": "https://www.grab.com",
  "scrape-sgpbusiness_sgbusiness_url": "https://www.sgbizfile.gov.sg/entity/201520234K"
}
```

## Skill Development

Each skill is a Python module with an `execute()` function:

```python
def execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process inputs and return structured output

    Args:
        inputs: Dictionary with skill-specific inputs

    Returns:
        Dictionary with 'status' and output fields
    """
    # Implementation here
    return {
        "status": "success",
        "output_field": "value"
    }
```

### Creating a New Skill

1. Create skill directory: `~/.openclaw/skills/my-skill/`
2. Create `skill.py` with `execute()` function
3. Create `skill.json` with skill metadata
4. Reference in agent config to use

## Configuration

Update `~/.openclaw/config.json` to customize:

```json
{
  "llm_endpoint": "http://localhost:11434",
  "model": "qwen3.5:9b",
  "perplexica_endpoint": "http://localhost:3000",
  "timeout": 30
}
```

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Verify model is available: `ollama list` (should show qwen3.5:9b)
- Test connection: `curl http://localhost:11434/api/tags`

### Perplexica Connection Error
- Ensure Perplexica is running at http://localhost:3000
- Check Perplexica logs for errors
- Verify API endpoint: `curl http://localhost:3000/api/search`

### SGPBusiness Scraper Issues
- Ensure scrapling is installed: `pip install "scrapling[fetchers]" && scrapling install`
- Verify website is accessible: `curl https://www.sgbizfile.gov.sg`
- Check that entity name format is correct

### Dependencies Not Installed Error
- Re-run: `pip install -r requirements.txt && scrapling install`
- Or install individually: `pip install "scrapling[fetchers]" && scrapling install`

## Testing

### Quick Test
```bash
python3 scripts/run-pipeline.py "Google Asia Pacific" --pretty
```

### Full Integration Test
```bash
# Test 1: Research skill
python3 -c "
from orchestrator import OpenClawOrchestrator
orch = OpenClawOrchestrator()
result = orch.run_agent('sgp-entity-finder', {'brand': 'META SINGAPORE'})
print(result)
"

# Test 2: Verify all skills are loaded
python3 -c "
from orchestrator import SkillRegistry
from pathlib import Path
registry = SkillRegistry(Path.home() / '.openclaw' / 'skills')
print('Loaded skills:', list(registry.skills.keys()))
"
```

## Development

### Project Structure Convention
- **Skills**: Reusable components that process specific tasks
- **Agents**: Workflows that chain multiple skills together
- **Orchestrator**: Framework that manages execution

### Adding a New Agent

Create `~/.openclaw/agents/my-agent.json`:

```json
{
  "name": "my-agent",
  "description": "Description of what agent does",
  "goal": "The goal/outcome of the agent",
  "skills": [
    {
      "name": "skill-1",
      "input_from_context": {
        "param": "input.field"
      }
    }
  ]
}
```

## Dependencies

- **requests**: HTTP client for Perplexica API calls
- **scrapling[fetchers]**: Adaptive web scraping with stealth HTTP fetching and CSS/XPath selectors (replaces beautifulsoup4 + lxml + requests for scraping)
- **ollama** (optional): Python client for Ollama (currently using requests)

## License

MIT

## Support

For issues or questions:
1. Check error messages in output (usually descriptive)
2. Enable debug mode in config.json
3. Check Perplexica, Ollama, and SGPBusiness service status
4. Review skill configuration files
