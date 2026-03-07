import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/visual",
  testMatch: ["*.spec.ts"],
  fullyParallel: false,
  reporter: "line",
  timeout: 30_000,
  expect: {
    toHaveScreenshot: {
      animations: "disabled",
      caret: "hide",
    },
  },
  snapshotPathTemplate: "{testDir}/__screenshots__/{testFilePath}/{arg}{ext}",
  use: {
    baseURL: "http://127.0.0.1:4173",
    colorScheme: "light",
    locale: "zh-CN",
    trace: "off",
    video: "off",
    viewport: {
      width: 1440,
      height: 1200,
    },
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        deviceScaleFactor: 1,
        viewport: {
          width: 1440,
          height: 1200,
        },
      },
    },
  ],
  webServer: {
    command: "pnpm snapshot:build && pnpm snapshot:serve",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
