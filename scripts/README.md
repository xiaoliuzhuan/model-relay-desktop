# scripts 目录说明

此目录用于仓库维护流程脚本，不面向普通最终用户。

## 前置依赖

- 已安装 [git-flow-next](https://git-flow.sh/)。
- 脚本调用命令名为 `git-flow`，请确保该命令在 `PATH` 中可用。
- Node.js 版本需满足仓库要求（见根目录 `package.json` 的 `engines.node`）。

## 推荐入口（统一）

- `node ./scripts/gitflow.mjs setup`
- `node ./scripts/gitflow.mjs finish`
- `node ./scripts/gitflow.mjs finish -v 2.0.0-beta.10 -r origin -m tauri -d dev`

也可通过 `pnpm`：

- `pnpm gitflow:setup`
- `pnpm release:push`
- `pnpm release:push -- -v 2.0.0-beta.10 -r origin -m tauri -d dev`

## 文件列表

- `gitflow.mjs`
  - `setup`：清理本地旧 `gitflow.*` 配置，重新初始化 git-flow，并配置 release 默认打 tag。
  - `finish`：执行 release finish 全流程校验、finish、推送分支与 tag。

- `setup-gitflow.ps1` / `setup-gitflow.sh`
  - 兼容脚本（与 `gitflow.mjs setup` 目标一致）。
  - 清理本地旧 `gitflow.*` 配置。
  - 重新初始化 git-flow（`main=tauri`、`develop=dev`，且不创建分支）。
  - 配置 release finish 默认创建 tag。

- `release-finish.ps1` / `release-finish.sh`
  - 兼容脚本（与 `gitflow.mjs finish` 目标一致）。
  - 在 `release/<version>` 分支执行发布收尾。
  - 检查工作区是否干净、版本参数是否与分支一致、远程/本地 tag 是否冲突。
  - 执行 `git-flow release finish`，并推送目标分支与当前提交上的 tag。

## 用法

### setup-gitflow

PowerShell:

```powershell
.\scripts\setup-gitflow.ps1
```

Bash:

```bash
./scripts/setup-gitflow.sh
```

### release-finish

PowerShell:

```powershell
.\scripts\release-finish.ps1
.\scripts\release-finish.ps1 -v 2.0.0-beta.10
.\scripts\release-finish.ps1 -v 2.0.0-beta.10 -r origin -m tauri -d dev
```

Bash:

```bash
./scripts/release-finish.sh
./scripts/release-finish.sh -v 2.0.0-beta.10
./scripts/release-finish.sh -v 2.0.0-beta.10 -r origin -m tauri -d dev
```
