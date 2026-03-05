# macOS CLI Startup Method

This page provides a command-line method to remove quarantine flags when macOS shows "App is damaged".

## Steps

1. Open Terminal.
2. Find your app path, for example:
   - `/Applications/Model Relay Desktop.app`
3. Run:

```zsh
xattr -d com.apple.quarantine "/Applications/Model Relay Desktop.app"
```

4. Launch the app again.

## Notes

- Run this only for apps you trust.
- If your app path contains spaces, keep it in quotes.
- You may still need admin permission depending on your install location.

---

# macOS 命令行启动方法

当 macOS 提示“应用已损坏”时，可通过命令行移除隔离标记。

## 操作步骤

1. 打开终端（Terminal）。
2. 确认应用路径，例如：
   - `/Applications/Model Relay Desktop.app`
3. 执行命令：

```zsh
xattr -d com.apple.quarantine "/Applications/Model Relay Desktop.app"
```

4. 重新启动应用。

## 注意事项

- 仅对你信任来源的应用执行该命令。
- 路径里有空格时，需使用引号。
- 若安装路径受保护，可能仍需管理员权限。
