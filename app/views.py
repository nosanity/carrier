from aiohttp import web
from app.service import produce

routes = web.RouteTableDef()

@routes.view('/produce/')
class ProduceView(web.View):

    async def post(self):
        params = await self.request.json()
        await produce(self.request.app.loop, params["message"])
        
        data = {
            "status": "success",
            "message": "message was sent successfully"
        }
        
        return web.json_response(data)