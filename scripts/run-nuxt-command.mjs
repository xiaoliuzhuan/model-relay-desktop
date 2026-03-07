import { spawn } from "node:child_process";

const [mode, ...rest] = process.argv.slice(2);
if (!mode || !["build", "generate"].includes(mode)) {
  console.error(
    "[run-nuxt-command] usage: node ./scripts/run-nuxt-command.mjs <build|generate> [args...]",
  );
  process.exit(1);
}

const child = spawn("npx", ["nuxt", mode, ...rest], {
  stdio: ["inherit", "pipe", "pipe"],
  shell: false,
  env: process.env,
});

const warningSnippets = [
  "Found 1 warning while optimizing generated CSS:",
  "@property --radialprogress",
  "Unknown at rule: @property",
  'syntax: "<percentage>";',
  "inherits: true;",
];

const filterChunk = (chunk) =>
  chunk
    .toString()
    .split(/\r?\n/)
    .filter((line) => !warningSnippets.some((snippet) => line.includes(snippet)))
    .join("\n");

child.stdout.on("data", (chunk) => {
  const text = filterChunk(chunk);
  if (text.trim()) {
    process.stdout.write(`${text}\n`);
  }
});

child.stderr.on("data", (chunk) => {
  const text = filterChunk(chunk);
  if (text.trim()) {
    process.stderr.write(`${text}\n`);
  }
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
