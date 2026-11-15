from app.models.enums import EventType

EVENT_WEIGHTS: dict[EventType, float] = {
    EventType.ProductView: 1.0,
    EventType.Search: 1.0,
    EventType.ClickRecommendation: 2.0,
    EventType.AddToFavorites: 3.0,
    EventType.AddToCart: 4.0,
    EventType.Purchase: 6.0,
}