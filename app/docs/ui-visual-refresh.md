# UI 视觉优化方案（不改功能）

> 目标：在不改业务逻辑的前提下，提升整体质感、层级与可读性。
> 说明：字体引入与调整暂不实施，仅保留设计建议。

## 现状诊断（主要问题）

- 层级不清：标题、分区、操作按钮权重接近，视觉焦点弱。
- 版式单调：统一卡片 + 网格布局缺乏主次关系。
- 色彩无方向：几乎全靠默认主题色，缺少“工具感”的视觉语言。
- 日志面板不突出：更像普通文本框，缺少“系统反馈面板”的识别度。
- 动效缺失：启动与交互缺乏节奏感，显得生硬。

## 设计方向（建议）

**主题：Tech Console + 轻量仪表盘**

- 明亮、清爽、偏灰白底，强调“工具/控制台”气质。
- 主色偏青绿/青蓝，辅色用于警告/注意，避免紫色与暗黑倾向。
- 通过背景微渐变与卡片边框建立“空间感”。

### 色彩建议（示例）

- 主色：青绿/青蓝（例：`#0EA5A4` / `#0891B2`）
- 辅色：琥珀/橙（用于 warning / 注意）
- 背景：浅灰白 + 冷色倾向（例：`#F8FAFC` / `#EEF2FF` / `#F1F5F9`）
- 卡片：白底 + 细边框 + 轻投影

### 背景建议（示例）

- 渐变方向：`linear-gradient(120deg, #F8FAFC 0%, #EEF2FF 55%, #F1F5F9 100%)`
- 可选：叠加超淡纹理（网格/噪点，透明度极低）

### 字体建议（暂不实施）

- 标题：`Space Grotesk` / `Sora`（几何感）
- 正文：`Inter Tight` / `IBM Plex Sans`
- 日志：`JetBrains Mono`

## 具体改造方案（按模块）

### 1) 全局基调

- 背景：柔和渐变 + 轻微纹理（不喧宾夺主）。
- 卡片：白底、细边框、柔和投影，提升层级分明度。
- 标题区：强化标题权重 + 补充副标题（可后续增加）。
- 字体：暂不做，但预留“标题/正文/等宽”三级结构。

### 2) 布局与区域

- 左侧为“操作台”，右侧为“状态台”（日志），构成主次对比。
- 右侧日志区建议在大屏保持 sticky（便于持续观察）。
- 主列与侧列固定比例（如 2:1），避免两列权重接近。
- 页脚做成“操作条”，突出“一键启动”。

### 3) 核心组件视觉

**ConfigGroupPanel**

- 列表项改为“分段列表 + 选中高亮条”。
- 选中项背景加浅色条带，按钮区靠右集中。
- 主按钮与次按钮区分为实体/描边/ghost。
- 编辑弹窗聚焦内容，弱化外框噪音。

**GlobalConfigPanel / RuntimeOptionsPanel**

- 标题区加入短描述，字段区域轻微底色区分块。

**MainTabs**

- Tabs 改成轻量底边高亮样式，内容区统一卡片布局。
- Tab 内容区域建议保持统一 padding 与标题样式。

**LogPanel**

- 打造成“控制台面板”：顶部小状态标签 + 终端样式文本区。
- 日志区可加超淡网格纹理（极轻）以提升“系统面板”质感。
- 日志区保持等宽字体风格，但暂不引入字体包。

**FooterActions**

- 主按钮加重视觉（尺寸/颜色/阴影）。
- 可加入简短提示文案（如权限提示），但不强制。

### 4) 轻量动效（可选）

- 页面加载淡入 + 卡片轻微上浮。
- 列表选中高亮渐变（轻微，不抢眼）。
- 新日志出现时短暂高亮。
- tab 切换可用轻微淡入（避免突兀）。

### 5) 响应式与可读性

- 小屏下日志区可折叠或移动到 tabs 内。
- 表单字段间距适当增大，减轻拥挤。
- 字号层级建议：标题 18/20，正文 14/16，辅助 12/13。

## 实施清单（文件级）

1. `app/components/AppShell.vue`：整体布局权重、header/footer 改造。
2. `app/components/LogPanel.vue`：控制台样式、状态标签。
3. `app/components/FooterActions.vue`：主按钮强化。
4. `app/components/panels/*`：卡片层级与按钮体系统一。
5. `app/components/tabs/*`：tabs 风格统一。
6. `app/assets/css/tailwind.css`：背景渐变与卡片风格变量。

## 暂不实施

- 字体引入（保留建议，不做加载/替换）。

---

## 落地样式规范（建议版本）

> 用于实施与后续优化对齐，避免细节发散。

### 全局变量（CSS 变量建议）

- `--mtga-bg`: `#F7F8FB`
- `--mtga-surface`: `#FFFFFF`
- `--mtga-surface-soft`: `#F3F6FA`
- `--mtga-border`: `#E5E7EB`
- `--mtga-accent`: `#0EA5A4`
- `--mtga-accent-strong`: `#0891B2`
- `--mtga-warn`: `#F59E0B`
- `--mtga-text`: `#0F172A`
- `--mtga-text-muted`: `#64748B`

### 背景与层级

- 页面背景：淡渐变 + 轻纹理（不强制）。
- 卡片背景：白底 + 细边框 + 轻阴影。
- 卡片圆角：`12px`。
- 卡片内间距：`16px` 起步，复杂面板可增至 `20px`。

### 标题与文字

- H1：`text-2xl` + `font-semibold`（主标题）
- H2：`text-lg` + `font-semibold`（面板标题）
- 正文：`text-sm` / `text-base`
- 说明文案：`text-xs` / `text-sm` + muted

### 按钮规范

- 主按钮：`btn-primary` + 更高对比度（适度阴影）
- 次按钮：`btn` + `btn-outline`
- 轻按钮：`btn-ghost`
- 危险操作：`btn-error` 或橙色/红色强调

### 列表与选择态

- 列表项高度：`40~44px`
- 选中态：背景加浅色条带 + 左侧 3px 竖线
- Hover：背景轻微上浮或加淡色

### 表单输入

- 输入框高度：`40px` 左右
- Label 与 Input 间距：`6~8px`
- 必填提示：加淡红色提示文字

### LogPanel 规范

- 顶部：标题 + 状态 badge
- 文本区：`font-mono`，背景略深于卡片
- 内边距：`12px`
- 最大高度：`320~360px`

### Tabs 规范

- tab 高度：`36px`
- 激活：底边高亮 + 文字加深
- 内容区：统一 padding 16px

### Footer 操作条

- 固定高度：`64px` 左右
- 主按钮靠右，左侧可放轻提示

### 动效（若使用）

- 页面加载：`opacity` + `translateY` 小幅过渡（200~300ms）
- 列表选中：`background-color` 过渡（150ms）
- Tabs 切换：轻微淡入（150ms）

---

## 当前实施进展（已完成）

### 全局样式

- 已添加 CSS 变量与背景渐变（含轻微光晕）。
- 已新增 `mtga-card` / `mtga-card-body` / `mtga-card-title` / `mtga-chip` 等基础样式。
- 文件：`app/assets/css/tailwind.css`

### 布局与结构

- Header 增强（标题层级、说明文案、状态 chip）。
- 主内容区改为 2:1 分栏，日志区在大屏保持 sticky。
- Footer 改为操作条卡片。
- 文件：`app/components/AppShell.vue`

### 日志与操作条

- LogPanel 增加状态标签、统计与终端质感背景。
- FooterActions 增强主按钮与说明文案。
- 文件：`app/components/LogPanel.vue`、`app/components/FooterActions.vue`

### 面板与 Tabs

- ConfigGroup / GlobalConfig / RuntimeOptions 统一卡片层级与按钮层级。
- Tabs 区域改为底边高亮式，内容区统一风格。
- 各 Tab 面板补充标题与说明文案。
- 文件：
  - `app/components/panels/ConfigGroupPanel.vue`
  - `app/components/panels/GlobalConfigPanel.vue`
  - `app/components/panels/RuntimeOptionsPanel.vue`
  - `app/components/tabs/MainTabs.vue`
  - `app/components/tabs/CertTab.vue`
  - `app/components/tabs/HostsTab.vue`
  - `app/components/tabs/ProxyTab.vue`
  - `app/components/tabs/DataManagementTab.vue`
  - `app/components/tabs/AboutTab.vue`

### 弹窗

- ConfirmDialog / UpdateDialog 统一卡片风格与按钮层级。
- 文件：
  - `app/components/dialogs/ConfirmDialog.vue`
  - `app/components/dialogs/UpdateDialog.vue`

## 下一步建议（可选）

1. 视觉微调：
   - 细化表格行间距、边框色与 hover 提示（ConfigGroup 表格）。
   - LogPanel 背景纹理强度微调，确保可读性。
   - Tabs 激活态与 hover 态再统一色阶（避免过强对比）。
2. 响应式完善：
   - 小屏下将 LogPanel 收纳为折叠卡或移动到 Tabs 内。
3. 字体方案（暂缓）：
   - 等确认整体风格稳定后再引入字体包并统一字号层级。
