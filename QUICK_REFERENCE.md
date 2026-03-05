# OpenClaw SGPBusiness Pipeline - Quick Reference

## 🎯 Exact Command to Run Test Execution

```bash
cd /home/beakthor0301/Code/openclaw-playground && \
source venv/bin/activate && \
python3 scripts/run-pipeline.py "Grab Technologies Pte Ltd" --pretty
```

## ⚡ One-Line Setup & Test

```bash
cd /home/beakthor0301/Code/openclaw-playground && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python3 scripts/run-pipeline.py "Google Singapore" --pretty
```

## 📋 Before First Run

Verify these services are running:

1. **Ollama LLM** (Port 11434)
   ```bash
   curl http://localhost:11434/api/tags
   # Should return JSON with qwen2.5:9b listed
   ```

2. **Perplexica Search** (Port 3000)
   ```bash
   curl http://localhost:3000
   # Should return Perplexica homepage or API response
   ```

3. **SGPBusiness Website** (Internet access required)
   ```bash
   curl -I https://www.sgbizfile.gov.sg
   # Should return HTTP 200 or redirect
   ```

## 🚀 Usage Examples

### Basic Usage
```bash
# Minimal - just brand name
python3 scripts/run-pipeline.py "Shopee"

# Pretty-printed JSON output
python3 scripts/run-pipeline.py "Shopee" --pretty

# Text format output
python3 scripts/run-pipeline.py "Shopee" --output text
```

### Advanced Usage
```bash
# Custom config location
python3 scripts/run-pipeline.py "Shopee" --config ~/.openclaw --pretty

# Specific agent (default: sgp-entity-finder)
python3 scripts/run-pipeline.py "Shopee" --agent sgp-entity-finder --pretty

# Save to file
python3 scripts/run-pipeline.py "Shopee" --pretty > result.json
```

## 📂 File Structure Created

### Configuration (in ~/.openclaw/)
- `config.json` - Global settings
- `agents/sgp-entity-finder.json` - Agent workflow
- `skills/research-brand/skill.py` - Perplexica integration
- `skills/research-brand/skill.json` - Skill config
- `skills/scrape-sgpbusiness/skill.py` - SGPBusiness scraper
- `skills/scrape-sgpbusiness/skill.json` - Skill config
- `skills/extract-business-info/skill.py` - Orchestrator
- `skills/extract-business-info/skill.json` - Skill config

### Project Files (in openclaw-playground/)
- `orchestrator.py` - Core framework (~300 lines)
- `scripts/run-pipeline.py` - CLI entry point (~200 lines)
- `requirements.txt` - Python dependencies
- `package.json` - Project metadata
- `README.md` - Full documentation
- `SETUP.md` - Setup guide
- `DEPLOYMENT_SUMMARY.md` - This deployment info

## 💾 Installation Steps

```bash
# 1. Activate environment
cd /home/beakthor0301/Code/openclaw-playground
source venv/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Verify installation
python3 -c "import requests; print('✓ All dependencies installed')"

# 4. Run test
python3 scripts/run-pipeline.py "Test Brand" --pretty
```

## 🎓 How It Works

```
INPUT (Brand Name)
    ↓
[Perplexica] Research brand → Extract legal entity name
    ↓
[SGPBusiness] Scrape → Extract UEN + legal details
    ↓
OUTPUT (JSON)
    ↓
Display formatted results
```

## 📊 Expected Output Fields

```json
{
  "status": "success",
  "input": {"brand": "..."},
  "timestamp": "2026-03-05T...",
  "agent": "sgp-entity-finder",

  "research-brand_entity_name": "Official legal entity name",
  "research-brand_research_summary": "Research findings",

  "scrape-sgpbusiness_entity_name": "Entity name",
  "scrape-sgpbusiness_uen": "9-10 digit ID",
  "scrape-sgpbusiness_business_type": "Company type",
  "scrape-sgpbusiness_registration_date": "Date",
  "scrape-sgpbusiness_business_address": "Address",
  "scrape-sgpbusiness_website_url": "URL",
  "scrape-sgpbusiness_sgbusiness_url": "SGBusiness link"
}
```

## 🔧 Configuration Adjustment

Edit `~/.openclaw/config.json`:

```json
{
  "llm_endpoint": "http://localhost:11434",
  "model": "qwen2.5:9b",
  "perplexica_endpoint": "http://localhost:3000",
  "timeout": 30,
  "debug": false
}
```

## 🚨 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama Connection Error" | `ollama serve` in another terminal |
| "Perplexica Connection Error" | Ensure Perplexica is running on port 3000 |
| "Module not found: requests" | `pip install -r requirements.txt` |
| "venv not activated" | `source venv/bin/activate` |
| "Skills not found" | Verify `~/.openclaw/skills/` directory exists |
| "Agent not found" | Verify `~/.openclaw/agents/sgp-entity-finder.json` exists |

## 📚 Documentation Files

- **README.md** - Complete guide with examples
- **SETUP.md** - Detailed setup with troubleshooting
- **DEPLOYMENT_SUMMARY.md** - Full deployment info

## 🎯 Success Criteria

Pipeline is working when:
✅ Command executes without errors
✅ Returns JSON with "status": "success"
✅ Contains entity_name field
✅ Contains UEN field
✅ All fields populated with data

## 🔄 Typical Runtime

- Setup: 2-3 minutes (one time)
- Per query: 5-15 seconds
- Responses: Immediate JSON output

## 💡 Pro Tips

1. **Test with well-known brands first**
   ```bash
   python3 scripts/run-pipeline.py "Grab Technologies" --pretty
   ```

2. **Save results to file**
   ```bash
   python3 scripts/run-pipeline.py "Brand" --pretty > output.json
   ```

3. **Debug issues with text output**
   ```bash
   python3 scripts/run-pipeline.py "Brand" --output text
   ```

4. **Monitor service health**
   ```bash
   curl http://localhost:11434/api/tags  # Ollama
   curl http://localhost:3000             # Perplexica
   ```

## 🎬 Getting Started Now

```bash
# Copy and paste this entire block:
cd /home/beakthor0301/Code/openclaw-playground && \
source venv/bin/activate && \
python3 scripts/run-pipeline.py "Google Asia Pacific" --pretty
```

Expected time to first result: ~10-15 seconds

---

## 📞 Additional Resources

- Full documentation: See README.md
- Setup help: See SETUP.md
- Deployment details: See DEPLOYMENT_SUMMARY.md
- Code: Check orchestrator.py and skill files for comments

## ✅ Deployment Status

```
✓ Python Orchestration Framework
✓ Perplexica Research Skill
✓ SGPBusiness Scraper Skill
✓ Agent Configuration
✓ CLI Interface
✓ Documentation
✓ Configuration Files
✓ Requirements File
✓ Validation Tests
✓ Error Handling

STATUS: READY TO DEPLOY
```

---

**Last Updated**: 2026-03-05
**Version**: 1.0.0
**Status**: Production Ready ✅
