from datetime import datetime

from aiohttp import web
from sentry_sdk import capture_message

from app.services.kafka import produce, check_produce

routes = web.RouteTableDef()

@routes.view('/produce/')
class ProduceView(web.View):

    async def post(self):

        if 'Authorization' in self.request.headers and \
            self.request.headers['Authorization'] == self.request.app["config"]["token"]:

            try: 
                params = await self.request.json()
            except ValueError:
                return web.HTTPBadRequest()

            if "topic" not in params or "payload" not in params:
                return web.HTTPBadRequest()
            if params["topic"] not in self.request.app["config"]["kafka"]["topics"]:
                return web.HTTPBadRequest()

            await produce(self.request.app, params["topic"], params["payload"])

            return web.HTTPOk()
        else:
            return web.HTTPUnauthorized()


@routes.view('/proxy/')
class ProxyView(web.View):

    async def post(self):
        header = self.request.headers.get('Authorization', '')
        splitted_header = header.split()
        if not header or len(splitted_header) != 2 or splitted_header[0] != 'Bearer' or \
                splitted_header[1] != self.request.app["config"]["token"]:
            return web.HTTPUnauthorized()

        topic = self.request.headers.get('X-Kafka-Topic', '')
        if not topic:
            capture_message("Request without X-Kafka-Topic header.", level="warning")
            return web.HTTPBadRequest(text='"X-Kafka-Topic" header is required.')

        try:
            data = await self.request.json()
        except ValueError:
            return web.HTTPBadRequest(text='Body must be valid JSON.')

        id_ = data.get('id', None)
        if not id_:
            return web.HTTPBadRequest(text='"id" is required parameter.')

        stored = data.get('stored', None)
        try:
            stored_dt = datetime.strptime(stored, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return web.HTTPBadRequest(text='"stored" must be datetime string '
                                           'in "%Y-%m-%dT%H:%M:%S%.fZ" format."')
        except TypeError:
            return web.HTTPBadRequest(text='"stored" is required.')

        authority = data.get('authority', None)
        if not authority:
            return web.HTTPBadRequest(text='"authority" is required parameter.')

        payload = {
            "action": "create",
            "timestamp": stored_dt.isoformat(),
            "source": "lrs",
            "type": "create",
            "id":
                {"id": id_, 'authority': authority}
            ,
            "title": ""
        }
        await produce(self.request.app, topic, payload)
        return web.HTTPOk()


@routes.view('/api/check/')
class CheckProduceView(web.View):
    async def post(self):
        if 'Authorization' in self.request.headers and \
            self.request.headers['Authorization'] == self.request.app["config"]["token"]:

            res = await check_produce(self.request.app)
            if res:
                return web.HTTPOk(body=str(res))
            return web.HTTPGatewayTimeout()
        else:
            return web.HTTPUnauthorized()
