-- ============================================
-- DREAM KNOWLEDGE — DEMO SEED DATA (Part 1)
-- Sections: Cleanup, Demo User, Symbols
-- ============================================

-- ============================================
-- 0. CLEANUP — Cascade delete for demo user
-- ============================================
DO $$
BEGIN
    DELETE FROM dream_emotions WHERE dream_id IN (SELECT id FROM dreams WHERE user_id = 1);
    DELETE FROM dream_symbols WHERE dream_id IN (SELECT id FROM dreams WHERE user_id = 1);
    DELETE FROM dream_characters WHERE dream_id IN (SELECT id FROM dreams WHERE user_id = 1);
    DELETE FROM dream_themes WHERE dream_id IN (SELECT id FROM dreams WHERE user_id = 1);
    DELETE FROM symbol_associations WHERE symbol_id IN (SELECT id FROM symbols WHERE user_id = 1);
    DELETE FROM character_associations WHERE character_id IN (SELECT id FROM characters WHERE user_id = 1);
    DELETE FROM symbols WHERE user_id = 1;
    DELETE FROM characters WHERE user_id = 1;
    DELETE FROM chat_messages WHERE chat_id IN (SELECT id FROM chats WHERE user_id = 1);
    DELETE FROM chats WHERE user_id = 1;
    DELETE FROM dreams WHERE user_id = 1;
    DELETE FROM users WHERE id = 1;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- ============================================
-- 1. DEMO USER
-- ============================================
INSERT INTO users (id, email, password_hash, name, timezone, dreams_indexed_count, created_at)
VALUES (
    1,
    'demo@dreamjournal.app',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V0LGh0Kj6Zh.Hy',
    'Dream Explorer',
    'UTC',
    0,
    '2025-09-15 10:00:00+00'
);

-- ============================================
-- 2. SYMBOLS (25 universal Jungian symbols)
-- Columns: id, user_id, name, name_normalized,
--          category, universal_meaning,
--          occurrence_count, first_appeared, last_appeared
-- Categories: OBJECT, PLACE, ACTION, ANIMAL, NATURE, BODY, OTHER
-- ============================================
INSERT INTO symbols (id, user_id, name, name_normalized, category, universal_meaning, occurrence_count, first_appeared, last_appeared) VALUES
-- Water (unconscious, transformation)
(1, 1, 'Ocean', 'ocean', 'NATURE', 'The primordial unconscious and source of all life; represents the vast depths of emotion and the unknown aspects of the psyche.', 10, '2025-10-03', '2026-02-05'),
(2, 1, 'River', 'river', 'NATURE', 'The flow of life energy and time; symbolizes the journey of individuation and the continuous movement of psychic energy between conscious and unconscious.', 6, '2025-10-15', '2026-01-20'),
(3, 1, 'Rain', 'rain', 'NATURE', 'Emotional release and purification from above; represents the fertilizing descent of unconscious contents into conscious awareness.', 5, '2025-11-02', '2026-01-22'),
-- Thresholds (transition)
(4, 1, 'Door', 'door', 'OBJECT', 'The threshold between known and unknown; represents choice, opportunity, and transition between conscious and unconscious realms.', 12, '2025-10-02', '2026-02-07'),
(5, 1, 'Bridge', 'bridge', 'PLACE', 'Connection between opposites and transition over danger; symbolizes the ego''s capacity to span the gap between consciousness and the unconscious.', 5, '2025-10-20', '2026-02-06'),
(6, 1, 'Staircase', 'staircase', 'PLACE', 'Ascent toward consciousness or descent into the unconscious; each step represents progressive stages of psychological development.', 6, '2025-10-15', '2026-01-30'),
-- Shadow/darkness
(7, 1, 'Shadow Figure', 'shadow figure', 'OTHER', 'The rejected, repressed, or unlived aspects of personality; contains both dangerous impulses and undeveloped gifts seeking integration.', 9, '2025-10-02', '2026-01-28'),
(8, 1, 'Dark Forest', 'dark forest', 'PLACE', 'The bewildering complexity of the unconscious; a place of trial, initiation, and encounter with unknown aspects of the self.', 7, '2025-10-08', '2026-01-25'),
(9, 1, 'Mirror', 'mirror', 'OBJECT', 'Self-reflection and confrontation with one''s true nature; reveals aspects of the self that the ego prefers not to acknowledge.', 7, '2025-10-05', '2026-02-05'),
-- Transformation
(10, 1, 'Snake', 'snake', 'ANIMAL', 'Transformation, healing, and kundalini energy; the ancient symbol of death and rebirth that sheds its skin to become new.', 5, '2025-11-05', '2026-01-28'),
(11, 1, 'Butterfly', 'butterfly', 'ANIMAL', 'Complete metamorphosis and soul emergence; represents the psyche''s capacity for radical transformation and spiritual rebirth.', 5, '2025-12-15', '2026-02-07'),
(12, 1, 'Fire', 'fire', 'NATURE', 'Transformation through destruction and illumination; represents passionate energy, purification, and the alchemical process of psychological change.', 5, '2025-11-20', '2026-01-22'),
-- Liberation/ascent
(13, 1, 'Flying', 'flying', 'ACTION', 'Transcendence of earthly limitations and liberation of spirit; represents the ego''s aspiration toward higher consciousness and freedom from complexes.', 7, '2025-10-12', '2026-02-07'),
(14, 1, 'Bird', 'bird', 'ANIMAL', 'Messengers between heaven and earth, carriers of the soul; represent thoughts, intuitions, and spiritual aspirations rising from the unconscious.', 5, '2025-11-10', '2026-02-04'),
-- Spaces/containers
(15, 1, 'Childhood Home', 'childhood home', 'PLACE', 'The original container of the psyche; represents foundational experiences, the mother complex, and the need to revisit origins for healing.', 6, '2025-10-18', '2026-01-18'),
(16, 1, 'Unknown Room', 'unknown room', 'PLACE', 'Undiscovered aspects of the self; each room represents unexplored potential, hidden talents, or repressed memories awaiting integration.', 7, '2025-10-22', '2026-01-22'),
-- Landscape/journey
(17, 1, 'Mountain', 'mountain', 'NATURE', 'Spiritual aspiration and the axis mundi; represents the arduous climb toward self-realization and the broad perspective gained through effort.', 5, '2025-12-01', '2026-02-06'),
(18, 1, 'Path', 'path', 'PLACE', 'The way of individuation itself; represents life direction, choices made and unmade, and the unique trajectory of psychological development.', 6, '2025-10-28', '2026-02-04'),
-- Illumination
(19, 1, 'Sun', 'sun', 'NATURE', 'Supreme consciousness, the Self archetype, and source of psychic illumination; represents wholeness, vitality, and the goal of individuation.', 5, '2025-12-20', '2026-02-07'),
(20, 1, 'Light', 'light', 'NATURE', 'Dawning consciousness and insight; represents the illumination of dark unconscious contents becoming available to awareness.', 5, '2025-11-25', '2026-02-05'),
-- Objects of knowledge/access
(21, 1, 'Key', 'key', 'OBJECT', 'Access to locked or hidden knowledge; symbolizes the solution to a psychological problem or the means to unlock repressed potential.', 5, '2025-11-08', '2026-01-28'),
(22, 1, 'Book', 'book', 'OBJECT', 'Accumulated wisdom and the record of the soul; represents self-knowledge, life narrative, and the collective wisdom available to the dreamer.', 4, '2025-10-25', '2026-01-20'),
(23, 1, 'Clock', 'clock', 'OBJECT', 'The pressure of temporal existence and mortality awareness; represents the tension between eternal psychic time and finite earthly existence.', 4, '2025-10-28', '2026-01-18'),
-- Growth/depth
(24, 1, 'Tree', 'tree', 'NATURE', 'The living axis connecting underworld roots to heavenly branches; represents growth, life force, and the organic process of individuation.', 5, '2025-11-18', '2026-02-04'),
(25, 1, 'Cave', 'cave', 'PLACE', 'Return to the womb of the unconscious for rebirth; represents the introverted journey inward where transformation occurs in darkness.', 4, '2025-11-22', '2026-01-22');
-- ============================================
-- 3. CHARACTERS
-- ============================================
INSERT INTO characters (id, user_id, name, name_normalized, character_type, real_world_relation, occurrence_count, first_appeared, last_appeared) VALUES
-- Archetypal
(1, 1, 'Shadow Man', 'shadow man', 'UNKNOWN_PERSON', NULL, 8, '2025-10-02', '2026-01-28'),
(2, 1, 'Wise Old Woman', 'wise old woman', 'UNKNOWN_PERSON', NULL, 5, '2025-11-15', '2026-02-05'),
(3, 1, 'Inner Child', 'inner child', 'SELF', NULL, 6, '2025-10-18', '2026-02-04'),
(4, 1, 'Mysterious Guide', 'mysterious guide', 'UNKNOWN_PERSON', NULL, 5, '2025-12-01', '2026-02-06'),
-- Known
(5, 1, 'Mother', 'mother', 'KNOWN_PERSON', 'mother', 6, '2025-10-08', '2026-01-22'),
(6, 1, 'Father', 'father', 'KNOWN_PERSON', 'father', 4, '2025-10-20', '2026-01-18'),
(7, 1, 'Best Friend Sarah', 'best friend sarah', 'KNOWN_PERSON', 'friend', 5, '2025-10-15', '2026-01-28'),
(8, 1, 'Ex-Partner', 'ex-partner', 'KNOWN_PERSON', 'ex-partner', 3, '2025-11-02', '2025-12-18'),
-- Self
(9, 1, 'Younger Self', 'younger self', 'SELF', NULL, 5, '2025-10-18', '2026-01-22'),
(10, 1, 'Future Self', 'future self', 'SELF', NULL, 3, '2025-12-28', '2026-02-06'),
-- Animals
(11, 1, 'White Wolf', 'white wolf', 'ANIMAL', NULL, 4, '2025-11-20', '2026-01-25'),
(12, 1, 'Black Cat', 'black cat', 'ANIMAL', NULL, 3, '2025-10-30', '2025-12-15'),
-- Other
(13, 1, 'Faceless Crowd', 'faceless crowd', 'ABSTRACT', NULL, 5, '2025-10-12', '2026-01-18'),
(14, 1, 'Teacher Figure', 'teacher figure', 'UNKNOWN_PERSON', NULL, 3, '2025-12-10', '2026-01-28');
-- ============================================
-- 4. DREAMS - OCTOBER 2025 (Anxiety/Shadow)
-- ============================================
INSERT INTO dreams (id, user_id, title, narrative, dream_date, setting, development, ending, emotion_on_waking, emotional_intensity, lucidity_level, sleep_quality, ritual_completed, ritual_description, is_recurring, is_nightmare, personal_interpretation, is_indexed, ai_extraction_done, conscious_context, created_at) VALUES

-- Dream 1: Tier C (4-6 sentences)
(1, 1, 'The Locked Door',
'I stood before a massive wooden door in a dimly lit corridor. The door had no handle, only a keyhole that pulsed with faint blue light, casting rhythmic shadows across the damp stone walls. I pressed my palms against the warm wood and heard whispers from beyond—dozens of voices layered on top of each other, urgent but unintelligible. When I peered through the keyhole, I saw only darkness, but felt something watching back with an intelligence that made my skin crawl. The corridor stretched endlessly in both directions, torches flickering in a breeze I could not feel. A cold draft touched my neck, and I sensed a presence behind me, but my body refused to turn around.',
'2025-10-02', 'Long stone corridor with flickering torches, damp walls glistening faintly in the unsteady light.', NULL, NULL, 'anxious', 7, 'NONE', 3, false, NULL, false, false, NULL, false, true, NULL, '2025-10-02 07:30:00+00'),

-- Dream 2: Tier C (4-6 sentences), nightmare + recurring
(2, 1, 'Drowning in the Depths',
'I was swimming in a vast, dark ocean at night, the water warm but impossibly heavy against my limbs. No matter how hard I kicked and pulled, the surface remained just out of reach, moonlight rippling above like a cruel promise. Below me, enormous shapes moved through the black water—ancient and indifferent to my struggle, displacing currents that spun me like driftwood. My lungs burned with a fire that spread into my chest and throat. A shaft of moonlight broke through and I desperately clawed toward it, but the water thickened around me like tar. Just before everything went dark, I glimpsed a massive eye watching me from the deep, unblinking and older than anything I had ever known.',
'2025-10-03', 'Open ocean at night under a full moon, black water stretching to every horizon.', NULL, NULL, 'terrified', 9, 'NONE', 1, false, NULL, true, true, NULL, false, true, NULL, '2025-10-03 06:45:00+00'),

-- Dream 3: Tier B (6-8 sentences), nightmare
(3, 1, 'Shadow in the Mirror',
'I found myself in my childhood bathroom, the tile floor cold under my bare feet and the fluorescent light buzzing with a frequency that set my teeth on edge. The mirror showed my reflection wrong—moving half a second behind, then breaking free entirely and moving on its own. Its eyes were darker than mine, sunk deeper into its skull, and its smile stretched too wide across its face. When it placed its hand flat against the glass, I felt a magnetic pull in my own hand and pressed my palm to meet it. Electricity jolted through me, sharp and hot, and for a moment I could feel its thoughts—a tangle of fury and longing that tasted like metal on my tongue. This was me, but the me I had buried long ago, the parts I had walled off and refused to look at. It mouthed words I couldn''t hear through the glass, then tilted its head and laughed silently, breath fogging its side of the mirror. I tried to pull my hand away but the glass had softened around my fingers, warm and yielding as flesh.',
'2025-10-05', 'Childhood home bathroom with yellowed tile and a buzzing fluorescent light, the proportions slightly distorted as if viewed through a fisheye lens.', 'The reflection''s movements became increasingly independent and deliberate. What began as a subtle delay turned into an entity with its own will, reaching through the barrier between us with obvious intent.', 'The mirror surface softened around my fingers and I could not pull free. I woke with my hand outstretched, still feeling the electric tingle.', 'shaken', 8, 'BRIEF', 2, false, NULL, false, true, 'I think the shadow in the mirror is what Jung would call my shadow self—the parts of my personality I''ve denied or suppressed. The fact that it wanted connection, not destruction, is significant. I''m beginning to wonder what I''ve lost by refusing to face these rejected pieces of myself.', false, true, NULL, '2025-10-05 08:00:00+00'),

-- Dream 4: Tier C (4-6 sentences)
(4, 1, 'Lost in Dark Woods',
'I was walking through a forest that grew darker with each step, the canopy thickening overhead until only slivers of gray sky remained. Trees leaned inward like eavesdroppers, their bark etched with patterns that almost formed words, whispering secrets just beyond my understanding. My mother appeared on the path ahead, her back to me in a familiar blue coat, but when I ran to her she maintained the same impossible distance no matter how fast I moved. Shadow figures slid between the trees in my peripheral vision, their movements fluid and wrong. I found a small clearing with a dead fire pit—charred stones in a circle, evidence someone had been here before me. Written in the cold ash with a careful finger: "Turn back."',
'2025-10-08', 'Dense old-growth forest at twilight, moss-covered trunks pressing close on a narrow dirt path.', NULL, NULL, 'unsettled', 6, 'NONE', 2, false, NULL, false, false, NULL, false, true, NULL, '2025-10-08 07:15:00+00'),

-- Dream 5: Tier B (6-8 sentences)
(5, 1, 'Flying Over the Unknown City',
'I stood on the roof of a tall building in a city I had never seen, the wind pulling at my clothes with a steady insistence that felt like an invitation. Without hesitation or fear, I stepped off the edge and flew—arms outstretched, body tilting into the updraft like something I had always known how to do. Pure exhilaration flooded through me, a freedom more total than anything waking life had ever offered. Birds joined my flight, wheeling around me between gleaming towers of glass and steel that caught the sun in blinding flashes. But below on the streets, a dark figure followed on the ground, matching every turn I made with mechanical precision, its shadow stretching up the sides of buildings to reach for me. The higher I flew, the more anxious I became, as if altitude and dread were tied to the same thread. The city below started to look less like a city and more like a maze—streets narrowing, dead-ending, folding back on themselves with no visible exit. I realized with a chill that I could fly above the maze but never leave it.',
'2025-10-12', 'Futuristic city of glass towers and wide avenues that gradually narrows into labyrinthine streets. The light is golden but the shadows between buildings are unnaturally deep.', 'The dream shifted from pure joy to creeping dread. The flight itself remained effortless, but the city below revealed itself as a trap—beautiful architecture concealing a structure with no way out.', 'I hovered high above, unable to land safely and unable to fly beyond the city''s edge. The dark figure below stood still, looking up, waiting.', 'conflicted', 6, 'PARTIAL', 3, false, NULL, false, false, 'The flying felt like my desire for transcendence—to rise above my problems rather than face them. But the shadow following below suggests I can''t outrun the parts of myself I''m trying to escape. The maze-city might represent my own mind, complex and inescapable.', false, true, NULL, '2025-10-12 06:30:00+00'),

-- Dream 6: Tier B (6-8 sentences), nightmare + recurring
(6, 1, 'Endless Staircase',
'I was climbing a spiral staircase inside a tower that seemed to have no top, each step groaning under my weight with a sound like a held breath being released. Sarah called my name from somewhere above, her voice echoing down the stone walls with an urgency that made my chest tight. No matter how many flights I climbed, her voice never grew closer—always the same distance away, always the same desperate tone. The stairs behind me crumbled and fell away into darkness with each step, the sound of stone hitting stone fading for impossibly long seconds below. Faceless people passed me going down, their blank features smooth as eggs, ignoring my pleas for help or even acknowledgment. My legs burned and my hands were raw from gripping the railing, but stopping meant falling into the void that had eaten the stairs. Finally I reached a door at the very top, heavy and iron-banded, but when I turned the handle it was locked. Through the keyhole I could see Sarah on the other side, sitting quietly, unaware I was there.',
'2025-10-15', 'An infinite spiral tower of gray stone, narrow windows letting in pale light that never reaches the center. The staircase wraps upward with no visible terminus.', 'The climb became increasingly desperate as the stairs crumbled behind me. Each flight felt steeper, the air thinner, the faceless figures more numerous and indifferent.', NULL, 'exhausted', 7, 'NONE', 1, false, NULL, true, true, 'This staircase dream keeps coming back. I think it''s about my fear of losing connection with the people I care about—always striving, never arriving. The crumbling stairs suggest there''s no going back to who I was, only forward into uncertainty.', false, true, 'I''ve been feeling isolated lately, struggling to maintain friendships while dealing with work stress. Sarah cancelled plans twice this week.', '2025-10-15 07:45:00+00'),

-- Dream 7: Tier B (6-8 sentences)
(7, 1, 'Return to Childhood',
'I was back in my childhood home, but everything was subtly wrong—the furniture rearranged into configurations that made no spatial sense, hallways stretching longer than any house could contain. The wallpaper was the same floral pattern I remembered, but the flowers were wilting, petals curling brown at the edges. I found a door I had never seen before, tucked between the kitchen and the living room where no door should fit. Inside was a room filled with forgotten toys—stuffed animals with matted fur, a wooden train set missing half its tracks, crayon drawings pinned to the walls in a child''s careful hand. My younger self sat cross-legged on the floor, playing alone with a concentration that felt like loneliness. The child looked up at me with my own eyes and said, very quietly, "You forgot about me." Overwhelming guilt flooded through me, thick and choking, because I knew it was true. I opened my mouth to apologize but no words came out, and the child simply nodded, as if this silence was expected, and pressed a small brass key into my palm.',
'2025-10-18', 'Childhood home with distorted dimensions—hallways too long, ceilings too high in some rooms and pressing low in others. The light has the amber quality of late afternoon in memory.', 'The exploration deepened from spatial wrongness into emotional confrontation. Finding the hidden room felt like uncovering something I had deliberately sealed away, and the child''s accusation carried the weight of years of neglect.', 'The child placed a small brass key in my hand without anger or sadness, just a quiet knowing. I clutched it and woke with tears on my face.', 'guilty', 8, 'BRIEF', 3, false, NULL, false, false, 'This dream hit me hard. The inner child motif feels very Jungian—the parts of myself I abandoned in the process of growing up, the spontaneity and vulnerability I traded for control. The key feels like an invitation to reconnect, but I don''t know what door it opens yet.', false, true, NULL, '2025-10-18 08:30:00+00'),

-- Dream 8: Tier B (6-8 sentences), nightmare
(8, 1, 'Bridge Over the Void',
'I stood at the foot of a massive suspension bridge that spanned an abyss filled with slow-moving fog, its cables disappearing into mist above and below. My father stood on the far side, a silhouette made recognizable by his posture and the way he held his shoulders, beckoning me forward with one raised hand. I stepped onto the bridge and it swayed immediately, the metal groaning, cables singing a low vibrato that I felt in my bones. Each step I took made the swaying worse—the bridge twisting beneath me like a living thing trying to shake me loose. Halfway across I made the mistake of looking down and saw no bottom, just gray infinity spiraling into itself like a drain. My hands locked onto the railing and my legs stopped working. I couldn''t move forward, couldn''t retreat. My father''s voice echoed across the void, distorted by distance and fog: "You have to choose."',
'2025-10-20', 'A vast suspension bridge stretching over an endless foggy abyss. The far side is barely visible, a smudge of solid ground where a figure waits.', 'The bridge became more unstable with each step forward, the physical danger escalating in proportion to my progress toward my father. The dream narrowed to a single point of paralysis at the bridge''s center.', 'Frozen at the midpoint, unable to advance or retreat. My father''s command to choose echoed endlessly without resolution.', 'paralyzed', 7, 'NONE', 2, false, NULL, false, true, NULL, false, true, NULL, '2025-10-20 06:15:00+00'),

-- Dream 9: Tier B (6-8 sentences)
(9, 1, 'Hidden Rooms',
'I discovered a hidden wing in my apartment by pushing on a wall that gave way like a door, revealing a corridor I had never suspected existed. The first room was Victorian—heavy curtains, dark wood furniture, a fireplace with cold ashes and a portrait of someone who looked like me but older, dressed in clothes from another century. The second room was aggressively modern, all white surfaces and chrome, humming with the sound of machines I couldn''t see. The third was completely empty, its walls, floor, and ceiling the same featureless white, and standing in it felt like floating in nothing. In the last room, a tall mirror in an ornate frame showed not my reflection but a vast landscape under two pale moons, wind visibly moving through alien grasses. Footsteps echoed behind me throughout my exploration, always one room back, but every time I doubled back to check, the room was empty and still. I found a leather journal in the Victorian room, its pages filled with my own handwriting—observations, dream records, interpretations—but I had no memory of writing any of it. The last entry read: "They are not rooms. They are selves."',
'2025-10-22', 'A hidden wing of the dreamer''s apartment, accessed through a false wall. Each room is decorated in a radically different style, as if belonging to different eras and personalities.', 'Each room revealed a different aesthetic and emotional register, creating a sense of moving through distinct identities. The footsteps following always stayed just out of sight, adding persistent unease to the exploration.', NULL, 'curious', 5, 'PARTIAL', 3, false, NULL, false, false, 'I think the hidden rooms represent unexplored aspects of my psyche—different selves I could have been or still contain within me. The journal written in my hand that I don''t remember writing feels like a message from my unconscious. "They are selves" is exactly the kind of insight Jung would describe as emerging from the collective unconscious.', false, true, NULL, '2025-10-22 07:00:00+00'),

-- Dream 10: Tier C (4-6 sentences)
(10, 1, 'Father''s Library',
'I stood in a vast library that somehow belonged to my father, though he never owned anything like it in waking life. Books with unreadable titles in shifting scripts lined shelves that stretched upward beyond sight, the air thick with the smell of old paper and wood polish. My father sat writing at a heavy oak desk, his pen scratching steadily, and he never looked up no matter what I said or how loudly I called his name. I pulled a book from the nearest shelf and found it filled with photographs of moments I don''t remember living—birthday parties I never attended, graduations in robes I never wore, a wedding to someone I didn''t recognize. Each photograph showed a version of my life I never chose, and turning the pages felt like grief for something I couldn''t name.',
'2025-10-25', 'An impossibly vast library with towering shelves and warm lamplight, centered around a heavy writing desk.', NULL, NULL, 'melancholy', 6, 'NONE', 3, false, NULL, false, false, NULL, false, true, NULL, '2025-10-25 08:15:00+00'),

-- Dream 11: Tier C (4-6 sentences)
(11, 1, 'The Branching Path',
'A forest path split before me, and then split again, and again—each fork multiplying into dozens of trails that curved away through identical trees. In my peripheral vision I caught glimpses of my alternate selves choosing differently at each junction, their movements mirroring and diverging from mine in an infinite cascade. A clock ticked somewhere I couldn''t see, growing louder with each passing second, the sound becoming a physical pressure against my temples. The weight of unmade decisions became unbearable, a paralysis born not from fear but from the impossibility of choosing rightly when every path looked the same. I stood frozen at a fork while my other selves walked confidently onward, their footsteps fading into the undergrowth.',
'2025-10-28', 'A dense forest of identical trees where every path branches endlessly, the light flat and directionless.', NULL, NULL, 'overwhelmed', 6, 'NONE', 3, false, NULL, false, false, NULL, false, true, NULL, '2025-10-28 07:30:00+00'),

-- Dream 12: Tier C (4-6 sentences)
(12, 1, 'The Knowing Cat',
'A black cat with luminous green eyes followed me through unfamiliar cobblestone streets, its paws making no sound on the worn stone. Its knowing gaze tracked my every move with an intelligence that felt older and deeper than any animal should possess. I walked and walked, turning corners at random, until the cat spoke in a calm, clear voice: "You''ve been going in circles." I looked around and realized with a jolt that I had passed the same crumbling cafe with its faded awning three times without noticing. The cat turned and padded down a hidden alley I hadn''t seen before, glancing back once to make sure I followed. At the end of the alley stood a narrow wooden door with my name carved deeply into its surface.',
'2025-10-30', 'A foreign town of narrow cobblestone streets, weathered facades, and wrought-iron balconies under an overcast sky.', NULL, NULL, 'intrigued', 5, 'BRIEF', 4, false, NULL, false, false, NULL, false, true, 'Started journaling my dreams this week after a colleague mentioned keeping a dream diary. Feeling like I''m going in circles in my waking life too.', '2025-10-30 06:45:00+00');
-- ============================================
-- 5. DREAMS - NOVEMBER 2025 (Confrontation/Transformation)
-- ============================================
INSERT INTO dreams (id, user_id, title, narrative, dream_date, setting, development, ending, emotion_on_waking, emotional_intensity, lucidity_level, sleep_quality, ritual_completed, ritual_description, is_recurring, is_nightmare, personal_interpretation, is_indexed, ai_extraction_done, conscious_context, created_at) VALUES

-- Dream 13: Rain of Renewal (Tier C)
(13, 1, 'Rain of Renewal',
'I was standing alone in the middle of a wide open field when warm rain began to fall. The drops were thick and golden, almost luminous against the grey sky. Wherever the rain touched my skin, dark streaks of shadow lifted off like smoke, trickling down my arms and soaking into the muddy ground beneath my feet. I could smell wet earth and something sweet, like crushed grass. My ex stood at the far edge of the field under a red umbrella, watching me, but for the first time in any dream I felt no pull toward them, no ache, no anger. When the rain finally stopped, I noticed tiny shoots of brilliant green grass pushing up through the soil exactly where the shadows had fallen.',
'2025-11-02', 'Wide open field under a warm rainstorm, grey sky with golden light filtering through clouds',
NULL, NULL,
'relief', 7, 'BRIEF', 4, false, NULL, false, false,
NULL,
false, true, NULL, '2025-11-02 07:00:00+00'),

-- Dream 14: The Drowning Garden (NEW - Tier B, regression nightmare)
(14, 1, 'The Drowning Garden',
'I found myself in the most beautiful garden I had ever seen, rows of flowers in impossible colors stretching out in every direction under a pale sky. I was kneeling in the soil, tending a bed of deep violet orchids, when I noticed water pooling around my knees. At first it was just a thin film, cool and clear, but it rose quickly, silently. The flowers began to bow under the weight of the current. I tried to build little dams with handfuls of earth, but the soil dissolved between my fingers like sugar. Roses snapped at their stems and drifted away. I was wading now, waist-deep, grabbing at flower heads and pressing them above the surface, but they slipped through my hands. The water was murky and cold and tasted of iron. I could feel something large moving beneath the surface, circling my legs. The garden I had worked so hard to grow was drowning, and there was nothing I could do to save it.',
'2025-11-04', 'Vast cultivated garden with impossible flowers, rapidly flooding under pale overcast sky',
'The flooding began slowly and accelerated. Initial calm tending gave way to frantic rescue attempts. Each intervention failed, the water dissolving all efforts at control.',
'The dreamer was trapped waist-deep in rising water, clutching at flower stems that slipped away. Something unseen circled beneath the surface. No resolution, only helplessness and loss.',
'dread', 7, 'NONE', 2, false, NULL, false, true,
'This felt like a warning that the progress I''ve been making is fragile. The garden is everything I''ve been cultivating internally, and the flood is the unconscious threatening to swallow it all back. The thing circling underwater terrifies me.',
false, true, 'Had a difficult week at work with a project setback, feeling like I was losing control of things again.', '2025-11-04 06:45:00+00'),

-- Dream 15: The Second Door (Tier B, recurring)
(15, 1, 'The Second Door',
'I was back in the familiar stone corridor, the flickering torchlight casting uneven shadows along the walls. The massive wooden door stood before me just as it always had, its brass keyhole pulsing faintly with that cold blue light. But this time I noticed something I had never seen before: a second, much smaller door set low into the wall to the left, barely reaching my waist, its frame worn smooth as driftwood. I knelt down and touched it, feeling warmth radiate from the wood. A key materialized in my coat pocket, heavy and ornate, and it fit the small lock perfectly. The door swung inward to reveal a narrow staircase descending into soft, golden light that smelled faintly of honey and warm stone. Behind me, the whispers leaking through the original locked door shifted into a melody, a lullaby I almost recognized from childhood but could not quite name.',
'2025-11-08', 'Familiar stone corridor with flickering torches, transformed by the appearance of a second smaller door',
'Discovery of the second door shifted focus from the intimidating locked door. The key appeared effortlessly, suggesting readiness. The descent into golden light reversed the usual anxiety of these corridor dreams.',
'The dreamer stood at the threshold of the small door, golden light warming their face, the old whispers becoming a half-remembered lullaby.',
'hopeful', 5, 'PARTIAL', 4, false, NULL, true, false,
'The corridor has always been about being locked out, but now there''s a way through that doesn''t require forcing the big door. I think this is about finding gentler, humbler paths forward rather than confronting everything head-on.',
false, true, NULL, '2025-11-08 07:15:00+00'),

-- Dream 16: Departure of Birds (Tier C)
(16, 1, 'Departure of Birds',
'I woke inside the dream to find hundreds of birds gathered on the ledge outside my bedroom window, their small bodies packed shoulder to shoulder in the early morning light. Sparrows, starlings, a few I could not identify with iridescent throats. They were not threatening, not clamoring, simply waiting in patient silence. Then one by one they lifted off, each departure accompanied by a distinct loosening in my chest, a weight I had not known I carried dissolving like breath into cold air. By the time the last bird had gone, the sky was an enormous open blue and I could breathe fully for what felt like the first time in years. A single white feather lay on the windowsill, still warm.',
'2025-11-10', 'Dreamer''s own bedroom, soft morning light, window overlooking open sky',
NULL, NULL,
'lightness', 4, 'NONE', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2025-11-10 06:30:00+00'),

-- Dream 17: Lantern in the Dark (NEW - Tier B, finding inner light)
(17, 1, 'Lantern in the Dark',
'I was standing in absolute darkness, the kind so thick it felt like a substance pressing against my skin. There was no ground visible beneath my feet, no sky above, just a vast undifferentiated black. My hand brushed against something cold and metallic on the ground, and I lifted it: an old brass lantern, its glass panes fogged with age. As I turned it over, it flickered to life on its own, casting a warm amber circle that reached perhaps three feet in every direction. Beyond that, nothing. I began to walk, trusting the small pool of light to show me the next step. The ground under my feet was smooth stone. After what felt like hours, I saw another glow in the distance, then another. Other people carrying their own lanterns, each illuminating only their own small sphere. We converged without speaking, and where our circles of light overlapped, the illumination was stronger, the stone beneath us revealing intricate mosaic patterns. We walked together, not knowing where we were going, but the darkness felt less absolute.',
'2025-11-12', 'Infinite featureless darkness, smooth stone underfoot, revealed only by lantern light',
'Progressed from isolation in total darkness to discovery of the lantern, then from solitary walking to finding other lantern-carriers. Each phase reduced the sense of threat.',
NULL,
'calm', 5, 'PARTIAL', 4, false, NULL, false, false,
NULL,
false, true, 'Started attending a weekly group meditation class, feeling less isolated.', '2025-11-12 07:30:00+00'),

-- Dream 18: The Wise Woman's Question (Tier B)
(18, 1, 'The Wise Woman''s Question',
'I arrived at a crossroads at dusk, four dirt paths radiating outward into rolling hills veiled in lavender mist. An old woman sat on a low stone wall where the paths converged. Her eyes were milky white, completely blind, yet she turned to face me the moment I approached, tracking me with an accuracy that made my skin prickle. She wore a shawl the color of storm clouds. She did not tell me which way to go. Instead, she tilted her head and asked in a voice like dry leaves shifting, "What are you most afraid to find?" The question dropped through me like a stone into deep water. I opened my mouth but no answer came. She laughed, not unkindly, the sound of wind chimes in a gentle breeze, and said, "That is your direction." She reached for my hand and pressed a small, smooth stone into my palm. It was warm and pulsed with a slow, steady rhythm, like a heartbeat separate from my own.',
'2025-11-15', 'Crossroads at twilight, four dirt paths through lavender-misted hills',
'The encounter was brief but dense. The wise woman''s question cut through surface anxiety to something deeper. Her laughter transformed the moment from confrontation to invitation.',
'The dreamer stood holding the warm, pulsing stone, the question unanswered but somehow clarifying.',
'wonder', 5, 'FULL', 4, false, NULL, false, false,
'The question she asked is the one I keep avoiding in waking life. I think my fear of what I''ll find in myself is exactly what I need to move toward. The pulsing stone felt like something real, like she gave me a tool I can carry.',
false, true, NULL, '2025-11-15 08:30:00+00'),

-- Dream 19: Tree of Photographs (Tier B)
(19, 1, 'Tree of Photographs',
'On the crest of a green hill stood a tree so massive its canopy blocked out the sky. Its bark was deep reddish-brown and warm to the touch, humming with a low vibration I felt through my palms. Instead of leaves, thousands of photographs hung from its branches on fine silver threads, rustling and spinning in the breeze. Each photograph was a forgotten memory: my fifth birthday, a rainy afternoon reading on the floor of my childhood bedroom, the face of a friend I had not thought about in twenty years. I began to climb, the bark yielding slightly under my fingers like living skin. The higher I climbed, the older the memories became. Near the crown, the photographs were faded and curled, their edges soft. At the very top, swaying gently, hung a single photograph of myself as an infant, cradled in hands I did not recognize. On the back, written in pencil so faint I had to squint: "Remember who you were before you learned to be afraid." The tree hummed louder, and I felt held.',
'2025-11-18', 'Solitary green hill crowned by an enormous tree with photograph-leaves',
'The ascent through the tree was a journey backward through time, each level bringing older and more primal memories. The emotional tone shifted from curiosity to deep nostalgia to a profound tenderness.',
NULL,
'tenderness', 6, 'BRIEF', 4, false, NULL, false, false,
'Climbing this tree felt like doing the inner work of therapy but in the most beautiful way imaginable. The message on the photograph is what I''m trying to get back to: a version of myself that existed before all the defense mechanisms.',
false, true, 'Have been looking through old family photo albums this week.', '2025-11-18 07:00:00+00'),

-- Dream 20: The White Wolf (Tier B)
(20, 1, 'The White Wolf',
'The white wolf appeared at the edge of the dark forest, its fur luminous against the black trunks, eyes the color of pale amber. But the forest itself felt different this time, less threatening, the darkness more like a held breath than a menace. The wolf walked beside me without hurry, guiding me along invisible paths that my feet seemed to know. I could hear water running somewhere nearby, and the scent of pine resin was sharp and clean. We emerged into a clearing where a fire already burned in a ring of stones, the flames steady and smokeless. The wolf lay down beside the fire and rested its great head on its paws, and I felt safe enough to sit, to rest, to stop scanning the tree line for danger. In the firelight, I noticed the wolf had my eyes, the same flecked hazel, watching the flames with the same quiet intensity I recognized from my own reflection.',
'2025-11-20', 'Dark forest transitioning to a firelit clearing, pine-scented night air',
NULL,
'Dreamer sat by the fire with the wolf, resting peacefully. The recognition of shared eyes created a moment of self-understanding.',
'safety', 4, 'PARTIAL', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2025-11-20 06:45:00+00'),

-- Dream 21: Cave of Echoes (Tier B)
(21, 1, 'Cave of Echoes',
'I descended stone steps into a cave whose walls were lined with crystalline formations that caught and scattered the dim blue-white light emanating from the rock itself. Every thought I had became audible, bouncing off the crystal faces and returning to me as layered sound. First came the doubts, sharp and percussive: "You''re not good enough, you''ll never change." Then the fears, lower and resonant, humming through the stone floor. Then, unexpectedly, the hopes, high and clear like bells. The noise was initially overwhelming, a cacophony of my own inner life made external. But as I sat with it, the sounds began to harmonize, as if the cave were teaching my thoughts to coexist. In the deepest chamber, I found a still, dark pool. I knelt at its edge and looked in, expecting my reflection. Instead, the surface showed a constellation I had never seen, its stars connected by faint lines that formed a shape I almost understood.',
'2025-11-22', 'Underground crystal cave with self-illuminating walls, deep pool in the innermost chamber',
'The experience shifted from overwhelming to harmonizing. Each layer of echoed thought, though initially chaotic, found its place in the larger acoustic tapestry of the cave.',
NULL,
'awe', 6, 'PARTIAL', 4, false, NULL, false, false,
'The cave made my inner life audible, and the key was that I didn''t have to silence any of it. Even the doubts and fears had a place in the harmony. The constellation in the pool feels like it represents my true self, a pattern I''m still learning to read.',
false, true, 'Journaling has been helping me sit with difficult emotions rather than pushing them away.', '2025-11-22 08:00:00+00'),

-- Dream 22: The Snake Sheds (Tier B, moved to Nov 24)
(22, 1, 'The Snake Sheds',
'I was standing in a garden at dawn, the air still cool and damp with dew, every surface glistening. Among the low herbs and flowering vines, a large emerald-green snake lay coiled, its body rippling as it began to shed its skin. There was something both beautiful and horrifying in the vulnerability of it, the way the old skin peeled back to reveal something raw and glistening underneath. The snake lifted its head and looked directly at me with ancient, golden eyes, and I understood without words that it wanted my help. I knelt and gently pulled away the last clinging piece of old skin, which came off in my hands and transformed into a fine silver thread that wound itself around my wrist like a bracelet. The snake then arched its body into a perfect circle, taking its own tail into its mouth, the ancient ouroboros, and in that moment it dissolved into a column of warm, golden light that entered my chest with a sensation like a deep breath held and then released.',
'2025-11-24', 'Herb garden at dawn, dewy and glistening, golden light breaking through low mist',
NULL,
'The ouroboros dissolved into light that entered the dreamer''s chest. A silver thread remained around the wrist as a tangible remnant of the transformation.',
'renewal', 6, 'PARTIAL', 4, false, NULL, false, false,
NULL,
false, true, NULL, '2025-11-24 08:00:00+00'),

-- Dream 23: Light Through Cracks (Tier B)
(23, 1, 'Light Through Cracks',
'I was in a small, dark room with no visible door, the walls close enough to touch on all sides. At first there was only panic, the suffocating sense of enclosure. But then I noticed light seeping through hairline cracks in the walls, thin bright lines like veins of gold in dark stone. I pressed my eye to one crack and saw a sunlit meadow. Another showed a rain-soaked city street at night, neon reflections on wet pavement. A third revealed a child running through a wheat field. I began to pull at the cracks, working my fingers into the gaps, and the walls offered surprisingly little resistance. Each crack I widened let in more light until the room was laced with it, a web of brilliance holding the darkness together. Then the walls themselves began to dissolve, not collapsing but thinning, becoming translucent, until I was standing in open air, surrounded by all the scenes at once. I was not escaping the room. I was expanding beyond its walls.',
'2025-11-26', 'Small enclosed dark room that dissolves into open multidimensional space',
'The emotional arc moved from claustrophobia through curiosity to active engagement and finally to a sense of expansion. Each widened crack represented a small act of agency.',
'The room dissolved into open air. The dreamer stood surrounded by multiple scenes simultaneously, feeling expanded rather than escaped.',
'exhilaration', 5, 'FULL', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2025-11-26 07:15:00+00'),

-- Dream 24: Dancing with Shadow (Tier B)
(24, 1, 'Dancing with Shadow',
'I stood in the center of an enormous ballroom, its floor polished to a mirror sheen, moonlight pouring through tall arched windows and casting long silver rectangles across the parquet. The shadow figure appeared at the far end of the room, the same dark silhouette that had stalked and frightened me through months of dreams. But this time I did not run. I stood still and watched it approach, my heart hammering but my feet planted. It stopped an arm''s length away. Up close, I could see it was not truly dark but rather composed of deep shifting blues and purples, like a figure made of twilight. It extended one hand, palm up, in an unmistakable invitation. I took it. The hand was cool and solid, and we began to dance, a slow, deliberate waltz with no music but our own breathing. As we turned across the moonlit floor, the shadow began to lighten, its edges softening, blurring into me. By the final turn, I was dancing alone, but I did not feel alone. I felt more complete than I ever had, as if a missing piece had slotted quietly into place.',
'2025-11-28', 'Grand moonlit ballroom with arched windows and polished mirror floor',
'The confrontation was transformed into collaboration through the act of dancing. The shadow''s gradual merging with the dreamer was gentle and consensual rather than violent.',
'The dreamer danced alone in the moonlit ballroom, feeling whole and complete. The shadow had merged without struggle, leaving a sense of integration.',
'peace', 6, 'FULL', 5, false, NULL, false, false,
'This is the dream I''ve been building toward without knowing it. Dancing with my shadow instead of running from it. The merging didn''t feel like losing something but like becoming more fully myself. Jung would call this the beginning of individuation.',
false, true, NULL, '2025-11-28 06:30:00+00');
-- ============================================
-- 6. DREAMS - DECEMBER 2025 (Integration/Guides)
-- ============================================
INSERT INTO dreams (id, user_id, title, narrative, dream_date, setting, development, ending, emotion_on_waking, emotional_intensity, lucidity_level, sleep_quality, ritual_completed, ritual_description, is_recurring, is_nightmare, personal_interpretation, is_indexed, ai_extraction_done, conscious_context, created_at) VALUES

(25, 1, 'Mountain Ascent',
'I found myself at the base of a towering mountain with a mysterious guide beside me, someone whose face I could never quite see. The path was steep but well-worn, as though many had climbed before us, and the guide moved with a patience that felt ancient. At each rest point carved into the rock, the guide shared stories that I slowly realized were about my own life, though set in different centuries and different lands. Near the summit the clouds parted, and where I expected a peak there was instead a luminous doorway framed in pale stone. The guide placed a hand on my shoulder and said, "I''ll be here when you return." I stood at the threshold feeling the mountain wind on my face, understanding that the climb itself had been the preparation. The doorway hummed with a warmth that pulled me forward, and I knew the real journey was about to begin.',
'2025-12-01', 'Mountain with winding path, rest points carved into rock',
'The climb progressed through changing weather and terrain, each rest point revealing a new story from the guide that mirrored a chapter of my life. The higher we climbed, the lighter I felt, as though the altitude was burning away something heavy I had carried.',
NULL,
'calm anticipation', 5, 'PARTIAL', 4, false, NULL, false, false,
NULL,
false, true, NULL, '2025-12-01 07:30:00+00'),

(26, 1, 'Library of Lives',
'I entered a vast circular library that spiraled upward beyond sight, every wall lined with books that glowed faintly with their own inner light. A teacher figure, a woman with silver-streaked hair and kind eyes, guided me between the shelves, explaining that each book contained a complete life I could have lived. She pulled volumes from the shelves and let me read passages: one where I became a marine biologist, another where I never left my hometown, another where I married someone I barely remembered. None were better or worse, she explained, just different expressions of the same soul seeking understanding. Near the center of the library she handed me a blank book with my name embossed on the cover, its pages warm to the touch. "The book you''re writing now is the only one that matters," she said, and the warmth from the pages spread through my hands into my chest.',
'2025-12-05', 'Circular infinite library with self-illuminated books',
'The teacher showed me increasingly divergent lives, each one revealing a different facet of who I could have been. The emotional weight of so many unlived possibilities gave way to acceptance as I understood none were wasted.',
'Received a blank book with my name, warm to the touch. The teacher''s words about the present being the only book that matters brought clarity.',
'gentle wonder', 4, 'PARTIAL', 5, false, NULL, false, false,
'The library feels like the Self archetype, containing all potentials. The blank book is my agency, the reminder that I am still writing my own story rather than mourning paths not taken.',
false, true, 'Have been reflecting on career choices and whether I made the right decisions after university.', '2025-12-05 08:00:00+00'),

(27, 1, 'Healing Waters',
'I descended ancient stone steps into an underground cavern where a lake of luminescent blue water stretched into darkness, casting rippling light across the ceiling. The wise woman sat at the shore on a flat rock, her blind eyes reflecting the water''s glow, and she spoke without turning: "The water remembers everything so you don''t have to." I stepped in and the cold shocked me at first, then melted into a warmth that seemed to come from inside my own body. Memories surfaced like bubbles, vivid and sharp, each one rising to the surface and dissolving into the glow before I could hold onto it. Years of accumulated weight lifted from my shoulders and my chest and the backs of my eyes. I emerged from the water feeling scrubbed clean, not of the memories themselves but of the pain that had barnacled onto them. The wise woman handed me a smooth stone from the shore and said, "Carry this instead."',
'2025-12-08', 'Underground cavern with luminescent blue lake',
'Entering the water triggered a cascade of surfacing memories, each one releasing its emotional charge as it dissolved into the glow. The process was overwhelming at first but became rhythmic and natural, like breathing.',
'Emerged from the water cleansed of emotional weight. The wise woman offered a smooth stone as a replacement for what was released.',
'deep peace', 6, 'FULL', 5, false, NULL, false, false,
'This dream felt like a genuine healing experience. The wise woman represents the anima at her most nurturing. The water as memory-keeper suggests my unconscious has been processing grief I wasn''t ready to face consciously.',
false, true, 'Had an emotional week after finding old photographs from college.', '2025-12-08 06:45:00+00'),

(28, 1, 'Teaching the Child',
'My younger self appeared on an infinite golden beach, tugging at my hand with an urgency that was half-play and half-desperation. The child needed help with something I had forgotten how to do: how to play without purpose, how to build without worrying about the outcome. We built elaborate sandcastles together, towers and moats and bridges, and the child''s laughter was so free it made my chest ache. "You think too much now," the child said, pressing a shell into the wet sand. I promised to remember how to just be, to let moments exist without analyzing them. The tide came in gently, soft fingers of foam dissolving our creation, and neither of us felt sadness about it. The child smiled and said, "See? That''s the part you forgot."',
'2025-12-10', 'Infinite beach at golden hour, warm shallow tide',
'The play deepened from simple sandcastle building into a genuine reconnection with spontaneity. Each structure we built was more elaborate and joyful, and I noticed myself letting go of the need for permanence.',
'The tide washed away our creations without sadness, and the child''s final words illuminated what I had been missing.',
'bittersweet joy', 4, 'PARTIAL', 5, false, NULL, false, false,
'The inner child is teaching me about non-attachment and presence. The sandcastles represent the things I build and cling to, while the tide is the natural impermanence I resist. I need to play more in waking life.',
false, true, NULL, '2025-12-10 07:15:00+00'),

(29, 1, 'The Weaver''s Loom',
'I stood in a vast chamber where an enormous loom stretched from floor to ceiling, its threads shimmering with colors I had no names for, each one humming with a different frequency. An ancient figure sat at the loom, neither male nor female, their hands moving with a rhythm older than language. They beckoned me closer and showed me how each thread was a relationship, an experience, a choice I had made or that had been made for me. Some threads were dark, almost black, and I instinctively reached to pull them out, but the weaver caught my hand. "Watch," they said, and traced how those dark threads created essential contrasts that made the bright patterns visible. Without the loss, the joy had no shape; without the fear, the courage had no meaning. I saw the whole tapestry of my life from a distance, and it was more beautiful than anything the individual threads could have promised. The weaver smiled and said, "You cannot edit what has already been woven, but you choose the next thread."',
'2025-12-14', 'Vast weaving chamber with cosmic loom, threads of light',
'The weaver demonstrated how every thread, even the darkest ones, served the overall pattern. My attempt to remove painful threads was gently corrected as the weaver revealed the interconnection of all experiences.',
'Stepped back to see the full tapestry and understood that wholeness requires every thread. The weaver offered me the choice of the next thread.',
'profound acceptance', 5, 'FULL', 5, false, NULL, true, false,
'This dream integrates so many themes from the past months. The weaver is a Self figure, showing me that shadow and light are equally necessary. The loom echoes the mountain and sunrise dreams, the same message of wholeness arriving in a new form.',
false, true, NULL, '2025-12-14 07:00:00+00'),

(30, 1, 'Butterfly Emergence',
'In a garden bursting with impossible blooms, I watched a butterfly struggling to free itself from a chrysalis attached to a low branch. Every instinct in me screamed to help, to peel back the casing and ease its pain, but something deeper held me back, a knowing that the struggle itself was forging the strength the wings would need. Minutes stretched into what felt like hours as the creature pushed and twisted and rested and pushed again. When it finally emerged, its wings were impossibly beautiful, covered in patterns that told a story I could almost read, spirals and fractals and colors that shifted as it moved. It rested on the branch, slowly opening and closing its wings as though learning its own new body. Then it lifted into the air and landed on my shoulder, so light I could barely feel it, and whispered in a voice like wind through leaves, "Thank you for not helping."',
'2025-12-15', 'Garden in full bloom, vibrant impossible flowers',
NULL,
'The butterfly landed on my shoulder and expressed gratitude for my restraint, teaching me that necessary struggle should not be interrupted.',
'quiet awe', 5, 'PARTIAL', 4, false, NULL, false, false, NULL,
false, true, NULL, '2025-12-15 08:30:00+00'),

(31, 1, 'Facing the Former Love',
'I found my ex sitting on a weathered park bench at sunset, the sky streaked with amber and violet, and for the first time in any dream about them there was no tension in my body when I sat down. We talked honestly, without the scripts we used to recite at each other, and they said something that unwound a knot I''d carried for years: "I needed to understand myself, and you were part of that journey, not the destination." I realized the same was true in reverse, that we had been mirrors for each other during a time when we each needed to see something we couldn''t find alone. We sat in comfortable silence and watched the sun sink below the tree line. When we stood to leave, we embraced with genuine warmth, the kind that comes from gratitude rather than longing. I walked away feeling lighter, no longer tethered by what couldn''t be, and the evening air smelled like jasmine and new rain.',
'2025-12-18', 'Park bench at sunset, amber and violet sky',
'The conversation moved from surface pleasantries into genuine honesty about what the relationship had meant. Each admission from my ex unlocked a corresponding understanding in me.',
'We parted with a warm embrace rooted in gratitude rather than attachment. Walking away felt like release rather than loss.',
'peaceful release', 5, 'FULL', 5, true,
'Journaled about the conversation with my ex-partner and wrote a letter of release that I burned safely',
false, false,
'This feels like the anima/animus projection finally being withdrawn. I can see my ex as a person who served a purpose in my development rather than as a source of pain or longing. The tether is genuinely cut.',
false, true, 'My ex''s birthday was last week and I noticed I felt neutral about it for the first time.', '2025-12-18 06:30:00+00'),

(32, 1, 'Sunrise on the Mountain',
'I stood at a mountain summit as the first light of dawn spread across the horizon, painting everything in shades of gold and rose. All the symbols from my months of dreaming were present and transformed: the door stood open behind me, no longer locked or mysterious, just a passage I had already walked through. The ocean stretched calm and silver far below, its depths no longer threatening but simply deep. The bridge I had once feared crossing was complete, its span solid and sure, connecting two lands I now recognized as different parts of myself. The shadow figure stood beside me, now exactly my height, and when I glanced sideways I saw my own face looking back with an expression of quiet companionship. We watched the sunrise together in comfortable silence, two halves of one whole witnessing the same beauty. The light reached us and I felt it not on my skin but inside my chest, warm and steady as a second heartbeat.',
'2025-12-20', 'Mountain summit at dawn, panoramic view',
NULL,
'The shadow and I stood together watching the full sunrise, no longer separate, both illuminated by the same light.',
'wholeness', 3, 'FULL', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2025-12-20 06:30:00+00'),

(33, 1, 'Solstice Fire',
'On the longest night of the year, I sat in a circle of dream figures around a great fire that burned without fuel, its flames reaching toward stars that seemed closer than they should be. I recognized each figure from dreams past: the shadow, the inner child, the wise woman, the guide, even the white wolf lying with its head on its paws. One by one they offered me gifts from the fire. The shadow placed courage in my hands, hot and pulsing like a coal that didn''t burn. The child gave wonder, light as a soap bubble but unbreakable. The wise woman offered patience, heavy and smooth like river stone. The guide gave purpose, sharp and clear as a blade of grass in morning light. As I received each gift, it transformed into golden light that sank through my skin and settled in my bones. The fire grew brighter with each exchange, and by the end the circle was bathed in a warmth that had nothing to do with temperature. The longest night, I understood, was also the turning point toward more light.',
'2025-12-20', 'Open clearing under winter stars, great fire at center',
'Each dream figure approached the fire in turn, drawing out a gift that matched their nature. The ritual was unhurried, each exchange deepening the sense of communion between all parts of the psyche.',
NULL,
'radiant gratitude', 6, 'FULL', 5, false, NULL, false, false,
'A solstice ritual of the psyche. Every major archetype from my dream journey appeared to offer their essential quality. This feels like a gathering of inner resources before the next phase of growth.',
false, true, 'Winter solstice today. Spent the evening by candlelight reflecting on the year.', '2025-12-20 08:00:00+00'),

(34, 1, 'River Journey',
'I lay in a small wooden boat on a calm river that wound through landscapes I half-recognized, the current gentle and sure beneath me. On the left bank, scenes from my past played like living paintings: my childhood kitchen, a university lecture hall, the apartment where I lived alone for the first time, each one vivid but untouchable. On the right bank, possible futures shimmered and shifted: a house with a garden, a desk covered in unfinished work, faces I hadn''t met yet smiling in doorways. The river didn''t force me toward either bank, and I realized I could row in any direction or simply stay centered in the current and trust its flow. I chose to stay, trailing my fingers in the cool water, watching both banks with equal curiosity and no urgency. Small fish darted beneath the surface, catching light, and I understood that the river itself was the point, not any destination it might reach. A heron lifted from the reeds ahead and flew the direction I was floating, as though confirming the way.',
'2025-12-23', 'Gentle river through varied landscapes, past and future on opposing banks',
'The river carried me past increasingly personal scenes, each bank showing complementary visions. The temptation to steer toward either past or future gradually gave way to contentment with the current.',
'Chose to stay in the river''s current, trusting its direction. A heron confirmed the path forward.',
'serene trust', 4, 'PARTIAL', 5, true,
'Drew the river journey in my sketchbook, mapping both banks with past and future scenes',
false, false,
'The river is the Tao, the flow of life that carries me when I stop fighting. Choosing the center rather than either bank feels like real progress toward equanimity.',
false, true, NULL, '2025-12-23 08:15:00+00'),

(35, 1, 'Clock Without Hands',
'I climbed the narrow spiral staircase of an ancient clock tower, the stone walls vibrating with a deep mechanical pulse, and emerged into the chamber where a massive clock face looked out over a sleeping city. The clock had no hands, its face blank and luminous as a full moon. An old clockmaker sat at a workbench surrounded by gears of every size, each one turning at its own pace, and he looked up at me without surprise. "Time isn''t as linear as you believe," he said, holding up a gear that showed how every moment connected to every other, past looping into future and back again. Inside the mechanism, I could see how a childhood afternoon linked to a moment I hadn''t lived yet, how grief and joy occupied the same gear tooth. Understanding dawned slowly, like the sunrise I had watched in another dream: rushing and waiting were both illusions. Only presence mattered, only the willingness to be fully inside each turning gear. The clockmaker handed me a small gear and said, "Keep this. It''s the one called Now."',
'2025-12-28', 'Ancient clock tower overlooking sleeping city',
'The clockmaker patiently demonstrated the non-linear connections between moments, using gears to show how past, present, and future interlock. Each revelation deepened my sense of time as a web rather than a line.',
NULL,
'quiet understanding', 4, 'FULL', 5, false, NULL, false, false,
'The clockmaker is another wise old man figure. The handless clock suggests freedom from time-anxiety. The gear called "Now" is the simplest and most powerful teaching from this dream series.',
false, true, 'Year-end reflections have me thinking about how fast time seems to move.', '2025-12-28 06:45:00+00');
-- ============================================
-- 7. DREAMS - JANUARY 2026 (Self-Discovery/Awakening)
-- ============================================
INSERT INTO dreams (id, user_id, title, narrative, dream_date, setting, development, ending, emotion_on_waking, emotional_intensity, lucidity_level, sleep_quality, ritual_completed, ritual_description, is_recurring, is_nightmare, personal_interpretation, is_indexed, ai_extraction_done, conscious_context, created_at) VALUES

-- Dream 36: Conversation with Mother — Tier B, Jan 3, PARTIAL, intensity 5, quality 5, ritual
(36, 1, 'Conversation with Mother',
'I sat across from my mother at a kitchen table bathed in warm morning light, but this was not a memory—it was something truer. She looked at me with eyes unburdened by the roles we had built between us and began to speak about her own fears at my age, the dreams she had shelved, the doubts she never voiced. I listened without the usual defenses rising and felt something ancient soften between us. She reached across and took my hand, and I saw her not as parent but as a woman who had done her best with what she understood. Tears fell from both of us, not from sadness but from the relief of finally being seen. I told her I forgave her for the things she could not give, and she said the same to me. The kitchen filled with sunlight so bright it dissolved the walls, and we sat together in that openness.',
'2026-01-03', 'Warm kitchen flooded with morning sunlight', 'Conversation deepened from surface pleasantries to authentic sharing of fears and dreams; defenses gradually dissolved on both sides', 'Kitchen walls dissolved into pure sunlight while mother and dreamer sat together in mutual forgiveness', 'tenderness',
5, 'PARTIAL', 5, true, 'Journaled key symbols and sat with emotions for 10 minutes', false, false,
'I think this dream is my psyche''s way of completing the mother-daughter reconciliation that has been building across months of dreamwork. Seeing her as a full person rather than just a parent feels like genuine progress toward wholeness.',
false, true, 'Had a phone call with my mother earlier that week where we discussed some old family stories', '2026-01-03 07:30:00+00'),

-- Dream 37: The Healed Home — Tier B, Jan 5, FULL, intensity 4, quality 5, no ritual
(37, 1, 'The Healed Home',
'I returned to my childhood home, but it had been transformed—not restored to what it once was, but elevated into what it could have been. The hallways were wide and filled with light, the ceilings higher, every room in gentle order. In the first room I entered, a gift waited on a table wrapped in gold paper: when I opened it, a feeling of deep peace washed through me. The next room offered creativity—paints and instruments and half-finished stories I recognized as my own. A third room held courage, though I could not say what shape it took, only that standing inside it made me feel unshakable. In the garden, my younger self played happily among flowers that had never grown there in waking life. I understood I could visit this home any time but no longer needed to live in it. Home had become something I carried within me.',
'2026-01-05', 'Childhood home, luminous and transformed', 'Moved room to room discovering gifts of peace, creativity, and courage; childhood self played safely in the garden', 'Realized home was now portable and internal rather than a fixed place to return to', 'freedom',
4, 'FULL', 5, false, NULL, false, false,
'The healed home feels like my unconscious telling me the work of reclaiming my childhood foundations is complete. I don''t need to keep going back—I can bring what matters forward.',
false, true, NULL, '2026-01-05 08:00:00+00'),

-- Dream 38: Fire of Transformation — Tier B, Jan 8, FULL, intensity 6, quality 5, recurring, ritual (2-dream day, 6:30am)
(38, 1, 'Fire of Transformation',
'I stood in a forest clearing and deliberately built a fire, feeding it with things I no longer needed—old resentments that looked like knotted rope, outdated beliefs shaped like cracked masks, worn-out identities draped like threadbare coats. The flames accepted everything without judgment, burning warm rather than destructive. Smoke rose in spiraling columns that caught the moonlight. From the center of the ashes, green shoots pushed upward with startling speed, unfurling into plants I had never seen but somehow recognized. A phoenix rose from the deepest embers, its feathers the color of every sunrise I had ever witnessed. It circled once overhead and then settled on my shoulder, weightless and radiant. I understood I was both the fire and what rose from it, both the destruction and the creation.',
'2026-01-08', 'Moonlit clearing surrounded by ancient forest', 'Fed old resentments and beliefs into the fire; watched smoke rise and green shoots emerge from ashes; phoenix appeared from embers', 'Phoenix settled on shoulder as dreamer realized they were both the destroyer and the creator', 'renewal',
6, 'FULL', 5, true, 'Active imagination dialogue with the fire--wrote what it said to me', true, false,
'This is the ocean dream''s counterpart in fire—a recurring transformation motif. The phoenix is almost too on-the-nose, but the felt sense of being both the burning and the rebirth was genuinely new.',
false, true, 'I had been journaling about habits I wanted to release, which probably fed into this dream', '2026-01-08 06:30:00+00'),

-- Dream 39: Voices in the Rain — NEW, Tier B, Jan 8, PARTIAL, intensity 5, quality 4 (2-dream day, 8:00am)
(39, 1, 'Voices in the Rain',
'I stood in a meadow as a gentle rain began to fall, each droplet carrying a whispered fragment—my grandmother''s lullaby, a friend''s laughter from years ago, my own voice reading aloud as a child. The whispers were not ghostly but warm, as though the rain itself were made of living memory. I tilted my face upward and let the voices wash over me without trying to catch any single one. The rain collected into a stream at my feet and flowed toward a garden I could see at the meadow''s edge. I followed the stream, kneeling to touch flowers that bloomed where the water touched soil. Each blossom held a remembered moment—a birthday candle, a first snow, a hand held in the dark. I understood that nothing truly loved is ever lost; it only changes form.',
'2026-01-08', 'Open meadow in gentle rainfall flowing to a garden', 'Rain of whispered memories collected into a stream; followed stream to garden where flowers bloomed with remembered moments', 'Knelt among flowers of memory and understood that love changes form but never disappears', 'warmth',
5, 'PARTIAL', 4, false, NULL, false, false,
'The rain carrying voices feels like a gentler version of the earlier Cave of Echoes. Instead of my thoughts bouncing back, I''m receiving the voices of people I love. Growth from self-focus to relational awareness.',
false, true, NULL, '2026-01-08 08:00:00+00'),

-- Dream 40: Shadow Integration — Tier B, Jan 10, FULL, intensity 5, quality 5, ritual
(40, 1, 'Shadow Integration',
'I entered a hall of mirrors expecting my reflection, but instead the shadow figure waited at the far end—wearing my face for the first time, no longer obscured. It spoke clearly: "I am everything you rejected, and I contain your greatest gifts." There was no confrontation, no chase, no bargaining. I simply walked toward it and it walked toward me. When we met in the center of the hall, the merge happened without struggle—like two streams joining a river. Every mirror now showed a single figure, more complete than either had been alone. The hall itself brightened, shadows lifting from the corners. I felt whole in a way I had never experienced while awake, as though a missing frequency had been restored to my inner music.',
'2026-01-10', 'Hall of mirrors, gradually brightening', 'Walked toward shadow figure who wore dreamer''s face; they met in the center without conflict and merged like two streams', 'All mirrors showed one complete figure; hall filled with light as wholeness settled in', 'wholeness',
5, 'FULL', 5, true, 'Meditation on shadow integration, 15 minutes of sitting with the feeling of wholeness', false, false,
'This feels like the culmination of every shadow encounter since October. No more running, no more dancing around it—just quiet acceptance. Jung would say I''ve integrated the shadow, but it feels less like a victory and more like a homecoming.',
false, true, 'I had been reading about Jungian shadow work and practicing acceptance meditation', '2026-01-10 07:45:00+00'),

-- Dream 41: Cave of Origins — Tier B, Jan 12, FULL, intensity 4, quality 5, no ritual
(41, 1, 'Cave of Origins',
'I descended into the crystal cave from earlier dreams, but now every formation glowed with its own inner light—amber, violet, blue-white—making the darkness irrelevant. At the heart of the cave, a circular chamber revealed a vast tapestry hanging in midair, woven from threads I recognized as moments from my life. Golden threads for joy, deep blue for grief, crimson for anger, silver for wonder—every color essential to the pattern. Even the dark threads created necessary contrast without which the image would be flat. I traced my finger along a thread and felt the memory it carried pulse through me. The weaving was far from complete, stretching into an unfinished edge that shimmered with possibility. I left the cave carrying the knowledge that my life was a work of art still in progress.',
'2026-01-12', 'Crystal cave glowing with inner light, central tapestry chamber', 'Descended into illuminated cave; found life-tapestry woven from colored threads of experience; traced memories', 'Left the cave understanding life as an incomplete but beautiful work of art', 'awe',
4, 'FULL', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2026-01-12 08:15:00+00'),

-- Dream 42: Rain and Sun Together — Tier B, Jan 15, FULL, intensity 5, quality 5, ritual
(42, 1, 'Rain and Sun Together',
'Rain and sunshine fell simultaneously, and a rainbow bridge materialized from the light-fractured drops—solid enough to stand on, vibrating gently underfoot. I climbed the arc and from its peak could see every landscape from my dreams laid out below as one continuous terrain. The dark forest adjoined the crystal cave, which opened onto the infinite beach, which curved toward the mountain, which overlooked the ocean. The corridor with its doors ran like a spine through all of it. I had been traveling a single country all along, visiting its provinces without seeing the whole. The rainbow bridge connected them all, and standing at its apex, I could feel the dream-territory breathing as one living thing. When the rain stopped, the bridge remained, permanent and shining.',
'2026-01-15', 'Rainbow bridge arching over entire dreamscape', 'Climbed rainbow bridge to its peak; surveyed all dream locations as one unified landscape; recognized interconnection', 'Bridge became permanent as rain stopped, connecting all dream territories', 'understanding',
5, 'FULL', 5, true, 'Drew the rainbow bridge connecting all my dream locations in my journal', false, false,
'Seeing all my dream places as one landscape gave me chills. It mirrors my waking realization that all the "separate" issues I''ve been working through are really facets of one process.',
false, true, 'Had been reviewing my dream journal and noticing recurring settings', '2026-01-15 06:45:00+00'),

-- Dream 43: Teaching What I Learned — Tier B, Jan 18, FULL, intensity 4, quality 5, no ritual (2-dream day, 6:30am)
(43, 1, 'Teaching What I Learned',
'The teacher figure from earlier dreams appeared and said simply, "Your turn." I found myself in a circular classroom made entirely of light, facing a group of seekers whose faces I could not quite resolve but whose attentiveness was palpable. I began to explain dream symbolism—how the shadow is not the enemy, how water represents the unconscious, how doors are thresholds of change. As I spoke, I understood each concept more deeply than when I had merely experienced it. The seekers asked questions I did not expect, and my answers surprised me with their clarity. The teacher watched from the back, nodding once. "Now you begin to see," she said, and the classroom expanded outward in every direction.',
'2026-01-18', 'Circular classroom constructed of light', 'Teacher figure stepped aside; dreamer taught seekers about dream symbolism, deepening own understanding through explanation', 'Teacher approved with "Now you begin to see" as classroom expanded infinitely', 'purpose',
4, 'FULL', 5, false, NULL, false, false,
'Teaching in the dream felt like a consolidation phase—my unconscious testing whether I truly understand what I''ve been learning. The deepening through teaching mirrors how I process insights in waking life.',
false, true, NULL, '2026-01-18 06:30:00+00'),

-- Dream 44: The Map Unfolds — NEW, Tier B, Jan 18, FULL, intensity 5, quality 5, ritual (2-dream day, 8:00am)
(44, 1, 'The Map Unfolds',
'A figure I could not see clearly pressed an ancient folded map into my hands. As I opened the first fold, a territory appeared—mountains labeled "Ambition" rising from a plateau of "Routine." Each subsequent fold revealed more: rivers of grief cutting deep canyons, dense forests of creativity teeming with half-formed ideas, a desert of patience stretching wide and still. The places I had already visited were marked in gold ink, trails and footprints visible. But vast regions shimmered in silver, unexplored, pulsing faintly as though waiting. At the center of the map sat a compass whose needle pointed not north but inward, always inward, no matter how I turned. I folded the map carefully and placed it against my chest, where it dissolved through skin and settled somewhere behind my ribs.',
'2026-01-18', 'Undefined space where the map itself became the landscape', 'Unfolded map revealing psychic territories; gold-marked visited regions and shimmering unexplored ones; compass pointed inward', 'Map dissolved into dreamer''s chest, becoming internalized', 'curiosity',
5, 'FULL', 5, true, 'Created a mind map of my inner landscape based on the dream map', false, false,
'The inward-pointing compass is the clearest symbol my unconscious has offered yet. The map dissolving into my body suggests that self-knowledge isn''t something I carry—it''s something I become.',
false, true, 'I had just finished a self-assessment exercise at work that prompted a lot of introspection', '2026-01-18 08:00:00+00'),

-- Dream 45: River to Ocean — Tier B, Jan 20, FULL, intensity 4, quality 5, no ritual
(45, 1, 'River to Ocean',
'I followed the familiar river downstream to the place where fresh water met salt. The ocean that had once terrified me in early dreams lay calm and transparent, sunlight reaching deep into its body. I could see the creatures below—vast and ancient, yes, but luminous rather than menacing, their movements slow and purposeful. Without hesitation I swam down, breathing underwater as naturally as air. The enormous shapes turned toward me, and I recognized them as guardians of the deep, not monsters. One brushed against me gently, and a current of ancient knowing flowed through the contact. I surfaced eventually, floating on my back, staring at a sky full of stars reflected perfectly in the still water.',
'2026-01-20', 'Where river meets calm, transparent ocean', 'Followed river to ocean; swam down voluntarily among ancient creatures; received knowing through contact', 'Floated on the surface between mirrored stars above and below', 'peace',
4, 'FULL', 5, false, NULL, false, false,
'The ocean that once represented drowning terror now represents deep knowing. Swimming down voluntarily is the exact opposite of dream 2. I''m no longer afraid of my own depths.',
false, true, NULL, '2026-01-20 08:00:00+00'),

-- Dream 46: Mirror of Acceptance — Tier B, Jan 22, FULL, intensity 4, quality 5, no ritual
(46, 1, 'Mirror of Acceptance',
'I stood before the mirror one final time, but this mirror was different—round, framed in living wood, placed in a room open to the sky. My reflection smiled genuinely and moved in perfect sync. Then it shifted, showing all my ages layered simultaneously: the wide-eyed child, the uncertain teenager, the striving young adult, the present self, and an elder I had not yet become. They were not separate but translucent, each visible through the others. "We are always all of us," the reflection spoke, and every version nodded. I pressed my hand to the glass, and it was warm. Integration, I understood, was not becoming one single thing but learning to hold many things at once without conflict.',
'2026-01-22', 'Open-air room with round mirror framed in living wood', 'Mirror showed all ages of self layered transparently; each version visible through the others', 'Touched warm glass and understood integration as holding multiplicity without conflict', 'acceptance',
4, 'FULL', 5, false, NULL, false, false,
NULL,
false, true, NULL, '2026-01-22 06:30:00+00'),

-- Dream 47: Wolf Pack — Tier B, Jan 25, FULL, intensity 3, quality 5, ritual
(47, 1, 'Wolf Pack',
'The white wolf appeared at the forest edge, but this time it was not alone—a full pack waited behind it, eyes gleaming in the twilight. They did not approach as guides or protectors; the invitation was to join as an equal. I dropped to four legs as naturally as breathing, seeing the world through wolf-eyes: scent-trails like colored ribbons, the forest floor a map of stories. We ran together through the trees, and the forest that had once been dark and threatening was now unmistakably home. I felt the pack''s awareness as an extension of my own—each wolf a node in a web of shared instinct. The forest welcomed us with rustling approval.',
'2026-01-25', 'Forest at twilight, welcoming and familiar', 'Joined wolf pack on four legs; perceived world through wolf-senses; ran as part of shared awareness', 'Forest accepted the pack and dreamer as its own', 'belonging',
3, 'FULL', 5, true, 'Went for a run in the forest, honoring the wolf energy', false, false,
'Running with the wolves feels like reconnecting with instinct after months of intellectual dreamwork. The pack represents community and belonging—something I''ve been cultivating more deliberately in waking life.',
false, true, 'I had recently joined a hiking group and felt a new sense of community', '2026-01-25 07:15:00+00'),

-- Dream 48: Garden of Forgiveness — NEW, Tier A, Jan 26, FULL, intensity 5, quality 5, ritual
(48, 1, 'Garden of Forgiveness',
'I entered a walled garden through a gate that opened at my touch, its iron warm as though sun-heated from the inside. Every plant within represented someone I needed to forgive—I knew this without being told, the way you know things in dreams. A thorny rosebush near the entrance was my father; a wilting orchid in the corner was a friend who had betrayed my trust years ago; a stunted sapling at the center, struggling for light, was myself. I found a watering can already full and began with the rose, letting water fall over its thorns. As I watered, old pain lifted from the plant as fine mist—visible, tangible, then dissipating into the open sky. The thorns softened but did not disappear; they simply stopped being weapons. I moved to each plant in turn, and with each watering, mist rose and vanished, the garden growing more vibrant. When I finally reached the sapling—my own unforgiven self—the watering can was nearly empty, but what remained was enough. The sapling straightened, its leaves deepening to emerald. As the last mist cleared, the garden wall began to crumble, not violently but like sand returning to a beach. Beyond it stretched an endless meadow of wildflowers reaching to the horizon in every direction. I stepped through the gap where the wall had been, and the garden followed me outward, roots spreading into the meadow, no longer needing boundaries to grow.',
'2026-01-26', 'Walled garden with diverse plants, opening to endless meadow', 'Watered each plant-person releasing pain as mist; thorns softened; garden grew vibrant; self-forgiveness came last', 'Garden wall crumbled revealing infinite meadow; garden spread outward without boundaries', 'release',
5, 'FULL', 5, true, 'Wrote forgiveness letters to three people, including myself', false, false,
'This is the most explicit forgiveness dream I''ve had, and the detail that the thorns softened but didn''t vanish feels important—forgiveness doesn''t erase what happened, it changes our relationship to it. Watering myself last mirrors my real pattern of prioritizing others'' feelings. The wall crumbling suggests that holding onto resentment was the real prison, not the people who hurt me.',
false, true, 'I had been working through a guided forgiveness meditation series and recently wrote in my journal about unresolved anger toward my father and an old friend', '2026-01-26 08:00:00+00'),

-- Dream 49: Flight Without Fear — Tier A, Jan 28, FULL, intensity 3, quality 5, no ritual (2-dream day, 6:30am)
(49, 1, 'Flight Without Fear',
'I stood on a rooftop—the same futuristic city from October, but now I recognized it as the architecture of my own mind, every tower a thought-structure, every bridge a connection I had built. I stepped off the edge without a moment''s hesitation and flew. There was no shadow following on the ground, no anxiety pulling at my stomach, nothing to flee from or toward—just the pure kinaesthetic joy of movement through open air. Wind pressed against my face and I laughed. Other dreamers appeared alongside me, strangers whose faces I could not quite see but whose presence I trusted completely. We flew in formation like migrating birds, then scattered joyfully, then regrouped, a dance of individual freedom within communal belonging. Below, the city pulsed with light in patterns that matched our movements, as though the mind itself was celebrating. I climbed higher and higher until the city became a single point of brilliance, and the sky opened into a field of stars so dense they looked like spilled milk. I floated there, weightless, breathing starlight, and understood that the freedom I had been seeking was never about escape—it was about choosing to be fully present wherever I was.',
'2026-01-28', 'Above a luminous cityscape of the dreamer''s own mind, then into starfield', 'Flew without shadow or fear; joined other dreamers in joyful formation flying; climbed above the city into stars', 'Floated in starfield understanding that freedom is presence, not escape', 'joy',
3, 'FULL', 5, false, NULL, false, false,
'This is the direct counterpoint to dream 5 from October—same city, same flight, but entirely transformed. No shadow pursuer, no anxiety. The other dreamers feel significant too; individuation doesn''t mean isolation. Floating among stars at the end has a quality of transcendence that is new in my dream life, as though the psyche is reaching beyond personal work toward something universal.',
false, true, 'I''d had a particularly good week—felt confident and connected at work and in my personal life', '2026-01-28 06:30:00+00'),

-- Dream 50: The Bridge Completed — NEW, Tier A, Jan 28, FULL, intensity 4, quality 5, ritual (2-dream day, 8:00am)
(50, 1, 'The Bridge Completed',
'I returned to the bridge over the void from October—the same fog below, the same impossible span—but the fear was gone, replaced by a workman''s calm. Sections of the bridge were missing, gaps where planks should be, and I understood that this time I was here to build rather than cross. I found wood and tools at my feet and knelt to work. Each plank I fitted into place carried the weight of a lesson: one was the night I forgave my shadow, another the morning I understood my mother, a third the moment I chose to swim into the ocean rather than away from it. My hands knew what to do. From the far side, my father appeared, working toward me from his end. He too was placing planks—his own lessons, his own hard-won pieces. We did not speak, but the rhythm of our hammers found a shared tempo, a conversation in percussion. We met precisely in the middle. The plank we placed together was heavier than the rest, and when it settled, the entire bridge shuddered and then steadied—permanent now, solid, beautiful in its honest craftsmanship. My father looked at me with an expression I had waited my whole life to see: pride without condition. We stood side by side at the center, the fog below thinning to reveal not a void but a river, flowing peacefully toward an ocean I could just barely see. The bridge was no longer a test. It was a meeting place.',
'2026-01-28', 'Bridge over the void from October, fog thinning to reveal river below', 'Built missing bridge sections with planks of learned lessons; father worked from the other side; hammers found shared rhythm', 'Met father at center; placed final plank together; bridge became permanent as fog revealed a peaceful river below', 'gratitude',
4, 'FULL', 5, true, 'Called my father and had an honest conversation about our relationship', false, false,
'This dream completes the bridge that terrified me in October. Building it with my own hands—with planks made of actual lessons—is such a clear integration metaphor. My father building from the other side and meeting me in the middle heals something I didn''t know still needed healing. The void becoming a river below suggests that what I feared as emptiness was always flowing life. I woke up wanting to call him, and I did.',
false, true, 'My father and I had exchanged some tentative texts about getting together, which felt like a small breakthrough after months of distance', '2026-01-28 08:00:00+00'),

-- Dream 51: Council of Selves — NEW, Tier A, Jan 29, FULL, intensity 5, quality 5, ritual
(51, 1, 'Council of Selves',
'I entered a circular stone chamber through an archway carved with symbols I had seen scattered across months of dreams—doors, waves, feathers, flames. Seated around a round table were all the figures who had populated my dream life: the shadow, no longer dark but merely shaded; the inner child, kicking her feet and humming; the wise old woman with her warm stone; the mysterious guide leaning on his staff; the white wolf curled at ease beneath the table; my mother and father seated side by side, their chairs touching; the teacher figure with ink-stained fingers. One by one, each spoke what they represented. The shadow said, "I am your unlived courage." The child said, "I am your capacity for wonder." The wise woman said, "I am your intuition." The guide said, "I am your will to grow." The wolf said nothing but pressed its warm flank against my leg, and I understood: instinct needs no words. My mother said, "I am your tenderness." My father said, "I am your structure." The teacher said, "I am your desire to make meaning." I sat at the center of them all, and as each spoke, light gathered on the floor beneath the table, forming an intricate mandala—gold and violet and ocean-blue and forest-green. I realized with a certainty that vibrated in my bones that I was the dreamer of every one of these figures. They were not visitors; they were me, expressed in the language my sleeping mind could understand. The mandala completed itself with a pulse of warmth that rose through the stone floor and into my body. The chamber dissolved, but the council remained, now seated in a circle under open sky, and I sat among them as both host and guest.',
'2026-01-29', 'Circular stone chamber with carved archway, then open sky', 'Each dream figure spoke their symbolic meaning; light gathered into mandala on floor; dreamer realized all figures were aspects of Self', 'Chamber dissolved to open sky; council remained with dreamer as both host and guest; mandala pulsed warmth into body', 'integration',
5, 'FULL', 5, true, 'Drew the mandala from the dream and placed it on my altar', false, false,
'This feels like the penultimate dream of the cycle—a gathering of every archetype, each naming itself. The mandala is Jung''s symbol of the Self, and its formation from the collective light of all these figures confirms what I''ve been intuiting: individuation is not about choosing one part but recognizing that all parts are the dreamer. I am the host and the guest, the question and the answer. Waking up, I felt as though something had clicked into place at a level deeper than thought.',
false, true, 'I had been rereading Jung''s "Man and His Symbols" and spent the previous evening meditating on what each recurring dream character might represent in my waking life', '2026-01-29 07:00:00+00'),

-- Dream 52: Future Self — Tier A, Jan 30, FULL, intensity 4, quality 5, no ritual
(52, 1, 'Future Self',
'I walked through a garden I had never seen but immediately recognized as my own—as though I had planted it years from now and was visiting it from the past. At a stone bench beneath a blooming magnolia, my future self sat waiting with an expression of calm amusement. They looked like me but softer around the edges, laugh lines deeper, eyes holding a quality of settled peace I was still learning. "You''ll figure it out," they said before I could ask any questions. "Not because you have to, but because you''ll choose to." I sat beside them and felt the bench warm beneath me. They showed me images without speaking—not of events but of qualities: patience flowing like honey, resilience bending like bamboo, joy rising like bread dough, slow and certain. "It''s not about reaching a destination," they continued, "it''s about finding meaning in the walk itself." A breeze carried magnolia petals across us both. I asked if they were happy, and they laughed—a real laugh, full and unguarded. "Happy isn''t quite the right word," they said. "Whole." The garden hummed around us, every flower turned toward the conversation as though listening. I woke carrying that word in my chest like a warm stone.',
'2026-01-30', 'Future garden beneath blooming magnolia', 'Met future self on stone bench; received wordless images of patience, resilience, joy; discussed meaning of the journey', 'Future self named their state as "whole" rather than "happy"; dreamer woke carrying the word like a warm stone', 'peace',
4, 'FULL', 5, false, NULL, false, false,
'Meeting my future self and hearing "whole" instead of "happy" feels like the most honest thing my unconscious has offered me. It reframes the entire individuation journey—not toward happiness as an emotion but wholeness as a state of being. The garden setting connects to the Garden of Forgiveness two dreams ago, suggesting that what I plant now in forgiveness will bloom into this future.',
false, true, 'I had been journaling about long-term goals and realized I couldn''t clearly define what "success" meant to me anymore—the old definitions felt hollow', '2026-01-30 06:45:00+00'),

-- Dream 53: The Dreamer Awakens — NEW, Tier A, Jan 31, FULL, intensity 6, quality 5, ritual
(53, 1, 'The Dreamer Awakens',
'I was dreaming, and I knew I was dreaming—not the partial awareness of earlier lucid moments, but a full, ringing clarity, as though someone had turned up the resolution on reality. More than that: I understood that every dream I had dreamt over these months formed one continuous story, each night a chapter, each symbol a word in a sentence the psyche had been writing since October. I began to move through the dream-territory at speed, revisiting key locations. The locked door from the first dream stood open, its corridor no longer dark but lamp-lit and welcoming. The ocean was calm and transparent, its guardians visible and benign, swimming in slow spirals. The dark forest had become cathedral-green, shafts of sunlight illuminating the wolf-trails. The bridge was solid, my father''s footprints alongside my own in the dust of its planks. The hall of mirrors reflected a single integrated self, smiling. I moved faster, touching each place like a hand running along a beloved bookshelf—the mountain summit, the crystal cave, the rainbow bridge, the garden of forgiveness, the circular classroom. Everything glowed with accumulated meaning, every surface rich with the residue of insight. I stopped at last in the center of it all—the mandala chamber from the council dream, but now the mandala floated in the air, spinning slowly, made of pure light. I stood beneath it and felt the warmth of recognition: I was the dreamer, and the dream was me, and waking up did not mean the dream would end. I chose to wake gently, easing out of sleep the way one surfaces from deep water—slowly, savoring the transition. I carried the awareness with me across the threshold, feeling it settle into my waking body like a second heartbeat.',
'2026-01-31', 'All dream locations revisited in sequence, centered on the mandala chamber', 'Full lucid awareness of all dreams as one continuous story; rapid revisitation of every key location, each transformed; arrived at mandala chamber', 'Chose to wake gently, carrying dream-awareness across the threshold into waking life like a second heartbeat', 'awakening',
6, 'FULL', 5, true, 'Morning meditation reflecting on the entire dream journey so far', false, false,
'This is the dream I have been building toward without knowing it. Full metacognition—seeing the whole arc from October''s anxiety to January''s integration as one unified narrative. Revisiting each location and finding it transformed is my unconscious showing me the evidence of my own growth. Choosing to wake gently, rather than being jolted awake by fear, feels like the most important moment of the entire journey. The "second heartbeat" I carried into waking is still with me as I write this. I believe this dream marks the completion of a major individuation cycle, though I suspect the spiral continues.',
false, true, 'I had spent the previous evening reading through my entire dream journal from October to now, and the patterns were overwhelming—I went to bed with a sense of approaching completion', '2026-01-31 07:30:00+00');
-- ============================================
-- 8. DREAMS - FEBRUARY 2026 (Wholeness/Peak)
-- ============================================
INSERT INTO dreams (id, user_id, title, narrative, dream_date, setting, development, ending, emotion_on_waking, emotional_intensity, lucidity_level, sleep_quality, ritual_completed, ritual_description, is_recurring, is_nightmare, personal_interpretation, is_indexed, ai_extraction_done, conscious_context, created_at) VALUES

-- Dream 54: Tier A (8-12 sentences), recurring, ritual
(54, 1, 'Dawn Chorus',
'I woke within the dream to birdsong—not a single voice but a vast, layered chorus that filled the air like warm light filling a room. I was lying in a meadow at the edge of a forest, the sky shifting from deep indigo to rose gold as dawn approached, dew glistening on every blade of grass around me. Every bird from my previous dreams was present: the departing flock that had lifted weight from my chest, the single white-feathered bird from the windowsill, the birds that had flown alongside me over the glass city. They perched in the trees surrounding the clearing—dozens of species, impossible combinations that would never gather in waking life, yet here they sang in perfect harmony. Each voice carried a distinct quality: one bird sang of grief released, another of fear confronted, a third of joy discovered in unexpected places. I realized that each song represented a lesson I had learned across these months of dreaming, and the harmony they created together was greater than any single melody. Without thinking, I opened my mouth and began to sing with them, and my voice fit perfectly into the chorus as if a space had always been held for it. The dawn light broke over the treeline and painted everything in gold and rose, the colors so vivid they seemed to hum with their own frequency. I could feel the vibration of every voice in my chest, in my bones, in the ground beneath me—a resonance that erased the boundary between listener and song. The birds began to lift from the branches one by one, spiraling upward into the brightening sky, their song not fading but expanding, becoming part of the air itself. I lay back in the wet grass, tears streaming down my temples into the earth, overwhelmed by a gratitude so complete it felt like being held by the morning itself.',
'2026-02-03', 'A wildflower meadow at the edge of a familiar forest, dawn light spreading across the sky in bands of indigo, rose, and gold. Dew covers everything, refracting the early light into tiny prisms.', 'The dream built from a single awareness of sound into a crescendo of participation. What began as passive listening became active joining—the dreamer''s voice merging with the chorus, dissolving the boundary between self and world.', 'The birds spiraled upward into the dawn sky, their song becoming part of the air. I lay in the grass weeping with gratitude, held by the morning.', 'profound gratitude', 4, 'FULL', 5, true, 'Listened to birdsong meditation for 20 minutes, journaled about what each bird voice represents', true, false, 'This dream gathers every bird that has appeared across my journey and unites them in song. In Jungian terms, the birds are messengers of the Self—each one a fragment of insight that alone is incomplete but together forms a whole understanding. My voice fitting into the chorus suggests I am no longer a passive observer of my own unconscious but an active participant in its unfolding. The recurring nature of the bird motif tells me transformation isn''t a single event but an accumulation of small awakenings, each building on the last.', false, true, 'Feeling grateful for the dream practice. Five months of consistent journaling.', '2026-02-03 07:00:00+00'),

-- Dream 55: Tier A (8-12 sentences), ritual
(55, 1, 'The Quiet Ocean',
'I stood at the shore of an ocean I recognized immediately—the same vast dark water from my very first nightmare, the one that had nearly drowned me in October. But the sea had changed, or perhaps I had changed enough to see it differently. The surface was perfectly calm, a mirror of glass reflecting the pale pre-dawn sky so precisely that the horizon line had vanished entirely. I stepped onto the water and it held me, cool and solid beneath my bare feet, each step sending gentle ripples outward in concentric circles. I walked for what felt like a long time, the shore receding behind me, surrounded by nothing but sky above and sky reflected below, as though I moved through the interior of a pearl. Then I chose to sink—not falling, not being pulled, but deliberately releasing the surface tension and letting the water welcome me down. Beneath the surface was a cathedral of coral and light, columns of living stone reaching upward through water so clear it barely existed, shafts of pale blue luminescence drifting like the breath of something vast. The enormous shapes that had terrified me in the nightmare were here—visible now as gentle whale-like beings moving through the underwater architecture with a grace that made my heart ache. They turned toward me and I felt their communication not as sound but as knowing, a wordless recognition that said: you are welcome here, you have always been welcome here. I swam among them, their massive bodies creating currents that carried me through chambers of coral stained rose and gold by bioluminescence. The terror that had defined my first encounter with this ocean had transmuted completely into reverence, and I understood that the depths had never been hostile—only unfamiliar, only waiting for me to be ready.',
'2026-02-04', 'A vast ocean at dawn, its surface perfectly still and mirror-like. Below the surface, a cathedral of luminescent coral formations and open water of impossible clarity.', 'The dream progressed from stillness to immersion to communion. Walking on the surface gave way to a deliberate descent, and the underwater world revealed itself as sacred architecture rather than threatening abyss.', 'Swimming among the whale-like beings in the coral cathedral, carried by their gentle currents. The old terror had become reverence.', 'deep peace', 3, 'FULL', 5, true, 'Took a long bath as ocean meditation, breathing through old fear memories', false, false, 'This is the complete reversal of my first nightmare—the drowning dream from October that started everything. What was once an ocean of primal terror has become a cathedral of belonging. Jung wrote that the unconscious is not inherently threatening, only unfamiliar, and this dream proves it viscerally. The whale-beings were always there; it was my fear that made them monstrous. Choosing to sink rather than struggling to stay on the surface is the deepest act of trust I have performed in any dream.', false, true, 'Remembered the first ocean nightmare and how far I have come since October.', '2026-02-04 07:15:00+00'),

-- Dream 56: Tier A (8-12 sentences), 2-dream day (first dream), NO ritual
(56, 1, 'Open Door',
'I found myself once more in the stone corridor where everything began—the same damp walls, the same flickering torchlight casting long shadows, the same ancient air that tasted of centuries. But the massive wooden door that had been locked since my very first dream now stood wide open, its hinges resting at full extension as though it had been waiting patiently for me to arrive. Beyond the threshold was not the dramatic revelation I had always imagined—no blinding light, no cosmic truth, no treasure. It was simply a garden, ordinary and beautiful in the way that only real things can be: flower beds slightly overgrown, a stone birdbath with moss climbing its pedestal, a wooden bench weathered silver by years of rain and sun. Bees moved between lavender bushes and the air smelled of warm earth and green things growing without anyone''s permission. I stood in the doorway for a long time, one hand on the ancient wood, understanding that the extraordinary had never been what waited beyond the door—it had been the journey through the corridor itself, every wrong turn and locked passage and moment of despair. The garden did not demand anything of me; it did not ask me to be transformed or enlightened or worthy. I could step through or stay in the corridor, and either choice was whole and complete. I stepped through, and the grass was soft and real beneath my feet, and a breeze carried the scent of something blooming that I could not name but recognized in my body. The corridor behind me did not vanish or close—it remained, an open passage between where I had been and where I now stood, both places equally mine. I sat on the weathered bench and watched light move through the garden, and felt the quiet completion of a circle that had taken five months to close.',
'2026-02-05', 'The familiar stone corridor with its flickering torches, opening onto a simple cottage garden with overgrown flower beds, a mossy birdbath, and a weathered wooden bench.', 'The dream moved from recognition of the familiar corridor to the revelation of what lay beyond the door. The anticlimax of the ordinary garden became the dream''s deepest statement—that the sacred can wear the clothing of the everyday.', 'Sitting on the weathered bench in the garden, watching light move through the flowers. The corridor remained open behind me, both spaces equally mine.', 'quiet completion', 3, 'FULL', 5, false, NULL, false, false, 'This dream closes the circle that opened with my very first dream in October. The locked door was the central image of my entire journey—thresholds, barriers, the question of what lies beyond. Jung taught that individuation is not about arriving at some grand destination but about becoming more fully who you already are. The garden''s ordinariness is the revelation: wholeness is not spectacular, it is the quiet miracle of being present in your own life.', false, true, 'Reflecting on thresholds - starting a new chapter at work next week.', '2026-02-05 06:30:00+00'),

-- Dream 57: Tier A (8-12 sentences), 2-dream day (second dream), ritual
(57, 1, 'The Living Mandala',
'A mandala appeared in the sky above me, vast and slowly rotating, its geometric patterns drawn in lines of living light that shifted through every color I had ever seen and some I had no names for. I stood in an open field looking up, and as the mandala turned, I recognized that each of its concentric sections contained a miniature scene from a previous dream—the dark ocean, the spiral staircase, the childhood room, the crystal cave, the wolf in the forest, the bridge over the void. Every dream I had recorded over these five months was present, arranged in a pattern that revealed connections I had never consciously noticed: water dreams formed one arc, threshold dreams another, and the shadow encounters traced a spiral of their own toward the center. The mandala descended slowly, growing larger as it approached, until I could step into its outermost ring and walk among the dream-scenes like rooms in a gallery. I moved inward through the rings, each layer more integrated than the last—the nightmares and the peaceful dreams no longer separate categories but complementary halves of the same understanding. At the center, where all the sections converged into a single point, stood a mirror unlike any I had encountered before—it reflected not my face or my body but pure light, warm and steady, the essence of something that had no form because it was the source of all forms. I reached out and touched the mirror''s surface and it was warm as skin, warm as breath, warm as the first moment of recognition between self and Self. The mandala began to descend further, its geometric patterns softening and spreading outward, and as it settled onto the earth it became a garden with paths radiating in every direction from the center where I stood. Each path led toward a different horizon, and I understood that the mandala was not a map of where I had been but of where I could go, the integration of my dream journey crystallized into a living symbol. Flowers grew along the paths in the exact colors of the mandala''s light, and the air hummed with a frequency I recognized as the same one the crystal cave had once echoed. I stood at the center of my own wholeness, not as a destination reached but as a perspective gained.',
'2026-02-05', 'An open field under a vast sky where a luminous mandala rotates overhead, its patterns composed of living light and miniature dream-scenes. As it descends, it transforms into a garden with radial paths.', 'The dream progressed from observation to participation to integration. Moving inward through the mandala''s rings was a journey through the entire dream sequence in compressed form, each layer reconciling what had seemed like opposing experiences.', 'Standing at the center of the mandala-garden, surrounded by radial paths leading in every direction. The geometric and the organic had merged into a single living symbol of wholeness.', 'awe', 5, 'FULL', 5, true, 'Drew the mandala in detail with colored pencils, spent an hour in contemplation', false, false, 'Jung considered the mandala the supreme symbol of the Self—the archetype of wholeness that emerges when the psyche begins to integrate its fragmented parts. That my unconscious produced this image spontaneously, containing every dream I have had, suggests the individuation process has reached a critical threshold. The mirror at the center showing light rather than my face speaks to what Jung called the transpersonal Self—not the ego but the totality of the psyche. I am deeply moved that my dreams have organized themselves into this pattern without my conscious direction.', false, true, 'Read about mandalas in Jung''s Red Book yesterday.', '2026-02-05 08:15:00+00'),

-- Dream 58: Tier A (8-12 sentences), ritual
(58, 1, 'Butterfly and Sun',
'A butterfly landed on my outstretched hand as the first light of sunrise crested the hill beneath me, its wings opening and closing with the slow rhythm of breathing, each movement revealing patterns of gold and crimson that shifted like stained glass in changing light. I recognized it immediately—the same butterfly that had struggled from its chrysalis in my December dream, the one that had whispered "thank you for not helping" as it found its wings. But it was larger now, more vivid, its patterns more complex, as though it had continued to grow and transform in the dreams between then and now. The sunrise behind it was the most beautiful I had ever witnessed, the sky layered in bands of amber, coral, rose, and deepening blue, the light arriving not all at once but in waves that washed over the landscape like warm water. Below the hilltop where I stood, the land stretched out in every direction—the forest, the meadow, the distant glint of the ocean—all illuminated by this same golden light, every surface catching fire with color. Other butterflies began to appear, drifting up from the valley in ones and twos, then dozens, then hundreds, their wings catching the sunrise until the air itself seemed to flutter and glow. They were all different species, impossible varieties, yet they moved together with the coherence of a single living thought. The butterfly on my hand pulsed once, and I felt its meaning not as words but as knowing: transformation never ends, but it becomes gentler, becomes joy rather than struggle, becomes the natural rhythm of a life that has learned to trust its own unfolding. I released it gently and watched it join the rising cloud of wings, a single point of gold and crimson merging into a living mosaic of flight. The sun cleared the horizon fully and the world was remade in light, and I understood in my body what my mind had been approaching for months—that I was not separate from this beauty, not an observer of transformation but transformation itself, continuous and unfinished and whole. Standing in the center of that sunrise, surrounded by wings, I felt the continuity of every dream I had ever had flowing through me like a river that had finally reached the sea.',
'2026-02-06', 'A grassy hilltop overlooking a vast landscape at sunrise, the sky ablaze with color. The air fills with hundreds of butterflies rising from the valley below.', 'The dream expanded from an intimate moment—a single butterfly on a hand—into a panoramic celebration of transformation. Each element amplified the last: the sunrise, the multiplying butterflies, the landscape revealed in full light.', 'Standing on the hilltop as the sun cleared the horizon, surrounded by hundreds of butterflies. The world remade in light, transformation recognized as continuous and whole.', 'joyful wholeness', 4, 'FULL', 5, true, 'Walked outside at sunrise, watched actual butterflies in the garden', false, false, 'The butterfly is one of the most universal symbols of psychic transformation, and its return here—grown larger and more vivid—mirrors my own inner development. In Jungian terms, the chrysalis represents the nigredo, the dark night of dissolution, and the butterfly is what emerges when the ego surrenders its rigid structures. That the butterfly told me transformation becomes gentler speaks to the maturation of the individuation process itself. I am no longer being broken open; I am unfolding.', false, true, 'Spring is approaching. Noticed butterflies in the garden for the first time this year.', '2026-02-06 07:30:00+00'),

-- Dream 59: Tier A (8-12 sentences), ritual
(59, 1, 'Morning Journal',
'I sat at a desk in a sunlit room that felt like every room I had ever loved compressed into one—the warmth of my childhood kitchen, the quiet of my adult study, the golden light of the dream-garden all present simultaneously. Before me lay my dream journal, its pages dense with months of handwritten entries, and I was writing in it with a pen that left ink the color of midnight blue. As I wrote, the words began to lift off the page, letter by letter, rising like delicate insects made of ink and light, hovering in the air around me. Each word became the thing it described: "ocean" became a tiny sphere of dark water rotating silently at eye level, "butterfly" became a palm-sized creature of golden script that fluttered past my ear. The room filled with miniature versions of every dream I had recorded—the small locked door, the spiral staircase no taller than a candlestick, the white wolf the size of a cat padding across the desktop, the shadow figure standing in the corner of the room but only two inches tall and waving at me. I laughed—a real, full laugh that I felt in my belly—at the absurdity and beauty of seeing my entire inner journey arrayed around me like the most precious and peculiar collection in the world. All the growth, all the terror, all the moments of grace—hovering in the golden air as miniatures, simultaneously monumental and small enough to hold. I could reach out and touch any scene, and when I did, I felt the emotion of that dream pass through my fingertips like a mild electric current—the fear of the ocean, the peace of the garden, the awe of the mandala. I closed the journal gently and the scenes began to settle back toward the pages, each miniature dissolving into golden words that arranged themselves into sentences more beautiful than what I had originally written. The journal glowed faintly in the morning light, and I understood with absolute clarity that the act of recording my dreams—the discipline of attention, the courage of looking directly at what the unconscious offers—had itself been the transformation. Not the dreams alone, not the analysis alone, but the faithful practice of witnessing and writing, night after night, had woven the raw material of the unconscious into something I could carry with me into waking life.',
'2026-02-07', 'A sunlit room combining elements of beloved spaces—warm wood, tall windows, morning light. A desk holds an open dream journal, and the air fills with miniature dream-scenes made of living words.', 'The dream built from the quiet act of writing into a magical realist spectacle of words becoming worlds. The tone shifted from contemplative to playful to reverent as the dreamer witnessed their entire journey in miniature.', 'Closing the journal as the miniature scenes settled back into golden words on the page. A profound understanding that the practice of recording and reflecting is itself the transformation.', 'clarity', 3, 'FULL', 5, true, 'Re-read my entire dream journal from October to today, noting the arc of transformation', false, false, 'This is the most meta dream I have had—a dream about the practice of dreaming itself. Jung emphasized that the ego''s conscious engagement with unconscious material is what makes individuation possible; the unconscious speaks, but someone must listen and record. This dream affirms that my five months of journaling were not merely documentation but active participation in my own psychological development. The words becoming three-dimensional scenes is the unconscious showing me that my attention has given its offerings substance and permanence.', false, true, 'Hackathon weekend coming up. Feeling creative and energized.', '2026-02-07 07:00:00+00'),

-- Dream 60: Tier A (8-12 sentences), ritual
(60, 1, 'The Integrated Self',
'I stood in a place that was simultaneously all of the dream locations I had ever visited—the forest clearing and the mountain summit and the ocean shore and the childhood home and the corridor with its open door, all occupying the same space without contradiction, layered like transparencies on a light table. The ground beneath my feet was soft earth and stone summit and sand and hardwood floor and damp flagstone, each surface real and present when I attended to it, the others waiting patiently beneath. Every dream character I had encountered was present: the shadow figure, the wise old woman, my inner child, the mysterious guide, my mother, my father, Sarah, the white wolf, the teacher—all standing at different points around me in a loose circle, and as I looked at each one, they became translucent, revealing something luminous at their core that was identical in each of them. They were all facets of me. I had always known this intellectually, but now I felt it in the architecture of the dream itself—each character a lens through which one aspect of my totality could be seen, loved, and integrated. The shadow man caught my eye and smiled, and I smiled back at him with genuine warmth—how far we had come from the terror of that first mirror. I breathed in, deeply, intentionally, and as I inhaled they began to drift toward me, not collapsing but merging, each one bringing their essential quality—courage, wisdom, innocence, guidance, nurture, strength, friendship, wildness, patience—into a wholeness that expanded my chest until I thought it might break open with the fullness of it. When the last figure merged, I stood alone in the composite landscape, but alone had changed its meaning entirely—not isolated but integrated, not singular but containing multitudes. I looked down at my hands and saw stars—not metaphorically but actually, tiny points of light embedded in my skin like freckles made of pure radiance, constellations mapped across my palms and wrists and forearms. The landscape around me pulsed once, gently, like the heartbeat of something immense and benevolent, and I understood that this was not an ending but a way of seeing that I could carry forward. I chose to wake—not startled awake, not fading, but deliberately choosing to return to waking life as an act of will and trust. I opened my eyes in my own bed, in my own room, in the gray light of a February morning, and for several minutes I could still see the stars in my hands.',
'2026-02-08', 'A composite space where all previous dream locations exist simultaneously—forest, mountain, ocean, childhood home, and stone corridor—layered transparently, each fully present. Dream characters stand in a loose circle.', 'The dream moved from panoramic recognition to intimate integration. Each character became translucent, revealed as a facet of the dreamer, and the merging was not dissolution but expansion—a gathering of every quality into felt wholeness.', 'Choosing deliberately to wake, carrying the integration forward. Opening my eyes in February morning light with the lingering sensation of stars in my hands.', 'wholeness', 5, 'FULL', 5, true, 'Full morning ritual: meditation, journaling, drawing, and gratitude for the journey', false, false, 'This is the culmination dream—what Jung called the coniunctio, the sacred marriage of all psychic opposites into a unified whole. Every character revealed as a facet of the Self is the central insight of analytical psychology made experiential: we project outward what we cannot yet own inward, and individuation is the gradual reclamation of those projections. The stars in my hands are the most powerful image my unconscious has ever produced—the macrocosm reflected in the microcosm, the universe not out there but in here, written on the body. Choosing to wake was the final act of integration: bringing the dream''s wholeness consciously into waking life.', false, true, 'Sense of completion and readiness for what comes next.', '2026-02-08 07:30:00+00');
-- ============================================
-- 9. DREAM SYMBOLS (Junction Table)
-- ============================================
INSERT INTO dream_symbols (dream_id, symbol_id, is_ai_extracted, is_confirmed, context_note, personal_meaning) VALUES
-- Dream 1: The Locked Door
(1, 4, true, true, 'Massive wooden door with a pulsing keyhole, standing alone in fog', 'I think this door represents the therapy I keep avoiding'),
(1, 7, true, true, 'Dark presence felt lurking just behind the dreamer', 'Something is always watching in my dreams — I think it''s the guilt I carry'),
-- Dream 2: Drowning in the Depths
(2, 1, true, true, 'Vast dark ocean pulling the dreamer under, no shore in sight', 'The ocean has always been both terrifying and calling to me'),
-- Dream 3: Shadow in the Mirror
(3, 9, true, true, 'Antique mirror reflecting a distorted version of the dreamer', 'Mirrors in my dreams always make me feel like I''m being judged by myself'),
(3, 7, true, true, 'Shadow figure standing behind the reflection, moving independently', 'This shadow is definitely the anger I buried after the breakup'),
(3, 15, true, true, 'Mirror hanging in the hallway of childhood home', 'That hallway mirror is exactly where it was in real life — I used to stare into it as a kid wondering who I''d become'),
-- Dream 4: Lost in Dark Woods
(4, 8, true, true, 'Dense forest with no visible path, trees closing in', 'The dark forest feels like the confusion I have about my career'),
(4, 7, true, true, 'Shadowy figure glimpsed between the trees, always at the edge of vision', NULL),
-- Dream 5: Flying Over the Unknown City
(5, 13, true, true, 'Soaring above rooftops with effortless control', 'Flying dreams are the only time I feel truly free from expectations'),
(5, 14, true, true, 'Flock of birds flying alongside the dreamer', NULL),
(5, 7, true, true, 'Shadow figure standing on a rooftop below, watching', 'I wonder if the shadow watching me fly is the part of me that doesn''t believe I deserve freedom'),
-- Dream 6: Endless Staircase
(6, 6, true, true, 'Spiral staircase that keeps extending upward with no landing', 'The staircase is my perfectionism — always climbing, never arriving'),
(6, 4, true, true, 'Door visible at each landing but always just out of reach', NULL),
-- Dream 7: Return to Childhood
(7, 15, true, true, 'Childhood home exactly as remembered but slightly wrong proportions', 'Going back to that house always stirs up complicated feelings about my parents'' divorce'),
(7, 4, true, true, 'Bedroom door that won''t open no matter how hard the dreamer tries', NULL),
(7, 21, true, true, 'Small golden key found in a coat pocket', 'The key feels like it''s about the conversation I need to have with my father'),
-- Dream 8: Bridge Over the Void
(8, 5, true, true, 'Narrow rope bridge swaying over a bottomless chasm', 'This bridge is about trusting people again after being let down so many times'),
-- Dream 9: Hidden Rooms
(9, 16, true, true, 'Series of rooms discovered behind wallpaper in a familiar house', 'The hidden rooms are talents and parts of myself I''ve been ignoring'),
(9, 9, true, true, 'Full-length mirror in the final hidden room', NULL),
-- Dream 10: Father''s Library
(10, 22, true, true, 'Shelves of leather-bound books with titles the dreamer can''t read', 'Books represent all the things my father never taught me'),
-- Dream 11: The Branching Path
(11, 18, true, true, 'Dirt path that splits into three directions in a meadow', NULL),
(11, 23, true, true, 'Large clock face embedded in a tree at the fork', 'The clock is my anxiety about turning 30 and feeling behind'),
-- Dream 12: The Knowing Cat
(12, 4, true, true, 'Cat sitting before a small door in a garden wall', NULL),
(12, 18, true, true, 'Winding cobblestone path the cat leads the dreamer along', 'Following the path the cat shows feels like learning to trust my intuition'),
-- Dream 13: Rain of Renewal
(13, 3, true, true, 'Warm golden rain falling on a barren landscape, bringing instant growth', 'The rain felt like the grief I finally let myself feel last month'),
-- Dream 14: The Drowning Garden
(14, 1, true, true, 'Saltwater flooding into a walled garden from nowhere', 'The ocean invading my safe space is how my anxiety works — it seeps in everywhere'),
(14, 12, true, true, 'Small fires burning on the water''s surface, refusing to go out', 'The fire on water reminds me of how my passion survived even the worst times'),
-- Dream 15: The Second Door
(15, 4, true, true, 'Second door appearing behind the first one after it opens', 'Another door — I''m starting to understand these are the emotional barriers I keep building'),
(15, 21, true, true, 'Key that changes shape in the dreamer''s hand', NULL),
(15, 6, true, true, 'Short staircase leading down to the second door', 'Going down stairs instead of up — this feels like descending into something I''ve been avoiding'),
-- Dream 16: Departure of Birds
(16, 14, true, true, 'Hundreds of birds lifting off from a single tree at once', 'The birds leaving feels like the friends who moved away this year'),
-- Dream 17: Lantern in the Dark
(17, 20, true, true, 'Warm lantern light cutting through thick darkness', 'This light is my therapist''s voice — steady and reliable'),
(17, 18, true, true, 'Narrow path revealed only by the lantern''s glow', NULL),
-- Dream 18: The Wise Woman''s Question
(18, 18, true, true, 'Stone path leading to a mountain shrine', 'The path to the wise woman is about the journey to self-knowledge, not the destination'),
(18, 21, true, true, 'Stone the wise woman hands over, shaped like an old key', NULL),
-- Dream 19: Tree of Photographs
(19, 24, true, true, 'Enormous tree with photographs hanging from every branch like leaves', 'This tree is my family — rooted but always changing'),
-- Dream 20: The White Wolf
(20, 8, true, true, 'Snow-covered forest at night, eerily quiet', 'The silent forest felt like depression — beautiful on the surface but isolating'),
(20, 12, true, true, 'Campfire that the white wolf circles protectively', 'The fire the wolf guards feels like the creative spark I almost gave up on'),
-- Dream 21: Cave of Echoes
(21, 25, true, true, 'Deep cave where every whisper returns as a different voice', 'The cave is my unconscious — I''m learning not to be afraid of going deeper'),
(21, 9, true, true, 'Underground pool that acts as a mirror, reflecting the cave ceiling as sky', NULL),
-- Dream 22: The Snake Sheds
(22, 10, true, true, 'Large snake slowly shedding its skin, revealing iridescent scales', 'The snake shedding is me letting go of the person I was in that toxic relationship'),
(22, 20, true, true, 'Soft golden light emanating from the new skin', NULL),
-- Dream 23: Light Through Cracks
(23, 20, true, true, 'Brilliant white light pouring through cracks in dark walls', 'The light breaking through is hope I didn''t think I still had'),
(23, 16, true, true, 'Dark sealed room with light forcing its way in through every crack', NULL),
-- Dream 24: Dancing with Shadow
(24, 7, true, true, 'Shadow figure that the dreamer takes by the hand and dances with', 'Dancing with my shadow felt like finally accepting the parts of myself I''ve been running from'),
(24, 9, true, true, 'Wall of mirrors surrounding the dance floor, all showing different angles', NULL),
-- Dream 25: Mountain Ascent
(25, 17, true, true, 'Steep rocky mountain with a visible peak catching sunlight', 'The mountain is my dissertation — massive but I can see the top now'),
(25, 4, true, true, 'Stone door set into the mountainside at the base', NULL),
(25, 18, true, true, 'Switchback path carved into the mountain face', 'The switchbacks are all the setbacks that were actually just part of the route'),
-- Dream 26: Library of Lives
(26, 22, true, true, 'Infinite library where each book contains a different possible life', 'These books are all the lives I could have lived if I''d made different choices'),
(26, 20, true, true, 'Reading lamp that illuminates whichever book the dreamer reaches for', NULL),
-- Dream 27: Healing Waters
(27, 1, true, true, 'Warm turquoise ocean water with visible healing properties', 'The healing ocean is the peace I''m finally starting to feel in therapy'),
(27, 25, true, true, 'Sea cave where the healing water pools into a still bath', NULL),
-- Dream 28: Teaching the Child
(28, 1, true, true, 'Gentle tide coming in while the dreamer teaches a child to swim', NULL),
(28, 15, true, true, 'Beach behind the childhood home that never existed in real life', 'The childhood home by the ocean is the safe space I''m building for my inner child'),
-- Dream 29: The Weaver''s Loom
(29, 24, true, true, 'Loom made from living tree branches, still sprouting leaves', 'The tree-loom is about how everything in my life is interconnected'),
(29, 20, true, true, 'Threads of light woven into the fabric on the loom', NULL),
-- Dream 30: Butterfly Emergence
(30, 11, true, true, 'Butterfly emerging from a cocoon attached to the dreamer''s chest', 'The butterfly is the person I''m becoming — I can feel the transformation happening'),
-- Dream 31: Facing the Former Love
(31, 18, true, true, 'Two parallel paths that converge briefly then separate again', 'The paths crossing is about accepting that some people are only in your life for a season'),
(31, 19, true, true, 'Setting sun casting long shadows as the paths diverge', NULL),
-- Dream 32: Sunrise on the Mountain
(32, 17, true, true, 'Mountain peak at dawn with panoramic view of the landscape below', NULL),
(32, 19, true, true, 'Brilliant sunrise painting the sky gold and rose', 'The sunrise feels like the new beginning I''ve been working toward all year'),
(32, 4, true, true, 'Door of light appearing at the summit', NULL),
(32, 1, true, true, 'Ocean visible far below, calm and shimmering', NULL),
(32, 5, true, true, 'Rainbow bridge arcing from the peak to another mountain', NULL),
(32, 7, true, true, 'Shadow figure standing beside the dreamer as an equal, not a threat', 'My shadow standing beside me at the summit — we''re finally on the same side'),
-- Dream 33: Solstice Fire
(33, 12, true, true, 'Massive bonfire at the center of a stone circle', 'The solstice fire is about burning away what no longer serves me'),
(33, 7, true, true, 'Shadow figures dancing around the fire in celebration', 'The shadows celebrating feels like my darker emotions finally being welcomed instead of exiled'),
(33, 20, true, true, 'Firelight illuminating ancient carvings on the standing stones', NULL),
-- Dream 34: River Journey
(34, 2, true, true, 'Wide slow river carrying the dreamer on a wooden raft', 'The river is about surrendering control and letting life carry me for once'),
-- Dream 35: Clock Without Hands
(35, 23, true, true, 'Giant clock tower with a blank face, no hands or numbers', 'The handless clock is freedom from the pressure I put on myself about timelines'),
-- Dream 36: Conversation with Mother
(36, 15, true, true, 'Kitchen of childhood home, warm and golden-lit', 'The childhood kitchen is where I felt safest — I miss that feeling'),
(36, 20, true, true, 'Warm light filling the kitchen, coming from no visible source', NULL),
-- Dream 37: The Healed Home
(37, 15, true, true, 'Childhood home fully repaired and renovated, bright and welcoming', 'The healed home is my inner world after a year of therapy'),
(37, 4, true, true, 'All doors in the house standing open for the first time', 'Every door being open means I''m not hiding from any part of myself anymore'),
(37, 16, true, true, 'Previously hidden room now bright and furnished, integrated into the house', NULL),
-- Dream 38: Fire of Transformation
(38, 12, true, true, 'Controlled fire burning through dead wood, leaving living trees unharmed', NULL),
(38, 24, true, true, 'Trees that survive the fire sprouting new growth immediately', 'The surviving trees are the relationships that made it through my worst period'),
-- Dream 39: Voices in the Rain
(39, 3, true, true, 'Gentle rain where each drop carries a whispered message', 'The rain voices are all the advice I''ve been given that I''m finally ready to hear'),
(39, 2, true, true, 'Rain collecting into a stream that becomes a calm river', NULL),
-- Dream 40: Shadow Integration
(40, 7, true, true, 'Shadow figure stepping forward and merging with the dreamer', 'Merging with my shadow is accepting my anger and jealousy as valid parts of me'),
(40, 9, true, true, 'Mirror showing a complete, whole person after the merging', 'Seeing myself whole in the mirror for the first time — that''s what integration looks like'),
-- Dream 41: Cave of Origins
(41, 25, true, true, 'Ancient cave with paintings on the walls depicting the dreamer''s life', NULL),
(41, 24, true, true, 'Tree roots breaking through the cave ceiling, connecting above and below', 'The roots in the cave connect my conscious life to my deeper self'),
-- Dream 42: Rain and Sun Together
(42, 3, true, true, 'Sunshower — rain and bright sunshine happening simultaneously', 'Rain and sun together is holding grief and joy at the same time'),
(42, 19, true, true, 'Sun breaking through rain clouds, creating a double rainbow', NULL),
(42, 5, true, true, 'Rainbow forming a solid bridge the dreamer can walk across', NULL),
-- Dream 43: Teaching What I Learned
(43, 22, true, true, 'Dreamer writing in a book that others gather around to read', 'The book I''m writing is about sharing what I''ve learned from my pain'),
(43, 20, true, true, 'Warm light emanating from the pages as the dreamer writes', NULL),
-- Dream 44: The Map Unfolds
(44, 17, true, true, 'Mountain ranges visible on a living, breathing map', NULL),
(44, 2, true, true, 'Rivers drawn in blue that actually flow across the map surface', 'The rivers on the map are the emotional currents that have shaped my journey'),
(44, 8, true, true, 'Dark forest region on the map that the dreamer has already crossed', 'Seeing the dark forest behind me on the map — I made it through'),
-- Dream 45: River to Ocean
(45, 2, true, true, 'River widening and slowing as it approaches the sea', NULL),
(45, 1, true, true, 'Vast peaceful ocean accepting the river without resistance', 'The river meeting the ocean is about my individual struggles dissolving into something bigger'),
-- Dream 46: Mirror of Acceptance
(46, 9, true, true, 'Mirror showing the dreamer exactly as they are, flaws and all, bathed in warm light', 'Looking in this mirror without flinching is the hardest and best thing I''ve done'),
(46, 20, true, true, 'Soft golden light radiating from the mirror itself', NULL),
-- Dream 47: Wolf Pack
(47, 8, true, true, 'Forest at twilight, familiar now rather than threatening', 'The forest isn''t scary anymore — it''s just another part of the landscape of who I am'),
-- Dream 48: Garden of Forgiveness
(48, 4, true, true, 'Garden gate standing open, inviting the dreamer in', NULL),
(48, 24, true, true, 'Fruit tree at the center of the garden in full bloom', 'The fruit tree is what grew from all the pain I composted this year'),
-- Dream 49: Flight Without Fear
(49, 13, true, true, 'Flying with total confidence and joy, no fear of falling', 'Flying without fear is the trust I''ve built in myself through this whole process'),
(49, 14, true, true, 'Birds flying in formation with the dreamer as part of the flock', NULL),
-- Dream 50: The Bridge Completed
(50, 5, true, true, 'Stone bridge fully built, connecting two lands the dreamer has visited before', 'The completed bridge is the connection between who I was and who I''m becoming'),
(50, 21, true, true, 'Keystone at the center of the bridge arch, holding everything together', 'The keystone is self-compassion — it''s the piece that holds everything else in place'),
-- Dream 51: Council of Selves
(51, 9, true, true, 'Circle of mirrors each reflecting the dreamer at a different age', 'Every mirror showing a different me — I''m all of these people at once'),
(51, 7, true, true, 'Shadow figure seated at the council as a respected member', NULL),
(51, 17, true, true, 'Council meeting on a mountain plateau above the clouds', NULL),
-- Dream 52: Future Self
(52, 18, true, true, 'Sunlit path leading toward a figure in the distance who is the dreamer''s future self', 'The path to my future self is clear for the first time'),
(52, 19, true, true, 'Warm sun illuminating the future self, who is smiling', NULL),
-- Dream 53: The Dreamer Awakens
(53, 4, true, true, 'Final door that opens onto a bright, limitless landscape', 'This last door opening feels like graduation from the hardest school I''ve ever attended'),
(53, 1, true, true, 'Ocean stretching to the horizon, no longer threatening', NULL),
(53, 8, true, true, 'Dark forest visible in the distance, small and manageable', NULL),
(53, 13, true, true, 'Dreamer lifting off the ground and flying over the open landscape', 'Flying at the end feels like everything has been building to this — real freedom'),
-- Dream 54: Dawn Chorus
(54, 14, true, true, 'Dozens of birds singing together as dawn breaks', 'The birds singing together are all the voices that supported me this year'),
(54, 19, true, true, 'Sun rising slowly, turning the sky from indigo to gold', NULL),
(54, 13, true, true, 'Dreamer rising with the birds into the brightening sky', NULL),
-- Dream 55: The Quiet Ocean
(55, 1, true, true, 'Perfectly still ocean under a clear sky, peaceful and welcoming', 'The quiet ocean is the calm I never thought I''d find inside myself'),
(55, 20, true, true, 'Sunlight sparkling across the surface of the still water', NULL),
-- Dream 56: Open Door
(56, 4, true, true, 'Simple door standing wide open in a field of wildflowers', 'An open door with no lock — I don''t need to fight my way through anymore'),
(56, 18, true, true, 'Clear path on both sides of the door, showing the way forward', NULL),
-- Dream 57: The Living Mandala
(57, 9, true, true, 'Circular mirror at the center of a mandala pattern on the ground', 'The mirror at the mandala''s center is about seeing myself as part of a larger pattern'),
(57, 19, true, true, 'Sun directly overhead, casting the mandala''s shadow perfectly centered', 'The sun at the center of the mandala is wholeness — everything in balance'),
(57, 11, true, true, 'Butterflies forming part of the mandala''s living pattern', NULL),
-- Dream 58: Butterfly and Sun
(58, 11, true, true, 'Single golden butterfly flying directly toward the sun', 'The butterfly heading for the sun is me choosing to live fully, even if it''s risky'),
(58, 19, true, true, 'Warm sun that welcomes the butterfly rather than burning it', NULL),
(58, 13, true, true, 'Dreamer flying alongside the butterfly, equally weightless', NULL),
-- Dream 59: Morning Journal
(59, 22, true, true, 'Journal open on a sunlit desk, words writing themselves', 'The self-writing book is my subconscious finally having a voice'),
(59, 4, true, true, 'Window beside the desk acting as a door to the outside world', NULL),
(59, 1, true, true, 'Ocean visible through the window, gentle waves catching morning light', NULL),
-- Dream 60: The Integrated Self
(60, 8, true, true, 'Dark forest now dappled with sunlight, paths clearly visible', NULL),
(60, 17, true, true, 'Mountain in the background, previously climbed and now familiar', 'The mountain behind me is every challenge I''ve overcome — it made me who I am'),
(60, 1, true, true, 'Ocean visible through the trees, calm and close', 'The ocean is no longer something to drown in — it''s where I go to feel connected'),
(60, 15, true, true, 'Childhood home visible at the forest edge, warm lights in the windows', 'The warm lights in my childhood home mean I''ve made peace with where I came from'),
(60, 4, true, true, 'All doors open throughout the landscape', 'Every door open everywhere — no more barriers between me and my own life'),
(60, 13, true, true, 'Dreamer able to fly at will, choosing to walk among it all instead', 'Choosing to walk instead of fly — I don''t need to escape anymore, I want to be here'),
(60, 11, true, true, 'Butterflies everywhere, symbols of completed transformation', NULL);
-- ============================================
-- 10. DREAM CHARACTERS (Junction Table)
-- ============================================
INSERT INTO dream_characters (dream_id, character_id, role_in_dream, archetype, traits, is_ai_extracted, is_confirmed, context_note, personal_significance) VALUES

-- Shadow Man (ID 1) - 7 appearances
(1, 1, 'OBSERVER', 'SHADOW', '["threatening","watching"]', true, true, 'Presence felt behind dreamer', 'This shadow stalker represents every part of myself I refuse to look at'),
(3, 1, 'ANTAGONIST', 'SHADOW', '["dark","independent","knowing"]', true, true, 'Reflection moving independently', 'The mirror version of me knows things I''m not ready to admit'),
(5, 1, 'ANTAGONIST', 'SHADOW', '["following","persistent"]', true, true, 'Following on ground', NULL),
(24, 1, 'HELPER', 'SHADOW', '["transforming","merging"]', true, true, 'Dancing partner, then merged', 'Dancing with my shadow felt like the first honest thing I''ve done in years'),
(33, 1, 'HELPER', 'SHADOW', '["giving","courageous"]', true, true, 'Offering the gift of courage', NULL),
(40, 1, 'TRANSFORMER', 'SHADOW', '["accepting","revealing"]', true, true, 'Final shadow integration', 'Feels like the parts of myself I buried after the breakup are finally welcome'),
(51, 1, 'HELPER', 'SHADOW', '["transparent","wise"]', true, true, 'Speaking his truth at council', NULL),

-- Wise Old Woman (ID 2) - 4 appearances
(18, 2, 'HELPER', 'WISE_OLD_WOMAN', '["blind","all-seeing","kind"]', true, true, 'Guide at crossroads', 'She represents the wisdom I don''t trust myself to have'),
(27, 2, 'HELPER', 'WISE_OLD_WOMAN', '["ancient","knowing"]', true, true, 'At underground lake', NULL),
(33, 2, 'HELPER', 'WISE_OLD_WOMAN', '["patient","generous"]', true, true, 'Offering the gift of patience', 'Her patience felt like permission to stop rushing through my own healing'),
(51, 2, 'HELPER', 'WISE_OLD_WOMAN', '["radiant","compassionate"]', true, true, 'Sharing wisdom at council', NULL),

-- Inner Child (ID 3) - 4 appearances
(7, 3, 'PROTAGONIST', 'CHILD', '["forgotten","lonely"]', true, true, 'Playing alone, gave key', 'This is the part of me that got locked away when I had to grow up too fast'),
(28, 3, 'HELPER', 'CHILD', '["playful","wise"]', true, true, 'Teaching dreamer to play', NULL),
(33, 3, 'HELPER', 'CHILD', '["bright","wonderous"]', true, true, 'Offering the gift of wonder', 'She reminds me that wonder isn''t weakness'),
(51, 3, 'HELPER', 'CHILD', '["innocent","joyful"]', true, true, 'Speaking at council', NULL),

-- Mysterious Guide (ID 4) - 4 appearances
(25, 4, 'HELPER', 'WISE_OLD_MAN', '["patient","storytelling"]', true, true, 'Mountain guide', 'He tells stories the way my grandfather used to, before he passed'),
(29, 4, 'HELPER', 'WISE_OLD_MAN', '["ancient","skilled"]', true, true, 'The weaver at the loom', NULL),
(44, 4, 'HELPER', 'WISE_OLD_MAN', '["cartographer","knowing"]', true, true, 'Presented the map', 'The map he gave me felt like someone finally handing me a plan for my life'),
(60, 4, 'TRANSFORMER', 'SELF', '["transparent","merging"]', true, true, 'Becoming part of the dreamer', 'When he merged with me it felt like I no longer needed anyone''s permission'),

-- Mother (ID 5) - 5 appearances
(4, 5, 'HELPER', 'MOTHER', '["distant","guiding"]', true, true, 'Appearing on path ahead', NULL),
(14, 5, 'OBSERVER', 'MOTHER', '["worried","reaching"]', true, true, 'Trying to help save flowers', 'Her worry mirrors every phone call where she asks if I''m eating enough'),
(36, 5, 'HELPER', 'MOTHER', '["authentic","vulnerable"]', true, true, 'True self conversation', 'We finally talked without the masks and I saw she was scared too'),
(37, 5, 'OBSERVER', 'MOTHER', '["peaceful","proud"]', true, true, 'Present in healed home', NULL),
(48, 5, 'TRANSFORMER', 'MOTHER', '["forgiving","releasing"]', true, true, 'One of the plants in the garden', NULL),

-- Father (ID 6) - 4 appearances
(8, 6, 'HELPER', 'FATHER', '["beckoning","waiting"]', true, true, 'On far side of bridge', 'He was waiting for me to be brave enough to cross, like he always does'),
(10, 6, 'OBSERVER', 'FATHER', '["absorbed","distant"]', true, true, 'Writing at desk, never looking up', NULL),
(50, 6, 'HELPER', 'FATHER', '["collaborative","present"]', true, true, 'Helping build bridge from other side', 'Building together felt like the relationship we never got to have'),
(51, 6, 'HELPER', 'FATHER', '["strong","supportive"]', true, true, 'Speaking at council', NULL),

-- Best Friend Sarah (ID 7) - 4 appearances
(6, 7, 'HELPER', NULL, '["calling","unreachable"]', true, true, 'Calling from above', 'This is definitely my fear of being truly seen by the people closest to me'),
(17, 7, 'HELPER', NULL, '["fellow-traveler","supportive"]', true, true, 'Another lantern carrier', NULL),
(42, 7, 'OBSERVER', NULL, '["joyful","celebrating"]', true, true, 'Celebrating the rainbow', NULL),
(49, 7, 'HELPER', NULL, '["flying","laughing"]', true, true, 'Flying alongside', 'Flying with Sarah felt like the friendship we had before everything got complicated'),

-- Ex-Partner (ID 8) - 3 appearances
(13, 8, 'OBSERVER', NULL, '["watching","separate"]', true, true, 'Under umbrella, no longer pulling', 'Seeing them separate from me without pain felt like real closure'),
(31, 8, 'HELPER', NULL, '["understanding","releasing"]', true, true, 'Peaceful conversation on bench', NULL),
(48, 8, 'OBSERVER', NULL, '["distant","fading"]', true, true, 'A plant being watered and released', 'They were fading and I didn''t try to hold on this time'),

-- Younger Self (ID 9) - 4 appearances
(7, 9, 'OBSERVER', 'CHILD', '["young","innocent"]', true, true, 'Younger self in room', NULL),
(28, 9, 'PROTAGONIST', 'CHILD', '["free","joyful"]', true, true, 'Building sandcastles', 'I miss the version of me that could build something just for the joy of it'),
(46, 9, 'TRANSFORMER', 'SELF', '["integrated","timeless"]', true, true, 'All ages in mirror', 'Seeing every age of myself at once made me feel whole for the first time'),
(53, 9, 'OBSERVER', 'SELF', '["watching","smiling"]', true, true, 'Seen briefly in revisited locations', NULL),

-- Future Self (ID 10) - 3 appearances
(52, 10, 'HELPER', 'SELF', '["wise","amused","peaceful"]', true, true, 'Guidance about journey', 'She looked at me the way I hope to look at myself someday'),
(57, 10, 'OBSERVER', 'SELF', '["serene","knowing"]', true, true, 'Visible in mandala center', NULL),
(60, 10, 'TRANSFORMER', 'SELF', '["merging","luminous"]', true, true, 'Becoming one with dreamer', 'Merging with my future self felt like finally trusting that I''ll be okay'),

-- White Wolf (ID 11) - 4 appearances
(20, 11, 'HELPER', 'SELF', '["guiding","protective"]', true, true, 'Guiding through forest', 'The wolf is the instinct I keep ignoring when I overthink everything'),
(47, 11, 'HELPER', 'SELF', '["welcoming","equal"]', true, true, 'Pack acceptance', NULL),
(51, 11, 'HELPER', 'SELF', '["instinctual","fierce"]', true, true, 'Representing instinct at council', NULL),
(60, 11, 'TRANSFORMER', 'SELF', '["wild","free"]', true, true, 'Merging with dreamer', 'The wildness I always kept caged finally came home'),

-- Black Cat (ID 12) - 3 appearances
(12, 12, 'HELPER', 'TRICKSTER', '["knowing","speaking"]', true, true, 'Black cat showing true path', 'The cat knows the shortcuts I''m too proud to take'),
(22, 12, 'OBSERVER', 'TRICKSTER', '["watching","amused"]', true, true, 'Sitting nearby watching transformation', NULL),
(29, 12, 'OBSERVER', 'TRICKSTER', '["playful","mysterious"]', true, true, 'Playing with loose threads', NULL),

-- Faceless Crowd (ID 13) - 3 appearances
(5, 13, 'OBSERVER', 'PERSONA', '["below","watching"]', true, true, 'People in the city streets', NULL),
(6, 13, 'OBSERVER', 'PERSONA', '["faceless","ignoring"]', true, true, 'People going down stairs', 'The faceless people are everyone I perform for instead of being real with'),
(60, 13, 'OBSERVER', NULL, '["transparent","dissolving"]', true, true, 'Background figures becoming light', 'Watching them dissolve felt like releasing my need for approval'),

-- Teacher Figure (ID 14) - 3 appearances
(26, 14, 'HELPER', 'WISE_OLD_WOMAN', '["explaining","patient"]', true, true, 'Library guide', NULL),
(43, 14, 'HELPER', 'WISE_OLD_MAN', '["teaching","approving"]', true, true, 'Asked dreamer to teach', 'Being asked to teach felt like someone finally saw that I have something to offer'),
(59, 14, 'OBSERVER', 'WISE_OLD_MAN', '["approving","silent"]', true, true, 'Nodding approvingly from corner', NULL);
-- ============================================
-- 11. DREAM EMOTIONS
-- ============================================
INSERT INTO dream_emotions (dream_id, emotion, emotion_type, intensity) VALUES

-- === OCTOBER (Dreams 1-12): Dark, anxious ===

-- Dream 1: Locked Door
(1, 'anxiety', 'DURING', 7),
(1, 'fear', 'DURING', 6),
(1, 'confusion', 'WAKING', 6),
(1, 'frustration', 'WAKING', 5),

-- Dream 2: Drowning
(2, 'terror', 'DURING', 9),
(2, 'fear', 'DURING', 8),
(2, 'helplessness', 'DURING', 7),
(2, 'anxiety', 'WAKING', 7),

-- Dream 3: Mirror Shadow
(3, 'fear', 'DURING', 7),
(3, 'shame', 'DURING', 6),
(3, 'confusion', 'DURING', 5),
(3, 'shame', 'WAKING', 7),

-- Dream 4: Dark Woods
(4, 'fear', 'DURING', 6),
(4, 'longing', 'DURING', 5),
(4, 'sadness', 'WAKING', 6),
(4, 'confusion', 'WAKING', 4),

-- Dream 5: Flying City
(5, 'joy', 'DURING', 7),
(5, 'anxiety', 'DURING', 5),
(5, 'excitement', 'DURING', 6),
(5, 'frustration', 'WAKING', 4),

-- Dream 6: Staircase
(6, 'anxiety', 'DURING', 7),
(6, 'helplessness', 'DURING', 6),
(6, 'frustration', 'DURING', 5),
(6, 'sadness', 'WAKING', 5),

-- Dream 7: Childhood
(7, 'guilt', 'DURING', 8),
(7, 'sadness', 'DURING', 7),
(7, 'grief', 'WAKING', 7),
(7, 'longing', 'WAKING', 6),

-- Dream 8: Bridge Void
(8, 'fear', 'DURING', 7),
(8, 'helplessness', 'DURING', 6),
(8, 'anxiety', 'WAKING', 6),
(8, 'frustration', 'WAKING', 5),

-- Dream 9: Hidden Rooms
(9, 'curiosity', 'DURING', 6),
(9, 'confusion', 'DURING', 4),
(9, 'wonder', 'DURING', 5),
(9, 'curiosity', 'WAKING', 5),

-- Dream 10: Library
(10, 'longing', 'DURING', 6),
(10, 'sadness', 'DURING', 5),
(10, 'nostalgia', 'DURING', 5),
(10, 'melancholy', 'WAKING', 5),

-- Dream 11: Branching Path
(11, 'anxiety', 'DURING', 6),
(11, 'helplessness', 'DURING', 5),
(11, 'confusion', 'DURING', 4),
(11, 'frustration', 'WAKING', 5),

-- Dream 12: Knowing Cat
(12, 'curiosity', 'DURING', 5),
(12, 'surprise', 'DURING', 4),
(12, 'wonder', 'WAKING', 4),
(12, 'hope', 'WAKING', 3),

-- === NOVEMBER (Dreams 13-24): Mixed, shifting positive ===

-- Dream 13: Rain Renewal
(13, 'peace', 'DURING', 7),
(13, 'relief', 'DURING', 6),
(13, 'relief', 'WAKING', 8),
(13, 'hope', 'WAKING', 5),

-- Dream 14: Drowning Garden
(14, 'fear', 'DURING', 6),
(14, 'helplessness', 'DURING', 5),
(14, 'sadness', 'DURING', 6),
(14, 'anxiety', 'WAKING', 5),

-- Dream 15: Second Door
(15, 'hope', 'DURING', 6),
(15, 'curiosity', 'DURING', 5),
(15, 'wonder', 'DURING', 4),
(15, 'excitement', 'WAKING', 5),

-- Dream 16: Birds Depart
(16, 'peace', 'DURING', 7),
(16, 'relief', 'DURING', 5),
(16, 'relief', 'WAKING', 8),
(16, 'freedom', 'WAKING', 6),

-- Dream 17: Lantern Dark
(17, 'curiosity', 'DURING', 5),
(17, 'hope', 'DURING', 5),
(17, 'trust', 'DURING', 4),
(17, 'safety', 'WAKING', 5),
(17, 'peace', 'WAKING', 4),

-- Dream 18: Wise Woman
(18, 'curiosity', 'DURING', 5),
(18, 'awe', 'DURING', 5),
(18, 'peace', 'WAKING', 6),
(18, 'understanding', 'WAKING', 5),

-- Dream 19: Tree Photos
(19, 'nostalgia', 'DURING', 6),
(19, 'wonder', 'DURING', 5),
(19, 'tenderness', 'DURING', 4),
(19, 'wonder', 'WAKING', 5),
(19, 'gratitude', 'WAKING', 4),

-- Dream 20: White Wolf
(20, 'peace', 'DURING', 7),
(20, 'safety', 'DURING', 6),
(20, 'safety', 'WAKING', 8),
(20, 'trust', 'WAKING', 6),

-- Dream 21: Cave Echoes
(21, 'awe', 'DURING', 6),
(21, 'fear', 'DURING', 4),
(21, 'peace', 'WAKING', 5),
(21, 'understanding', 'WAKING', 5),

-- Dream 22: Snake Sheds
(22, 'wonder', 'DURING', 6),
(22, 'awe', 'DURING', 5),
(22, 'curiosity', 'DURING', 5),
(22, 'awe', 'WAKING', 7),
(22, 'renewal', 'WAKING', 5),

-- Dream 23: Light Cracks
(23, 'hope', 'DURING', 6),
(23, 'excitement', 'DURING', 5),
(23, 'wonder', 'DURING', 5),
(23, 'joy', 'WAKING', 7),
(23, 'freedom', 'WAKING', 5),

-- Dream 24: Dancing Shadow
(24, 'acceptance', 'DURING', 7),
(24, 'peace', 'DURING', 5),
(24, 'surprise', 'DURING', 4),
(24, 'peace', 'WAKING', 8),
(24, 'wholeness', 'WAKING', 6),

-- === DECEMBER (Dreams 25-35): Mostly positive ===

-- Dream 25: Mountain
(25, 'curiosity', 'DURING', 5),
(25, 'peace', 'DURING', 4),
(25, 'wonder', 'DURING', 4),
(25, 'peace', 'WAKING', 6),
(25, 'trust', 'WAKING', 5),

-- Dream 26: Library Lives
(26, 'wonder', 'DURING', 5),
(26, 'acceptance', 'DURING', 4),
(26, 'acceptance', 'WAKING', 6),
(26, 'clarity', 'WAKING', 5),

-- Dream 27: Healing Waters
(27, 'peace', 'DURING', 8),
(27, 'relief', 'DURING', 6),
(27, 'acceptance', 'DURING', 5),
(27, 'peace', 'WAKING', 9),
(27, 'renewal', 'WAKING', 7),

-- Dream 28: Teaching Child
(28, 'joy', 'DURING', 7),
(28, 'nostalgia', 'DURING', 5),
(28, 'tenderness', 'DURING', 6),
(28, 'peace', 'WAKING', 6),
(28, 'acceptance', 'WAKING', 5),

-- Dream 29: Weaver's Loom
(29, 'awe', 'DURING', 6),
(29, 'wonder', 'DURING', 5),
(29, 'acceptance', 'DURING', 5),
(29, 'understanding', 'WAKING', 6),
(29, 'peace', 'WAKING', 5),

-- Dream 30: Butterfly
(30, 'wonder', 'DURING', 6),
(30, 'peace', 'DURING', 5),
(30, 'awe', 'WAKING', 7),
(30, 'hope', 'WAKING', 6),

-- Dream 31: Former Love
(31, 'peace', 'DURING', 6),
(31, 'acceptance', 'DURING', 5),
(31, 'tenderness', 'DURING', 4),
(31, 'acceptance', 'WAKING', 7),
(31, 'freedom', 'WAKING', 6),

-- Dream 32: Sunrise Mountain
(32, 'peace', 'DURING', 8),
(32, 'joy', 'DURING', 6),
(32, 'awe', 'DURING', 7),
(32, 'joy', 'WAKING', 7),
(32, 'wholeness', 'WAKING', 6),

-- Dream 33: Solstice Fire
(33, 'power', 'DURING', 6),
(33, 'gratitude', 'DURING', 7),
(33, 'love', 'DURING', 5),
(33, 'renewal', 'WAKING', 7),
(33, 'wholeness', 'WAKING', 6),

-- Dream 34: River Journey
(34, 'peace', 'DURING', 6),
(34, 'trust', 'DURING', 5),
(34, 'curiosity', 'DURING', 4),
(34, 'trust', 'WAKING', 7),
(34, 'freedom', 'WAKING', 5),

-- Dream 35: Clock Hands
(35, 'wonder', 'DURING', 5),
(35, 'understanding', 'DURING', 5),
(35, 'understanding', 'WAKING', 7),
(35, 'peace', 'WAKING', 6),

-- === JANUARY (Dreams 36-53): Positive, integrated ===

-- Dream 36: Mother Conv
(36, 'love', 'DURING', 7),
(36, 'tenderness', 'DURING', 6),
(36, 'peace', 'WAKING', 8),
(36, 'gratitude', 'WAKING', 6),

-- Dream 37: Healed Home
(37, 'peace', 'DURING', 7),
(37, 'joy', 'DURING', 5),
(37, 'freedom', 'DURING', 5),
(37, 'freedom', 'WAKING', 8),
(37, 'gratitude', 'WAKING', 6),

-- Dream 38: Fire Transform
(38, 'power', 'DURING', 7),
(38, 'excitement', 'DURING', 5),
(38, 'renewal', 'DURING', 6),
(38, 'renewal', 'WAKING', 8),
(38, 'clarity', 'WAKING', 6),

-- Dream 39: Voices Rain
(39, 'nostalgia', 'DURING', 5),
(39, 'peace', 'DURING', 5),
(39, 'tenderness', 'DURING', 4),
(39, 'peace', 'WAKING', 6),
(39, 'hope', 'WAKING', 5),

-- Dream 40: Shadow Integ
(40, 'acceptance', 'DURING', 8),
(40, 'peace', 'DURING', 6),
(40, 'wholeness', 'WAKING', 9),
(40, 'peace', 'WAKING', 7),

-- Dream 41: Cave Origins
(41, 'awe', 'DURING', 6),
(41, 'wonder', 'DURING', 5),
(41, 'acceptance', 'DURING', 5),
(41, 'peace', 'WAKING', 7),
(41, 'understanding', 'WAKING', 6),

-- Dream 42: Rain Sun
(42, 'wonder', 'DURING', 7),
(42, 'joy', 'DURING', 6),
(42, 'awe', 'DURING', 5),
(42, 'understanding', 'WAKING', 8),
(42, 'wholeness', 'WAKING', 6),

-- Dream 43: Teaching
(43, 'peace', 'DURING', 6),
(43, 'hope', 'DURING', 5),
(43, 'joy', 'DURING', 5),
(43, 'hope', 'WAKING', 7),
(43, 'clarity', 'WAKING', 6),

-- Dream 44: Map Unfolds
(44, 'curiosity', 'DURING', 6),
(44, 'wonder', 'DURING', 6),
(44, 'excitement', 'DURING', 5),
(44, 'clarity', 'WAKING', 7),
(44, 'hope', 'WAKING', 6),

-- Dream 45: River Ocean
(45, 'peace', 'DURING', 7),
(45, 'freedom', 'DURING', 6),
(45, 'awe', 'DURING', 5),
(45, 'freedom', 'WAKING', 8),
(45, 'acceptance', 'WAKING', 6),

-- Dream 46: Mirror Accept
(46, 'acceptance', 'DURING', 8),
(46, 'love', 'DURING', 5),
(46, 'peace', 'DURING', 6),
(46, 'wholeness', 'WAKING', 9),
(46, 'joy', 'WAKING', 6),

-- Dream 47: Wolf Pack
(47, 'joy', 'DURING', 8),
(47, 'freedom', 'DURING', 7),
(47, 'belonging', 'DURING', 6),
(47, 'belonging', 'WAKING', 9),
(47, 'peace', 'WAKING', 7),

-- Dream 48: Garden Forgive
(48, 'peace', 'DURING', 6),
(48, 'relief', 'DURING', 7),
(48, 'love', 'DURING', 5),
(48, 'freedom', 'WAKING', 8),
(48, 'renewal', 'WAKING', 7),

-- Dream 49: Flight Free
(49, 'joy', 'DURING', 9),
(49, 'freedom', 'DURING', 8),
(49, 'excitement', 'DURING', 6),
(49, 'freedom', 'WAKING', 9),
(49, 'joy', 'WAKING', 7),

-- Dream 50: Bridge Complete
(50, 'love', 'DURING', 6),
(50, 'gratitude', 'DURING', 7),
(50, 'peace', 'DURING', 5),
(50, 'wholeness', 'WAKING', 7),
(50, 'trust', 'WAKING', 8),

-- Dream 51: Council Selves
(51, 'awe', 'DURING', 7),
(51, 'understanding', 'DURING', 6),
(51, 'peace', 'DURING', 6),
(51, 'wholeness', 'WAKING', 8),
(51, 'acceptance', 'WAKING', 7),

-- Dream 52: Future Self
(52, 'peace', 'DURING', 8),
(52, 'trust', 'DURING', 7),
(52, 'joy', 'DURING', 4),
(52, 'trust', 'WAKING', 9),
(52, 'peace', 'WAKING', 7),

-- Dream 53: Dreamer Awakens
(53, 'awe', 'DURING', 8),
(53, 'wonder', 'DURING', 7),
(53, 'clarity', 'DURING', 6),
(53, 'wholeness', 'WAKING', 9),
(53, 'gratitude', 'WAKING', 8),

-- === FEBRUARY (Dreams 54-60): Peak integration ===

-- Dream 54: Dawn Chorus
(54, 'joy', 'DURING', 7),
(54, 'peace', 'DURING', 8),
(54, 'gratitude', 'DURING', 6),
(54, 'wonder', 'DURING', 5),
(54, 'peace', 'WAKING', 8),
(54, 'wholeness', 'WAKING', 7),

-- Dream 55: Quiet Ocean
(55, 'peace', 'DURING', 9),
(55, 'acceptance', 'DURING', 7),
(55, 'wonder', 'DURING', 6),
(55, 'peace', 'WAKING', 9),
(55, 'love', 'WAKING', 7),

-- Dream 56: Open Door
(56, 'peace', 'DURING', 8),
(56, 'acceptance', 'DURING', 7),
(56, 'joy', 'DURING', 6),
(56, 'peace', 'WAKING', 9),
(56, 'freedom', 'WAKING', 8),

-- Dream 57: Living Mandala
(57, 'awe', 'DURING', 8),
(57, 'wonder', 'DURING', 7),
(57, 'understanding', 'DURING', 6),
(57, 'wholeness', 'WAKING', 9),
(57, 'clarity', 'WAKING', 8),

-- Dream 58: Butterfly Sun
(58, 'joy', 'DURING', 8),
(58, 'wonder', 'DURING', 7),
(58, 'gratitude', 'DURING', 6),
(58, 'freedom', 'DURING', 5),
(58, 'wonder', 'WAKING', 9),
(58, 'renewal', 'WAKING', 7),

-- Dream 59: Morning Journal
(59, 'gratitude', 'DURING', 7),
(59, 'peace', 'DURING', 7),
(59, 'clarity', 'DURING', 6),
(59, 'peace', 'WAKING', 8),
(59, 'understanding', 'WAKING', 7),

-- Dream 60: Integrated Self
(60, 'wholeness', 'DURING', 9),
(60, 'love', 'DURING', 8),
(60, 'peace', 'DURING', 7),
(60, 'awe', 'DURING', 7),
(60, 'wholeness', 'WAKING', 9),
(60, 'peace', 'WAKING', 9);
-- ============================================
-- 12. DREAM THEMES
-- ============================================
INSERT INTO dream_themes (dream_id, theme, is_ai_extracted, is_confirmed) VALUES

-- October themes (dreams 1-12)
(1, 'threshold', true, true), (1, 'unknown', true, true),
(2, 'unconscious', true, true), (2, 'overwhelm', true, true), (2, 'survival', true, true),
(3, 'shadow', true, true), (3, 'identity', true, true), (3, 'reflection', true, true),
(4, 'lost', true, true), (4, 'mother', true, true), (4, 'darkness', true, true),
(5, 'freedom', true, true), (5, 'pursuit', true, true), (5, 'duality', true, true),
(6, 'striving', true, true), (6, 'separation', true, true), (6, 'endurance', true, true),
(7, 'childhood', true, true), (7, 'forgotten', true, true), (7, 'guilt', true, true),
(8, 'choice', true, true), (8, 'father', true, true), (8, 'courage', true, true),
(9, 'discovery', true, true), (9, 'hidden self', true, true), (9, 'mystery', true, true),
(10, 'memory', true, true), (10, 'unlived lives', true, true), (10, 'father', true, true),
(11, 'choice', true, true), (11, 'paralysis', true, true), (11, 'time', true, true),
(12, 'guidance', true, true), (12, 'repetition', true, true), (12, 'awareness', true, true),

-- November themes (dreams 13-24)
(13, 'cleansing', true, true), (13, 'release', true, true), (13, 'renewal', true, true),
(14, 'regression', true, true), (14, 'overwhelm', true, true), (14, 'vulnerability', true, true),
(15, 'opportunity', true, true), (15, 'threshold', true, true), (15, 'return', true, true),
(16, 'release', true, true), (16, 'lightness', true, true), (16, 'freedom', true, true),
(17, 'inner light', true, true), (17, 'trust', true, true), (17, 'guidance', true, true),
(18, 'guidance', true, true), (18, 'fear', true, true), (18, 'wisdom', true, true),
(19, 'memory', true, true), (19, 'origin', true, true), (19, 'identity', true, true),
(20, 'guidance', true, true), (20, 'safety', true, true), (20, 'instinct', true, true),
(21, 'reflection', true, true), (21, 'unconscious', true, true), (21, 'acceptance', true, true),
(22, 'transformation', true, true), (22, 'rebirth', true, true), (22, 'surrender', true, true),
(23, 'expansion', true, true), (23, 'light', true, true), (23, 'liberation', true, true),
(24, 'integration', true, true), (24, 'shadow', true, true), (24, 'partnership', true, true),

-- December themes (dreams 25-35)
(25, 'journey', true, true), (25, 'guidance', true, true), (25, 'aspiration', true, true),
(26, 'choice', true, true), (26, 'possibility', true, true), (26, 'wisdom', true, true),
(27, 'healing', true, true), (27, 'purification', true, true), (27, 'surrender', true, true),
(28, 'play', true, true), (28, 'inner child', true, true), (28, 'teaching', true, true),
(29, 'weaving', true, true), (29, 'acceptance', true, true), (29, 'wholeness', true, true),
(30, 'transformation', true, true), (30, 'patience', true, true), (30, 'emergence', true, true),
(31, 'release', true, true), (31, 'closure', true, true), (31, 'forgiveness', true, true),
(32, 'integration', true, true), (32, 'wholeness', true, true), (32, 'dawn', true, true),
(33, 'ritual', true, true), (33, 'community', true, true), (33, 'gifts', true, true),
(34, 'flow', true, true), (34, 'trust', true, true), (34, 'surrender', true, true),
(35, 'time', true, true), (35, 'presence', true, true), (35, 'eternity', true, true),

-- January themes (dreams 36-53)
(36, 'understanding', true, true), (36, 'mother', true, true), (36, 'forgiveness', true, true),
(37, 'home', true, true), (37, 'healing', true, true), (37, 'restoration', true, true),
(38, 'transformation', true, true), (38, 'rebirth', true, true), (38, 'purification', true, true),
(39, 'memory', true, true), (39, 'nourishment', true, true), (39, 'growth', true, true),
(40, 'integration', true, true), (40, 'shadow', true, true), (40, 'wholeness', true, true),
(41, 'wholeness', true, true), (41, 'self', true, true), (41, 'tapestry', true, true),
(42, 'unity', true, true), (42, 'perspective', true, true), (42, 'connection', true, true),
(43, 'teaching', true, true), (43, 'knowledge', true, true), (43, 'service', true, true),
(44, 'exploration', true, true), (44, 'mapping', true, true), (44, 'self-knowledge', true, true),
(45, 'depth', true, true), (45, 'acceptance', true, true), (45, 'courage', true, true),
(46, 'integration', true, true), (46, 'self', true, true), (46, 'reflection', true, true),
(47, 'belonging', true, true), (47, 'instinct', true, true), (47, 'freedom', true, true),
(48, 'forgiveness', true, true), (48, 'release', true, true), (48, 'growth', true, true),
(49, 'freedom', true, true), (49, 'joy', true, true), (49, 'community', true, true),
(50, 'completion', true, true), (50, 'father', true, true), (50, 'bridge', true, true),
(51, 'archetypes', true, true), (51, 'council', true, true), (51, 'mandala', true, true),
(52, 'future', true, true), (52, 'trust', true, true), (52, 'journey', true, true),
(53, 'awakening', true, true), (53, 'metacognition', true, true), (53, 'integration', true, true),

-- February themes (dreams 54-60)
(54, 'dawn', true, true), (54, 'celebration', true, true), (54, 'continuity', true, true),
(55, 'ocean', true, true), (55, 'reversal', true, true), (55, 'homecoming', true, true),
(56, 'completion', true, true), (56, 'simplicity', true, true), (56, 'threshold', true, true),
(57, 'mandala', true, true), (57, 'integration', true, true), (57, 'wholeness', true, true),
(58, 'transformation', true, true), (58, 'continuity', true, true), (58, 'renewal', true, true),
(59, 'reflection', true, true), (59, 'practice', true, true), (59, 'gratitude', true, true),
(60, 'integration', true, true), (60, 'wholeness', true, true), (60, 'transcendence', true, true);
-- ============================================
-- 13. SYMBOL ASSOCIATIONS
-- ============================================
-- ~30 rows: 22 AI_SUGGESTED + 8 USER

INSERT INTO symbol_associations (symbol_id, association_text, source, is_confirmed) VALUES
-- AI_SUGGESTED (original 16)
(4, 'Represents thresholds between conscious and unconscious', 'AI_SUGGESTED', true),
(4, 'Symbol of opportunity and choice', 'AI_SUGGESTED', true),
(7, 'Rejected aspects of personality seeking integration', 'AI_SUGGESTED', true),
(7, 'Contains undeveloped potential and unlived life', 'AI_SUGGESTED', true),
(1, 'The collective unconscious and source of all life', 'AI_SUGGESTED', true),
(1, 'Overwhelming emotions and the unknown depths of psyche', 'AI_SUGGESTED', true),
(9, 'Self-reflection and confronting the true self', 'AI_SUGGESTED', true),
(10, 'Transformation, healing, and kundalini energy', 'AI_SUGGESTED', true),
(11, 'Complete transformation and soul emergence', 'AI_SUGGESTED', true),
(13, 'Transcendence, expanded perspective, and freedom from constraints', 'AI_SUGGESTED', true),
(15, 'Origin and foundation of psyche, formative experiences', 'AI_SUGGESTED', true),
(17, 'Spiritual aspiration, overview, and achievement', 'AI_SUGGESTED', true),
(19, 'Consciousness, enlightenment, and life force', 'AI_SUGGESTED', true),
(21, 'Access, solution, and unlocking hidden potential', 'AI_SUGGESTED', true),
(24, 'Life force, growth, and connection between earth and sky', 'AI_SUGGESTED', true),
(25, 'Return to unconscious, womb symbolism, inner transformation', 'AI_SUGGESTED', true),
-- AI_SUGGESTED (6 new)
(2, 'The flow of psychic energy and the passage of life experience', 'AI_SUGGESTED', true),
(3, 'Emotional cleansing from above; grace descending into consciousness', 'AI_SUGGESTED', true),
(5, 'Spanning the gap between conscious and unconscious, connecting opposites', 'AI_SUGGESTED', true),
(12, 'Alchemical transformation through passionate destruction and renewal', 'AI_SUGGESTED', true),
(14, 'Soul messengers carrying intuitions between realms of consciousness', 'AI_SUGGESTED', true),
(20, 'The dawn of consciousness; insight breaking through unconscious darkness', 'AI_SUGGESTED', true),
-- USER (8 entries)
(4, 'In my life the door always means a decision I''m putting off—therapy, the difficult conversation, the career change', 'USER', true),
(7, 'My therapist helped me see this is my anger—the parts I was taught to hide as a child', 'USER', true),
(1, 'The ocean is my relationship with my emotions. When I was drowning, I was avoiding feeling. Now I can swim.', 'USER', true),
(9, 'Every time the mirror appears, I''m being asked to look at something I don''t want to see about myself', 'USER', true),
(15, 'My childhood home represents unfinished business with my family—the healing I still need to do', 'USER', true),
(13, 'Flying is my freedom dream. It only comes when I''m ready to let go of control in waking life.', 'USER', true),
(12, 'The fire is always about burning away what doesn''t serve me anymore. It used to scare me, now it feels necessary.', 'USER', true),
(10, 'The snake is change itself. I used to be terrified of change, and the snake reflected that. Now I welcome the shedding.', 'USER', true);

-- ============================================
-- 14. CHARACTER ASSOCIATIONS
-- ============================================
-- ~18 rows: 13 AI_SUGGESTED + 5 USER

INSERT INTO character_associations (character_id, association_text, source, is_confirmed) VALUES
-- AI_SUGGESTED (original 7)
(1, 'Represents rejected aspects of personality', 'AI_SUGGESTED', true),
(1, 'Contains unlived life and undeveloped potential', 'AI_SUGGESTED', true),
(2, 'Represents wisdom and guidance from the collective unconscious', 'AI_SUGGESTED', true),
(3, 'The vulnerable, authentic self before socialization', 'AI_SUGGESTED', true),
(5, 'The nurturing principle, origin, and emotional foundation', 'AI_SUGGESTED', true),
(6, 'Authority, structure, and the paternal principle of order', 'AI_SUGGESTED', true),
(11, 'Instinctual wisdom and guidance from the animal unconscious', 'AI_SUGGESTED', true),
-- AI_SUGGESTED (6 new)
(4, 'The psychopomp figure who guides between conscious and unconscious realms', 'AI_SUGGESTED', true),
(9, 'Earlier version of self holding pre-trauma innocence and authenticity', 'AI_SUGGESTED', true),
(10, 'The Self archetype projected into temporal form, representing potential wholeness', 'AI_SUGGESTED', true),
(12, 'Trickster energy that disrupts habitual patterns to reveal hidden truths', 'AI_SUGGESTED', true),
(13, 'The collective persona; social masks and the pressure of conformity', 'AI_SUGGESTED', true),
(14, 'The senex or wise teacher archetype offering structured knowledge', 'AI_SUGGESTED', true),
-- USER (5 entries)
(1, 'I''ve come to understand Shadow Man as everything I was taught was unacceptable—my anger, my ambition, my sexuality', 'USER', true),
(3, 'The Inner Child is the me who got lost when I started performing for others. I''m learning to listen to them again.', 'USER', true),
(5, 'My dream mother is not my actual mom—she''s the nurturing I needed but didn''t always get. Seeing her evolve in dreams has helped me forgive.', 'USER', true),
(8, 'My ex in dreams represents the relationship pattern, not the person. I keep replaying the dynamic until I understand it.', 'USER', true),
(11, 'The wolf is my gut instinct. I spent years ignoring it. These dreams taught me to trust my body again.', 'USER', true);

-- ============================================
-- 15. RESET SEQUENCES
-- ============================================
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1));
SELECT setval('dreams_id_seq', COALESCE((SELECT MAX(id) FROM dreams), 1));
SELECT setval('symbols_id_seq', COALESCE((SELECT MAX(id) FROM symbols), 1));
SELECT setval('characters_id_seq', COALESCE((SELECT MAX(id) FROM characters), 1));
SELECT setval('dream_symbols_id_seq', COALESCE((SELECT MAX(id) FROM dream_symbols), 1));
SELECT setval('dream_characters_id_seq', COALESCE((SELECT MAX(id) FROM dream_characters), 1));
SELECT setval('dream_emotions_id_seq', COALESCE((SELECT MAX(id) FROM dream_emotions), 1));
SELECT setval('dream_themes_id_seq', COALESCE((SELECT MAX(id) FROM dream_themes), 1));
SELECT setval('symbol_associations_id_seq', COALESCE((SELECT MAX(id) FROM symbol_associations), 1));
SELECT setval('character_associations_id_seq', COALESCE((SELECT MAX(id) FROM character_associations), 1));

-- ============================================
-- DONE!
-- Summary: 60 dreams, 25 symbols, 14 characters
-- ~130 dream-symbol links, ~55 dream-character links
-- ~210 emotions, ~135 themes
-- ~30 symbol associations, ~18 character associations
-- Patterns: Shadow integration journey over 5 months
-- ============================================
