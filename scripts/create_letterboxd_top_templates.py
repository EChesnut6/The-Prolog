from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "movies"

MOVIES = [
    (1, "Harakiri", "1962"),
    (2, "The Human Condition III: A Soldier's Prayer", "1961"),
    (3, "12 Angry Men", "1957"),
    (4, "Come and See", "1985"),
    (5, "Seven Samurai", "1954"),
    (6, "High and Low", "1963"),
    (7, "The Shawshank Redemption", "1994"),
    (8, "The Godfather Part II", "1974"),
    (9, "The Human Condition I: No Greater Love", "1959"),
    (10, "City of God", "2002"),
    (11, "The Lord of the Rings: The Return of the King", "2003"),
    (12, "Schindler's List", "1993"),
    (13, "Yi Yi", "2000"),
    (14, "Parasite", "2019"),
    (15, "The Godfather", "1972"),
    (16, "Ikiru", "1952"),
    (17, "Cinema Paradiso", "1988"),
    (18, "Ran", "1985"),
    (19, "Le Trou", "1960"),
    (20, "The Good, the Bad and the Ugly", "1966"),
    (21, "La Haine", "1995"),
    (22, "A Brighter Summer Day", "1991"),
    (23, "Autumn Sonata", "1978"),
    (24, "The Human Condition II: Road to Eternity", "1959"),
    (25, "The Dark Knight", "2008"),
    (26, "Grave of the Fireflies", "1988"),
    (27, "Neon Genesis Evangelion: The End of Evangelion", "1997"),
    (28, "Woman in the Dunes", "1964"),
    (29, "The Battle of Algiers", "1966"),
    (30, "There Will Be Blood", "2007"),
    (31, "GoodFellas", "1990"),
    (32, "The Cranes Are Flying", "1957"),
    (33, "I Am Cuba", "1964"),
    (34, "Paths of Glory", "1957"),
    (35, "Interstellar", "2014"),
    (36, "Incendies", "2010"),
    (37, "Spirited Away", "2001"),
    (38, "Andrei Rublev", "1966"),
    (39, "It's a Wonderful Life", "1946"),
    (40, "The Ascent", "1977"),
    (41, "Apocalypse Now", "1979"),
    (42, "The Apartment", "1960"),
    (43, "Sunset Boulevard", "1950"),
    (44, "Tokyo Story", "1953"),
    (45, "The Lord of the Rings: The Two Towers", "2002"),
    (46, "Sansho the Bailiff", "1954"),
    (47, "The Passion of Joan of Arc", "1928"),
    (48, "Whiplash", "2014"),
    (49, "Fanny and Alexander", "1982"),
    (50, "Portrait of a Lady on Fire", "2019"),
    (51, "Mishima: A Life in Four Chapters", "1985"),
    (52, "Memories of Murder", "2003"),
    (53, "Close-Up", "1990"),
    (54, "Red Beard", "1965"),
    (55, "Life Is Beautiful", "1997"),
    (56, "The Red Shoes", "1948"),
    (57, "Nobody Knows", "2004"),
    (58, "Witness for the Prosecution", "1957"),
    (59, "Nights of Cabiria", "1957"),
    (60, "Barry Lyndon", "1975"),
    (61, "The Pianist", "2002"),
    (62, "Lawrence of Arabia", "1962"),
    (63, "Spider-Man: Across the Spider-Verse", "2023"),
    (64, "Farewell My Concubine", "1993"),
    (65, "The Empire Strikes Back", "1980"),
    (66, "Eternity and a Day", "1998"),
    (67, "A Woman Under the Influence", "1974"),
    (68, "Stalker", "1979"),
    (69, "Do the Right Thing", "1989"),
    (70, "Spider-Man: Into the Spider-Verse", "2018"),
    (71, "Satantango", "1994"),
    (72, "Princess Mononoke", "1997"),
    (73, "The Handmaiden", "2016"),
    (74, "The Voice of Hind Rajab", "2025"),
    (75, "Love Exposure", "2008"),
    (76, "The Lord of the Rings: The Fellowship of the Ring", "2001"),
    (77, "Once Upon a Time in the West", "1968"),
    (78, "Swing Girls", "2004"),
    (79, "Paper Moon", "1973"),
    (80, "An Elephant Sitting Still", "2018"),
    (81, "Persona", "1966"),
    (82, "Scenes from a Marriage", "1974"),
    (83, "Perfect Blue", "1997"),
    (84, "Good Will Hunting", "1997"),
    (85, "Dune: Part Two", "2024"),
    (86, "Where Is the Friend's House?", "1987"),
    (87, "In the Mood for Love", "2000"),
    (88, "A Separation", "2011"),
    (89, "Apur Sansar", "1959"),
    (90, "Se7en", "1995"),
    (91, "Sherlock Jr.", "1924"),
    (92, "Paris, Texas", "1984"),
    (93, "One Flew Over the Cuckoo's Nest", "1975"),
    (94, "Z", "1969"),
    (95, "Oldboy", "2003"),
    (96, "Rear Window", "1954"),
    (97, "Landscape in the Mist", "1988"),
    (98, "Inglourious Basterds", "2009"),
    (99, "All About Eve", "1950"),
    (100, "Army of Shadows", "1969"),
    (101, "The Wages of Fear", "1953"),
    (102, "It's Such a Beautiful Day", "2012"),
    (103, "Judgment at Nuremberg", "1961"),
    (104, "Howl's Moving Castle", "2004"),
    (105, "Central Station", "1998"),
    (106, "Amadeus", "1984"),
    (107, "Ordet", "1955"),
    (108, "Chainsaw Man – The Movie: Reze Arc", "2025"),
    (109, "The Thing", "1982"),
    (110, "How to Make Millions Before Grandma Dies", "2024"),
    (111, "A Man Escaped", "1956"),
    (112, "Raise the Red Lantern", "1991"),
    (113, "Dead Poets Society", "1989"),
    (114, "Singin' in the Rain", "1952"),
    (115, "A Special Day", "1977"),
    (116, "All That Jazz", "1979"),
    (117, "Still Walking", "2008"),
    (118, "The Departed", "2006"),
    (119, "I'm Still Here", "2024"),
    (120, "Monster", "2023"),
    (121, "The Silence of the Lambs", "1991"),
    (122, "To Be or Not to Be", "1942"),
    (123, "Three Colours: Red", "1994"),
    (124, "Late Spring", "1949"),
    (125, "Django Unchained", "2012"),
    (126, "Twin Peaks: Fire Walk with Me", "1992"),
    (127, "Wild Strawberries", "1957"),
    (128, "Prisoners", "2013"),
    (129, "Das Boot", "1981"),
    (130, "City Lights", "1931"),
    (131, "The Great Dictator", "1940"),
    (132, "Funeral Parade of Roses", "1969"),
    (133, "Rocco and His Brothers", "1960"),
    (134, "The Seventh Seal", "1957"),
    (135, "Pather Panchali", "1955"),
    (136, "Taste of Cherry", "1997"),
    (137, "Underground", "1995"),
    (138, "Brief Encounter", "1945"),
    (139, "The Young Girls of Rochefort", "1967"),
    (140, "The Celebration", "1998"),
    (141, "Mirror", "1975"),
    (142, "Project Hail Mary", "2026"),
    (143, "Mommy", "2014"),
    (144, "Before Sunset", "2004"),
    (145, "Perfect Days", "2023"),
    (146, "Tampopo", "1985"),
    (147, "No Country for Old Men", "2007"),
    (148, "Psycho", "1960"),
    (149, "Werckmeister Harmonies", "2000"),
    (150, "Wings of Desire", "1987"),
    (151, "Nirvanna the Band the Show the Movie", "2025"),
    (152, "Sing Sing", "2023"),
    (153, "Heat", "1995"),
    (154, "Dog Day Afternoon", "1975"),
    (155, "Shoplifters", "2018"),
    (156, "Puella Magi Madoka Magica the Movie Part III: Rebellion", "2013"),
    (157, "The 400 Blows", "1959"),
    (158, "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb", "1964"),
    (159, "The Cremator", "1969"),
    (160, "Chinatown", "1974"),
    (161, "The Elephant Man", "1980"),
    (162, "Before Sunrise", "1995"),
    (163, "Children of Men", "2006"),
    (164, "Dersu Uzala", "1975"),
    (165, "Yojimbo", "1961"),
    (166, "Fantastic Mr. Fox", "2009"),
    (167, "Opening Night", "1977"),
    (168, "The Treasure of the Sierra Madre", "1948"),
    (169, "Children of Paradise", "1945"),
    (170, "The Lives of Others", "2006"),
    (171, "M", "1931"),
    (172, "The Sacrifice", "1986"),
    (173, "The Father", "2020"),
    (174, "Azur & Asmar: The Princes' Quest", "2006"),
    (175, "Malcolm X", "1992"),
    (176, "Terminator 2: Judgment Day", "1991"),
    (177, "Secrets & Lies", "1996"),
    (178, "We All Loved Each Other So Much", "1974"),
    (179, "La Notte", "1961"),
    (180, "Bicycle Thieves", "1948"),
    (181, "The Man Who Shot Liberty Valance", "1962"),
    (182, "Evangelion: 3.0+1.0 Thrice Upon a Time", "2021"),
    (183, "The Hunt", "2012"),
    (184, "Nostalgia", "1983"),
    (185, "The Green Mile", "1999"),
    (186, "Fail Safe", "1964"),
    (187, "The Prestige", "2006"),
    (188, "Life, and Nothing More…", "1992"),
    (189, "The Iron Giant", "1999"),
    (190, "Akira", "1988"),
    (191, "Chungking Express", "1994"),
    (192, "Song of the Sea", "2014"),
    (193, "Casablanca", "1942"),
    (194, "Cure", "1997"),
    (195, "Ace in the Hole", "1951"),
    (196, "Ritual", "2000"),
    (197, "Some Like It Hot", "1959"),
    (198, "8½", "1963"),
    (199, "Look Back", "2024"),
    (200, "Fight Club", "1999"),
    (201, "Throne of Blood", "1957"),
    (202, "Interstella 5555: The 5tory of the 5ecret 5tar 5ystem", "2003"),
    (203, "Who's Afraid of Virginia Woolf?", "1966"),
    (204, "La Dolce Vita", "1960"),
    (205, "Sorcerer", "1977"),
    (206, "Rififi", "1955"),
    (207, "Mary and Max", "2009"),
    (208, "Jeanne Dielman, 23, quai du Commerce, 1080 Bruxelles", "1975"),
    (209, "A Matter of Life and Death", "1946"),
    (210, "Aparajito", "1956"),
    (211, "Ugetsu", "1953"),
    (212, "Network", "1976"),
    (213, "The Tale of The Princess Kaguya", "2013"),
    (214, "Mulholland Drive", "2001"),
    (215, "Il Sorpasso", "1962"),
    (216, "Modern Times", "1936"),
    (217, "Umberto D.", "1952"),
    (218, "The Night of the Hunter", "1955"),
    (219, "The Face of Another", "1966"),
    (220, "Double Indemnity", "1944"),
    (221, "Saving Private Ryan", "1998"),
    (222, "The Holdovers", "2023"),
    (223, "I Swear", "2025"),
    (224, "Winter Light", "1963"),
    (225, "A Moment of Innocence", "1996"),
    (226, "The Fall", "2006"),
    (227, "The First Slam Dunk", "2022"),
    (228, "Kes", "1969"),
    (229, "Tokyo Godfathers", "2003"),
    (230, "Alien", "1979"),
    (231, "The Best Years of Our Lives", "1946"),
    (232, "2001: A Space Odyssey", "1968"),
    (233, "4 Months, 3 Weeks and 2 Days", "2007"),
    (234, "The Sound of Music", "1965"),
    (235, "Macario", "1960"),
    (236, "Everything Everywhere All at Once", "2022"),
    (237, "The Bridge on the River Kwai", "1957"),
    (238, "Quo Vadis, Aida?", "2020"),
    (239, "Anatomy of a Murder", "1959"),
    (240, "Metropolis", "1927"),
    (241, "Marcel the Shell with Shoes On", "2021"),
    (242, "Son of the White Mare", "1981"),
    (243, "The Secret in Their Eyes", "2009"),
    (244, "Kwaidan", "1964"),
    (245, "The Grand Budapest Hotel", "2014"),
    (246, "Sweet Smell of Success", "1957"),
    (247, "Vada Chennai", "2018"),
    (248, "Eternal Sunshine of the Spotless Mind", "2004"),
    (249, "Time of the Gypsies", "1988"),
    (250, "Kamikaze Girls", "2004"),
]


def main() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for rank, title, year in MOVIES:
        slug = _slugify(title)
        path = CONTENT_DIR / f"{slug}.md"
        if path.exists():
            skipped += 1
            continue

        path.write_text(_template(title, slug, year), encoding="utf-8")
        created += 1

    print(f"Created {created} template(s); skipped {skipped} existing file(s).")


def _template(title: str, slug: str, year: str) -> str:
    return f"""---
title: {title}
slug: {slug}
tmdb_title: {title}
year: {year}
enjoyment_rating: TBD
filmmaking_rating: TBD
reviewed: false
teaser: Draft pre-flight checklist template.
---

## Primer

Add spoiler-light context for someone before watching.

## Technical Footnotes

- Add technical notes worth noticing before or during the watch.

## Review

Write the full critique here.

## Gallery

- Visual reference
- Production still idea
- Related artwork or image category
"""


def _slugify(value: str) -> str:
    allowed = []
    previous_dash = False
    for character in value.lower():
        if character.isalnum():
            allowed.append(character)
            previous_dash = False
        elif not previous_dash:
            allowed.append("-")
            previous_dash = True
    return "".join(allowed).strip("-")


if __name__ == "__main__":
    main()
