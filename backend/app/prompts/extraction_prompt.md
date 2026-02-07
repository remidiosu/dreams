You are an expert in Jungian dream analysis. Analyze the following dream and extract key elements.

{context}

Extract and return a JSON object with the following structure:
{{
"symbols": [
    {{
        "name": "string - the symbol name (e.g., 'water', 'door', 'snake')",
        "category": "string - one of: object, place, action, animal, nature, body, other",
        "context": "string - how the symbol appeared in the dream",
        "universal_meaning": "string or null - common symbolic meaning",
        "personal_associations": ["list of potential personal meanings"]
    }}
],
"characters": [
    {{
        "name": "string - descriptive name (e.g., 'Unknown woman', 'My father', 'Shadow figure')",
        "character_type": "string - one of: known_person, unknown_person, self, animal, mythical, abstract",
        "real_world_relation": "string or null - relationship if known person",
        "role_in_dream": "string - one of: protagonist, antagonist, helper, observer, transformer, unknown",
        "archetype": "string or null - Jungian archetype if applicable (shadow, anima, animus, wise_old_man, wise_old_woman, trickster, hero, mother, father, child, self, persona, or any other archetype)",
        "traits": ["list of character traits observed"],
        "context": "string - what they did in the dream"
    }}
],
"themes": [
    {{
        "theme": "string - the theme name (e.g., 'transformation', 'pursuit', 'loss')",
        "description": "string - how this theme manifests in the dream"
    }}
],
"emotions": [
    {{
        "emotion": "string - the emotion (e.g., 'fear', 'joy', 'anxiety')",
        "intensity": "integer 1-10",
        "emotion_type": "during"
    }}
],
"setting_analysis": "string or null - analysis of the dream setting's symbolic significance",
"jungian_interpretation": "string or null - brief Jungian interpretation of the dream's possible meaning"
}}

Important guidelines:
1. Extract ALL distinct symbols, not just the obvious ones
2. Include the dreamer as a character if they appear (type: "self")
3. For archetypes, use classic Jungian archetypes when clear, but feel free to identify other archetypal patterns
4. Be specific about context - how each element appeared in the dream
5. Emotions should reflect what the dreamer likely felt DURING the dream
6. Keep interpretations suggestive, not definitive

Return ONLY valid JSON, no markdown formatting or explanation.
