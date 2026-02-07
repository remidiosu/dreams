from typing import Optional
from datetime import date
from collections import Counter

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.characters import Character
from app.models.character_associations import CharacterAssociation
from app.models.dream_characters import DreamCharacter
from app.models.dreams import Dream
from app.models.enums.dream_enums import CharacterType, RoleInDream, AssociationSource


class CharacterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_character(
            self,
            user_id: int,
            name: str,
            character_type: Optional[str] = None,
            real_world_relation: Optional[str] = None,
    ) -> tuple[Character, bool]:
        name_normalized = name.lower().strip()
        query = select(Character).where(
            and_(Character.user_id == user_id, Character.name_normalized == name_normalized)
        )
        result = await self.db.execute(query)
        character = result.scalar_one_or_none()

        if character:
            return character, False

        character = Character(
            user_id=user_id,
            name=name.strip(),
            name_normalized=name_normalized,
            character_type=CharacterType(character_type) if character_type else None,
            real_world_relation=real_world_relation,
            occurrence_count=0,
            first_appeared=None,
            last_appeared=None,
        )
        self.db.add(character)
        await self.db.flush()
        await self.db.refresh(character)

        return character, True

    async def get_character_by_id(self, character_id: int, user_id: int) -> Optional[Character]:
        query = select(Character).where(
            and_(Character.id == character_id, Character.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def list_characters(
            self,
            user_id: int,
            per_page: int = 50,
            cursor: Optional[int] = None,
    ) -> tuple[list[Character], bool]:
        query = select(Character).where(Character.user_id == user_id)

        if cursor:
            query = query.where(Character.id < cursor)

        query = query.order_by(Character.occurrence_count.desc(), Character.id.desc()).limit(per_page + 1)
        result = await self.db.execute(query)
        characters = list(result.scalars().all())

        has_more = len(characters) > per_page
        if has_more:
            characters = characters[:per_page]

        return characters, has_more

    async def update_character(
            self,
            character_id: int,
            user_id: int,
            name: Optional[str] = None,
            character_type: Optional[str] = None,
            real_world_relation: Optional[str] = None,
    ) -> Optional[Character]:
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            return None

        if name:
            character.name = name.strip()
            character.name_normalized = name.lower().strip()
        if character_type:
            character.character_type = CharacterType(character_type)
        if real_world_relation is not None:
            character.real_world_relation = real_world_relation

        await self.db.flush()
        await self.db.refresh(character)

        return character

    async def delete_character(self, character_id: int, user_id: int) -> bool:
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            return False

        await self.db.delete(character)
        await self.db.flush()

        return True

    async def add_character_to_dream(
            self,
            dream_id: int,
            character_id: int,
            dream_date: date,
            role_in_dream: Optional[str] = None,
            archetype: Optional[str] = None,
            traits: list[str] = None,
            context_note: Optional[str] = None,
            personal_significance: Optional[str] = None,
            is_ai_extracted: bool = False,
    ) -> DreamCharacter:
        dream_character = DreamCharacter(
            dream_id=dream_id,
            character_id=character_id,
            role_in_dream=RoleInDream(role_in_dream) if role_in_dream else None,
            archetype=archetype,
            traits=traits or [],
            is_ai_extracted=is_ai_extracted,
            is_confirmed=not is_ai_extracted,
            context_note=context_note,
            personal_significance=personal_significance,
        )
        self.db.add(dream_character)
        character = await self.db.get(Character, character_id)
        if character:
            character.occurrence_count += 1
            if character.first_appeared is None or dream_date < character.first_appeared:
                character.first_appeared = dream_date
            if character.last_appeared is None or dream_date > character.last_appeared:
                character.last_appeared = dream_date

        await self.db.flush()
        await self.db.refresh(dream_character)

        return dream_character

    async def get_dream_character(
            self,
            dream_character_id: int,
            dream_id: int,
    ) -> Optional[DreamCharacter]:
        query = select(DreamCharacter).where(
            and_(DreamCharacter.id == dream_character_id, DreamCharacter.dream_id == dream_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_dream_characters(self, dream_id: int) -> list[dict]:
        query = (
            select(DreamCharacter, Character)
            .join(Character, DreamCharacter.character_id == Character.id)
            .where(DreamCharacter.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.all()

        characters = []
        for dream_character, character in rows:
            associations = await self.get_character_associations(character.id)
            characters.append({
                "dream_character": dream_character,
                "character": character,
                "associations": associations,
            })

        return characters

    async def update_dream_character(
            self,
            dream_character_id: int,
            dream_id: int,
            role_in_dream: Optional[str] = None,
            archetype: Optional[str] = None,
            traits: Optional[list[str]] = None,
            context_note: Optional[str] = None,
            is_confirmed: Optional[bool] = None,
    ) -> Optional[DreamCharacter]:
        dream_character = await self.get_dream_character(dream_character_id, dream_id)
        if not dream_character:
            return None

        if role_in_dream is not None:
            dream_character.role_in_dream = RoleInDream(role_in_dream) if role_in_dream else None
        if archetype is not None:
            dream_character.archetype = archetype
        if traits is not None:
            dream_character.traits = traits
        if context_note is not None:
            dream_character.context_note = context_note
        if is_confirmed is not None:
            dream_character.is_confirmed = is_confirmed

        await self.db.flush()
        await self.db.refresh(dream_character)

        return dream_character

    async def remove_character_from_dream(
            self,
            dream_character_id: int,
            dream_id: int,
    ) -> bool:
        dream_character = await self.get_dream_character(dream_character_id, dream_id)
        if not dream_character:
            return False

        character = await self.db.get(Character, dream_character.character_id)
        if character and character.occurrence_count > 0:
            character.occurrence_count -= 1

        await self.db.delete(dream_character)
        await self.db.flush()

        return True

    async def add_association(
            self,
            character_id: int,
            association_text: str,
            source: str = "user",
    ) -> CharacterAssociation:
        association = CharacterAssociation(
            character_id=character_id,
            association_text=association_text,
            source=AssociationSource(source),
            is_confirmed=source == "user",
        )
        self.db.add(association)
        await self.db.flush()
        await self.db.refresh(association)

        return association

    async def get_character_associations(self, character_id: int) -> list[CharacterAssociation]:
        query = select(CharacterAssociation).where(
            CharacterAssociation.character_id == character_id
        ).order_by(CharacterAssociation.created_at)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def delete_association(
            self,
            association_id: int,
            character_id: int,
    ) -> bool:
        query = select(CharacterAssociation).where(
            and_(
                CharacterAssociation.id == association_id,
                CharacterAssociation.character_id == character_id
            )
        )
        result = await self.db.execute(query)
        association = result.scalar_one_or_none()

        if not association:
            return False

        await self.db.delete(association)
        await self.db.flush()

        return True

    async def get_character_with_dreams(self, character_id: int, user_id: int) -> Optional[dict]:
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            return None

        associations = await self.get_character_associations(character_id)
        query = (
            select(DreamCharacter, Dream)
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(DreamCharacter.character_id == character_id)
            .order_by(Dream.dream_date.desc())
        )
        result = await self.db.execute(query)
        rows = result.all()

        dreams = []
        archetype_list = []
        all_traits = []

        for dream_character, dream in rows:
            dreams.append({
                "dream_id": dream.id,
                "dream_title": dream.title,
                "dream_date": dream.dream_date,
                "role_in_dream": dream_character.role_in_dream.value if dream_character.role_in_dream else None,
                "archetype": dream_character.archetype,
                "traits": dream_character.traits or [],
                "context_note": dream_character.context_note,
                "is_confirmed": dream_character.is_confirmed,
            })

            if dream_character.archetype:
                archetype_list.append(dream_character.archetype)
            all_traits.extend(dream_character.traits or [])

        archetype_counts = dict(Counter(archetype_list))
        trait_counts = Counter(all_traits)
        common_traits = [trait for trait, _ in trait_counts.most_common(10)]

        return {
            "character": character,
            "associations": associations,
            "dreams": dreams,
            "archetype_counts": archetype_counts,
            "common_traits": common_traits,
        }

    async def character_exists_in_dream(self, dream_id: int, character_id: int) -> bool:
        query = select(DreamCharacter.id).where(
            and_(DreamCharacter.dream_id == dream_id, DreamCharacter.character_id == character_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None
