"""Development seed data: catalog + gemstones + shipping + users.

Single market (Ukraine, UAH). Settings read ../.env themselves, so no `source` is needed
(sourcing it in zsh strips the quotes from JSON values like CORS_ORIGINS):

    cd api && python -m scripts.seed
"""
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from argon2 import PasswordHasher
from faker import Faker
from PIL import Image

from app.db.session import get_session
from app.models import (
    Category,
    CategoryTranslation,
    Gemstone,
    Product,
    ProductGemstone,
    ProductImage,
    ProductTranslation,
    ProductVariant,
    ShippingMethod,
    User,
    UserProfile,
    VariantPrice,
)
from app.models.enums import (
    Currency,
    DeliveryProvider,
    GemstoneType,
    MetalColor,
    MetalType,
    Role,
    UserStatus,
)
from app.services.admin_catalog_service import save_image

hasher = PasswordHasher()

# Optional real photos: seed_photos/<product-slug>.jpg|png|webp; otherwise a metal-coloured placeholder
SEED_PHOTOS = Path(__file__).resolve().parent / "seed_photos"
PLACEHOLDER_COLORS = {
    MetalColor.White: "#d9dadc",
    MetalColor.Yellow: "#e6c46a",
    MetalColor.Rose: "#e3a99a",
    MetalColor.Bicolor: "#dccfa0",
}


def seed_image(category_slug: str, slug: str, metal_color: MetalColor | None) -> tuple[str, int, int]:
    """Run the seed photo through the same WebP pipeline as admin uploads."""
    photo = next((p for p in sorted(SEED_PHOTOS.glob(f"{slug}.*"))), None)
    if photo:
        data = photo.read_bytes()
    else:
        buf = BytesIO()
        Image.new("RGB", (1600, 1600), PLACEHOLDER_COLORS.get(metal_color, "#e8e2d6")).save(buf, "PNG")
        data = buf.getvalue()
    key = f"seed/{category_slug}/{slug}"
    width, height = save_image(key, data)
    return key, width, height
faker = Faker("uk_UA")

GEMSTONES = [
    ("diamond", "Діамант", "precious"),
    ("sapphire", "Сапфір", "precious"),
    ("ruby", "Рубін", "precious"),
    ("emerald", "Смарагд", "precious"),
    ("amethyst", "Аметист", "semi-precious"),
    ("topaz", "Топаз", "semi-precious"),
    ("pearl", "Перлина", "organic"),
    ("cubic_zirconia", "Фіаніт", "simulant"),
]

CATEGORIES = [
    ("rings", None, "Перстені", "Перстені з золота та срібла на щодень і особливі випадки."),
    ("wedding-rings", "rings", "Обручки", "Парні та одинарні обручки класичних і сучасних форм."),
    ("earrings", None, "Сережки", "Сережки-пусети, висячі та кільця з камінням і без."),
    ("necklaces", None, "Кольє", "Кольє та колети для вечірніх і щоденних образів."),
    ("pendants", None, "Підвіски", "Підвіски та кулони на ланцюжок окремо від основного вибору."),
    ("bracelets", None, "Браслети", "Браслети-ланцюжки, жорсткі та з підвісками."),
    ("chains", None, "Ланцюжки", "Ланцюжки плетіння панцерне, якірне та снейк."),
    ("sets", None, "Набори", "Готові комплекти: сережки + кольє/підвіска в одному стилі."),
]

# pl/en translations; uk lives in CATEGORIES above (D8: three locales)
CATEGORY_TRANSLATIONS = {
    "rings": {
        "pl": ("Pierścionki", "Pierścionki ze złota i srebra na co dzień i na wyjątkowe okazje."),
        "en": ("Rings", "Gold and silver rings for everyday wear and special occasions."),
    },
    "wedding-rings": {
        "pl": ("Obrączki", "Obrączki parowe i pojedyncze w klasycznych i nowoczesnych formach."),
        "en": ("Wedding rings", "Paired and single wedding bands in classic and modern shapes."),
    },
    "earrings": {
        "pl": ("Kolczyki", "Kolczyki sztyfty, wiszące i koła, z kamieniami i bez."),
        "en": ("Earrings", "Studs, drop earrings and hoops, with or without stones."),
    },
    "necklaces": {
        "pl": ("Naszyjniki", "Naszyjniki i kolie na wieczorne i codzienne stylizacje."),
        "en": ("Necklaces", "Necklaces and collars for evening and everyday looks."),
    },
    "pendants": {
        "pl": ("Zawieszki", "Zawieszki i wisiorki do noszenia na łańcuszku."),
        "en": ("Pendants", "Pendants and charms to wear on a chain."),
    },
    "bracelets": {
        "pl": ("Bransoletki", "Bransoletki łańcuszkowe, sztywne i z zawieszkami."),
        "en": ("Bracelets", "Chain, bangle and charm bracelets."),
    },
    "chains": {
        "pl": ("Łańcuszki", "Łańcuszki o splocie pancerka, kotwica i snake."),
        "en": ("Chains", "Curb, anchor and snake chains."),
    },
    "sets": {
        "pl": ("Komplety", "Gotowe komplety: kolczyki + naszyjnik/zawieszka w jednym stylu."),
        "en": ("Sets", "Matching sets: earrings plus a necklace or pendant in one style."),
    },
}

# (slug, category, name, description, is_featured, variants)
# variant: (sku_suffix, size, length_mm, weight, metal_type, metal_color, fineness,
#           base_price, stock, gemstone_slug, carat)
PRODUCTS = [
    (
        "persten-klasyka-bile-zoloto", "rings", 'Перстень "Класика" з білого золота',
        "Лаконічний перстень із білого золота 585 проби з доріжкою фіанітів.", True,
        [
            ("16", "16", None, Decimal("3.1"), MetalType.Gold, MetalColor.White, 585, Decimal("8900.00"), 4, "cubic_zirconia", Decimal("0.30")),
            ("17", "17", None, Decimal("3.3"), MetalType.Gold, MetalColor.White, 585, Decimal("9200.00"), 3, "cubic_zirconia", Decimal("0.30")),
        ],
    ),
    (
        "persten-tonkyi-bile-zoloto", "rings", "Тонкий перстень з білого золота",
        "Тонкий гладкий перстень із білого золота 585 проби, вага до 1 г.", False,
        [
            ("15", "15", None, Decimal("0.8"), MetalType.Gold, MetalColor.White, 585, Decimal("2790.00"), 6, None, None),
            ("16", "16", None, Decimal("0.9"), MetalType.Gold, MetalColor.White, 585, Decimal("2950.00"), 4, None, None),
        ],
    ),
    (
        "persten-solitaire-diamant", "rings", 'Перстень "Соло" з діамантом',
        "Жовте золото 750 проби, один центральний діамант кругового бриліантового шліфування.", True,
        [
            ("17", "17", None, Decimal("2.8"), MetalType.Gold, MetalColor.Yellow, 750, Decimal("24500.00"), 2, "diamond", Decimal("0.20")),
        ],
    ),
    (
        "persten-rozove-zoloto-ametyst", "rings", "Перстень з рожевого золота та аметистом",
        "Рожеве золото 585 проби, аметист овальної форми.", False,
        [
            ("18", "18", None, Decimal("3.5"), MetalType.Gold, MetalColor.Rose, 585, Decimal("10200.00"), 5, "amethyst", Decimal("1.10")),
        ],
    ),
    (
        "obruchka-klasychna-bicolor", "wedding-rings", "Обручка класична біколор",
        "Обручка з жовтого та білого золота 585 проби, пряма форма.", True,
        [
            ("18", "18", None, Decimal("4.0"), MetalType.Gold, MetalColor.Bicolor, 585, Decimal("11800.00"), 6, None, None),
            ("20", "20", None, Decimal("4.4"), MetalType.Gold, MetalColor.Bicolor, 585, Decimal("12600.00"), 4, None, None),
        ],
    ),
    (
        "obruchka-dorizhka-brilianty", "wedding-rings", "Обручка з доріжкою діамантів",
        "Біле золото 750 проби, доріжка невеликих діамантів по колу.", False,
        [
            ("17", "17", None, Decimal("3.6"), MetalType.Gold, MetalColor.White, 750, Decimal("32500.00"), 2, "diamond", Decimal("0.45")),
        ],
    ),
    (
        "serezhky-pusety-sribni", "earrings", "Сережки-пусети срібні",
        "Срібло 925 проби, мінімалістичні пусети з фіанітом.", False,
        [
            ("one", None, None, Decimal("1.2"), MetalType.Silver, MetalColor.White, 925, Decimal("950.00"), 12, "cubic_zirconia", Decimal("0.10")),
        ],
    ),
    (
        "serezhky-visyachi-sapfir", "earrings", "Сережки висячі з сапфіром",
        "Біле золото 585 проби, підвісні сережки з синім сапфіром.", True,
        [
            ("one", None, None, Decimal("2.6"), MetalType.Gold, MetalColor.White, 585, Decimal("15400.00"), 3, "sapphire", Decimal("0.60")),
        ],
    ),
    (
        "serezhky-perlyny-klasyka", "earrings", "Сережки з перлинами класичні",
        "Жовте золото 375 проби, культивовані перлини округлої форми.", False,
        [
            ("one", None, None, Decimal("1.8"), MetalType.Gold, MetalColor.Yellow, 375, Decimal("4200.00"), 7, "pearl", Decimal("0.00")),
        ],
    ),
    (
        "kolie-tonke-zolote", "necklaces", "Кольє тонке золоте",
        "Жовте золото 585 проби, якірне плетіння, застібка карабін.", False,
        [
            ("40", "40cm", 400, Decimal("3.9"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("13900.00"), 5, None, None),
            ("45", "45cm", 450, Decimal("4.3"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("14700.00"), 4, None, None),
        ],
    ),
    (
        "kolie-sribne-z-topazom", "necklaces", "Кольє срібне з топазом",
        "Срібло 925 проби, кольє з блакитним топазом по центру.", False,
        [
            ("42", "42cm", 420, Decimal("5.1"), MetalType.Silver, MetalColor.White, 925, Decimal("2600.00"), 6, "topaz", Decimal("1.80")),
        ],
    ),
    (
        "pidviska-serce-zoloto", "pendants", 'Підвіска "Серце" золота',
        "Рожеве золото 585 проби, гладка підвіска у формі серця.", True,
        [
            ("one", None, None, Decimal("1.5"), MetalType.Gold, MetalColor.Rose, 585, Decimal("6300.00"), 8, None, None),
        ],
    ),
    (
        "pidviska-smaragd-bile-zoloto", "pendants", "Підвіска зі смарагдом",
        "Біле золото 750 проби, підвіска з натуральним смарагдом огранки \"крапля\".", False,
        [
            ("one", None, None, Decimal("2.1"), MetalType.Gold, MetalColor.White, 750, Decimal("21800.00"), 2, "emerald", Decimal("0.55")),
        ],
    ),
    (
        "pidviska-fianit-sribna", "pendants", "Підвіска срібна з фіанітом",
        "Срібло 925 проби, компактна підвіска для щоденного носіння.", False,
        [
            ("one", None, None, Decimal("0.9"), MetalType.Silver, MetalColor.White, 925, Decimal("780.00"), 15, "cubic_zirconia", Decimal("0.20")),
        ],
    ),
    (
        "braslet-lantsyuzhok-zoloto", "bracelets", "Браслет-ланцюжок золотий",
        "Жовте золото 585 проби, плетіння панцерне, регулювання довжини.", True,
        [
            ("17", "17cm", 170, Decimal("3.2"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("10900.00"), 5, None, None),
            ("19", "19cm", 190, Decimal("3.6"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("11600.00"), 3, None, None),
        ],
    ),
    (
        "braslet-zhorstkyi-sribnyi", "bracelets", "Браслет жорсткий срібний",
        "Срібло 925 проби, жорсткий браслет-манжета.", False,
        [
            ("one", "M", None, Decimal("6.0"), MetalType.Silver, MetalColor.White, 925, Decimal("2100.00"), 6, None, None),
        ],
    ),
    (
        "braslet-rubiny-rozove-zoloto", "bracelets", "Браслет з рубінами",
        "Рожеве золото 750 проби, браслет із рядом дрібних рубінів.", False,
        [
            ("18", "18cm", 180, Decimal("4.5"), MetalType.Gold, MetalColor.Rose, 750, Decimal("28900.00"), 1, "ruby", Decimal("0.80")),
        ],
    ),
    (
        "lantsyuzhok-yakirne-pletinnya", "chains", "Ланцюжок якірне плетіння",
        "Жовте золото 585 проби, класичне якірне плетіння.", False,
        [
            ("45", "45cm", 450, Decimal("2.8"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("9800.00"), 7, None, None),
            ("50", "50cm", 500, Decimal("3.1"), MetalType.Gold, MetalColor.Yellow, 585, Decimal("10500.00"), 5, None, None),
        ],
    ),
    (
        "lantsyuzhok-snake-bile-zoloto", "chains", "Ланцюжок snake біле золото",
        "Біле золото 585 проби, плетіння snake, тонкий профіль.", False,
        [
            ("50", "50cm", 500, Decimal("2.4"), MetalType.Gold, MetalColor.White, 585, Decimal("8700.00"), 6, None, None),
        ],
    ),
    (
        "lantsyuzhok-sribny-panceme", "chains", "Ланцюжок срібний панцерне",
        "Срібло 925 проби, щільне панцерне плетіння.", False,
        [
            ("55", "55cm", 550, Decimal("4.0"), MetalType.Silver, MetalColor.White, 925, Decimal("1450.00"), 10, None, None),
        ],
    ),
    (
        "nabir-pusety-pidviska-perlyny", "sets", "Набір з перлинами",
        "Жовте золото 375 проби: сережки-пусети та підвіска з перлинами в комплекті.", True,
        [
            ("one", None, None, Decimal("3.0"), MetalType.Gold, MetalColor.Yellow, 375, Decimal("7600.00"), 4, "pearl", Decimal("0.00")),
        ],
    ),
    (
        "nabir-sapfiry-bile-zoloto", "sets", "Набір із сапфірами",
        "Біле золото 585 проби: сережки та кольє з синіми сапфірами.", False,
        [
            ("one", None, None, Decimal("5.2"), MetalType.Gold, MetalColor.White, 585, Decimal("26800.00"), 1, "sapphire", Decimal("0.90")),
        ],
    ),
    (
        "nabir-sribny-fianity", "sets", "Срібний набір з фіанітами",
        "Срібло 925 проби: сережки та підвіска з фіанітами, бюджетний варіант.", False,
        [
            ("one", None, None, Decimal("2.7"), MetalType.Silver, MetalColor.White, 925, Decimal("1850.00"), 8, "cubic_zirconia", Decimal("0.40")),
        ],
    ),
]

# pl/en translations; uk lives in PRODUCTS above. Keys must match product slugs exactly.
PRODUCT_TRANSLATIONS = {
    "persten-klasyka-bile-zoloto": {
        "pl": ('Pierścionek "Klasyka" z białego złota', "Minimalistyczny pierścionek z białego złota próby 585 z rzędem cyrkonii."),
        "en": ('"Classic" white gold ring', "A minimalist 585 white gold ring with a row of cubic zirconia."),
    },
    "persten-tonkyi-bile-zoloto": {
        "pl": ("Cienki pierścionek z białego złota", "Cienki gładki pierścionek z białego złota próby 585, waga do 1 g."),
        "en": ("Thin white gold ring", "A thin smooth 585 white gold ring weighing under 1 g."),
    },
    "persten-solitaire-diamant": {
        "pl": ('Pierścionek "Solo" z diamentem', "Żółte złoto próby 750, jeden centralny diament w szlifie brylantowym."),
        "en": ('"Solo" diamond ring', "750 yellow gold with a single round brilliant-cut centre diamond."),
    },
    "persten-rozove-zoloto-ametyst": {
        "pl": ("Pierścionek z różowego złota z ametystem", "Różowe złoto próby 585, owalny ametyst."),
        "en": ("Rose gold ring with amethyst", "585 rose gold with an oval amethyst."),
    },
    "obruchka-klasychna-bicolor": {
        "pl": ("Obrączka klasyczna dwukolorowa", "Obrączka z żółtego i białego złota próby 585, prosty profil."),
        "en": ("Classic bicolor wedding band", "585 yellow and white gold wedding band with a straight profile."),
    },
    "obruchka-dorizhka-brilianty": {
        "pl": ("Obrączka z rzędem diamentów", "Białe złoto próby 750, rząd drobnych diamentów dookoła."),
        "en": ("Diamond eternity wedding band", "750 white gold with a row of small diamonds all around."),
    },
    "serezhky-pusety-sribni": {
        "pl": ("Kolczyki sztyfty srebrne", "Srebro próby 925, minimalistyczne sztyfty z cyrkonią."),
        "en": ("Silver stud earrings", "925 silver minimalist studs with cubic zirconia."),
    },
    "serezhky-visyachi-sapfir": {
        "pl": ("Kolczyki wiszące z szafirem", "Białe złoto próby 585, wiszące kolczyki z niebieskim szafirem."),
        "en": ("Sapphire drop earrings", "585 white gold drop earrings with a blue sapphire."),
    },
    "serezhky-perlyny-klasyka": {
        "pl": ("Kolczyki z perłami klasyczne", "Żółte złoto próby 375, okrągłe perły hodowlane."),
        "en": ("Classic pearl earrings", "375 yellow gold with round cultured pearls."),
    },
    "kolie-tonke-zolote": {
        "pl": ("Naszyjnik cienki złoty", "Żółte złoto próby 585, splot kotwica, zapięcie karabińczyk."),
        "en": ("Fine gold necklace", "585 yellow gold, anchor link, lobster clasp."),
    },
    "kolie-sribne-z-topazom": {
        "pl": ("Naszyjnik srebrny z topazem", "Srebro próby 925, naszyjnik z niebieskim topazem pośrodku."),
        "en": ("Silver necklace with topaz", "925 silver necklace with a blue topaz centrepiece."),
    },
    "pidviska-serce-zoloto": {
        "pl": ('Zawieszka "Serce" złota', "Różowe złoto próby 585, gładka zawieszka w kształcie serca."),
        "en": ('"Heart" gold pendant', "585 rose gold smooth heart-shaped pendant."),
    },
    "pidviska-smaragd-bile-zoloto": {
        "pl": ("Zawieszka ze szmaragdem", 'Białe złoto próby 750, zawieszka z naturalnym szmaragdem w szlifie "kropla".'),
        "en": ("Emerald pendant", "750 white gold pendant with a natural pear-cut emerald."),
    },
    "pidviska-fianit-sribna": {
        "pl": ("Zawieszka srebrna z cyrkonią", "Srebro próby 925, niewielka zawieszka do codziennego noszenia."),
        "en": ("Silver pendant with cubic zirconia", "925 silver compact pendant for everyday wear."),
    },
    "braslet-lantsyuzhok-zoloto": {
        "pl": ("Bransoletka łańcuszkowa złota", "Żółte złoto próby 585, splot pancerka, regulowana długość."),
        "en": ("Gold chain bracelet", "585 yellow gold curb chain with adjustable length."),
    },
    "braslet-zhorstkyi-sribnyi": {
        "pl": ("Bransoletka sztywna srebrna", "Srebro próby 925, sztywna bransoletka typu mankiet."),
        "en": ("Silver cuff bracelet", "925 silver rigid cuff bracelet."),
    },
    "braslet-rubiny-rozove-zoloto": {
        "pl": ("Bransoletka z rubinami", "Różowe złoto próby 750, bransoletka z rzędem drobnych rubinów."),
        "en": ("Ruby bracelet", "750 rose gold bracelet with a row of small rubies."),
    },
    "lantsyuzhok-yakirne-pletinnya": {
        "pl": ("Łańcuszek splot kotwica", "Żółte złoto próby 585, klasyczny splot kotwica."),
        "en": ("Anchor link chain", "585 yellow gold classic anchor link chain."),
    },
    "lantsyuzhok-snake-bile-zoloto": {
        "pl": ("Łańcuszek snake z białego złota", "Białe złoto próby 585, splot snake, cienki profil."),
        "en": ("White gold snake chain", "585 white gold snake chain with a slim profile."),
    },
    "lantsyuzhok-sribny-panceme": {
        "pl": ("Łańcuszek srebrny pancerka", "Srebro próby 925, gęsty splot pancerka."),
        "en": ("Silver curb chain", "925 silver chain with a dense curb link."),
    },
    "nabir-pusety-pidviska-perlyny": {
        "pl": ("Komplet z perłami", "Żółte złoto próby 375: kolczyki sztyfty i zawieszka z perłami w komplecie."),
        "en": ("Pearl set", "375 yellow gold: stud earrings and a pendant with pearls."),
    },
    "nabir-sapfiry-bile-zoloto": {
        "pl": ("Komplet z szafirami", "Białe złoto próby 585: kolczyki i naszyjnik z niebieskimi szafirami."),
        "en": ("Sapphire set", "585 white gold: earrings and a necklace with blue sapphires."),
    },
    "nabir-sribny-fianity": {
        "pl": ("Srebrny komplet z cyrkoniami", "Srebro próby 925: kolczyki i zawieszka z cyrkoniami, wersja budżetowa."),
        "en": ("Silver set with cubic zirconia", "925 silver: earrings and a pendant with cubic zirconia, a budget option."),
    },
}

SHIPPING_METHODS = [
    (DeliveryProvider.NovaPoshta, "Нова Пошта — відділення", Decimal("70.00"), Decimal("1500.00"), 1, 2),
    (DeliveryProvider.UkrPoshta, "Укрпошта", Decimal("50.00"), Decimal("1500.00"), 2, 5),
    (DeliveryProvider.Courier, "Курʼєр по Києву", Decimal("120.00"), Decimal("2000.00"), 0, 1),
]


def seed_gemstones(session) -> dict[str, Gemstone]:
    by_slug = {}
    for slug, name, kind in GEMSTONES:
        gem = Gemstone(slug=slug, name=name, kind=kind)
        session.add(gem)
        by_slug[slug] = gem
    session.flush()
    return by_slug


def seed_categories(session) -> dict[str, Category]:
    by_slug: dict[str, Category] = {}
    for slug, _parent_slug, name, description in CATEGORIES:
        category = Category(slug=slug)
        session.add(category)
        by_slug[slug] = category
    session.flush()

    for slug, parent_slug, name, description in CATEGORIES:
        if parent_slug:
            by_slug[slug].parent_id = by_slug[parent_slug].id
        translations = {"uk": (name, description), **CATEGORY_TRANSLATIONS[slug]}
        for locale, (tr_name, tr_description) in translations.items():
            session.add(
                CategoryTranslation(
                    category_id=by_slug[slug].id,
                    locale=locale,
                    name=tr_name,
                    description=tr_description,
                )
            )
    session.flush()
    return by_slug


def seed_products(session, categories: dict[str, Category], gemstones: dict[str, Gemstone]) -> None:
    for slug, category_slug, name, description, is_featured, variants in PRODUCTS:
        product = Product(
            category_id=categories[category_slug].id,
            slug=slug,
            is_featured=is_featured,
            published_at=datetime.now(timezone.utc),
        )
        session.add(product)
        session.flush()

        translations = {"uk": (name, description), **PRODUCT_TRANSLATIONS[slug]}
        for locale, (tr_name, tr_description) in translations.items():
            session.add(
                ProductTranslation(
                    product_id=product.id,
                    locale=locale,
                    name=tr_name,
                    description=tr_description,
                    meta_title=tr_name,
                    meta_description=tr_description[:320],
                )
            )
        storage_key, width, height = seed_image(category_slug, slug, variants[0][5])  # [5] = metal_color
        session.add(
            ProductImage(
                product_id=product.id,
                storage_key=storage_key,
                alt_text=name,
                width=width,
                height=height,
                is_primary=True,
                sort_order=0,
            )
        )

        for (
            sku_suffix,
            size,
            length_mm,
            weight,
            metal_type,
            metal_color,
            fineness,
            base_price,
            stock,
            gemstone_slug,
            carat,
        ) in variants:
            variant = ProductVariant(
                product_id=product.id,
                sku=f"{slug.upper()[:16]}-{sku_suffix.upper()}",
                size=size,
                length_mm=length_mm,
                weight=weight,
                metal_type=metal_type,
                metal_color=metal_color,
                fineness=fineness,
                base_price=base_price,
                stock_quantity=stock,
            )
            session.add(variant)
            session.flush()

            session.add(
                VariantPrice(
                    variant_id=variant.id,
                    currency=Currency.UAH,
                    price=base_price,
                )
            )

            if gemstone_slug:
                session.add(
                    ProductGemstone(
                        product_id=product.id,
                        variant_id=variant.id,
                        gemstone_id=gemstones[gemstone_slug].id,
                        gemstone_type=GemstoneType.Natural if gemstone_slug != "cubic_zirconia" else GemstoneType.LabGrown,
                        quantity=1,
                        carat=carat,
                        is_center_stone=True,
                    )
                )


def seed_shipping_methods(session) -> None:
    for provider, name, cost, free_from, days_min, days_max in SHIPPING_METHODS:
        session.add(
            ShippingMethod(
                provider=provider,
                name=name,
                cost=cost,
                currency=Currency.UAH,
                free_from_amount=free_from,
                delivery_days_min=days_min,
                delivery_days_max=days_max,
            )
        )


def seed_users(session) -> None:
    admin = User(
        email="admin@tndc.ua",
        role=Role.Admin,
        status=UserStatus.Active,
        password_hash=hasher.hash("Admin123!"),
    )
    session.add(admin)
    session.flush()
    session.add(
        UserProfile(
            user_id=admin.id,
            first_name="Admin",
            last_name="TNDC",
            preferred_language="uk",
            consent_personal_data=True,
            consent_marketing=False,
        )
    )

    for i in range(6):
        first_name = faker.first_name()
        last_name = faker.last_name()
        user = User(
            email=f"test.user{i + 1}@tndc.ua",
            role=Role.User,
            status=UserStatus.Active if i else UserStatus.PendingVerification,
            password_hash=hasher.hash("Password123!"),
        )
        session.add(user)
        session.flush()
        session.add(
            UserProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                phone_number=faker.unique.numerify("+380#########"),
                preferred_language="uk",
                consent_personal_data=True,
                consent_marketing=faker.boolean(),
            )
        )


def main() -> None:
    session = get_session()
    try:
        if session.query(Category).first() is not None:
            print("Seed skipped: categories already exist.")
            return

        gemstones = seed_gemstones(session)
        categories = seed_categories(session)
        seed_products(session, categories, gemstones)
        seed_shipping_methods(session)
        seed_users(session)

        session.commit()
        print(
            f"Seeded {len(CATEGORIES)} categories, {len(PRODUCTS)} products, "
            f"{len(GEMSTONES)} gemstones, {len(SHIPPING_METHODS)} shipping methods, 7 users."
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
