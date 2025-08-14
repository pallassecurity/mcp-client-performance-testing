from pathlib import Path
import aiofiles

from mcp.client.auth import TokenStorage
from mcp.shared.auth import OAuthToken, OAuthClientInformationFull


class InMemoryTokenStorage(TokenStorage):
    def __init__(self):
        self.tokens: OAuthToken | None = None
        self.client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self.client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self.client_info = client_info


class FileTokenStorage(TokenStorage):
    def __init__(self, tokens_path: str = ".tokens", info_path: str = ".info"):
        self.tokens_path = Path(tokens_path)
        self.info_path = Path(info_path)

    async def get_tokens(self) -> OAuthToken | None:
        if not self.tokens_path.exists():
            return None

        async with aiofiles.open(self.tokens_path, "r") as f:
            contents = await f.read()
        tokens = OAuthToken.model_validate_json(contents)
        return tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        contents = tokens.model_dump_json()
        async with aiofiles.open(self.tokens_path, "w") as f:
            await f.write(contents)

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        if not self.info_path.exists():
            return None

        async with aiofiles.open(self.info_path, "r") as f:
            contents = await f.read()
        info = OAuthClientInformationFull.model_validate_json(contents)
        return info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        contents = client_info.model_dump_json()
        async with aiofiles.open(self.info_path, "w") as f:
            await f.write(contents)
