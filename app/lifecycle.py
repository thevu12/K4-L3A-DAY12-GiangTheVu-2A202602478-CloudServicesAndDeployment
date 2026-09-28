"""Theo dõi SIGTERM/SIGINT để service ngừng nhận traffic trước khi thoát."""

from __future__ import annotations

import signal


class Lifecycle:
    """Giữ trạng thái vòng đời của process."""

    def __init__(self) -> None:
        self.shutting_down = False
        # Handler trước đó, thường là của Uvicorn.
        self._previous: dict = {}

    def request_shutdown(self, signum=None, frame=None) -> None:
        """Bật cờ shutdown và chuyển tiếp signal cho handler cũ.

        Mỗi signal chỉ có một handler; không thực hiện I/O tại đây.
        """
        self.shutting_down = True
        previous = self._previous.get(signum)
        if callable(previous):
            previous(signum, frame)

    def install(self) -> None:
        """Đăng ký handler cho SIGTERM và SIGINT một cách idempotent."""
        self.shutting_down = False
        for sig in (signal.SIGTERM, signal.SIGINT):
            current = signal.getsignal(sig)
            if current == self.request_shutdown:
                continue
            self._previous[sig] = current
            signal.signal(sig, self.request_shutdown)


lifecycle = Lifecycle()
