from typing import Literal

from pydantic import BaseModel

from app.schemas.catalog import ProductListItem

class RecommendationOut(BaseModel):
    algorithm: Literal["content", "vector", "popularity", "hybrid", "history", "co_view"]
    items: list[ProductListItem]