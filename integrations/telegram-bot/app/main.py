from __future__ import annotations

import logging

from app.bot import build_application
from app.config import load_settings


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=logging.INFO,
    )
    settings = load_settings()
    application = build_application(settings)
    application.run_polling()


if __name__ == "__main__":
    main()
