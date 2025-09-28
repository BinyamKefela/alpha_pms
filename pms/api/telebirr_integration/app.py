from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import json
from config import env
from service import createOrderService
from service import applyFabricTokenService
enviroment = env.ENV_VARIABLES
token = applyFabricTokenService.ApplyFabricTokenService(enviroment["baseUrl"],enviroment["fabricAppId"],enviroment["appSecret"],enviroment["merchantAppId"])
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json"),
            self.send_header("Access-Control-Allow-Origin"," *"),
            self.send_header("Access-Control-Allow-Methods", "*"),
            self.send_header("Access-Control-Allow-Methods", "PUT, GET,DELETE, POST,OPTIONS"),
            self.send_header("Access-Control-Allow-Headers"," Origin, X-Requested-With, Content-Type, Accept")
            self.end_headers()
            self.wfile.write(b'WELCOME TO API SERVER!')
        else:
            self.send_error(404)
    def do_POST(self):
        if self.path == "/create/order":
            self
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            requestParam= json.loads(body.decode('utf-8'))
            self.send_response(200)
            self.send_header("Content-type", "application/json"),
            self.send_header("Access-Control-Allow-Origin"," *"),
            self.send_header("Access-Control-Allow-Methods", "*"),
            self.send_header("Access-Control-Allow-Methods", "PUT, GET,DELETE, POST,OPTIONS"),
            self.send_header("Access-Control-Allow-Headers"," Origin, X-Requested-With, Content-Type, Accept")
            self.end_headers()
            response = BytesIO()
            module = createOrderService.CreateOrderService(requestParam,enviroment["baseUrl"],enviroment["fabricAppId"],enviroment["appSecret"],enviroment["merchantAppId"],enviroment["merchantCode"])
            order = module.createOrder()
            response.write(bytes(order,'utf-8'))
            self.wfile.write(response.getvalue())
            return order
        elif self.path == "/auth/token":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.send_header("Content-type", "application/json"),
            self.send_header("Access-Control-Allow-Origin"," *"),
            self.send_header("Access-Control-Allow-Methods", "*"),
            self.send_header("Access-Control-Allow-Methods", "PUT, GET,DELETE, POST,OPTIONS"),
            self.send_header("Access-Control-Allow-Headers"," Origin, X-Requested-With, Content-Type, Accept")
            self.end_headers()
            token.applyFabricToken()
            response = BytesIO()
            response.write(b'AUTH TOKEN SERVICE')
            response.write(body)
            self.wfile.write(response.getvalue())
        else:
            self.send_error(404)



print("Server started http://localhost:8080")
httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
httpd.serve_forever()