# Model Relay Desktop

<picture>
    <img alt="Model Relay Desktop" src="./icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](docs/README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](docs/README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](docs/README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](docs/README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](docs/README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](docs/README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](docs/README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](docs/README.ru.md)

## 简介

Model Relay Desktop 是一个基于本地代理的 IDE 固定模型服务商解决方案，适用于 Windows 和 macOS。

**注意：本项目目前只支持 openai 格式的 api ，请确认。其他格式可以转为 openai 格式后再使用。**

## 开源与来源说明

- 本仓库是基于上游项目 `BiFangKNT/mtga` 的二次开发版本，非上游官方发布。
- 本仓库遵循并保留上游采用的 `GNU AGPLv3` 协议，详见 [LICENSE](LICENSE)。
- 若你对外提供网络服务或分发二进制，请按 AGPL 要求提供对应源码与协议声明。
- 本仓库未与任何第三方品牌形成官方合作或背书关系。

 <details>
  <summary>你什么也看不见~~</summary>
  <br>
  <p>Model Relay Desktop：本地模型中转桌面工具。</p>
 </details>

## 目录

- [Model Relay Desktop](#model-relay-desktop)
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
  - [配置 Trae IDE](#配置-trae-ide)
  - [😎 保持更新](#-保持更新)
  - [贡献](#贡献)
  - [架构与依赖约束](#架构与依赖约束)
  - [引用](#引用)
  - [Star History](#star-history)

---

## 更新日志

最新日志详见： [最新发行版](https://github.com/xiaoliuzhuan/model-relay-desktop/releases/latest)

历史日志归档： [CHANGELOG.md](CHANGELOG.md)

---

## 快速开始

### 安装

#### Windows

1. 从 [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases) 下载最新版本的安装包
2. 双击安装

#### macOS

1. 从 [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases) 下载最新版本的 DMG 包
   - `{arch}` 为指令集架构：
     - `x64`：Intel 处理器
     - `aarch64`：Apple Silicon 处理器（M 系列）
2. 双击 DMG 文件，系统会自动挂载安装包
3. 将 `Model Relay Desktop.app` 拖拽到 `Applications` 文件夹

### 使用

1. 启动 Model Relay Desktop 应用程序
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
6. 完成后，按照[配置 Trae IDE](#配置-trae-ide)进行IDE配置

> [!NOTE]
>
> - 代理配置和生成证书会持久化存储于用户数据目录，见 `设置 - 用户数据`

> [!WARNING]
>
> - 需要管理员权限
> - macOS 端如提示“包已损坏”，请参考 [macOS 解决 “包已损坏” 问题](#macos-解决-包已损坏-问题)
> - 如 trae 端添加模型失败，请参考 [trae 端提示 “添加模型失败” 的排查方案](#trae-端提示-添加模型失败-的排查方案)

## macOS 解决 “包已损坏” 问题

如果启动 `Model Relay Desktop.app` 时弹出这样的提示：

<img width="244" height="223" alt="app corrupted" src="./images/app-corrupted.png?raw=true" />

**点击取消**。然后参考以下步骤解决：

### 图形化解决方案

1. 到 [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) 下载 `Sentinel.dmg`
2. 双击 `Sentinel.dmg` 文件，将 `Sentinel.app` 拖拽到 `Applications` 文件夹
3. 从启动台或 Applications 文件夹启动 `Sentinel.app`
4. 将本项目的 `Model Relay Desktop.app` 拖拽到 `Sentinel.app` 的左侧窗口中
   - <img width="355.33" height="373.33" alt="sentinel add app" src="./images/sentinel-add-app.png?raw=true" />

`Model Relay Desktop.app` 将被自动处理并启动

### cli 解决方案

1. 找到 `Model Relay Desktop.app` 完整路径，如 `/Applications/Model Relay Desktop.app`。
2. 打开终端（Terminal）应用程序。
3. 执行以下命令签名 `Model Relay Desktop.app`：
   ```zsh
   xattr -d com.apple.quarantine <应用完整路径>
   ```
   这会移除 `Model Relay Desktop.app` 中的 `com.apple.quarantine` 扩展属性。
4. 启动 `Model Relay Desktop.app`。

## trae 端提示 “添加模型失败” 的排查方案

如果一切顺利，你应该会在日志区看到收到请求的日志：

<img width="40%" alt="received list request" src="./images/received-list-request.png?raw=true" />

如无日志，请检查：

- **hosts**：确保包含 `127.0.0.1 api.openai.com` 这一行，且未被注释掉（# 开头）。
- **端口监听**：确保没有其他程序正在使用端口 443（如浏览器、VPN 等）。
  - 可以使用以下命令检查：

    ```
    # windows
    netstat -ano | find ":443" | find "LISTENING"

    # macos
    netstat -lnp tcp | grep :443
    ```

  - 如果有进程在监听 443 端口，建议关闭该进程。

- **网络代理**：确保没有其他代理软件正在运行，它们可能会干扰本项目的代理功能。
  - 如需科学上网，请使用 TUN 模式而非系统代理。有条件的请在 **本机之外** 部署其他代理服务。
  - 如果 DNS 配置错误，也可能导致无法解析。
  - 不懂的请保持网络环境干净。
- **证书问题**：如果 Trae 报错 SSL/TLS 相关错误，请检查 CA 证书是否已正确安装到"受信任的根证书颁发机构"。
- **防火墙**：确保防火墙允许监听 443 端口的入站连接 (尽管是本地连接 `127.0.0.1`，通常不需要特别配置防火墙，但值得检查)。
- **进阶排查方法**：
  - 配置好本项目后，`主要流程 - 代理服务器操作 - 勾选 “关闭SSL严格模式”`，启动全部服务。
  - 安装并打开 [Reqable](https://reqable.com/) 工具，根据其提示安装其证书。
  - 其启动默认会打开调试，在右上角关闭它：
    <img width="40%" alt="reqable debug mode off" src="./images/reqable-debug-mode-off.png?raw=true" />
  - 打开一个 http 测试页：
    <img width="55%" alt="reqable http create" src="./images/reqable-http-create.png?raw=true" />
  - 填写 list api 的 url，授权选择 “Bearer Token”，并填写你在全局配置处的 Key：
    <img width="70%" alt="reqable fill in config" src="./images/reqable-fill-in-config.png?raw=true" />
  - 点击发送并观察响应体。

---

## 配置 Trae IDE

1.  打开并登录 Trae IDE。
2.  在 AI 对话框中，点击右下角的模型图标，选择末尾的"添加模型"。
3.  **服务商**：选择 `OpenAI`。
4.  **模型**：按你在全局配置中填写的模型 ID，如果是 `gpt-5`，则选择 `GPT-5`。
5.  **API 密钥**：全局配置中填写的 Key。
6.  点击"添加模型"。
7.  回到 AI 聊天框，右下角选择你刚刚添加的自定义模型。

现在，当你通过 Trae 与这个自定义模型交互时，请求会经过你的本地代理，并被转发到你配置的 `API URL`。

---

## 😎 保持更新

点击仓库右上角 Star 和 Watch 按钮，获取最新动态。

![star to keep latest](https://github.com/xiaoliuzhuan/model-relay-desktop/blob/main/images/star-to-keep-latest.gif?raw=true)

---

## 贡献

请查阅 [贡献指南](CONTRIBUTING.md)

## 架构与依赖约束

为避免模块耦合失控，项目遵循以下分层与依赖规则：

- UI -> actions -> services -> 领域模块（cert/hosts/network/proxy/update）-> runtime/platform
- UI 不得直接依赖领域模块，所有操作通过 actions/services 统一编排。
- 平台相关逻辑放在 `modules/platform`。

## 引用

`ca`目录引用自`wkgcass/vproxy`仓库，感谢大佬！

## Star History

<a href="https://www.star-history.com/#xiaoliuzhuan/model-relay-desktop&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=xiaoliuzhuan/model-relay-desktop&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=xiaoliuzhuan/model-relay-desktop&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=xiaoliuzhuan/model-relay-desktop&type=date&legend=top-left" />
 </picture>
</a>
