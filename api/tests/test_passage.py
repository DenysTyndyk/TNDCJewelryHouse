from decimal import Decimal

from app.models.catalog import ProductTranslation, ProductVariant
from app.models.enums import MetalColor, MetalType
from app.services.search.passage import build_passage, content_hash


def _variant(weight="3.200"):
    return ProductVariant(
        metal_type=MetalType.Gold, metal_color=MetalColor.Yellow, fineness=585, weight=Decimal(weight)
    )


def _passage(description="Класичний перстень.", locale="uk", weight="3.200"):
    translation = ProductTranslation(name="Перстень Сонце", description=description)
    return build_passage(translation, "Перстені", [_variant(weight), _variant(weight)], ["diamond"], locale)


def test_uk_passage_structure_and_numbers():
    assert _passage() == (
        "Перстень Сонце. Перстені. Класичний перстень. "
        "золото, жовтий колір, проба 585, 14 карат. вага 3,2 г. камені: діамант."
    )


def test_same_input_same_hash():
    assert content_hash(_passage()) == content_hash(_passage())


def test_changed_description_changes_hash():
    assert content_hash(_passage()) != content_hash(_passage(description="Інший опис"))


def test_version_change_changes_hash():
    passage = _passage()
    assert content_hash(passage, version=1) != content_hash(passage, version=2)


def test_pl_passage_uses_polish_words():
    passage = _passage(locale="pl")
    assert "złoto" in passage and "próba 585" in passage and "waga 3,2 g" in passage and "diament" in passage


def test_weight_labels():
    assert "легка прикраса" in _passage(weight="1.500")
    assert "масивна прикраса" in _passage(weight="9.000")