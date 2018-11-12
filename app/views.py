from aiohttp import web
from app.services.kafka import produce

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