from beanie import Document
from pydantic import HttpUrl, Field, BaseModel
from typing import Literal, Optional
from datetime import datetime


class FieldBase(BaseModel):
    pass

class FooterBase(BaseModel):
    pass

class ImageBase(BaseModel):
    pass

class ThumbBase(BaseModel):
    pass

class VideoBase(BaseModel):
    pass

class ProviderBase(BaseModel):
    pass

class AuthorBase(BaseModel):
    pass

class EmbedBase(Document):
    title: str = Field(default="Default Title", max_length=256)
    type: Literal['rich'] = 'rich'
    description: str = Field(default="Default Description", max_length=4096)
    url: Optional[HttpUrl]
    timestamp: datetime = datetime.now().isoformat()
    color: int = 0
    footer: Optional[FooterBase]
    image: Optional[ImageBase]
    thumbnail: Optional[ThumbBase]
    video: Optional[VideoBase]
    provider: Optional[ProviderBase]
    author: Optional[AuthorBase]
    fields: list[FieldBase] = Field(default_factory=list, max_length=25)