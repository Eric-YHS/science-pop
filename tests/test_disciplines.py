"""Structural checks for the static discipline/source catalogue."""

from app.utils.disciplines import DISCIPLINES, SOURCE_DISCIPLINE_MAP

SOURCE_KEYS = {"name", "url", "type"}
VALID_SOURCE_TYPES = {"api", "web"}


def test_slugs_are_unique():
    slugs = [item["slug"] for item in DISCIPLINES]
    assert len(slugs) == len(set(slugs)), "duplicate discipline slug"


def test_every_discipline_has_sources():
    for item in DISCIPLINES:
        assert item["sources"], f"discipline {item['slug']} has no sources"


def test_source_entries_are_well_formed():
    for item in DISCIPLINES:
        for source in item["sources"]:
            assert SOURCE_KEYS.issubset(source), f"bad source entry in {item['slug']}: {source}"
            assert source["type"] in VALID_SOURCE_TYPES, source
            assert source["url"].startswith(("http://", "https://")), source


def test_map_covers_every_declared_source():
    for item in DISCIPLINES:
        for source in item["sources"]:
            assert source["name"] in SOURCE_DISCIPLINE_MAP


def test_sources_with_a_crawler_resolve_to_a_discipline():
    """The scheduler looks a discipline up by source name for manual triggers."""
    from app.services.crawler.scheduler import CRAWLERS

    for name in CRAWLERS:
        assert SOURCE_DISCIPLINE_MAP.get(name), f"{name} has a crawler but no discipline mapping"
