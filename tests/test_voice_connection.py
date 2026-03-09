import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("ID_CHANNEL", "1")
os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("URL", "https://example.com")

import bot  # noqa: E402


class ConnectVoiceSafelyTests(unittest.IsolatedAsyncioTestCase):
    async def test_connects_with_reconnect_enabled_when_not_connected(self):
        expected_voice_client = object()
        channel = SimpleNamespace(connect=AsyncMock(return_value=expected_voice_client))
        ctx = SimpleNamespace(guild=SimpleNamespace(voice_client=None))

        result = await bot.connect_voice_safely(ctx, channel)

        self.assertIs(result, expected_voice_client)
        channel.connect.assert_awaited_once_with(
            timeout=15,
            reconnect=True,
            self_deaf=True,
        )

    async def test_moves_existing_connection_instead_of_reconnecting(self):
        target_channel = object()
        voice_client = SimpleNamespace()
        voice_client.channel = object()
        voice_client.is_connected = Mock(return_value=True)
        voice_client.is_playing = Mock(return_value=False)

        async def move_to(channel, timeout=15):
            voice_client.channel = channel

        voice_client.move_to = AsyncMock(side_effect=move_to)

        ctx = SimpleNamespace(guild=SimpleNamespace(voice_client=voice_client))
        channel = SimpleNamespace(connect=AsyncMock())

        result = await bot.connect_voice_safely(ctx, target_channel)

        self.assertIs(result, voice_client)
        voice_client.move_to.assert_awaited_once_with(target_channel, timeout=15)
        channel.connect.assert_not_awaited()

    async def test_reports_incompatible_voice_dependency_versions(self):
        with patch.object(bot, "is_voice_library_compatible", return_value=False):
            self.assertIsNotNone(bot.get_voice_dependency_issue())


if __name__ == "__main__":
    unittest.main()
