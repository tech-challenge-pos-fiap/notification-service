import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app import main as app_main


class TestMain:
    @pytest.mark.asyncio
    async def test_main_runs_consumer_forever(self):
        consumer = MagicMock()
        consumer.run_forever = AsyncMock()

        with patch("app.main.configure_logging") as configure_logging_mock, patch(
            "app.main.build_container", return_value={"consumer": consumer}
        ) as build_container_mock:
            await app_main.main()

        configure_logging_mock.assert_called_once()
        build_container_mock.assert_called_once()
        consumer.run_forever.assert_awaited_once()

    def test_module_main_handles_keyboard_interrupt(self, monkeypatch):
        def fake_run(coro):
            coro.close()
            raise KeyboardInterrupt()

        monkeypatch.setattr("asyncio.run", fake_run)
        app_main.run()

    def test_module_main_reraises_unexpected_exception(self, monkeypatch):
        def fake_run(coro):
            coro.close()
            raise Exception("fatal")

        monkeypatch.setattr("asyncio.run", fake_run)

        with pytest.raises(Exception, match="fatal"):
            app_main.run()
