from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def handle(self):
        try:
            super().handle()
        except BrokenPipeError:
            pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), CORSRequestHandler)
    print("CORS server running at http://localhost:8000  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("\nStopped.", flush=True)