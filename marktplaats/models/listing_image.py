class ListingImage:
    def __init__(self, extra_small, medium, large, extra_large):
        self.extra_small = extra_small
        self.medium = medium
        self.large = large
        self.extra_large = extra_large

    @classmethod
    def parse_images(cls, data):
        images = []
        for image_data in data:
            images.append(cls(
                image_data["extraSmallUrl"],
                image_data["mediumUrl"],
                image_data["largeUrl"],
                image_data["extraExtraLargeUrl"],
            ))
        return images
