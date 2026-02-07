# MTGA
<picture>
    <img alt="MTGA" src="https://github.com/BiFangKNT/mtga/blob/gui/icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](docs/README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](docs/README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](docs/README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](docs/README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](docs/README.fr.md) [![Documentação em Português (Brasil)](<https://img.shields.io/badge/docs-Português-purple>)](docs/README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](docs/README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](docs/README.ru.md)

## 简介

 MTGA 是一个基于本地代理的 IDE 固定模型服务商解决方案，适用于 Windows 和 macOS。

 **注意：本项目目前只支持 openai 格式的 api ，请确认。其他格式可以转为 openai 格式后再使用。**



 <details>
  <summary>你什么也看不见~~</summary>
  <br>
  <p>MTGA 即 Make Trae Great Again !</p>
 </details>

## 目录

- [MTGA](#mtga)
  - [简介](#简介)
  - [目录](#目录)
  - [更新日志](#更新日志)
  - [快速开始](#快速开始)
    - [安装](#安装)
      - [Windows](#windows)
      - [macOS](#macos)
    - [使用](#使用)
  - [macOS 解决 “包已损坏” 问题](#macos-解决-包已损坏-问题)
    - [图形化解决方案](#图形化解决方案)
    - [cli 解决方案](#cli-解决方案)
  - [trae 端提示 “添加模型失败” 的排查方案](#trae-端提示-添加模型失败-的排查方案)
        - [第 5 步：配置 Trae IDE](#第-5-步配置-trae-ide)
      - [macOS](#macos-1)
  - [😎 保持更新](#-保持更新)
  - [架构与依赖约束](#架构与依赖约束)
  - [引用](#引用)
  - [Star History](#star-history)

---

## 更新日志

最新日志详见： [最新发行版](https://github.com/BiFangKNT/mtga/releases/latest)

历史日志归档： [CHANGELOG.md](CHANGELOG.md)

---

## 快速开始

### 安装

#### Windows

1. 从 [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) 下载最新版本的 `MTGA_v{version}_windows_x64-setup.exe`
2. 双击安装

#### macOS

1. 从 [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) 下载最新版本的 `MTGA_v{version}_apple_{arch}.dmg`
  - `{arch}` 为指令集架构：
    - `x64`：Intel 处理器
    - `aarch64`：Apple Silicon 处理器（M 系列）
2. 双击 DMG 文件，系统会自动挂载安装包
3. 将 `MTGA_GUI.app` 拖拽到 `Applications` 文件夹

### 使用
1. 启动 MTGA 应用程序
2. 添加代理配置组
   - **API URL 只需要填域名（端口号可选，不懂的就不要填），不需要填后面的路由，例如：`https://your-api.example.com`**
   - 如果你的接口不是标准 `/v1` 路由，可以自定义中间路由
     <img width="70%" alt="modify middle route" src="./images/modify-middle-route.png?raw=true" />
3. 填写全局配置
   - **如果希望启用多模态能力，可以将模型名映射到内置多模态模型名上：**
     - <div style="display:flex;flex-direction:column;font-size:0">
        <img width="70%" alt="model mapping" src="./images/model-mapping-above.png?raw=true" />
        <img width="70%" alt="model mapping" src="./images/model-mapping-below.png?raw=true" />
       </div>
     - <img width="70%" alt="model mapping effects" src="./images/model-mapping-effects.png?raw=true" />
4. 点击"一键启动全部服务"按钮（macOS 需要管理员权限）
5. 等待程序自动完成以下操作：
   - 生成并安装证书
   - 修改hosts文件
   - 启动代理服务器
6. 完成后，按照[第 5 步：配置 Trae IDE](#第-5-步配置-trae-ide)进行IDE配置

> [!NOTE]
> - 支持用户数据持久化存储，代理配置组和证书会自动保存

> [!WARNING]
> - 需要管理员权限
> - macOS 端如提示“包已损坏”，请参考 [macOS 解决 “包已损坏” 问题](#macos-解决-包已损坏-问题)
> - 如 trae 端添加模型失败，请参考 [trae 端提示 “添加模型失败” 的排查方案](#trae-端提示-添加模型失败-的排查方案)

## macOS 解决 “包已损坏” 问题

如果启动 `MTGA_GUI.app` 时弹出这样的提示：

<img width="244" height="223" alt="app corrupted" src="./images/app-corrupted.png?raw=true" />

**点击取消**。然后参考以下步骤解决：

### 图形化解决方案

1. 到 [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) 下载 `Sentinel.dmg`
2. 双击 `Sentinel.dmg` 文件，将 `Sentinel.app` 拖拽到 `Applications` 文件夹
3. 从启动台或 Applications 文件夹启动 `Sentinel.app`
4. 将本项目的 `MTGA_GUI.app` 拖拽到 `Sentinel.app` 的左侧窗口中
   - <img width="355.33" height="373.33" alt="sentinel add app" src="./images/sentinel-add-app.png?raw=true" />

`MTGA_GUI.app` 将被自动处理并启动

### cli 解决方案

1. 找到 `MTGA_GUI.app` 完整路径，如 `/Applications/MTGA_GUI.app`。
2. 打开终端（Terminal）应用程序。
3. 执行以下命令签名 `MTGA_GUI.app`：
   ```zsh
   xattr -d com.apple.quarantine <应用完整路径>
   ```
   这会移除 `MTGA_GUI.app` 中的 `com.apple.quarantine` 扩展属性。
4. 启动 `MTGA_GUI.app`。

## trae 端提示 “添加模型失败” 的排查方案

如果一切顺利，你应该会在日志区看到收到请求的日志：


请检查：
- 确保 hosts 包含 `127.0.0.1 api.openai.com` 这一行，且未被注释掉（# 开头）。
- 确保没有其他程序正在使用端口 443（如浏览器、VPN 等）。
  - 可以使用以下命令检查：
    ```
    # windows
    netstat -ano | find ":443" | find "LISTENING"

    # macos
    netstat -lnp tcp | grep :443
    ```
  - 如果有进程在监听 443 端口，建议关闭该进程。
- 确保没有其他代理软件正在运行，它们可能会干扰 MTGA 的代理功能。
  - 如需科学上网，请使用 TUN 模式而非系统代理。有条件的请在 **本机之外** 部署其他代理服务。
  - 如果 DNS 配置错误，也可能导致无法解析。
  - 不懂的请保持网络环境干净。

---

##### 第 5 步：配置 Trae IDE

1.  打开并登录 Trae IDE。
2.  在 AI 对话框中，点击右下角的模型图标，选择末尾的"添加模型"。
3.  **服务商**：选择 `OpenAI`。
4.  **模型**：选择"自定义模型"。
5.  **模型 ID**：填写你在 Python 脚本中 `CUSTOM_MODEL_ID` 定义的值 (例如: `my-custom-local-model`)。
6.  **API 密钥**：
    *   如果你的目标 API 需要 API 密钥，并且 Trae 会将其通过 `Authorization: Bearer <key>` 传递，那么这里填写的密钥会被 Python 代理转发。
    *   Trae 配置 OpenAI 时，API 密钥与 `remove_reasoning_content` 配置相关。我们的 Python 代理不处理这个逻辑，它只是简单地转发 Authorization 头部。你可以尝试填写你的目标 API 所需的密钥，或者一个任意的 `sk-xxxx` 格式的密钥。

7.  点击"添加模型"。
8.  回到 AI 聊天框，右下角选择你刚刚添加的自定义模型。

现在，当你通过 Trae 与这个自定义模型交互时，请求应该会经过你的本地 Python 代理，并被转发到你配置的 `TARGET_API_BASE_URL`。

**故障排除提示：**
*   **端口冲突**：如果 443 端口已被占用 (例如被 IIS、Skype 或其他服务占用)，Python 脚本会启动失败。你需要停止占用该端口的服务，或者修改 Python 脚本和 Nginx (如果使用) 监听其他端口 (但这会更复杂，因为 Trae 硬编码访问 `https://api.openai.com` 的 443 端口)。
*   **防火墙**：确保 Windows 防火墙允许 Python 监听 443 端口的入站连接 (尽管是本地连接 `127.0.0.1`，通常不需要特别配置防火墙，但值得检查)。
*   **证书问题**：如果 Trae 报错 SSL/TLS 相关错误，请仔细检查 CA 证书是否已正确安装到"受信任的根证书颁发机构"，以及 Python 代理是否正确加载了 `api.openai.com.crt` 和 `.key`。
*   **代理日志**：Python 脚本会打印一些日志，可以帮助你诊断问题。

这个方案比直接使用 vproxy + nginx 的方式更集成一些，将 TLS 终止和代理逻辑都放在了一个 Python 脚本中，更适合快速在 Windows 上进行原型验证。

#### macOS

-> [Mac OS 脚本启动方法](https://github.com/BiFangKNT/mtga/blob/gui/docs/README_macOS_cli.md)

---

## 😎 保持更新

点击仓库右上角 Star 和 Watch 按钮，获取最新动态。

![star to keep latest](https://github.com/BiFangKNT/mtga/blob/gui/images/star-to-keep-latest.gif?raw=true)

---
## 架构与依赖约束

为避免模块耦合失控，项目遵循以下分层与依赖规则：

- UI -> actions -> services -> 领域模块（cert/hosts/network/proxy/update）-> runtime/platform
- UI 不得直接依赖领域模块，所有操作通过 actions/services 统一编排。
- 平台相关逻辑放在 `modules/platform`（或显式平台子模块）。

更多细节与错误处理规范见：`docs/ARCHITECTURE.md`。

## 引用

`ca`目录引用自`wkgcass/vproxy`仓库，感谢大佬！

## Star History

<a href="https://www.star-history.com/#BiFangKNT/mtga&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=BiFangKNT/mtga&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=BiFangKNT/mtga&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=BiFangKNT/mtga&type=date&legend=top-left" />
 </picture>
</a>
