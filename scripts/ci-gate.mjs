import { execFileSync } from "node:child_process";

const supportedTargets = new Set(["app", "py", "rs", "all"]);
const args = process.argv.slice(2).filter((arg) => arg !== "--");
const target = args[0] ?? "all";

if (!supportedTargets.has(target)) {
  console.error(`Unsupported gate target: ${target}`);
  console.error("Usage: pnpm gate -- <app|py|rs|all>");
  process.exit(1);
}

const run = (command, args, options = {}) => {
  execFileSync(command, args, {
    stdio: "inherit",
    ...options,
  });
};

const runPnpm = (args) => {
  if (process.platform === "win32") {
    run("cmd.exe", ["/d", "/s", "/c", `pnpm ${args.join(" ")}`]);
    return;
  }
  run("pnpm", args);
};

const runAppGate = () => {
  runPnpm(["postinstall"]);
  runPnpm(["prettier", ".", "--check"]);
  runPnpm(["eslint", "."]);
  runPnpm(["vue-tsc", "-p", ".nuxt/tsconfig.app.json", "--noEmit"]);
};

const runPyGate = () => {
  run("uv", ["run", "pyright"], { cwd: "python-src" });
  run("uv", ["run", "ruff", "check", "."], { cwd: "python-src" });
};

const runRsGate = () => {
  run("node", ["./scripts/rs-check.mjs", "gate"]);
};

if (target === "app") {
  runAppGate();
} else if (target === "py") {
  runPyGate();
} else if (target === "rs") {
  runRsGate();
} else {
  runAppGate();
  runPyGate();
  runRsGate();
}
