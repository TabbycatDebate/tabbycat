"""Tabbycat-specific channel layer backends."""

from channels_postgres.core import PostgresChannelLayer


class SingleListenerPostgresChannelLayer(PostgresChannelLayer):
    """Prevent concurrent receives from starting duplicate LISTEN tasks.

    ``runworker`` starts one receive coroutine per named channel. The upstream
    Postgres layer doesn't mark its listener as started until its asynchronous
    setup completes, so all of those coroutines can start a listener in the
    meantime. Every listener then queues the same PostgreSQL notification.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listener_task_starting = False

    def _get_or_create_listener_task(self):
        listener_ready, should_start = super()._get_or_create_listener_task()
        if not should_start:
            return listener_ready, False
        if self._listener_task_starting:
            return listener_ready, False

        # Set this synchronously, before control returns to the event loop and
        # another channel's receive coroutine can reach this method.
        self._listener_task_starting = True
        return listener_ready, True

    async def listen_to_all_channels(self):
        try:
            await super().listen_to_all_channels()
        finally:
            # Permit a later receive to restart a listener that exits.
            self._listener_task_starting = False
