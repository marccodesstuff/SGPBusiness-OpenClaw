# OpenClaw SGPBusiness Pipeline - Complete Setup Guide

## Step-by-Step Setup Instructions

### Step 1: Prerequisite Services Verification

Ensure these services are running before testing:

#### A. Verify Ollama (LLM Engine)

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If running, should return JSON with available models
# Expected response includes: qwen3.5:9b

# If not running, start it:
ollama serve

# In another terminal, ensure qwen3.5:9b is available:
ollama list

# If not available, pull it:
ollama pull qwen3.5:9b
```

#### B. Verify Perplexica (Research Engine)

```bash
# Test Perplexica connection
curl http://localhost:3000

# Or test specific endpoint:
curl -X POST http://localhost:3000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# If Perplexica not running, start it according to its documentation
```

#### C. Verify SGPBusiness Website Access

```bash
# Test website availability
curl -I https://www.sgbizfile.gov.sg

# Should return HTTP 200 or 301/302 (redirect)
```

### Step 2: Python Environment Setup

```bash
# Navigate to project directory
cd /home/beakthor0301/Code/openclaw-playground

# Create Python virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Verify activation (prompt should show: (venv) ...)
python3 --version

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt

# Verify installations
pip list | grep -E "requests|beautifulsoup4|lxml"
```

### Step 3: Verify OpenClaw Configuration

```bash
# Check ~/.openclaw structure was created
ls -la ~/.openclaw/

# Expected output:
# drwxr-xr-x  agents
# -rw-r--r--  config.json
# drwxr-xr-x  skills

# Verify all skill directories exist
ls -la ~/.openclaw/skills/

# Expected:
# drwxr-xr-x  research-brand
# drwxr-xr-x  scrape-sgpbusiness
# drwxr-xr-x  extract-business-info

# Verify all agent configurations exist
ls -la ~/.openclaw/agents/

# Expected:
# -rw-r--r--  sgp-entity-finder.json

# Check configuration validity
python3 -c "
import json
with open('~/.openclaw/config.json'.replace('~', os.path.expanduser('~'))) as f:
    config = json.load(f)
    print('✓ Config loaded successfully')
    print('  LLM Endpoint:', config.get('llm_endpoint'))
    print('  Model:', config.get('model'))
    print('  Perplexica:', config.get('perplexica_endpoint'))
" 2>&1 || echo "Configuration file check skipped"
```

### Step 4: Syntax Validation

```bash
# Validate Python syntax
python3 -m py_compile orchestrator.py
python3 -m py_compile scripts/run-pipeline.py

# Validate all skills
for skill in ~/.openclaw/skills/*/skill.py; do
    python3 -m py_compile "$skill" && echo "✓ $skill valid"
done

# Validate all JSON configs
for config in ~/.openclaw/**/*.json; do
    python3 -c "import json; json.load(open('$config'))" && echo "✓ $config valid"
done
```

### Step 5: Component Testing

#### Test 1: Verify Orchestrator Loads

```bash
cd /home/beakthor0301/Code/openclaw-playground
source venv/bin/activate

python3 << 'EOF'
from orchestrator import OpenClawOrchestrator, SkillRegistry
from pathlib import Path

print("Testing orchestrator components...")

# Test 1: Load orchestrator
print("\n1. Loading OpenClaw Orchestrator...")
orch = OpenClawOrchestrator()
print("   ✓ Orchestrator loaded")
print(f"   - LLM Model: {orch.config.get('model')}")
print(f"   - Skills Dir: {orch.skills_dir}")
print(f"   - Agents Dir: {orch.agents_dir}")

# Test 2: Load skills
print("\n2. Available Skills:")
for skill_name, skill_data in orch.skill_registry.skills.items():
    print(f"   ✓ {skill_name}")

# Test 3: Configuration loaded
print("\n3. Configuration:")
for key, value in orch.config.items():
    print(f"   - {key}: {value}")

print("\n✓ All components loaded successfully!")
EOF
```

#### Test 2: Test Individual Skill (Research Only)

```bash
cd /home/beakthor0301/Code/openclaw-playground
source venv/bin/activate

python3 << 'EOF'
from orchestrator import SkillRegistry
from pathlib import Path

# Load skills
skills = SkillRegistry(Path.home() / ".openclaw" / "skills")

# Test research-brand skill independently
print("Testing research-brand skill...")
result = skills.execute_skill("research-brand", {
    "brand": "GocaBaya Technologies",
    "perplexica_endpoint": "http://localhost:3000"
})

print("Result:")
import json
print(json.dumps(result, indent=2))
EOF
```

#### Test 3: Full Pipeline Test

```bash
cd /home/beakthor0301/Code/openclaw-playground
source venv/bin/activate

# Test basic invocation
python3 scripts/run-pipeline.py "Grab Technologies" --pretty

# Test with text output
python3 scripts/run-pipeline.py "Google Asia" --output text
```

### Step 6: Troubleshooting Guide

If tests fail, follow this troubleshooting checklist:

#### Issue: "Connection refused" - Ollama

```bash
# Verify Ollama is running
ps aux | grep ollama

# Start Ollama if not running:
ollama serve &

# Check if qwen3.5:9b is pulled:
ollama list | grep qwen3.5

# If not pulled, pull it:
ollama pull qwen3.5:9b

# Wait for it to complete, then test:
curl http://localhost:11434/api/tags | grep qwen3.5
```

#### Issue: "Connection refused" - Perplexica

```bash
# Check if Perplexica is running on port 3000
netstat -tuln | grep 3000

# Or using lsof (if available):
lsof -i :3000

# Start Perplexica (exact command depends on your setup):
# Usually: cd /path/to/perplexica && npm start
# Or: docker run -p 3000:3000 perplexica/perplexica

# Wait for startup (usually 5-10 seconds)

# Test connection:
curl http://localhost:3000
```

#### Issue: "Module not found" or "No module named requests"

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install --force-reinstall -r requirements.txt

# Verify installations
pip list | grep -i requests
pip list | grep -i beautifulsoup
```

#### Issue: "Skill not found"

```bash
# Verify skill files exist
ls -la ~/.openclaw/skills/research-brand/
ls -la ~/.openclaw/skills/scrape-sgpbusiness/

# Check skill.py and skill.json are present
file ~/.openclaw/skills/research-brand/skill.py
file ~/.openclaw/skills/research-brand/skill.json

# Verify skill.json is valid JSON
python3 -c "import json; json.load(open(os.path.expanduser('~/.openclaw/skills/research-brand/skill.json')))"
```

#### Issue: "No execute function"

```bash
# Verify execute function is defined in skill.py
grep -n "def execute" ~/.openclaw/skills/research-brand/skill.py

# Should return: def execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
```

### Step 7: Production Readiness Checklist

Before deploying, verify:

```bash
# [ ] All three services running:
#     - Ollama at http://localhost:11434
#     - Perplexica at http://localhost:3000
#     - SGPBusiness website accessible

# [ ] Python environment setup:
#     - Virtual env created and activated
#     - Dependencies installed with pip

# [ ] Configuration files in place:
#     - ~/.openclaw/config.json
#     - ~/.openclaw/agents/sgp-entity-finder.json
#     - ~/.openclaw/skills/*/skill.py and skill.json

# [ ] All tests passing:
python3 scripts/run-pipeline.py "Test Brand" --pretty

# [ ] Output has expected fields:
#     - status: success
#     - entity_name
#     - uen (or similar identifiers)
#     - research_summary or research data
```

## Running the Pipeline

### After All Setup is Complete

```bash
# Activate environment
cd /home/beakthor0301/Code/openclaw-playground
source venv/bin/activate

# Run pipeline with a test input
python3 scripts/run-pipeline.py "Your Brand Name" --pretty
```

### Expected Output

```json
{
  "status": "success",
  "input": {
    "brand": "Your Brand Name"
  },
  "timestamp": "2026-03-05T...",
  "agent": "sgp-entity-finder",
  "research-brand_entity_name": "...",
  "scrape-sgpbusiness_uen": "...",
  ...
}
```

## Next Steps

1. Test with real brand names from your use case
2. Customize skills if needed
3. Monitor performance and adjust timeouts in config.json if necessary
4. Consider running as background service for production

## Support & Issues

For specific issues, check:
1. Service status (Ollama, Perplexica, SGPBusiness)
2. Network connectivity
3. Dependency installations
4. Configuration file validity
5. Python version (3.12+)
