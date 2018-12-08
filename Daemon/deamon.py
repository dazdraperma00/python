import asyncio
import aiofiles
from aiohttp import web
import aiohttp
import yaml


class Daemon:
    def __init__(self, path):
        config = Daemon.get_config(path)

        self.port = config['port']
        self.dir = config['directory']
        self.nodes = config['nodes']
        self.save = config['save']

    @staticmethod
    def get_config(path):
        with open(path) as f:
            config = yaml.load(f)
        return config

    def start(self):
        app = web.Application()
        app.add_routes([
            web.get('/{name}', self.handle_client),
            web.get('/check/{name}', self.handle_daemon)
        ])

        # Создаем сессию один раз и навсегда
        loop = asyncio.get_event_loop()
        loop.create_task(self.create_session())

        web.run_app(app, port=self.port)

    async def create_session(self):
        # Запускаем сервер
        self.session = aiohttp.ClientSession()

    async def handle_client(self, request):
        name = request.match_info.get('name')
        text = await self.reader(name)

        if text:
            return web.Response(text=text)
        else:
            text = await self.send_requests(name)

        if not text:
            raise aiohttp.web.HTTPNotFound()

        if self.save:
            print("Записываем текст в файл")
            await self.writer(name, text)

        return web.Response(text=text)

    async def handle_daemon(self, request):
        name = request.match_info.get('name')

        text = await self.reader(name)
        if not text:
            raise aiohttp.web.HTTPNotFound()

        return web.Response(text=text)

    async def send_requests(self, name):
        text = ''
        futures = [self.session.get(f"http://{node['host']}:{node['port']}/check/{name}")
                   for node in self.nodes
                   ]
        for f in asyncio.as_completed(futures):
            response = await f
            if response.status == 200:
                text = await response.text()
                break

        return text

    async def reader(self, name):
        try:
            async with aiofiles.open(self.dir + name) as f:
                text = await f.read()
        except FileNotFoundError:
            return ''
        return text

    async def writer(self, name, text):
        async with aiofiles.open(self.dir + name, 'w') as f:
            await f.write(text)
