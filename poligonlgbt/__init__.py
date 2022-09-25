import aiohttp
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Union, BinaryIO
from .magic import get_extension

@dataclass
class Image:
    name: str
    size: int
    time: datetime

    def __str__(self) -> str:
        return Poligon.URL + self.name

class Poligon:
    URL = "https://poligon.lgbt/"
    API_URL = URL + "/api"

    async def __new__(cls, *args):
        instance = super().__new__(cls)
        await instance.__init__(*args)
        return instance

    async def __init__(self, api_key: str, upload_key: str):
        self.session = aiohttp.ClientSession()

        self.api_key = api_key
        self.upload_key = upload_key

        self.images = []

        async with self._me("/files") as response:
            data = await response.json()

            for image in data:
                self.images.append(Image(
                    name = image["name"],
                    size = image["size"],
                    time = datetime.fromtimestamp(image["time"])
                ))

    def _me(self, url: str) -> aiohttp.client._RequestContextManager:
        return self.session.get(self.API_URL + "/@me" + url, headers={"authorization": self.api_key})

    def _upload(self, content: bytes, *, filename: str = None) -> aiohttp.client._RequestContextManager:
        filename = filename or "unknown." + get_extension(content)
        print(filename)

        form = aiohttp.FormData()
        form.add_field("file", content, filename=filename)

        return self.session.post(self.API_URL + "/upload", headers={"authorization": self.upload_key}, data=form)

    def _delete(self, image: Image) -> aiohttp.client._RequestContextManager:
        return self.session.delete(self.API_URL + "/file/" + image.name, headers={"authorization": self.upload_key})

    async def upload(self, image: Union[str, bytes, BinaryIO], *, filename: str = None) -> Image:
        if isinstance(image, str):
            image = open(image, "rb")
        elif isinstance(image, bytes):
            image = BytesIO(image)

        content = image.read()
        image.close()

        async with self._upload(content, filename=filename) as response:
            data = await response.json()

            image = Image(
                name = data["name"],
                size = len(content),
                time = datetime.now()
            )

            self.images.append(image)

        return image

    async def delete(self, image: Image) -> None:
        with self._delete(image) as response:
            if response.status == 204:
                return self.images.remove(image)

        raise Exception("Image not found")

    async def close(self):
        await self.session.close()