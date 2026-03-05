"""
OpenClaw-compatible Python orchestration framework
Manages skills, agents, and LLM orchestration
"""
import json
import os
import sys
import importlib.util
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class OllamaGateway:
    """Interface to Ollama LLM engine"""

    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "qwen2.5:9b"):
        self.endpoint = endpoint
        self.model = model

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Query the Ollama model"""
        try:
            import requests
        except ImportError:
            return f"[Mock] Ollama response to: {prompt}"

        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"[Error] Ollama returned status {response.status_code}"
        except Exception as e:
            return f"[Error] Failed to connect to Ollama: {str(e)}"


class SkillRegistry:
    """Manages and executes skills"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.load_skills()

    def load_skills(self):
        """Load all available skills from skills directory"""
        if not self.skills_dir.exists():
            print(f"Skills directory not found: {self.skills_dir}")
            return

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_name = skill_dir.name
                config_file = skill_dir / "skill.json"

                if config_file.exists():
                    with open(config_file) as f:
                        self.skills[skill_name] = {
                            "config": json.load(f),
                            "path": skill_dir
                        }

    def execute_skill(self, skill_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific skill"""
        if skill_name not in self.skills:
            return {
                "status": "error",
                "message": f"Skill '{skill_name}' not found"
            }

        skill = self.skills[skill_name]
        skill_path = skill["path"]

        # Load and execute skill module
        skill_module_path = skill_path / "skill.py"
        if skill_module_path.exists():
            try:
                spec = importlib.util.spec_from_file_location(skill_name, skill_module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'execute'):
                    result = module.execute(inputs)
                    result["status"] = "success"
                    return result
                else:
                    return {"status": "error", "message": f"Skill '{skill_name}' has no execute function"}
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error executing skill '{skill_name}': {str(e)}"
                }
        else:
            return {
                "status": "error",
                "message": f"Skill module not found at {skill_module_path}"
            }


class Agent:
    """OpenClaw-compatible Agent for orchestrating skills"""

    def __init__(self, config: Dict[str, Any], skill_registry: SkillRegistry, llm: OllamaGateway):
        self.config = config
        self.skills = skill_registry
        self.llm = llm
        self.name = config.get("name", "Unknown Agent")
        self.description = config.get("description", "")
        self.goal = config.get("goal", "")
        self.skills_sequence = config.get("skills", [])

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent workflow"""
        print(f"\n[Agent] {self.name} starting execution")
        print(f"[Agent] Input: {input_data}")

        # Initialize context with input
        context = {"input": input_data, "results": {}}

        # Execute skills in sequence
        for skill_config in self.skills_sequence:
            skill_name = skill_config.get("name")
            print(f"\n[Agent] Executing skill: {skill_name}")

            # Prepare inputs for this skill
            skill_inputs = self._prepare_skill_inputs(skill_config, context)
            print(f"[Agent] Skill inputs: {skill_inputs}")

            # Execute the skill
            result = self.skills.execute_skill(skill_name, skill_inputs)
            print(f"[Agent] Skill result: {result}")

            # Store result in context for next skill
            context["results"][skill_name] = result

            if result.get("status") == "error":
                print(f"[Agent] Error in skill {skill_name}, stopping execution")
                return {
                    "status": "error",
                    "message": f"Skill {skill_name} failed: {result.get('message')}",
                    "results": context["results"]
                }

        # Combine final results
        return self._format_output(context)

    def _prepare_skill_inputs(self, skill_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare inputs for a skill based on skill config and current context"""
        inputs = {}

        # Get static inputs
        if "inputs" in skill_config:
            inputs.update(skill_config["inputs"])

        # Get dynamic inputs from context
        if "input_from_context" in skill_config:
            for key, path in skill_config["input_from_context"].items():
                # Navigate context using dot notation: "results.previous_skill.output"
                parts = path.split(".")
                value = context
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        break
                if value is not None:
                    inputs[key] = value

        return inputs

    def _format_output(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format final output from all skill results"""
        # Extract the most relevant result for output
        all_results = context.get("results", {})

        final_output = {
            "status": "success",
            "input": context.get("input"),
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

        # Merge all skill results
        for skill_name, result in all_results.items():
            if result.get("status") == "success":
                # Extract data fields from successful skills
                for key, value in result.items():
                    if key not in ["status"]:
                        final_output[f"{skill_name}_{key}"] = value

        return final_output


class OpenClawOrchestrator:
    """Main orchestrator for the OpenClaw pipeline"""

    def __init__(self, config_dir: str = os.path.expanduser("~/.openclaw")):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.skills_dir = self.config_dir / "skills"
        self.agents_dir = self.config_dir / "agents"

        # Load main configuration
        self.config = self._load_config()

        # Initialize components
        self.llm = OllamaGateway(
            endpoint=self.config.get("llm_endpoint", "http://localhost:11434"),
            model=self.config.get("model", "qwen2.5:9b")
        )

        self.skill_registry = SkillRegistry(str(self.skills_dir))

    def _load_config(self) -> Dict[str, Any]:
        """Load main configuration file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        else:
            return {
                "llm_endpoint": "http://localhost:11434",
                "model": "qwen2.5:9b",
                "perplexica_endpoint": "http://localhost:3000"
            }

    def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific agent"""
        agent_file = self.agents_dir / f"{agent_name}.json"

        if not agent_file.exists():
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' not found at {agent_file}"
            }

        with open(agent_file) as f:
            agent_config = json.load(f)

        agent = Agent(agent_config, self.skill_registry, self.llm)
        return agent.run(input_data)


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <agent_name> <input_brand>")
        print("\nExample: python orchestrator.py sgp-entity-finder 'Grab Technologies'")
        sys.exit(1)

    agent_name = sys.argv[1]
    input_brand = sys.argv[2] if len(sys.argv) > 2 else ""

    orchestrator = OpenClawOrchestrator()
    result = orchestrator.run_agent(agent_name, {"brand": input_brand})

    print("\n" + "="*60)
    print("FINAL OUTPUT")
    print("="*60)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
