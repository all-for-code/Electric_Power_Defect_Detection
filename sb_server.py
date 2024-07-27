import json
import http.server
import socketserver



class SBHandler(http.server.BaseHTTPRequestHandler):
    
    def do_POST(self):
        # content_length = int(self.headers['Content-Length'])
        # req_body = self.rfile.read(int(self.headers['Content-Length']))
        # data = json.loads(req_body)

        # self.send_response(200)
        # self.send_header('Content-Type', 'application/json')
        # self.end_headers()

        # response = {'message': f"{data['name']}, {data['age']}"}
        # self.wfile.write(json.dumps(response).encode())
    

        # print("***********************")
        if self.path == '/pcr/contest/submit_result':
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(req_body)
            print(f"checkoutNum:{data['checkoutNum']}")
            print(f"isEnd:{data['isEnd']}")
            for result in data['results']:
                print(result)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response1 = json.dumps(
                {
                    'statusCode': 0,
                    'message': "成功",
                },
                ensure_ascii=False
            )
            
            self.wfile.write(response1.encode())

        elif self.path == '/pcr/contest/submit_state':
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(req_body)
            print(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response2 = json.dumps(
                {
                    'statusCode': 0,
                    'message': "成功",
                },
                ensure_ascii=False
            )
            
            self.wfile.write(response2.encode())
        
        elif self.path == '/pcr/contest/to_start':
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(req_body)
            print(data)
            print("start_inference............")
            cmd = 'bash run.sh'
            # subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.system(cmd)
        


# ip = 'localhost'
address = ('localhost', 8080)

#address = f'http://{ip}:{port}/pcr/contest/submit_result'
# address = ("", port)
httpd = http.server.HTTPServer(address, SBHandler)
httpd.serve_forever()


