from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import sqlite3
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import unquote

from pypdf import PdfReader


OPENAI_URL = "https://api.openai.com/v1/responses"
DB_PATH = Path(__file__).with_name("pbl_create.db")
def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """
        )


class AppHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._send_json({"status": "ok"}, 200)
            return
        if self.path == "/api/courses":
            with sqlite3.connect(DB_PATH) as connection:
                rows = connection.execute("SELECT id, name FROM courses ORDER BY name").fetchall()
            self._send_json({"courses": [{"id": row[0], "name": row[1]} for row in rows]}, 200)
            return
        if self.path == "/api/materials":
            with sqlite3.connect(DB_PATH) as connection:
                rows = connection.execute("SELECT id, name FROM materials ORDER BY name").fetchall()
            self._send_json({"materials": [{"id": row[0], "name": row[1]} for row in rows]}, 200)
            return
        self.send_error(404, "Not found")

    def do_POST(self):
        if self.path in ("/api/courses", "/api/materials"):
            self._create_record(self.path.rsplit("/", 1)[-1])
            return
        if self.path == "/api/extract-text":
            self._extract_text()
            return

        if self.path != "/api/openai":
            self.send_error(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            api_key = payload.pop("apiKey", "").strip()

            if not api_key:
                self._send_json({"error": "API key is required."}, 400)
                return

            request = urllib.request.Request(
                OPENAI_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=90) as response:
                body = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as error:
            body = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as error:
            self._send_json({"error": str(error)}, 500)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _create_record(self, record_type):
        try:
            payload = self._read_json()
            name = str(payload.get("name", "")).strip()
            if not name:
                self._send_json({"error": "名前を入力してください。"}, 400)
                return
            table = "courses" if record_type == "courses" else "materials"
            with sqlite3.connect(DB_PATH) as connection:
                connection.execute(
                    f"INSERT INTO {table}(name) VALUES (?)", (name,)
                )
            self._send_json({"name": name}, 201)
        except sqlite3.IntegrityError:
            self._send_json({"error": "同じ名前がすでに登録されています。"}, 409)
        except Exception as error:
            self._send_json({"error": str(error)}, 400)

    def _extract_text(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            file_name = unquote(self.headers.get("X-File-Name", "uploaded-file"))
            file_type = self.headers.get("X-File-Type", "")
            data = self.rfile.read(length)

            text = ""
            try:
                import tempfile
                import os
                from pathlib import Path
                import class_materials_compiler as cmc

                suffix = Path(file_name).suffix
                # Create a temporary file in the current directory (workspace)
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=".") as temp_file:
                    temp_file.write(data)
                    temp_file_path = Path(temp_file.name)

                try:
                    text = cmc.extract_text(temp_file_path, "jpn+eng")
                finally:
                    if temp_file_path.exists():
                        os.unlink(temp_file_path)
            except Exception as e:
                print(f"Compiler-based extraction failed, falling back: {e}")

            if not text.strip():
                if file_name.lower().endswith(".pdf") or file_type == "application/pdf":
                    text = self._extract_pdf_text(data)
                else:
                    text = self._decode_text(data)

            if not text.strip():
                self._send_json({"error": "ファイルからテキストを抽出できませんでした。"}, 422)
                return

            self._send_json({"fileName": file_name, "text": text}, 200)
        except Exception as error:
            self._send_json({"error": str(error)}, 500)

    def _extract_pdf_text(self, data):
        reader = PdfReader(BytesIO(data))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"--- page {index} ---\n{page_text.strip()}")
        return "\n\n".join(pages)

    def _decode_text(self, data):
        for encoding in ("utf-8-sig", "utf-8", "cp932", "shift_jis"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def _send_json(self, body, status):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Serving on http://127.0.0.1:8000")
    server.serve_forever()
