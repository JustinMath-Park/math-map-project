import http.server
import socketserver
import threading
import os
import time
import subprocess
import sys

# Configuration
APPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps')
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
MVP_TEST_DIR = os.path.join(APPS_DIR, 'mvp-test')
LEVEL_TEST_DIR = os.path.join(APPS_DIR, 'level-test')

MVP_PORT = 8011
LEVEL_PORT = 8012
ADAPTIVE_PORT = 8013

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

def run_server(directory, port, name):
    os.chdir(directory)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"🚀 {name} running at: http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()

def main():
    print("Starting local development servers...")
    print("Press Ctrl+C to stop all servers.\n")

    # Create threads for each server
    mvp_thread = threading.Thread(target=run_server, args=(MVP_TEST_DIR, MVP_PORT, "MVP Test (No Auth)"))
    level_thread = threading.Thread(target=run_server, args=(LEVEL_TEST_DIR, LEVEL_PORT, "Level Test (Auth)"))
    adaptive_thread = threading.Thread(target=run_server, args=(os.path.join(APPS_DIR, 'adaptive-test'), ADAPTIVE_PORT, "Adaptive Test (New)"))

    # Daemonize threads so they exit when main thread exits
    mvp_thread.daemon = True
    level_thread.daemon = True
    adaptive_thread.daemon = True

    # Start threads
    mvp_thread.start()
    level_thread.start()
    adaptive_thread.start()

    # Start Backend (Flask)
    print("🚀 Backend API running at: http://localhost:5001")
    backend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=BACKEND_DIR,
        env=os.environ.copy()
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        backend_process.terminate()
        backend_process.wait()

if __name__ == "__main__":
    main()
