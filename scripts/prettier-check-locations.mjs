import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import prettier from "prettier";

const execFileAsync = promisify(execFile);
const PRETTIER_CLI = path.resolve("node_modules", "prettier", "bin", "prettier.cjs");

function parseFileList(stdout) {
  return stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

async function getUnformattedFiles() {
  try {
    const { stdout } = await execFileAsync(
      process.execPath,
      [PRETTIER_CLI, ".", "--list-different"],
      {
        maxBuffer: 20 * 1024 * 1024,
      },
    );
    return parseFileList(stdout);
  } catch (error) {
    if (typeof error?.stdout === "string") {
      return parseFileList(error.stdout);
    }
    throw error;
  }
}

function getFirstDifference(originalText, formattedText) {
  const originalLines = originalText.split(/\r?\n/);
  const formattedLines = formattedText.split(/\r?\n/);
  const maxLines = Math.max(originalLines.length, formattedLines.length);

  for (let i = 0; i < maxLines; i += 1) {
    const oldLine = originalLines[i] ?? "";
    const newLine = formattedLines[i] ?? "";
    if (oldLine !== newLine) {
      const maxCols = Math.max(oldLine.length, newLine.length);
      let column = 1;
      for (let c = 0; c < maxCols; c += 1) {
        if ((oldLine[c] ?? "") !== (newLine[c] ?? "")) {
          column = c + 1;
          break;
        }
      }
      return {
        line: i + 1,
        column,
        oldLine,
        newLine,
      };
    }
  }

  return {
    line: 1,
    column: 1,
    oldLine: "",
    newLine: "",
  };
}

function summarizeLine(text) {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (normalized.length <= 40) {
    return normalized || "(空行)";
  }
  return `${normalized.slice(0, 40)}...`;
}

function report(file, line, column, message) {
  // VS Code problem matcher format: file:line:column: message
  console.log(`${file}:${line}:${column}: ${message}`);
}

async function main() {
  const files = await getUnformattedFiles();
  if (files.length === 0) {
    return;
  }

  let hasIssues = false;

  for (const file of files) {
    const absolutePath = path.resolve(process.cwd(), file);
    let sourceText = "";

    try {
      sourceText = await fs.readFile(absolutePath, "utf8");
    } catch (error) {
      hasIssues = true;
      report(file, 1, 1, `无法读取文件: ${error.message}`);
      continue;
    }

    try {
      const config = (await prettier.resolveConfig(absolutePath)) ?? {};
      const formattedText = await prettier.format(sourceText, {
        ...config,
        filepath: absolutePath,
      });

      if (formattedText !== sourceText) {
        hasIssues = true;
        const diff = getFirstDifference(sourceText, formattedText);
        const oldPart = summarizeLine(diff.oldLine);
        const newPart = summarizeLine(diff.newLine);
        report(file, diff.line, diff.column, `Prettier 不一致: "${oldPart}" -> "${newPart}"`);
      }
    } catch (error) {
      hasIssues = true;
      report(file, 1, 1, `Prettier 处理失败: ${error.message}`);
    }
  }

  if (hasIssues) {
    process.exitCode = 1;
  }
}

await main();
