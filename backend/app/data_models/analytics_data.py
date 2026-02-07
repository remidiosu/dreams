from pydantic import BaseModel
from datetime import date
from typing import Optional


class AnalyticsSummary(BaseModel):
    total_dreams: int
    dreams_this_month: int
    dreams_this_week: int
    total_symbols: int
    total_characters: int
    unique_emotions: int
    avg_emotional_intensity: Optional[float]
    lucid_dream_percentage: float
    ritual_completion_rate: float
    dreams_indexed: int
    longest_streak: int
    current_streak: int

class EmotionCount(BaseModel):
    emotion: str
    count: int
    percentage: float

class EmotionTrend(BaseModel):
    period: str
    emotion: str
    count: int

class EmotionAnalytics(BaseModel):
    total_emotion_entries: int
    most_common: list[EmotionCount]
    by_type: dict[str, list[EmotionCount]]
    intensity_avg: Optional[float]
    intensity_by_emotion: list[dict]
    trends: list[EmotionTrend]

class SymbolCount(BaseModel):
    name: str
    category: Optional[str]
    count: int
    percentage: float
    first_appeared: Optional[date]
    last_appeared: Optional[date]

class SymbolCooccurrence(BaseModel):
    symbol_a: str
    symbol_b: str
    count: int

class SymbolTrend(BaseModel):
    period: str
    symbol: str
    count: int

class SymbolAnalytics(BaseModel):
    total_symbols: int
    total_occurrences: int
    most_frequent: list[SymbolCount]
    by_category: dict[str, list[SymbolCount]]
    cooccurrences: list[SymbolCooccurrence]
    trends: list[SymbolTrend]
    new_symbols_this_month: int

class CharacterCount(BaseModel):
    name: str
    character_type: Optional[str]
    real_world_relation: Optional[str]
    count: int
    percentage: float

class ArchetypeDistribution(BaseModel):
    archetype: str
    count: int
    percentage: float
    example_characters: list[str]

class RoleDistribution(BaseModel):
    role: str
    count: int
    percentage: float

class CharacterAnalytics(BaseModel):
    total_characters: int
    total_appearances: int
    most_frequent: list[CharacterCount]
    by_type: dict[str, int]
    archetype_distribution: list[ArchetypeDistribution]
    role_distribution: list[RoleDistribution]
    recurring_characters: list[CharacterCount]

class PeriodStats(BaseModel):
    period: str
    dream_count: int
    avg_intensity: Optional[float]
    lucid_count: int
    ritual_count: int
    nightmare_count: int

class TimelineAnalytics(BaseModel):
    daily_counts: list[dict]
    weekly_counts: list[dict]
    monthly_counts: list[dict]
    by_day_of_week: dict[str, int]
    period_stats: list[PeriodStats]
    most_active_period: Optional[str]
    avg_dreams_per_week: float

class DreamPattern(BaseModel):
    pattern_type: str
    description: str
    confidence: float
    supporting_dreams: list[int]
    elements: list[str]

class LucidityAnalytics(BaseModel):
    level: str
    count: int
    percentage: float

class SleepQualityCorrelation(BaseModel):
    sleep_quality: int  # 1-5
    avg_emotional_intensity: Optional[float]
    lucid_percentage: float
    dream_count: int

class PatternAnalytics(BaseModel):
    recurring_themes: list[dict]
    symbol_emotion_correlations: list[dict]
    lucidity_distribution: list[LucidityAnalytics]
    sleep_quality_correlations: list[SleepQualityCorrelation]
    detected_patterns: list[DreamPattern]

class AnalyticsParams(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 10
