from enum import Enum


class LucidityLevel(str, Enum):
    NONE = "none"
    BRIEF = "brief_awareness"
    PARTIAL = "partial"
    FULL = "full"


class CharacterType(str, Enum):
    KNOWN_PERSON = "known_person"
    UNKNOWN_PERSON = "unknown_person"
    SELF = "self"
    ANIMAL = "animal"
    MYTHICAL = "mythical"
    ABSTRACT = "abstract"


class RoleInDream(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    HELPER = "helper"
    OBSERVER = "observer"
    TRANSFORMER = "transformer"
    UNKNOWN = "unknown"


class Archetype(str, Enum):
    SHADOW = "shadow"
    ANIMA = "anima"
    ANIMUS = "animus"
    WISE_OLD_MAN = "wise_old_man"
    WISE_OLD_WOMAN = "wise_old_woman"
    TRICKSTER = "trickster"
    HERO = "hero"
    MOTHER = "mother"
    FATHER = "father"
    CHILD = "child"
    SELF = "self"
    PERSONA = "persona"


class SymbolCategory(str, Enum):
    OBJECT = "object"
    PLACE = "place"
    ACTION = "action"
    ANIMAL = "animal"
    NATURE = "nature"
    BODY = "body"
    OTHER = "other"


class EmotionType(str, Enum):
    DURING = "during"
    WAKING = "waking"


class AssociationSource(str, Enum):
    USER = "user"
    AI_SUGGESTED = "ai_suggested"


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class QueryType(str, Enum):
    PATTERN = "pattern"
    SYMBOL = "symbol"
    TIMELINE = "timeline"
    GENERAL = "general"


class EmotionValence(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    AMBIGUOUS = "ambiguous"
    