from typing import Optional
from datetime import date, datetime, timedelta
from collections import Counter

from sqlalchemy import select, func, and_, case, distinct, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dreams import Dream
from app.models.dream_emotions import DreamEmotion
from app.models.dream_symbols import DreamSymbol
from app.models.dream_characters import DreamCharacter
from app.models.dream_themes import DreamTheme
from app.models.symbols import Symbol
from app.models.characters import Character
from app.models.enums.dream_enums import LucidityLevel


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary_stats(self, user_id: int) -> dict:
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        total_query = select(func.count(Dream.id)).where(Dream.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_dreams = total_result.scalar() or 0

        month_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.created_at >= start_of_month)
        )
        month_result = await self.db.execute(month_query)
        dreams_this_month = month_result.scalar() or 0

        week_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.created_at >= start_of_week)
        )
        week_result = await self.db.execute(week_query)
        dreams_this_week = week_result.scalar() or 0

        symbols_query = select(func.count(Symbol.id)).where(Symbol.user_id == user_id)
        symbols_result = await self.db.execute(symbols_query)
        total_symbols = symbols_result.scalar() or 0
        chars_query = select(func.count(Character.id)).where(Character.user_id == user_id)
        chars_result = await self.db.execute(chars_query)
        total_characters = chars_result.scalar() or 0
        emotions_query = (
            select(func.count(distinct(DreamEmotion.emotion)))
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(Dream.user_id == user_id)
        )
        emotions_result = await self.db.execute(emotions_query)
        unique_emotions = emotions_result.scalar() or 0

        intensity_query = (
            select(func.avg(Dream.emotional_intensity))
            .where(and_(Dream.user_id == user_id, Dream.emotional_intensity.isnot(None)))
        )
        intensity_result = await self.db.execute(intensity_query)
        avg_intensity = intensity_result.scalar()

        lucid_query = select(func.count(Dream.id)).where(
            and_(
                Dream.user_id == user_id,
                Dream.lucidity_level.in_([LucidityLevel.PARTIAL, LucidityLevel.FULL])
            )
        )
        lucid_result = await self.db.execute(lucid_query)
        lucid_count = lucid_result.scalar() or 0
        lucid_percentage = (lucid_count / total_dreams * 100) if total_dreams > 0 else 0

        ritual_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.ritual_completed == True)
        )
        ritual_result = await self.db.execute(ritual_query)
        ritual_count = ritual_result.scalar() or 0
        ritual_rate = (ritual_count / total_dreams * 100) if total_dreams > 0 else 0

        indexed_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.is_indexed == True)
        )
        indexed_result = await self.db.execute(indexed_query)
        dreams_indexed = indexed_result.scalar() or 0

        streaks = await self._calculate_streaks(user_id)

        return {
            "total_dreams": total_dreams,
            "dreams_this_month": dreams_this_month,
            "dreams_this_week": dreams_this_week,
            "total_symbols": total_symbols,
            "total_characters": total_characters,
            "unique_emotions": unique_emotions,
            "avg_emotional_intensity": round(avg_intensity, 2) if avg_intensity else None,
            "lucid_dream_percentage": round(lucid_percentage, 1),
            "ritual_completion_rate": round(ritual_rate, 1),
            "dreams_indexed": dreams_indexed,
            "longest_streak": streaks["longest"],
            "current_streak": streaks["current"],
        }

    async def _calculate_streaks(self, user_id: int) -> dict:
        query = (
            select(Dream.dream_date)
            .where(Dream.user_id == user_id)
            .order_by(Dream.dream_date.desc())
            .distinct()
        )
        result = await self.db.execute(query)
        dates = [row[0] for row in result.fetchall()]

        if not dates:
            return {"longest": 0, "current": 0}

        current_streak = 0
        today = date.today()
        check_date = today

        for d in dates:
            if d == check_date or d == check_date - timedelta(days=1):
                current_streak += 1
                check_date = d - timedelta(days=1)
            else:
                break

        if len(dates) < 2:
            return {"longest": current_streak, "current": current_streak}

        longest_streak = 1
        current_run = 1
        sorted_dates = sorted(set(dates))

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1

        return {"longest": longest_streak, "current": current_streak}

    async def get_emotion_analytics(
            self,
            user_id: int,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            limit: int = 10,
    ) -> dict:
        base_filter = [Dream.user_id == user_id]
        if date_from:
            base_filter.append(Dream.dream_date >= date_from)
        if date_to:
            base_filter.append(Dream.dream_date <= date_to)

        total_query = (
            select(func.count(DreamEmotion.id))
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter))
        )
        total_result = await self.db.execute(total_query)
        total_entries = total_result.scalar() or 0

        common_query = (
            select(DreamEmotion.emotion, func.count(DreamEmotion.id).label("count"))
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(DreamEmotion.emotion)
            .order_by(func.count(DreamEmotion.id).desc())
            .limit(limit)
        )
        common_result = await self.db.execute(common_query)
        most_common = [
            {
                "emotion": row[0],
                "count": row[1],
                "percentage": round(row[1] / total_entries * 100, 1) if total_entries > 0 else 0,
            }
            for row in common_result.fetchall()
        ]

        by_type_query = (
            select(
                DreamEmotion.emotion_type,
                DreamEmotion.emotion,
                func.count(DreamEmotion.id).label("count")
            )
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(DreamEmotion.emotion_type, DreamEmotion.emotion)
            .order_by(func.count(DreamEmotion.id).desc())
        )
        by_type_result = await self.db.execute(by_type_query)

        by_type = {"during": [], "waking": []}
        type_totals = {"during": 0, "waking": 0}

        for row in by_type_result.fetchall():
            emotion_type = row[0].value if row[0] else "during"
            type_totals[emotion_type] = type_totals.get(emotion_type, 0) + row[2]

        by_type_result = await self.db.execute(by_type_query)
        for row in by_type_result.fetchall():
            emotion_type = row[0].value if row[0] else "during"
            total_for_type = type_totals.get(emotion_type, 1)
            by_type[emotion_type].append({
                "emotion": row[1],
                "count": row[2],
                "percentage": round(row[2] / total_for_type * 100, 1) if total_for_type > 0 else 0,
            })

        intensity_query = (
            select(func.avg(DreamEmotion.intensity))
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter, DreamEmotion.intensity.isnot(None)))
        )
        intensity_result = await self.db.execute(intensity_query)
        intensity_avg = intensity_result.scalar()

        intensity_by_emotion_query = (
            select(
                DreamEmotion.emotion,
                func.avg(DreamEmotion.intensity).label("avg_intensity")
            )
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter, DreamEmotion.intensity.isnot(None)))
            .group_by(DreamEmotion.emotion)
            .order_by(func.avg(DreamEmotion.intensity).desc())
            .limit(limit)
        )
        intensity_by_emotion_result = await self.db.execute(intensity_by_emotion_query)
        intensity_by_emotion = [
            {"emotion": row[0], "avg_intensity": round(row[1], 2) if row[1] else None}
            for row in intensity_by_emotion_result.fetchall()
        ]

        trends_query = (
            select(
                func.to_char(Dream.dream_date, 'YYYY-MM').label("period"),
                DreamEmotion.emotion,
                func.count(DreamEmotion.id).label("count")
            )
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(literal_column("period"), DreamEmotion.emotion)
            .order_by(literal_column("period"))
        )
        trends_result = await self.db.execute(trends_query)
        trends = [
            {"period": row[0], "emotion": row[1], "count": row[2]}
            for row in trends_result.fetchall()
        ]

        return {
            "total_emotion_entries": total_entries,
            "most_common": most_common,
            "by_type": by_type,
            "intensity_avg": round(intensity_avg, 2) if intensity_avg else None,
            "intensity_by_emotion": intensity_by_emotion,
            "trends": trends,
        }

    async def get_symbol_analytics(
            self,
            user_id: int,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            limit: int = 10,
    ) -> dict:
        total_symbols_query = select(func.count(Symbol.id)).where(Symbol.user_id == user_id)
        total_symbols_result = await self.db.execute(total_symbols_query)
        total_symbols = total_symbols_result.scalar() or 0

        base_filter = [Dream.user_id == user_id]
        if date_from:
            base_filter.append(Dream.dream_date >= date_from)
        if date_to:
            base_filter.append(Dream.dream_date <= date_to)

        occurrences_query = (
            select(func.count(DreamSymbol.id))
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
        )
        occurrences_result = await self.db.execute(occurrences_query)
        total_occurrences = occurrences_result.scalar() or 0
        frequent_query = (
            select(
                Symbol.name,
                Symbol.category,
                func.count(DreamSymbol.id).label("count"),
                func.min(Dream.dream_date).label("first"),
                func.max(Dream.dream_date).label("last")
            )
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Symbol.id, Symbol.name, Symbol.category)
            .order_by(func.count(DreamSymbol.id).desc())
            .limit(limit)
        )
        frequent_result = await self.db.execute(frequent_query)
        most_frequent = [
            {
                "name": row[0],
                "category": row[1].value if row[1] else None,
                "count": row[2],
                "percentage": round(row[2] / total_occurrences * 100, 1) if total_occurrences > 0 else 0,
                "first_appeared": row[3],
                "last_appeared": row[4],
            }
            for row in frequent_result.fetchall()
        ]

        # By category
        by_category_query = (
            select(
                Symbol.category,
                Symbol.name,
                func.count(DreamSymbol.id).label("count")
            )
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Symbol.category, Symbol.id, Symbol.name)
            .order_by(Symbol.category, func.count(DreamSymbol.id).desc())
        )
        by_category_result = await self.db.execute(by_category_query)

        by_category = {}
        category_totals = {}
        rows = by_category_result.fetchall()

        for row in rows:
            cat = row[0].value if row[0] else "uncategorized"
            category_totals[cat] = category_totals.get(cat, 0) + row[2]

        for row in rows:
            cat = row[0].value if row[0] else "uncategorized"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                "name": row[1],
                "category": cat,
                "count": row[2],
                "percentage": round(row[2] / category_totals[cat] * 100, 1) if category_totals[cat] > 0 else 0,
                "first_appeared": None,
                "last_appeared": None,
            })

        # Co-occurrences (symbols that appear in the same dream)
        cooccurrence_query = (
            select(
                DreamSymbol.dream_id,
                Symbol.name
            )
            .join(Symbol, DreamSymbol.symbol_id == Symbol.id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
        )
        cooccurrence_result = await self.db.execute(cooccurrence_query)

        # Group by dream and find pairs
        dream_symbols = {}
        for row in cooccurrence_result.fetchall():
            dream_id, symbol = row[0], row[1]
            if dream_id not in dream_symbols:
                dream_symbols[dream_id] = []
            dream_symbols[dream_id].append(symbol)

        pair_counts = Counter()
        for symbols in dream_symbols.values():
            if len(symbols) >= 2:
                for i, s1 in enumerate(symbols):
                    for s2 in symbols[i + 1:]:
                        pair = tuple(sorted([s1, s2]))
                        pair_counts[pair] += 1

        cooccurrences = [
            {"symbol_a": pair[0], "symbol_b": pair[1], "count": count}
            for pair, count in pair_counts.most_common(limit)
        ]

        # Monthly trends
        trends_query = (
            select(
                func.to_char(Dream.dream_date, 'YYYY-MM').label("period"),
                Symbol.name,
                func.count(DreamSymbol.id).label("count")
            )
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(literal_column("period"), Symbol.name)
            .order_by(literal_column("period"))
        )
        trends_result = await self.db.execute(trends_query)
        trends = [
            {"period": row[0], "symbol": row[1], "count": row[2]}
            for row in trends_result.fetchall()
        ]

        # New symbols this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_symbols_query = select(func.count(Symbol.id)).where(
            and_(Symbol.user_id == user_id, Symbol.created_at >= start_of_month)
        )
        new_symbols_result = await self.db.execute(new_symbols_query)
        new_symbols_this_month = new_symbols_result.scalar() or 0

        return {
            "total_symbols": total_symbols,
            "total_occurrences": total_occurrences,
            "most_frequent": most_frequent,
            "by_category": by_category,
            "cooccurrences": cooccurrences,
            "trends": trends,
            "new_symbols_this_month": new_symbols_this_month,
        }

    # ============== CHARACTER ANALYTICS ==============

    async def get_character_analytics(
            self,
            user_id: int,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            limit: int = 10,
    ) -> dict:
        """Get character analytics"""
        # Total characters
        total_chars_query = select(func.count(Character.id)).where(Character.user_id == user_id)
        total_chars_result = await self.db.execute(total_chars_query)
        total_characters = total_chars_result.scalar() or 0

        # Base filter
        base_filter = [Dream.user_id == user_id]
        if date_from:
            base_filter.append(Dream.dream_date >= date_from)
        if date_to:
            base_filter.append(Dream.dream_date <= date_to)

        # Total appearances
        appearances_query = (
            select(func.count(DreamCharacter.id))
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter))
        )
        appearances_result = await self.db.execute(appearances_query)
        total_appearances = appearances_result.scalar() or 0

        # Most frequent characters
        frequent_query = (
            select(
                Character.name,
                Character.character_type,
                Character.real_world_relation,
                func.count(DreamCharacter.id).label("count")
            )
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Character.id, Character.name, Character.character_type, Character.real_world_relation)
            .order_by(func.count(DreamCharacter.id).desc())
            .limit(limit)
        )
        frequent_result = await self.db.execute(frequent_query)
        most_frequent = [
            {
                "name": row[0],
                "character_type": row[1].value if row[1] else None,
                "real_world_relation": row[2],
                "count": row[3],
                "percentage": round(row[3] / total_appearances * 100, 1) if total_appearances > 0 else 0,
            }
            for row in frequent_result.fetchall()
        ]

        # By type
        by_type_query = (
            select(
                Character.character_type,
                func.count(distinct(Character.id)).label("count")
            )
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Character.character_type)
        )
        by_type_result = await self.db.execute(by_type_query)
        by_type = {
            (row[0].value if row[0] else "unknown"): row[1]
            for row in by_type_result.fetchall()
        }

        # Archetype distribution
        archetype_query = (
            select(
                DreamCharacter.archetype,
                func.count(DreamCharacter.id).label("count")
            )
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter, DreamCharacter.archetype.isnot(None)))
            .group_by(DreamCharacter.archetype)
            .order_by(func.count(DreamCharacter.id).desc())
        )
        archetype_result = await self.db.execute(archetype_query)

        archetype_total = 0
        archetype_rows = archetype_result.fetchall()
        for row in archetype_rows:
            archetype_total += row[1]

        archetype_distribution = [
            {
                "archetype": row[0] or "unknown",
                "count": row[1],
                "percentage": round(row[1] / archetype_total * 100, 1) if archetype_total > 0 else 0,
                "example_characters": [],
            }
            for row in archetype_rows
        ]

        # Role distribution
        role_query = (
            select(
                DreamCharacter.role_in_dream,
                func.count(DreamCharacter.id).label("count")
            )
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter, DreamCharacter.role_in_dream.isnot(None)))
            .group_by(DreamCharacter.role_in_dream)
            .order_by(func.count(DreamCharacter.id).desc())
        )
        role_result = await self.db.execute(role_query)

        role_total = 0
        role_rows = role_result.fetchall()
        for row in role_rows:
            role_total += row[1]

        role_distribution = [
            {
                "role": row[0].value if row[0] else "unknown",
                "count": row[1],
                "percentage": round(row[1] / role_total * 100, 1) if role_total > 0 else 0,
            }
            for row in role_rows
        ]

        # Recurring characters (3+ appearances)
        recurring_query = (
            select(
                Character.name,
                Character.character_type,
                Character.real_world_relation,
                func.count(DreamCharacter.id).label("count")
            )
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Character.id, Character.name, Character.character_type, Character.real_world_relation)
            .having(func.count(DreamCharacter.id) >= 3)
            .order_by(func.count(DreamCharacter.id).desc())
        )
        recurring_result = await self.db.execute(recurring_query)
        recurring_characters = [
            {
                "name": row[0],
                "character_type": row[1].value if row[1] else None,
                "real_world_relation": row[2],
                "count": row[3],
                "percentage": round(row[3] / total_appearances * 100, 1) if total_appearances > 0 else 0,
            }
            for row in recurring_result.fetchall()
        ]

        return {
            "total_characters": total_characters,
            "total_appearances": total_appearances,
            "most_frequent": most_frequent,
            "by_type": by_type,
            "archetype_distribution": archetype_distribution,
            "role_distribution": role_distribution,
            "recurring_characters": recurring_characters,
        }

    # ============== TIMELINE ANALYTICS ==============

    async def get_timeline_analytics(
            self,
            user_id: int,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
    ) -> dict:
        """Get time-based analytics"""
        now = datetime.utcnow()

        # Default date range: last 12 months
        if not date_from:
            date_from = (now - timedelta(days=365)).date()
        if not date_to:
            date_to = now.date()

        base_filter = [
            Dream.user_id == user_id,
            Dream.dream_date >= date_from,
            Dream.dream_date <= date_to,
        ]

        # Daily counts (last 30 days)
        thirty_days_ago = now.date() - timedelta(days=30)
        daily_query = (
            select(
                Dream.dream_date,
                func.count(Dream.id).label("count")
            )
            .where(and_(Dream.user_id == user_id, Dream.dream_date >= thirty_days_ago))
            .group_by(Dream.dream_date)
            .order_by(Dream.dream_date)
        )
        daily_result = await self.db.execute(daily_query)
        daily_counts = [
            {"date": str(row[0]), "count": row[1]}
            for row in daily_result.fetchall()
        ]

        # Weekly counts (last 12 weeks)
        weekly_query = (
            select(
                func.to_char(Dream.dream_date, 'IYYY-IW').label("week"),
                func.count(Dream.id).label("count")
            )
            .where(and_(*base_filter))
            .group_by(literal_column("week"))
            .order_by(literal_column("week"))
        )
        weekly_result = await self.db.execute(weekly_query)
        weekly_counts = [
            {"week": row[0], "count": row[1]}
            for row in weekly_result.fetchall()
        ]

        # Monthly counts
        monthly_query = (
            select(
                func.to_char(Dream.dream_date, 'YYYY-MM').label("month"),
                func.count(Dream.id).label("count")
            )
            .where(and_(*base_filter))
            .group_by(literal_column("month"))
            .order_by(literal_column("month"))
        )
        monthly_result = await self.db.execute(monthly_query)
        monthly_counts = [
            {"month": row[0], "count": row[1]}
            for row in monthly_result.fetchall()
        ]

        # By day of week
        dow_query = (
            select(
                func.to_char(Dream.dream_date, 'Day').label("day"),
                func.count(Dream.id).label("count")
            )
            .where(and_(*base_filter))
            .group_by(literal_column("day"))
        )
        dow_result = await self.db.execute(dow_query)
        by_day_of_week = {
            row[0].strip(): row[1]
            for row in dow_result.fetchall()
        }

        # Period stats (monthly with additional metrics)
        period_stats_query = (
            select(
                func.to_char(Dream.dream_date, 'YYYY-MM').label("period"),
                func.count(Dream.id).label("dream_count"),
                func.avg(Dream.emotional_intensity).label("avg_intensity"),
                func.sum(
                    case((Dream.lucidity_level.in_([LucidityLevel.PARTIAL, LucidityLevel.FULL]), 1), else_=0)).label(
                    "lucid_count"),
                func.sum(case((Dream.ritual_completed == True, 1), else_=0)).label("ritual_count"),
                func.sum(case((Dream.is_nightmare == True, 1), else_=0)).label("nightmare_count")
            )
            .where(and_(*base_filter))
            .group_by(literal_column("period"))
            .order_by(literal_column("period"))
        )
        period_stats_result = await self.db.execute(period_stats_query)
        period_stats = [
            {
                "period": row[0],
                "dream_count": row[1],
                "avg_intensity": round(row[2], 2) if row[2] else None,
                "lucid_count": row[3] or 0,
                "ritual_count": row[4] or 0,
                "nightmare_count": row[5] or 0,
            }
            for row in period_stats_result.fetchall()
        ]

        # Most active period
        most_active = max(monthly_counts, key=lambda x: x["count"]) if monthly_counts else None

        # Average dreams per week
        total_weeks = max(len(weekly_counts), 1)
        total_dreams = sum(w["count"] for w in weekly_counts)
        avg_per_week = round(total_dreams / total_weeks, 1)

        return {
            "daily_counts": daily_counts,
            "weekly_counts": weekly_counts,
            "monthly_counts": monthly_counts,
            "by_day_of_week": by_day_of_week,
            "period_stats": period_stats,
            "most_active_period": most_active["month"] if most_active else None,
            "avg_dreams_per_week": avg_per_week,
        }

    # ============== PATTERN ANALYTICS ==============

    async def get_pattern_analytics(
            self,
            user_id: int,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
    ) -> dict:
        """Get pattern detection analytics"""
        base_filter = [Dream.user_id == user_id]
        if date_from:
            base_filter.append(Dream.dream_date >= date_from)
        if date_to:
            base_filter.append(Dream.dream_date <= date_to)

        # Recurring themes
        themes_query = (
            select(
                DreamTheme.theme,
                func.count(DreamTheme.id).label("count"),
                func.array_agg(DreamTheme.dream_id).label("dreams")
            )
            .join(Dream, DreamTheme.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(DreamTheme.theme)
            .having(func.count(DreamTheme.id) >= 2)
            .order_by(func.count(DreamTheme.id).desc())
            .limit(10)
        )
        themes_result = await self.db.execute(themes_query)
        recurring_themes = [
            {"theme": row[0], "count": row[1], "dreams": row[2][:5] if row[2] else []}
            for row in themes_result.fetchall()
        ]

        # Symbol-emotion correlations
        correlation_query = (
            select(
                Symbol.name,
                DreamEmotion.emotion,
                func.count(distinct(Dream.id)).label("count")
            )
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .join(DreamEmotion, Dream.id == DreamEmotion.dream_id)
            .where(and_(*base_filter))
            .group_by(Symbol.name, DreamEmotion.emotion)
            .having(func.count(distinct(Dream.id)) >= 2)
            .order_by(func.count(distinct(Dream.id)).desc())
            .limit(15)
        )
        correlation_result = await self.db.execute(correlation_query)
        symbol_emotion_correlations = [
            {"symbol": row[0], "emotion": row[1], "count": row[2]}
            for row in correlation_result.fetchall()
        ]

        # Lucidity distribution
        lucidity_query = (
            select(
                Dream.lucidity_level,
                func.count(Dream.id).label("count")
            )
            .where(and_(*base_filter))
            .group_by(Dream.lucidity_level)
        )
        lucidity_result = await self.db.execute(lucidity_query)
        lucidity_rows = lucidity_result.fetchall()

        lucidity_total = sum(row[1] for row in lucidity_rows)
        lucidity_distribution = [
            {
                "level": row[0].value if row[0] else "none",
                "count": row[1],
                "percentage": round(row[1] / lucidity_total * 100, 1) if lucidity_total > 0 else 0,
            }
            for row in lucidity_rows
        ]

        # Sleep quality correlations
        sleep_query = (
            select(
                Dream.sleep_quality,
                func.avg(Dream.emotional_intensity).label("avg_intensity"),
                func.sum(
                    case((Dream.lucidity_level.in_([LucidityLevel.PARTIAL, LucidityLevel.FULL]), 1), else_=0)).label(
                    "lucid_count"),
                func.count(Dream.id).label("dream_count")
            )
            .where(and_(*base_filter, Dream.sleep_quality.isnot(None)))
            .group_by(Dream.sleep_quality)
            .order_by(Dream.sleep_quality)
        )
        sleep_result = await self.db.execute(sleep_query)
        sleep_quality_correlations = [
            {
                "sleep_quality": row[0],
                "avg_emotional_intensity": round(row[1], 2) if row[1] else None,
                "lucid_percentage": round(row[2] / row[3] * 100, 1) if row[3] > 0 else 0,
                "dream_count": row[3],
            }
            for row in sleep_result.fetchall()
        ]

        # Detected patterns (basic pattern detection)
        detected_patterns = await self._detect_patterns(user_id, base_filter)

        return {
            "recurring_themes": recurring_themes,
            "symbol_emotion_correlations": symbol_emotion_correlations,
            "lucidity_distribution": lucidity_distribution,
            "sleep_quality_correlations": sleep_quality_correlations,
            "detected_patterns": detected_patterns,
        }

    async def _detect_patterns(self, user_id: int, base_filter: list) -> list:
        """Detect patterns in dream data"""
        patterns = []

        # Pattern 1: Recurring symbol clusters
        cluster_query = (
            select(
                Symbol.name,
                func.count(DreamSymbol.id).label("count")
            )
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(and_(*base_filter))
            .group_by(Symbol.name)
            .having(func.count(DreamSymbol.id) >= 5)
        )
        cluster_result = await self.db.execute(cluster_query)

        for row in cluster_result.fetchall():
            patterns.append({
                "pattern_type": "recurring_symbol",
                "description": f"'{row[0]}' appears frequently in your dreams ({row[1]} times)",
                "confidence": min(0.9, row[1] / 20),
                "supporting_dreams": [],
                "elements": [row[0]],
            })

        # Pattern 2: Emotion triggers (symbols that often appear with specific emotions)
        # This is simplified - a real implementation would use statistical analysis

        return patterns[:10]  # Limit to top 10 patterns
