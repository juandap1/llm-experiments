import json
import os
import re
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from langchain_community.graphs import Neo4jGraph 

# --- CONFIG ---
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password123")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Set up connections (even though we don't save, it's good practice)
try:
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASS)
except:
    pass

llm = Ollama(model="gemma3:4b", base_url=OLLAMA_URL, format="json") 

def clean_json(text: str) -> str:
    """Cleans common LLM JSON formatting issues."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()

def get_course_units(course_name: str) -> List[str]:
    """
    Step 1: Generates the high-level chronological units for the course.
    Uses strict constraints to ensure academic sequencing.
    """
    print("\n1️⃣ STEP: Generating Syllabus Units...")
    syllabus_prompt = f"""
    Act as a Syllabus Designer for a rigorous University '{course_name}' course.
    Your goal is to list the major academic Units in strict chronological order.

    CRITICAL INSTRUCTION:
    Derive the units based on **Prerequisite Flow**. The course MUST start with foundational concepts necessary for later units.

    For example, Calculus I MUST begin with 'Limits' because 'Derivatives' cannot be understood without it. 'Applications' MUST come after 'Rules'.

    List 3-5 major units covering the entire course.
    Return ONLY valid JSON with the root key "units": {{ "units": ["Unit Name 1", "Unit Name 2", ...] }}
    """
    res = llm.invoke(syllabus_prompt)
    try:
        units = json.loads(clean_json(res)).get('units', [])
        print(f"   ✅ Success: Found {len(units)} Units.")
        return units
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse Syllabus JSON.")
        return []

def get_unit_content(course_name: str, unit_name: str) -> Dict[str, Any]:
    """
    Step 2: Expands a single Unit into the Concept -> Rule -> Skill hierarchy.
    Enforces pedagogical order within the unit.
    """
    print(f"   👉 STEP 2: Expanding Unit: {unit_name}...")
    
    content_prompt = f"""
    Act as a Math Teacher. 
    Course: {course_name}
    Unit: {unit_name}
    
    Break this unit down strictly: Concept -> Rule -> Skill.
    
    CRITICAL RULES (Chronology and Completeness):
    1. Include ALL standard rules for this topic (e.g., if Chain Rule is expected, include it).
    2. Skills MUST be listed in the order a student MUST learn them.
    3. Definitions (e.g., Limit Definition) MUST appear before shortcut rules (e.g., Power Rule).
    
    Return JSON:
    {{
        "concepts": [
            {{
                "name": "Concept Name",
                "rules": [
                    {{ "name": "Rule Name", "skills": [ {{ "name": "Skill Name", "description": "..." }} ] }}
                ]
            }}
        ]
    }}
    """
    res = llm.invoke(content_prompt)
    try:
        data = json.loads(clean_json(res))
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse content for unit {unit_name}. Raw LLM Response:")
        print(f"   >>> {res[:300]}...")
        return {}

    # --- New Robust Content Key Fallback ---
    # The expected key is 'concepts', but some models might wrap it differently.
    unit_data = data.get('concepts')
    
    if unit_data is None and isinstance(data, list):
        # Fallback: LLM returned a raw list of concepts instead of {"concepts": [...]}
        unit_data = data
        
    if unit_data is None:
        print(f"   ❌ Failed: Expected key 'concepts' not found in data. Keys present: {list(data.keys())}")
        return {}
    
    # Return structure wrapped correctly for consistency with the expected output format
    print("   ✅ Success: Content expanded.")
    return {"concepts": unit_data}


def get_dependencies(all_skills: List[str]) -> List[Dict[str, str]]:
    """
    Step 3: Generates the dependency edges between all skills.
    Uses aggressive negative constraints to prevent reverse causality errors.
    """
    print("\n3️⃣ STEP: Linking Dependencies...")
    if not all_skills:
        print("   No skills generated to link.")
        return []

    dep_prompt = f"""
    Act as a Logic Engine.
    List of Skills: {json.dumps(all_skills)}

    Determine STRICT prerequisites (Skill A MUST be known to DO Skill B).

    CRITICAL CONSTRAINTS (Preventing Logic Errors):
    1. **Definition** skills (e.g., 'Limit Definition') MUST be prerequisites for all **Rule-based** skills.
    2. **Basic Rules** (e.g., 'Power Rule') MUST be prerequisites for **Complex Rules** (e.g., 'Chain Rule', 'Product Rule').
    3. **DO NOT** create a dependency where the target skill is a prerequisite for the source skill (check for reverse causality, e.g., NO Product Rule -> Power Rule).
    4. **DO NOT** create circular dependencies or same-rule dependencies.

    Return JSON: {{ "dependencies": [ {{ "source": "Prereq Skill", "target": "Advanced Skill", "reason": "..." }} ] }}
    """
    
    res = llm.invoke(dep_prompt)
    try:
        data = json.loads(clean_json(res))
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse Dependency JSON. Raw LLM Response starts with: {res[:100]}...")
        return []

    # --- Robust Key Fallback ---
    deps = data.get('dependencies')
    if deps is None:
        # Check if the LLM returned a raw list or used a different key
        deps = data.get('links') or data.get('prerequisites')
    
    if deps is None and isinstance(data, list):
        # Fallback if LLM returns a raw list of dependencies
        deps = data

    if not isinstance(deps, list):
        print(f"   ❌ Failed: Expected key 'dependencies' not found or not a list. Keys present: {list(data.keys())}")
        return []

    print(f"   ✅ Success: Linked {len(deps)} dependencies.")
    return deps


def build_curriculum_pipeline_preview(course_name: str, max_units_to_run: int = 3):
    """Orchestrates the curriculum generation process."""
    
    print(f"🚀 Starting Curriculum Build PREVIEW (Modular) for: {course_name}")
    
    final_curriculum_data = {"units_content": [], "dependencies": []}
    all_skills_global = []

    # 1. Get Units
    units = get_course_units(course_name)
    
    # 2. Expand Units and Collect Skills
    # NOTE: Limiting to max_units_to_run for preview
    for index, unit_name in enumerate(units[:max_units_to_run]):
        # This is where the successful LLM call happens
        unit_content = get_unit_content(course_name, unit_name) 
        
        # --- START OF FIX: ENSURE DATA IS COLLECTED ---
        if unit_content and unit_content.get('concepts'):
            # A. Append Unit Content
            final_curriculum_data["units_content"].append({
                "unit": unit_name,
                "order": index,
                "data": unit_content
            })
            
            # B. Extract and Collect Skills
            for concept in unit_content.get('concepts', []):
                for rule in concept.get('rules', []):
                    # Safely extract skills and extend the global list
                    skills_list = [skill['name'] for skill in rule.get('skills', []) if skill.get('name')]
                    all_skills_global.extend(skills_list)
            
            # (Optional Debugging Check)
            print(f"   (Collected {len(all_skills_global)} skills so far)") 
        # --- END OF FIX ---
        else:
            print(f"   ⚠️ Unit {unit_name} skipped due to empty content.")

    # 3. Get Dependencies (This step will now run correctly)
    dependencies = get_dependencies(all_skills_global)
    final_curriculum_data["dependencies"].extend(dependencies)

    # 4. Final Output
    print("\n\n=== ✅ FINAL GENERATED CURRICULUM DATA (JSON PREVIEW) ===")
    print(json.dumps(final_curriculum_data, indent=2))
    print("=======================================================")
    
    return final_curriculum_data

if __name__ == "__main__":
    build_curriculum_pipeline_preview("Calculus I", max_units_to_run=3)