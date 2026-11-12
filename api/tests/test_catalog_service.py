from types import SimpleNamespace

from app.services import catalog_service as svc


def test_query_locale_wins():
    assert svc.resolve_locale("en", "pl-PL,pl;q=0.9") == "en"


def test_accept_language_used():
    assert svc.resolve_locale(None, "de-DE,pl;q=0.8,en;q=0.5") == "pl"


def test_fallback_uk():
    assert svc.resolve_locale(None, None) == "uk"
    assert svc.resolve_locale(None, "de,fr") == "uk"


def test_tree_hides_children_of_inactive_parent(monkeypatch):
    rows = [
        SimpleNamespace(id=1, parent_id=None, slug="rings", name="Rings", description=None),
        SimpleNamespace(id=2, parent_id=1, slug="wedding", name="Wedding", description=None),
        SimpleNamespace(id=3, parent_id=99, slug="orphan", name="Orphan", description=None),
    ]
    monkeypatch.setattr(svc.repo, "list_categories", lambda db, locale: rows)
    tree = svc.get_category_tree(None, "uk")
    assert [n.slug for n in tree] == ["rings"]
    assert tree[0].children[0].slug == "wedding"
