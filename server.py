import json
import http.server
import socketserver
import subprocess, os
import threading, time

class SBHandler(http.server.BaseHTTPRequestHandler):
    request_count = 0

    def do_POST(self):
        if self.path == '/contest/to_start':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response2 = json.dumps(
                {
                    'statusCode': 0,
                    'message': "启动成功",
                },
                ensure_ascii=False
            )
            self.wfile.write(response2.encode())
            SBHandler.request_count += 1
            if SBHandler.request_count == 1:
                print("start_inference............")
                threading.Thread(target=self.run_command).start()

    def run_command(self):
        cmd = 'bash run.sh'
        # process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        os.system(cmd)
        self.shutdown_server()

    def shutdown_server(self):
        time.sleep(1)  # 等待一段时间后关闭服务
        self.server.shutdown()

address = ('0.0.0.0', 28888)
httpd = http.server.HTTPServer(address, SBHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
