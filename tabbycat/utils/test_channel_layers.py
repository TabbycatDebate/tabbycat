"""Exercise PostgreSQL delivery across independent sender/receiver processes."""

import asyncio
import json
import os
import subprocess
import sys

from django.conf import settings
from django.db import connection
from django.test import TransactionTestCase


class PostgresChannelLayerTests(TransactionTestCase):

    def test_cross_process_delivery(self):
        if connection.vendor != 'postgresql':
            self.skipTest('PostgreSQL channel layer requires PostgreSQL')
        result = subprocess.run(
            [sys.executable, '-m', 'utils.test_channel_layers'],
            input=json.dumps(connection.settings_dict), text=True, capture_output=True,
            env={**os.environ, 'PYTHONPATH': settings.BASE_DIR}, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


async def _close_pool():
    import channels_postgres.db as db

    if db.connection_pool is not None:
        await db.connection_pool.close()


async def _receive(database, channels):
    from utils.channel_layers import SingleListenerPostgresChannelLayer

    layer = SingleListenerPostgresChannelLayer(**database)

    async def consume(channel):
        while True:
            message = await layer.receive(channel)
            print(json.dumps({'channel': channel, 'message': message}), flush=True)

    tasks = [asyncio.create_task(consume(channel)) for channel in channels]
    await layer._get_listener()
    print(json.dumps({'ready': True}), flush=True)
    await asyncio.gather(*tasks)


async def _start_receiver(database, *channels):
    process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'utils.test_channel_layers', '--receive', *channels,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    process.stdin.write(json.dumps(database).encode())
    await process.stdin.drain()
    process.stdin.close()
    process.messages = []
    while True:
        line = await asyncio.wait_for(process.stdout.readline(), 10)
        if not line:
            raise AssertionError((await process.stderr.read()).decode())
        data = json.loads(line)
        if data.get('ready'):
            return process
        process.messages.append(data)


async def _messages(process, timeout=0.3):
    messages = process.messages[:]
    process.messages.clear()
    deadline = asyncio.get_running_loop().time() + timeout
    while (remaining := deadline - asyncio.get_running_loop().time()) > 0:
        try:
            line = await asyncio.wait_for(process.stdout.readline(), remaining)
        except TimeoutError:
            break
        if not line:
            raise AssertionError((await process.stderr.read()).decode())
        messages.append(json.loads(line))
    return messages


async def _check_delivery(database):
    from utils.channel_layers import SingleListenerPostgresChannelLayer

    layer = SingleListenerPostgresChannelLayer(**database)
    processes = []

    async def start(*channels):
        process = await _start_receiver(database, *channels)
        processes.append(process)
        return process

    async def stop(process):
        process.terminate()
        await process.wait()
        processes.remove(process)

    async def expect(process, expected):
        received = await _messages(process)
        assert [item['message'] for item in received] == expected, received

    try:
        # Three concurrent receives must not duplicate either payload size.
        worker = await start('notifications', 'adjallocation', 'venues')
        for payload in ('short', 'large' * 2000):
            message = {'type': 'test.message', 'payload': payload}
            await layer.send('adjallocation', message)
            await expect(worker, [message])
        await stop(worker)

        # Neither delivered message may be recovered by a restarted worker.
        worker = await start('notifications', 'adjallocation', 'venues')
        await expect(worker, [])
        await stop(worker)

        # An unrelated process must leave queued work for its actual receiver.
        message = {'type': 'test.message', 'payload': 'queued'}
        await layer.send('adjallocation', message)
        web = await start('test.unrelated')
        worker = await start('adjallocation')
        await expect(worker, [message])
        await stop(worker)
        await stop(web)

        # Competing processes must claim each message only once.
        first = await start('test.shared')
        second = await start('test.shared')
        sent = [{'type': 'test.message', 'id': i} for i in range(10)]
        for message in sent:
            await layer.send('test.shared', message)
        received = await asyncio.gather(_messages(first), _messages(second))
        assert sorted(item['message']['id'] for batch in received for item in batch) == list(range(10)), received
        await stop(first)
        await stop(second)

        # Group members in separate processes must each get exactly one copy.
        first = await start('test.first')
        second = await start('test.second')
        await layer.group_add('test.group', 'test.first')
        await layer.group_add('test.group', 'test.second')
        message = {'type': 'test.message', 'payload': 'broadcast'}
        await layer.group_send('test.group', message)
        await asyncio.gather(expect(first, [message]), expect(second, [message]))
        await layer.group_discard('test.group', 'test.first', expire=0)
        await layer.group_send('test.group', message)
        await asyncio.gather(expect(first, []), expect(second, [message]))
    finally:
        for process in processes:
            process.terminate()
        await asyncio.gather(*(process.wait() for process in processes))
        await _close_pool()


if __name__ == '__main__':
    import django

    database = json.loads(sys.stdin.read())
    settings.configure(
        USE_TZ=True,
        DATABASES={'default': database, 'channels_postgres': database},
        INSTALLED_APPS=['channels_postgres'],
    )
    django.setup()
    if sys.argv[1:2] == ['--receive']:
        asyncio.run(_receive(database, sys.argv[2:]))
    else:
        asyncio.run(_check_delivery(database))
