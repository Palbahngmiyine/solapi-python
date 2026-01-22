from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel

from solapi.model.kakao.bms.bms_button import BmsButton
from solapi.model.kakao.bms.bms_carousel import (
    BmsCarouselCommerceSchema,
    BmsCarouselFeedSchema,
)
from solapi.model.kakao.bms.bms_commerce import BmsCommerce
from solapi.model.kakao.bms.bms_coupon import BmsCoupon
from solapi.model.kakao.bms.bms_option import (
    BMS_REQUIRED_FIELDS,
    WIDE_ITEM_LIST_MIN_SUB_ITEMS,
    BmsChatBubbleType,
    _to_camel,
)
from solapi.model.kakao.bms.bms_video import BmsVideo
from solapi.model.kakao.bms.bms_wide_item import BmsMainWideItem, BmsSubWideItem


class Bms(BaseModel):
    targeting: Optional[Literal["I", "M", "N"]] = None
    chat_bubble_type: Optional[BmsChatBubbleType] = None

    adult: Optional[bool] = None
    header: Optional[str] = None
    image_id: Optional[str] = None
    image_link: Optional[str] = None
    additional_content: Optional[str] = None
    content: Optional[str] = None

    carousel: Optional[Union[BmsCarouselFeedSchema, BmsCarouselCommerceSchema]] = None
    main_wide_item: Optional[BmsMainWideItem] = None
    sub_wide_item_list: Optional[list[BmsSubWideItem]] = None
    buttons: Optional[list[BmsButton]] = None
    coupon: Optional[BmsCoupon] = None
    commerce: Optional[BmsCommerce] = None
    video: Optional[BmsVideo] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_required_fields(self) -> "Bms":
        chat_bubble_type = self.chat_bubble_type
        if chat_bubble_type is None:
            return self

        required_fields = BMS_REQUIRED_FIELDS.get(chat_bubble_type, [])
        missing_fields = [
            field for field in required_fields if getattr(self, field, None) is None
        ]

        if missing_fields:
            camel_fields = [_to_camel(f) for f in missing_fields]
            raise ValueError(
                f"BMS {chat_bubble_type} 타입에 필수 필드가 누락되었습니다: "
                f"{', '.join(camel_fields)}"
            )

        if chat_bubble_type == "WIDE_ITEM_LIST":
            sub_wide_item_list = self.sub_wide_item_list
            if (
                not sub_wide_item_list
                or len(sub_wide_item_list) < WIDE_ITEM_LIST_MIN_SUB_ITEMS
            ):
                raise ValueError(
                    f"WIDE_ITEM_LIST 타입의 subWideItemList는 최소 "
                    f"{WIDE_ITEM_LIST_MIN_SUB_ITEMS}개 이상이어야 합니다. "
                    f"현재: {len(sub_wide_item_list) if sub_wide_item_list else 0}개"
                )

        return self
