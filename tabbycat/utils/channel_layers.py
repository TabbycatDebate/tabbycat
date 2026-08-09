"""Tabbycat-specific channel layer backends."""

import asyncio
from weakref import WeakValueDictionary

import psycopg
from channels_postgres.core import PostgresChannelLayer


class SingleListenerPostgresChannelLayer(PostgresChannelLayer):
    """Wake receivers with LISTEN, then atomically claim their channel's rows."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listeners = {}

    async def _listen(self, ready, channel_events):
        try:
            async with await psycopg.AsyncConnection.connect(**self.db_params, autocommit=True) as connection:
                await connection.execute('LISTEN channels_postgres_messages')
                ready.set()
                async for notification in connection.notifies():
                    channel = notification.payload.split(':', 2)[1]
                    if channel in channel_events:
                        channel_events[channel].set()
        finally:
            ready.set()
            for event in channel_events.values():
                event.set()

    async def _get_listener(self):
        loop = asyncio.get_running_loop()
        state = self._listeners.get(loop)
        if state is None or state[0].done():
            ready = asyncio.Event()
            channel_events = WeakValueDictionary()
            task = asyncio.create_task(self._listen(ready, channel_events))
            state = task, ready, channel_events
            self._listeners[loop] = state

            def cleanup(finished):
                if self._listeners.get(loop, (None,))[0] is finished:
                    del self._listeners[loop]
                if not finished.cancelled():
                    finished.exception()

            task.add_done_callback(cleanup)

        task, ready, channel_events = state
        await ready.wait()
        if task.done():
            await task
            raise ConnectionError('PostgreSQL channel listener stopped')
        return task, channel_events

    async def receive(self, channel):
        self.require_valid_channel_name(channel)
        listener, channel_events = await self._get_listener()
        event = channel_events.setdefault(channel, asyncio.Event())
        while True:
            if listener.done():
                await listener
                raise ConnectionError('PostgreSQL channel listener stopped')

            # Listen before checking the database, and clear before the query,
            # so inserts during either step cannot leave a receiver asleep.
            event.clear()
            message = await self.django_db.retrieve_non_expired_queued_message_from_channel(channel)
            if message is not None:
                return self.deserialize(message[0])
            await event.wait()
