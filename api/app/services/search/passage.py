import hashlib
from decimal import Decimal

from app.core.config import settings
from app.models.catalog import ProductTranslation, ProductVariant
from app.models.enums import MetalType

KARATS = {375: 9, 500: 12, 585: 14, 750: 18, 875: 21, 958: 23, 999: 24}
LIGHT_MAX_G = Decimal("2")
MASSIVE_MIN_G = Decimal("8")

WORDS = {
    "uk": {
        "Gold": "золото", "Silver": "срібло", "Platinum": "платина",
        "White": "білий колір", "Yellow": "жовтий колір", "Rose": "рожевий колір",
        "Bicolor": "двоколірний метал",
        "fineness": "проба {}", "karat": "{} карат", "weight": "вага {} г",
        "light": "легка прикраса", "massive": "масивна прикраса", "stones": "камені: {}",
        "diamond": "діамант", "sapphire": "сапфір", "ruby": "рубін", "emerald": "смарагд",
        "amethyst": "аметист", "topaz": "топаз", "pearl": "перлина", "cubic_zirconia": "фіаніт",
    },
    "pl": {
        "Gold": "złoto", "Silver": "srebro", "Platinum": "platyna",
        "White": "kolor biały", "Yellow": "kolor żółty", "Rose": "kolor różowy",
        "Bicolor": "metal dwukolorowy",
        "fineness": "próba {}", "karat": "{} karatów", "weight": "waga {} g",
        "light": "lekka biżuteria", "massive": "masywna biżuteria", "stones": "kamienie: {}",
        "diamond": "diament", "sapphire": "szafir", "ruby": "rubin", "emerald": "szmaragd",
        "amethyst": "ametyst", "topaz": "topaz", "pearl": "perła", "cubic_zirconia": "cyrkonia",
    },
    "en": {
        "Gold": "gold", "Silver": "silver", "Platinum": "platinum",
        "White": "white color", "Yellow": "yellow color", "Rose": "rose color",
        "Bicolor": "two-tone metal",
        "fineness": "fineness {}", "karat": "{} karat", "weight": "weight {} g",
        "light": "lightweight piece", "massive": "massive piece", "stones": "stones: {}",
        "diamond": "diamond", "sapphire": "sapphire", "ruby": "ruby", "emerald": "emerald",
        "amethyst": "amethyst", "topaz": "topaz", "pearl": "pearl", "cubic_zirconia": "cubic zirconia",
    },
}

def _num(value: Decimal,locale: str) -> str:
    text = f"{value.normalize():f}"
    return text if locale == "en" else text.replace(".", ",")

def _metal(variant: ProductVariant, w: dict) -> str:
    parts = [w[variant.metal_type]] if variant.metal_type else []
    if variant.metal_color:
        parts.append(w[variant.metal_color.value])
    if variant.fineness:
        parts.append(w["fineness"].format(variant.fineness))
        if variant.metal_type == MetalType.Gold and variant.fineness in KARATS:
            parts.append(w["karat"].format(KARATS[variant.fineness]))
    return ", ".join(parts)

def _weight(variants: list[ProductVariant], locale: str, w:dict) -> str:
    weight = [v.weight for v in variants if v.weight]
    if not weight:
        return ""
    lightest = min(weight)
    text = w["weight"].format(_num(lightest, locale))
    if lightest < LIGHT_MAX_G:
        text += ", " + w["light"]
    elif lightest > MASSIVE_MIN_G:
        text += ", " + w["massive"]
    return text

def build_passage(translation: ProductTranslation, category_name: str, variants: list[ProductVariant], gemstone_slugs: list[str], locale: str) -> str:
    w = WORDS[locale]
    metals = "; ".join(sorted({_metal(v,w) for v in variants} -{""}))
    stones = "; ".join(sorted({w.get(s,s.replace("_"," ")) for s in gemstone_slugs}))
    parts=[
        translation.name,
        category_name,
        translation.description,
        metals,
        _weight(variants, locale, w),
        w["stones"].format(stones) if stones else "",
    ]
    return ". ".join(p.strip().rstrip(".") for p in parts if p and p.strip()) + "."

def content_hash(
    passage: str,
    model: str = settings.embedding_model,
    version: int = settings.embedding_version,
) -> str:
    return hashlib.sha256(f"{model}|{version}|{passage}".encode()).hexdigest()