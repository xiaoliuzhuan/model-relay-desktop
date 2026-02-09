import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const gitflowScript = fileURLToPath(new URL("./gitflow.mjs", import.meta.url));

const command = process.execPath;
const commandArgs = [gitflowScript, "finish", ...args];

const result = spawnSync(command, commandArgs, {
  stdio: "inherit",
  shell: false,
});

if (result.error) {
  console.error(`❌ 执行失败: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
