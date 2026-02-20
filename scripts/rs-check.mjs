import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const pyembedPython =
  process.platform === "win32"
    ? path.resolve("src-tauri", "pyembed", "python", "python.exe")
    : path.resolve("src-tauri", "pyembed", "python", "bin", "python3");

if (!fs.existsSync(pyembedPython)) {
  console.error(`pyembed Python 不存在: ${pyembedPython}`);
  process.exit(1);
}

const env = {
  ...process.env,
  PYO3_PYTHON: pyembedPython,
};

execFileSync("cargo", ["fmt"], {
  cwd: "src-tauri",
  stdio: "inherit",
  env,
});

execFileSync("cargo", ["check", "-p", "mtga-tauri"], {
  cwd: "src-tauri",
  stdio: "inherit",
  env,
});
