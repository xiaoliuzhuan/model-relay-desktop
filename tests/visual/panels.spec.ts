import { expect, test, type Page } from "@playwright/test";

type Scenario = {
  name: string;
  path: string;
  panel: string;
  mainTab?: string;
  heading: string;
  updateDialog?: boolean;
};

const scenarios: Scenario[] = [
  {
    name: "config-group-panel",
    path: "/?snapshot=1&panel=config-group",
    panel: "config-group",
    heading: "代理配置组",
  },
  {
    name: "global-config-panel",
    path: "/?snapshot=1&panel=global-config",
    panel: "global-config",
    heading: "全局配置",
  },
  {
    name: "main-tabs-cert",
    path: "/?snapshot=1&panel=main-tabs&mainTab=cert",
    panel: "main-tabs",
    mainTab: "cert",
    heading: "证书管理",
  },
  {
    name: "main-tabs-hosts",
    path: "/?snapshot=1&panel=main-tabs&mainTab=hosts",
    panel: "main-tabs",
    mainTab: "hosts",
    heading: "hosts 文件",
  },
  {
    name: "main-tabs-proxy",
    path: "/?snapshot=1&panel=main-tabs&mainTab=proxy",
    panel: "main-tabs",
    mainTab: "proxy",
    heading: "代理服务",
  },
  {
    name: "run-logs-panel",
    path: "/?snapshot=1&panel=run-logs",
    panel: "run-logs",
    heading: "运行日志",
  },
  {
    name: "settings-panel",
    path: "/?snapshot=1&panel=settings",
    panel: "settings",
    heading: "应用设置",
  },
  {
    name: "update-dialog",
    path: "/?snapshot=1&panel=config-group&update=1",
    panel: "config-group",
    heading: "发现新版本",
    updateDialog: true,
  },
];

const waitForSnapshotPage = async (page: Page, scenario: Scenario) => {
  await page.goto(scenario.path);
  await expect(
    page.locator(`[data-snapshot-enabled="true"][data-active-panel="${scenario.panel}"]`),
  ).toBeVisible();
  if (scenario.mainTab) {
    await expect(page.locator(`[data-active-main-tab="${scenario.mainTab}"]`)).toBeVisible();
  }
  if (scenario.updateDialog) {
    await expect(page.locator("dialog.modal-open")).toBeVisible();
  }
  await expect(page.getByText(scenario.heading, { exact: false }).first()).toBeVisible();
  await page.waitForTimeout(250);
};

for (const scenario of scenarios) {
  test(scenario.name, async ({ page }) => {
    await waitForSnapshotPage(page, scenario);
    await expect(page).toHaveScreenshot(`${scenario.name}.png`, {
      animations: "disabled",
      caret: "hide",
      fullPage: true,
    });
  });
}
