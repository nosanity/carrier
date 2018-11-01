from aiohttp import web
from app.service import produce

routes = web.RouteTableDef()

@routes.view('/produce/')
class ProduceView(web.View):

    async def post(self):
        # TODO validate incoming request
        params = await self.request.json()
        await produce(self.request.app, params["topic"], params["payload"])
        
        data = {
            "status": "success",
            "topic": params["topic"],
            "message": params["message"]
        }
        
        return web.json_response(data)