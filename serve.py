import http.server
import socketserver
import os
import urllib.parse
import mimetypes
import gzip
import io
import sys

PORT = 3000
DIRECTORY = os.path.abspath("./clone")
RSC_CACHE = os.path.join(DIRECTORY, "_rsc_cache")

# Pre-register critical web MIME types
mimetypes.add_type("application/font-woff2", ".woff2")
mimetypes.add_type("application/font-woff", ".woff")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("text/x-component", ".rsc")
mimetypes.add_type("application/json", ".json")

# Security: Allowed file extensions for static serving
ALLOWED_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".woff2", ".woff", ".ttf",
    ".jpg", ".jpeg", ".png", ".webp", ".svg", ".ico", ".mp4",
    ".webm", ".rsc", ".txt", ".xml"
}

def is_safe_path(base_dir, path):
    """
    Prevents Directory Traversal attacks (Path Traversal / LFI)
    by ensuring the resolved canonical path is strictly inside base_dir.
    """
    try:
        resolved_path = os.path.abspath(os.path.join(base_dir, path.lstrip("/\\")))
        common = os.path.commonpath([base_dir, resolved_path])
        return common == base_dir, resolved_path
    except Exception:
        return False, None

class SecurePuppyHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "TeddyPupsSecureGateway/1.0"
    sys_version = ""  # Hide Python runtime version from response headers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_security_headers(self):
        """Add modern HTTP security headers to protect clients"""
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")

    def end_headers(self):
        self.send_security_headers()
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests gracefully"""
        self.send_response(204)
        self.send_security_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type, RSC, Next-Router-State-Tree")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = urllib.parse.unquote(parsed.path)

        # 1. Sanitize & Prevent Directory Traversal
        is_safe, full_local_path = is_safe_path(DIRECTORY, clean_path)
        if not is_safe:
            self.send_error(403, "Access Denied: Path Traversal Detected")
            return

        # 2. Fix accidental trailing slash on media/asset requests (.jpg/, .png/, etc.)
        if clean_path.endswith((".jpg/", ".jpeg/", ".png/", ".webp/", ".mp4/", ".svg/", ".css/", ".js/")):
            self.send_response(301)
            self.send_header("Location", clean_path.rstrip("/"))
            self.end_headers()
            return

        # 3. Handle Next.js Image Optimization endpoint redirects
        if clean_path.startswith("/_next/image"):
            query = urllib.parse.parse_qs(parsed.query)
            if "url" in query:
                target_url = urllib.parse.unquote(query["url"][0]).rstrip("/")
                # Validate redirect target is strictly internal
                if target_url.startswith(("/", "media/", "brand/")):
                    self.send_response(302)
                    self.send_header("Location", target_url)
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.end_headers()
                    return
                else:
                    self.send_error(400, "Invalid image URL redirection target")
                    return

        # 4. Handle Next.js RSC Flight requests (Client-side fast navigation)
        is_rsc = "RSC" in self.headers or "_rsc" in parsed.query
        if is_rsc:
            route_key = clean_path.strip("/").replace("/", "__")
            if not route_key:
                route_key = "home"
            rsc_file = os.path.join(RSC_CACHE, route_key + ".rsc")
            if os.path.exists(rsc_file):
                try:
                    with open(rsc_file, "rb") as fp:
                        data = fp.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/x-component; charset=utf-8")
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Cache-Control", "public, max-age=3600")
                    self.end_headers()
                    if not head_only:
                        self.wfile.write(data)
                    return
                except Exception as e:
                    pass

        # 5. Clean Route Handling without .html suffix
        _, ext = os.path.splitext(clean_path.rstrip("/"))
        if not ext:
            if not os.path.exists(full_local_path):
                if os.path.exists(full_local_path + ".html"):
                    self.path = clean_path + ".html"
                elif os.path.exists(os.path.join(full_local_path, "index.html")):
                    self.path = clean_path.rstrip("/") + "/index.html"
        else:
            # Enforce allowed extensions whitelist
            if ext.lower() not in ALLOWED_EXTENSIONS:
                self.send_error(403, "Forbidden file type")
                return

        return super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SecurePuppyHandler) as httpd:
        print("="*60)
        print(f"  TeddyPups Production-Ready Server Active")
        print(f"  Local Gateway: http://localhost:{PORT}")
        print(f"  Security Features: Path Traversal Guard, Safe MIME Type Enforcement,")
        print(f"  CORS & Strict Header Injection, RSC Flight Stream Router")
        print("="*60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server cleanly...")
            sys.exit(0)
