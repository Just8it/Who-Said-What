import json
import os
import re
from typing import List, Dict, Any, Optional
from book_processor import Segment

class CharacterManager:
    """
    Manages character profiles (UniversalContextManager style).
    Supports:
    - Loading/Saving config.
    - Context-Aware Prompt Generation (get_dynamic_prompt_header).
    - Local Autosync (update_profiles).
    - Active Cleaning & Enrichment (enrich_db) via LLM.
    """
    def __init__(self, config_path: str = "book_config_dcc.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._ensure_structure()
        self.characters = self.config.get("characters", {}) # Helper ref

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _ensure_structure(self):
        """Ensures the basic schema exists."""
        if "characters" not in self.config:
            self.config["characters"] = {}
        if "book_title" not in self.config:
            self.config["book_title"] = "Unknown Book"
        if "pov_type" not in self.config:
            self.config["pov_type"] = "third_person"

    def save_config(self):
        """Persists the current state to JSON."""
        self.config["characters"] = self.characters
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get_dynamic_prompt_header(self, text_chunk: str) -> str:
        """
        Scans the text chunk and builds a custom header with Static + Evolving descriptions.
        """
        active_chars = []
        pov_char = self.config.get("pov_character", "")
        pov_type = self.config.get("pov_type", "third_person")
        
        # Helper to format description
        def format_desc(data):
            base = data.get("description", "Unknown")
            evo = data.get("evolving_description", "")
            return f"{base} [Current: {evo}]" if evo else base

        # 1. Start with POV Character
        if pov_type == "first_person" and pov_char:
            if re.search(r'\bI\b', text_chunk) or re.search(r'\b(me|my)\b', text_chunk, re.IGNORECASE):
                data = self.characters.get(pov_char, {})
                active_chars.append(f"- {pov_char}: {format_desc(data)} [Aliases: 'I', 'Me']")

        # 2. Scan for others
        for name, data in self.characters.items():
            if name == pov_char and pov_type == "first_person": continue 
            
            aliases = data.get("aliases", []) + [name]
            if any(alias in text_chunk for alias in aliases):
                active_chars.append(f"- {name}: {format_desc(data)}")

        if "Narrator" not in [x.split(":")[0][2:].strip() for x in active_chars]:
             active_chars.append("- Narrator: Describes actions and scenes.")

        header = "### KNOWN SPEAKERS IN THIS SCENE:\n" + "\n".join(active_chars)
        return header

    def update_profiles(self, segments: List[Segment], chapter_id: int = -1):
        """
        Local Autosync: Adds new speakers and updates 'last_seen'.
        """
        changes_made = False
        
        for seg in segments:
            speaker_name = seg.speaker.strip()
            if not speaker_name: continue

            if speaker_name not in self.characters:
                # NEW CHARACTER
                self.characters[speaker_name] = {
                    "description": f"Auto-detected in chapter {chapter_id}.",
                    "voice_signature": "Unknown",
                    "aliases": [],
                    "last_seen": chapter_id
                }
                changes_made = True
            else:
                # EXISTING
                if self.characters[speaker_name].get("last_seen", -1) != chapter_id:
                    self.characters[speaker_name]["last_seen"] = chapter_id
                    changes_made = True
        
        if changes_made:
            self.save_config()

    def enrich_db(self, llm_client, recent_segments: List[Segment], model: str):
        """
        The 'Second Pass' (Stage 2). 
        1. Deduplicates newly found names (Consolidation).
        2. Generates active/evolving descriptions (Bulk Optimized).
        """
        print("[DB] Starting Enrichment Cycle...")
        
        # --- SUB-STEP 1: Deduplication (CONDITIONAL) ---
        # Optimization: Only run if we have "Auto-detected" (new) characters.
        has_new_chars = any("Auto-detected" in v.get("description", "") for v in self.characters.values())
        
        if has_new_chars:
            names_data = {
                k: v.get('description','Unknown')[:150] 
                for k, v in self.characters.items()
            }
            if len(names_data) > 3: 
                 self._run_safe_deduplication(llm_client, model, names_data)
        else:
            print("[DB] Skipping Deduplication (Stable Cast).")

        # --- SUB-STEP 2: Description Generation ---
        active_names = set(s.speaker for s in recent_segments)
        
        base_updates = []
        evolve_updates = {} # Name -> ContextString
        
        for name in active_names:
            if name not in self.characters: continue

            char_data = self.characters[name]
            is_auto = "Auto-detected" in char_data.get("description", "")
            
            # Gather Context
            context_samples = self._gather_contextual_samples(recent_segments, name)
            if not context_samples: continue
            
            # OPTIMIZATION: Chatterbox Threshold
            # If context is too short (< 25 words), LLM can't infer much. Skip to save $.
            if len(context_samples.split()) < 25:
                # print(f"[DB] Skipping update for '{name}' (Insufficient Context)")
                continue
            
            if is_auto:
                base_updates.append((name, context_samples))
            else:
                evolve_updates[name] = context_samples

        # A. Handle New Characters (Individual - need specific Identity focus)
        for name, samples in base_updates:
            self._generate_description(llm_client, model, name, samples, "description", "BASE")
            
        # B. Handle Evolving Characters (Bulk - Optimization)
        if evolve_updates:
            self._bulk_update_evolving_descriptions(llm_client, model, evolve_updates)

    def _gather_contextual_samples(self, segments: List[Segment], target_speaker: str, max_samples: int = 3) -> str:
        samples = []
        count = 0
        for i, seg in enumerate(segments):
            if seg.speaker == target_speaker:
                window = []
                if i > 0: window.append(f"<{segments[i-1].speaker}>: {segments[i-1].text}")
                window.append(f"<{target_speaker}>: {seg.text}")
                if i < len(segments)-1: window.append(f"<{segments[i+1].speaker}>: {segments[i+1].text}")
                samples.append("\n".join(window))
                count += 1
                if count >= max_samples: break
        return "\n---\n".join(samples)

    def _run_safe_deduplication(self, client, model, names_data):
        # HARDCODED PROTECTION: Names that should NEVER be deleted/merged into others
        protected_names = {
            "Carl", "Crawler Carl", 
            "Donut", "Princess Donut", 
            "Narrator", 
            "System AI", "System",
            "Mordecai", 
            "Mrs. Parsons"
        }
        
        prompt = f"""
You are a Database Administrator. Identify duplicates.
Rules:
1. Merge "Generic" -> "Specific" (e.g. "The Guard" -> "Guard 1").
2. Descriptions MUST MATCH.
3. Threshold: 9/10.
4. **DO NOT MERGE** distinct entities (e.g. "Narrator" is NOT "Lexis").

### DATABASE:
{json.dumps(names_data, indent=2)}

### OUTPUT JSON:
{{ "merges": [ {{ "target": "Generic", "source": "Specific", "confidence": 10 }} ] }}
"""
        try:
            resp = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}, temperature=0.0
            )
            data = json.loads(resp.choices[0].message.content)
            merges = data.get("merges", [])
            
            changes = False
            for m in merges:
                dupe, prime = m.get("target"), m.get("source")
                conf = m.get("confidence", 0)

                # 1. Check Threshold
                if conf < 9: 
                    # print(f"[DB] Skipped low-conf merge: {dupe} -> {prime}")
                    continue
                
                # 2. Check Protection
                if dupe in protected_names:
                    print(f"[DB] BLOCKED PROTECTED MERGE: '{dupe}' -> '{prime}'")
                    continue
                    
                if dupe in self.characters and prime in self.characters and dupe != prime:
                    print(f"[DB] SAFE MERGE: {dupe} -> {prime}")
                    self.characters[prime]["aliases"] = list(set(self.characters[prime].get("aliases",[]) + self.characters[dupe].get("aliases",[]) + [dupe]))
                    del self.characters[dupe]
                    changes = True
            if changes: self.save_config()
        except Exception as e:
            print(f"[DB] Dedup Error: {e}")

    def _bulk_update_evolving_descriptions(self, client, model, text_samples_map: Dict[str, str]):
        """
        Updates multiple characters in one shot to save API calls.
        """
        payload = ""
        for name, text in text_samples_map.items():
            payload += f"--- CHARACTER: {name} ---\n{text[:800]}\n\n"

        prompt = f"""
You are a Character Profiler.
Update the 'Current Persona' for the characters below based on the provided dialogue samples.

### INSTRUCTIONS:
- For EACH character, write a comprehensive summary (max 40 words) of their **Current Mindset & Internal Growth**.
- Stick to the provided text.
- Output JSON mapping names to descriptions.

### SAMPLES:
{payload}

### OUTPUT JSON:
{{
  "Character Name": "New Description...",
  ...
}}
"""
        try:
            resp = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}, temperature=0.3
            )
            data = json.loads(resp.choices[0].message.content)
            
            changes = False
            for name, desc in data.items():
                if name in self.characters:
                    print(f"[DB] Bulk Update '{name}': {desc[:50]}...")
                    self.characters[name]["evolving_description"] = desc
                    changes = True
            
            if changes: self.save_config()
            
        except Exception as e:
            print(f"[DB] Bulk API Error: {e}")

    def _generate_description(self, client, model, name, text_sample, target_field, prompt_type):
        if prompt_type == "BASE":
            instruction = f"Define the Identity/Role of '{name}' based on their dialogue."
            length_constraint = "max 20 words"
            # Keep individual generation for NEW/Base chars as they are rare
        else:
             # Legacy fallback, but main path is now Bulk
            instruction = f"Update Persona for '{name}'."
            length_constraint = "max 40 words"

        prompt = f"""
You are a Character Profiler.
{instruction}

### INPUT SAMPLES:
{text_sample[:1000]}

### INSTRUCTION:
- Focus ONLY on the speaker <{name}>.
- Output text only ({length_constraint}).
"""
        try:
            resp = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], temperature=0.3
            )
            val = resp.choices[0].message.content.strip()
            print(f"[DB] Updated {target_field} for '{name}': {val}")
            self.characters[name][target_field] = val
            self.save_config()
        except Exception as e:
            print(f"[DB] Gen Error: {e}")
