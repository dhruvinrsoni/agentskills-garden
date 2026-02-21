import difflib
import os
import requests
from typing import Optional

from .skills_loader import SkillsLoader


class Orchestrator:
    def __init__(self, repo_root: str = None, model_endpoint: Optional[str] = None):
        self.loader = SkillsLoader(repo_root)
        self.model_endpoint = model_endpoint or os.environ.get('MODEL_ENDPOINT')

    def find_best_skill(self, user_intent: str):
        # naive librarian: match against name + description using difflib
        candidates = []
        for name, meta in self.loader.list_skills().items():
            text = name + ' ' + (meta.get('description') or '')
            ratio = difflib.SequenceMatcher(a=user_intent.lower(), b=text.lower()).ratio()
            candidates.append((ratio, name))
        candidates.sort(reverse=True)
        if not candidates:
            return None
        best = candidates[0][1]
        return self.loader.get_skill(best)

    def build_prompt(self, skill_meta: dict, user_intent: str):
        # Use the skill content + a short instruction template
        skill_text = skill_meta.get('content', '')
        header = f"Skill: {skill_meta.get('path')}\nDescription: {skill_meta.get('description')}\n"
        prompt = header + "\nUser Intent:\n" + user_intent + "\n\nSkill Context:\n" + (skill_text[:4000])
        return prompt

    def call_model(self, prompt: str) -> str:
        # Minimal: if MODEL_ENDPOINT is set, POST there; otherwise return demo text
        if self.model_endpoint:
            try:
                resp = requests.post(self.model_endpoint, json={'prompt': prompt, 'max_tokens': 512}, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                # try common shapes
                if isinstance(data, dict):
                    if 'text' in data:
                        return data['text']
                    if 'generated_text' in data:
                        return data['generated_text']
                    # TGI-like
                    if 'results' in data and isinstance(data['results'], list):
                        return data['results'][0].get('text', str(data))
                return str(data)
            except Exception as e:
                return f"[model error] {e}"
        # fallback demo
        return "[demo output] This is a local demo response. Replace with MODEL_ENDPOINT for real generation."

    def run_task(self, user_intent: str):
        skill = self.find_best_skill(user_intent)
        if not skill:
            return {'error': 'no-skill-found'}
        prompt = self.build_prompt(skill, user_intent)
        output = self.call_model(prompt)
        return {'skill': skill.get('path'), 'prompt': prompt, 'output': output}
