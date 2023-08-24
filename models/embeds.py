from beanie import Document
from pydantic import HttpUrl, Field, BaseModel, model_validator, field_serializer
from typing import Literal, Optional, Any, Union
from datetime import datetime


class FieldBase(BaseModel):
    name: str
    value: str
    inline: bool = False


class FooterBase(BaseModel):
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


class ImageBase(BaseModel):
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class ThumbBase(BaseModel):
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class VideoBase(BaseModel):
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class ProviderBase(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class AuthorBase(BaseModel):
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


def datetime_to_str(v: datetime):
    return v.isoformat()

class EmbedBase(Document):
    title: str = Field(default="Default Title", max_length=256)
    type: Literal["rich"] = "rich"
    description: str = Field(default="Default Description", max_length=4096)
    url: Optional[str] = None
    timestamp: Union[datetime, str, None] = datetime.now()
    color: int
    footer: Optional[FooterBase] = None
    image: Optional[ImageBase] = None
    thumbnail: Optional[ThumbBase] = None
    video: Optional[VideoBase] = None
    provider: Optional[ProviderBase] = None
    author: Optional[AuthorBase] = None
    fields: list[Optional[FieldBase]] = Field(default_factory=list)



    class Settings:
        bson_encoders = {
          datetime: datetime_to_str
        }
    #
    # @field_serializer('timestamp')
    # def time_changer(self, timestamp: datetime, _info):
    #     return timestamp.isoformat()

    @model_validator(mode='before')
    @classmethod
    def convert_color(cls, data: Any):
        try:
            if isinstance(data, dict):
                if 'color' in data:
                    if not isinstance(p := data.get('color'), int):
                        data.update({'color': int(p.replace('#', ''), 16)})
            return data
        except ValueError:
            raise ValueError

    # @model_validator(mode='before')
    # @classmethod
    # def convert_subthings(cls, data: Any):
    #     try:
    #         if isinstance(data, dict):
    #             if 'footer' in data and data.get('footer'):
    #                 data.update({'footer': FooterBase(**data.get('footer'))})
    #             if 'thumbnail' in data:
    #                 data.update({'thumbnail': ThumbBase(**data.get('thumbnail'))})
    #             if 'image' in data:
    #                 data.update({'image': ImageBase(**data.get('image'))})
    #             if 'video' in data and data.get('video'):
    #                 data.update({'video': VideoBase(**data.get('video'))})
    #             if 'provider' in data and data.get('provider'):
    #                 data.update({'provider': ProviderBase(**data.get('provider'))})
    #             if 'author' in data and data.get('author'):
    #                 data.update({'author': AuthorBase(**data.get('author'))})
    #             if 'fields' in data:
    #                 f = []
    #                 for field in data.get('fields'):
    #                     f.append(FieldBase(**field))
    #             return data
    #     except ValueError:
    #         raise ValueError
