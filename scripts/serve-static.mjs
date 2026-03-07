import { createReadStream } from "node:fs";
import { access, stat } from "node:fs/promises";
import http from "node:http";
import path from "node:path";

const rootDir = path.resolve(process.cwd(), process.argv[2] ?? ".output/public");
const port = Number(process.argv[3] ?? 4173);

const contentTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
  [".ico", "image/x-icon"],
  [".txt", "text/plain; charset=utf-8"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
]);

const server = http.createServer(async (req, res) => {
  try {
    const requestUrl = new URL(req.url || "/", `http://${req.headers.host || "127.0.0.1"}`);
    const pathname = decodeURIComponent(requestUrl.pathname);
    const relativePath = pathname === "/" ? "index.html" : pathname.replace(/^\//, "");
    const filePath = path.join(rootDir, relativePath);
    const fallbackPath = path.join(rootDir, "index.html");

    let finalPath = filePath;
    try {
      const fileStat = await stat(filePath);
      if (fileStat.isDirectory()) {
        finalPath = path.join(filePath, "index.html");
      }
      await access(finalPath);
    } catch {
      finalPath = fallbackPath;
      await access(finalPath);
    }

    const ext = path.extname(finalPath).toLowerCase();
    res.writeHead(200, {
      "Content-Type": contentTypes.get(ext) || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    createReadStream(finalPath).pipe(res);
  } catch (error) {
    res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
    res.end(error instanceof Error ? error.message : String(error));
  }
});

server.listen(port, "127.0.0.1", () => {
  console.log(`[serve-static] serving ${rootDir} at http://127.0.0.1:${port}`);
});
