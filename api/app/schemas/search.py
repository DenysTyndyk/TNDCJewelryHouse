from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.catalog import ProductFilter, ProductListItem

SearchMode = Literal["lexical", "semantic", "hybrid"]


class SearchParams(ProductFilter):
    q: str = Field(min_length=1, max_length=200, pattern=r"\S", examples=["золота каблучка", "prezent dla mamy"])
    mode: SearchMode = "hybrid"
    offset: int = Field(default=0, ge=0, le=1000)


class SearchOut(BaseModel):
    mode_used: SearchMode
    total: int
    items: list[ProductListItem]