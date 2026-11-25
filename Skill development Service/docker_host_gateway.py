import http.server
import socketserver
import subprocess
import urllib.parse
import sys

PORT = 5178

class ContainerProxyHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {self.command} {self.path} - {args[1]}\n")

    def do_GET(self):
        self._proxy_request('GET')

    def do_POST(self):
        self._proxy_request('POST')

    def do_PATCH(self):
        self._proxy_request('PATCH')

    def do_PUT(self):
        self._proxy_request('PUT')

    def do_DELETE(self):
        self._proxy_request('DELETE')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _proxy_request(self, method):
        # Read request body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        # Pass request via python script inside nagriksetu-skill-backend
        # Note: nagriksetu-skill-frontend has Nginx reverse proxying to skill-backend:8000
        # We can directly invoke python in backend container to make an internal HTTP request to http://skill-frontend or http://127.0.0.1:8000
        # If path starts with /api or /health or /docs, proxy to backend http://127.0.0.1:8000
        # If static asset or /, proxy to http://skill-frontend:80
        target_url = f"http://127.0.0.1:8000{self.path}" if (self.path.startswith('/api') or self.path.startswith('/health') or self.path.startswith('/docs') or self.path.startswith('/openapi.json')) else f"http://skill-frontend:80{self.path}"

        # Build python script for container
        script = f"""
import urllib.request, sys
headers = {{k: v for k, v in {dict(self.headers)}.items() if k.lower() not in ('host', 'content-length')}}
req = urllib.request.Request({repr(target_url)}, data=sys.stdin.buffer.read() if {len(body)} > 0 else None, headers=headers, method={repr(method)})
try:
    with urllib.request.urlopen(req) as resp:
        sys.stdout.buffer.write(str(resp.status).encode() + b'\\n')
        for k, v in resp.getheaders():
            if k.lower() not in ('transfer-encoding', 'connection'):
                sys.stdout.buffer.write(f'{{k}}: {{v}}\\n'.encode())
        sys.stdout.buffer.write(b'\\n')
        sys.stdout.buffer.write(resp.read())
except urllib.error.HTTPError as e:
    sys.stdout.buffer.write(str(e.code).encode() + b'\\n')
    for k, v in e.headers.items():
        if k.lower() not in ('transfer-encoding', 'connection'):
            sys.stdout.buffer.write(f'{{k}}: {{v}}\\n'.encode())
    sys.stdout.buffer.write(b'\\n')
    sys.stdout.buffer.write(e.read())
except Exception as e:
    sys.stdout.buffer.write(b'502\\n\\n' + str(e).encode())
"""
        proc = subprocess.Popen(
            ['docker', 'exec', '-i', 'nagriksetu-skill-backend', 'python', '-c', script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=body)
        
        parts = stdout.split(b'\n\n', 1)
        if len(parts) >= 2:
            header_lines = parts[0].split(b'\n')
            status_code = int(header_lines[0].decode('latin1').strip())
            resp_body = parts[1]
            self.send_response(status_code)
            for hl in header_lines[1:]:
                if b':' in hl:
                    k, v = hl.decode('latin1').split(':', 1)
                    if k.strip().lower() not in ('transfer-encoding', 'content-length', 'connection'):
                        self.send_header(k.strip(), v.strip())
            self.send_header('Content-Length', str(len(resp_body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resp_body)
        else:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(stdout or stderr or b'Gateway Error')

if __name__ == '__main__':
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), ContainerProxyHandler) as httpd:
        print(f"Container Gateway running on http://127.0.0.1:{PORT}")
        httpd.serve_forever()
