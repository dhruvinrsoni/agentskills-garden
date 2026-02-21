import os
import yaml
from typing import Dict, Any


class SkillsLoader:
    def __init__(self, repo_root: str = None):
        self.repo_root = repo_root or os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.registry_path = os.path.join(self.repo_root, 'registry.yaml')
        self.skills = {}  # name -> metadata + content
        self._load_registry()

    def _load_registry(self):
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"registry.yaml not found at {self.registry_path}")
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            reg = yaml.safe_load(f)

        # registry groups (foundation, discovery, etc.) may be present
        for section, items in reg.items():
            if section in ('version', 'templates'):
                continue
            if not isinstance(items, list):
                continue
            for entry in items:
                # entry expected to have name and path
                if not isinstance(entry, dict):
                    continue
                name = entry.get('name')
                path = entry.get('path')
                desc = entry.get('description', '')
                if name and path:
                    full = os.path.join(self.repo_root, path.replace('/', os.path.sep))
                    content = ''
                    try:
                        with open(full, 'r', encoding='utf-8') as sf:
                            content = sf.read()
                    except Exception:
                        content = ''
                    self.skills[name] = {
                        'section': section,
                        'path': path,
                        'description': desc,
                        'content': content,
                    }

    def list_skills(self) -> Dict[str, Any]:
        return self.skills

    def get_skill(self, name: str) -> Dict[str, Any]:
        return self.skills.get(name)
