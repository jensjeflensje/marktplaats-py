from dataclasses import dataclass


@dataclass
class ListingImage:
    extra_small: str
    medium: str
    large: str
    extra_large: str

    @classmethod
    def parse(cls, data):
        if data is None:
            return []
        images = []
        for image_data in data:
            images.append(cls(
                image_data["extraSmallUrl"],
                image_data["mediumUrl"],
                image_data["largeUrl"],
                image_data["extraExtraLargeUrl"],
            ))
        return images
