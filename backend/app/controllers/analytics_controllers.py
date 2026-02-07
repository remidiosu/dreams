from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.analytics_repository import AnalyticsRepository
from app.data_models.analytics_data import (
    AnalyticsSummary,
    EmotionAnalytics,
    EmotionCount,
    EmotionTrend,
    SymbolAnalytics,
    SymbolCount,
    SymbolCooccurrence,
    SymbolTrend,
    CharacterAnalytics,
    CharacterCount,
    ArchetypeDistribution,
    RoleDistribution,
    TimelineAnalytics,
    PeriodStats,
    PatternAnalytics,
    LucidityAnalytics,
    SleepQualityCorrelation,
    DreamPattern,
)


analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    stats = await repo.get_summary_stats(user_id)

    return AnalyticsSummary(**stats)


@analytics_router.get("/emotions", response_model=EmotionAnalytics)
async def get_emotion_analytics(
        date_from: Optional[date] = Query(None, description="Start date filter"),
        date_to: Optional[date] = Query(None, description="End date filter"),
        limit: int = Query(10, ge=1, le=50, description="Number of top emotions to return"),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_emotion_analytics(user_id, date_from, date_to, limit)

    return EmotionAnalytics(
        total_emotion_entries=data["total_emotion_entries"],
        most_common=[EmotionCount(**e) for e in data["most_common"]],
        by_type={
            k: [EmotionCount(**e) for e in v]
            for k, v in data["by_type"].items()
        },
        intensity_avg=data["intensity_avg"],
        intensity_by_emotion=data["intensity_by_emotion"],
        trends=[EmotionTrend(**t) for t in data["trends"]],
    )


@analytics_router.get("/emotions/frequency", response_model=list[EmotionCount])
async def get_emotion_frequency(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(15, ge=1, le=50),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_emotion_analytics(user_id, date_from, date_to, limit)
    
    return [EmotionCount(**e) for e in data["most_common"]]


@analytics_router.get("/emotions/trends", response_model=list[EmotionTrend])
async def get_emotion_trends(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_emotion_analytics(user_id, date_from, date_to, limit=50)
    
    return [EmotionTrend(**t) for t in data["trends"]]


@analytics_router.get("/symbols", response_model=SymbolAnalytics)
async def get_symbol_analytics(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(10, ge=1, le=50),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_symbol_analytics(user_id, date_from, date_to, limit)

    return SymbolAnalytics(
        total_symbols=data["total_symbols"],
        total_occurrences=data["total_occurrences"],
        most_frequent=[SymbolCount(**s) for s in data["most_frequent"]],
        by_category={
            k: [SymbolCount(**s) for s in v]
            for k, v in data["by_category"].items()
        },
        cooccurrences=[SymbolCooccurrence(**c) for c in data["cooccurrences"]],
        trends=[SymbolTrend(**t) for t in data["trends"]],
        new_symbols_this_month=data["new_symbols_this_month"],
    )


@analytics_router.get("/symbols/frequency", response_model=list[SymbolCount])
async def get_symbol_frequency(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_symbol_analytics(user_id, date_from, date_to, limit)
    
    return [SymbolCount(**s) for s in data["most_frequent"]]


@analytics_router.get("/symbols/cooccurrences", response_model=list[SymbolCooccurrence])
async def get_symbol_cooccurrences(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(15, ge=1, le=50),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_symbol_analytics(user_id, date_from, date_to, limit)
    
    return [SymbolCooccurrence(**c) for c in data["cooccurrences"]]


@analytics_router.get("/symbols/trends", response_model=list[SymbolTrend])
async def get_symbol_trends(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_symbol_analytics(user_id, date_from, date_to, limit=100)
    
    return [SymbolTrend(**t) for t in data["trends"]]


@analytics_router.get("/characters", response_model=CharacterAnalytics)
async def get_character_analytics(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(10, ge=1, le=50),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_character_analytics(user_id, date_from, date_to, limit)

    return CharacterAnalytics(
        total_characters=data["total_characters"],
        total_appearances=data["total_appearances"],
        most_frequent=[CharacterCount(**c) for c in data["most_frequent"]],
        by_type=data["by_type"],
        archetype_distribution=[ArchetypeDistribution(**a) for a in data["archetype_distribution"]],
        role_distribution=[RoleDistribution(**r) for r in data["role_distribution"]],
        recurring_characters=[CharacterCount(**c) for c in data["recurring_characters"]],
    )


@analytics_router.get("/characters/frequency", response_model=list[CharacterCount])
async def get_character_frequency(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_character_analytics(user_id, date_from, date_to, limit)
    
    return [CharacterCount(**c) for c in data["most_frequent"]]


@analytics_router.get("/characters/archetypes", response_model=list[ArchetypeDistribution])
async def get_archetype_distribution(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_character_analytics(user_id, date_from, date_to, limit=100)
    
    return [ArchetypeDistribution(**a) for a in data["archetype_distribution"]]


@analytics_router.get("/characters/roles", response_model=list[RoleDistribution])
async def get_role_distribution(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_character_analytics(user_id, date_from, date_to, limit=100)
    
    return [RoleDistribution(**r) for r in data["role_distribution"]]


@analytics_router.get("/timeline", response_model=TimelineAnalytics)
async def get_timeline_analytics(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_timeline_analytics(user_id, date_from, date_to)

    return TimelineAnalytics(
        daily_counts=data["daily_counts"],
        weekly_counts=data["weekly_counts"],
        monthly_counts=data["monthly_counts"],
        by_day_of_week=data["by_day_of_week"],
        period_stats=[PeriodStats(**p) for p in data["period_stats"]],
        most_active_period=data["most_active_period"],
        avg_dreams_per_week=data["avg_dreams_per_week"],
    )


@analytics_router.get("/timeline/daily", response_model=list[dict])
async def get_daily_dream_counts(
        days: int = Query(30, ge=7, le=90),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_timeline_analytics(user_id)
    
    return data["daily_counts"][-days:]


@analytics_router.get("/timeline/monthly", response_model=list[dict])
async def get_monthly_dream_counts(
        months: int = Query(12, ge=3, le=24),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_timeline_analytics(user_id)
    
    return data["monthly_counts"][-months:]


@analytics_router.get("/patterns", response_model=PatternAnalytics)
async def get_pattern_analytics(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_pattern_analytics(user_id, date_from, date_to)

    return PatternAnalytics(
        recurring_themes=data["recurring_themes"],
        symbol_emotion_correlations=data["symbol_emotion_correlations"],
        lucidity_distribution=[LucidityAnalytics(**l) for l in data["lucidity_distribution"]],
        sleep_quality_correlations=[SleepQualityCorrelation(**s) for s in data["sleep_quality_correlations"]],
        detected_patterns=[DreamPattern(**p) for p in data["detected_patterns"]],
    )


@analytics_router.get("/patterns/correlations", response_model=list[dict])
async def get_symbol_emotion_correlations(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        min_count: int = Query(2, ge=1, description="Minimum co-occurrence count"),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_pattern_analytics(user_id, date_from, date_to)

    correlations = [
        c for c in data["symbol_emotion_correlations"]
        if c["count"] >= min_count
    ]
    return correlations


@analytics_router.get("/patterns/lucidity", response_model=list[LucidityAnalytics])
async def get_lucidity_distribution(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_pattern_analytics(user_id, date_from, date_to)
    
    return [LucidityAnalytics(**l) for l in data["lucidity_distribution"]]


@analytics_router.get("/patterns/sleep-quality", response_model=list[SleepQualityCorrelation])
async def get_sleep_quality_correlations(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_pattern_analytics(user_id, date_from, date_to)
    
    return [SleepQualityCorrelation(**s) for s in data["sleep_quality_correlations"]]


@analytics_router.get("/patterns/detected", response_model=list[DreamPattern])
async def get_detected_patterns(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    data = await repo.get_pattern_analytics(user_id, date_from, date_to)
    
    return [DreamPattern(**p) for p in data["detected_patterns"]]


@analytics_router.get("/jungian/shadow-activity", response_model=dict)
async def get_shadow_activity(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    char_data = await repo.get_character_analytics(user_id, date_from, date_to, limit=100)
    pattern_data = await repo.get_pattern_analytics(user_id, date_from, date_to)

    shadow_stats = None
    for arch in char_data["archetype_distribution"]:
        if arch["archetype"].lower() == "shadow":
            shadow_stats = arch
            break

    shadow_emotions = []
    for corr in pattern_data["symbol_emotion_correlations"]:
        emotion = corr.get("emotion", "")
        if emotion and emotion not in shadow_emotions:
            shadow_emotions.append(emotion)
        if len(shadow_emotions) >= 5:
            break

    return {
        "shadow_appearances": shadow_stats["count"] if shadow_stats else 0,
        "shadow_percentage": shadow_stats["percentage"] if shadow_stats else 0,
        "example_characters": shadow_stats["example_characters"] if shadow_stats else [],
        "common_emotions": shadow_emotions or ["No emotion data yet"],
        "insight": "Shadow figures often represent repressed aspects of the self that seek integration.",
    }


@analytics_router.get("/jungian/anima-animus", response_model=dict)
async def get_anima_animus_activity(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)
    char_data = await repo.get_character_analytics(user_id, date_from, date_to, limit=100)

    anima_stats = None
    animus_stats = None

    for arch in char_data["archetype_distribution"]:
        if arch["archetype"].lower() == "anima":
            anima_stats = arch
        elif arch["archetype"].lower() == "animus":
            animus_stats = arch

    return {
        "anima": {
            "appearances": anima_stats["count"] if anima_stats else 0,
            "percentage": anima_stats["percentage"] if anima_stats else 0,
            "characters": anima_stats["example_characters"] if anima_stats else [],
        },
        "animus": {
            "appearances": animus_stats["count"] if animus_stats else 0,
            "percentage": animus_stats["percentage"] if animus_stats else 0,
            "characters": animus_stats["example_characters"] if animus_stats else [],
        },
        "insight": "The Anima/Animus represents the unconscious feminine/masculine aspects and often appears as guides or challenging figures.",
    }


@analytics_router.get("/jungian/individuation-progress", response_model=dict)
async def get_individuation_progress(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    repo = AnalyticsRepository(db)

    summary = await repo.get_summary_stats(user_id)
    char_data = await repo.get_character_analytics(user_id, limit=100)
    pattern_data = await repo.get_pattern_analytics(user_id)

    archetype_diversity = len(char_data["archetype_distribution"])
    recurring_count = len(char_data["recurring_characters"])
    pattern_count = len(pattern_data["detected_patterns"])
    theme_count = len(pattern_data["recurring_themes"])

    journal_consistency = min(100, summary["current_streak"] * 10 + summary["longest_streak"] * 5)
    archetype_engagement = min(100, archetype_diversity * 15)
    pattern_awareness = min(100, (pattern_count + theme_count) * 10)
    ritual_practice = summary["ritual_completion_rate"]

    overall_score = (journal_consistency + archetype_engagement + pattern_awareness + ritual_practice) / 4

    return {
        "overall_score": round(overall_score, 1),
        "metrics": {
            "journal_consistency": round(journal_consistency, 1),
            "archetype_engagement": round(archetype_engagement, 1),
            "pattern_awareness": round(pattern_awareness, 1),
            "ritual_practice": round(ritual_practice, 1),
        },
        "stats": {
            "total_dreams": summary["total_dreams"],
            "archetypes_encountered": archetype_diversity,
            "patterns_identified": pattern_count,
            "recurring_themes": theme_count,
            "current_streak": summary["current_streak"],
        },
        "recommendations": _generate_recommendations(
            journal_consistency, archetype_engagement, pattern_awareness, ritual_practice
        ),
    }


def _generate_recommendations(consistency: float, archetype: float, pattern: float, ritual: float) -> list[str]:
    recommendations = []

    if consistency < 50:
        recommendations.append("Try to journal your dreams more consistently. Even brief notes help build awareness.")

    if archetype < 30:
        recommendations.append(
            "Pay attention to character roles in your dreams. Who appears as helpers, challengers, or guides?")

    if pattern < 40:
        recommendations.append("Look for recurring symbols or themes. These often carry important personal meaning.")

    if ritual < 30:
        recommendations.append(
            "Consider adding a simple ritual after significant dreams to help integrate their messages.")

    if not recommendations:
        recommendations.append(
            "Excellent progress! Continue your practice and explore the deeper patterns emerging in your dreams.")

    return recommendations
