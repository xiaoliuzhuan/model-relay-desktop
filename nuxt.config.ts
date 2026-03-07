import tailwindcss from "@tailwindcss/vite";
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  appDir: "app",
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxt/eslint"],
  runtimeConfig: {
    public: {
      mtgaSnapshot: process.env.MTGA_SNAPSHOT ?? process.env.NUXT_PUBLIC_MTGA_SNAPSHOT ?? "",
    },
  },
  components: {
    dirs: [{ path: "~/components", pathPrefix: false }],
  },
  // 禁用 SSR，因为 Tauri 不支持
  ssr: false,
  // 使开发服务器能够被其他设备发现，以便在 iOS 物理机运行。
  devServer: { host: process.env.TAURI_DEV_HOST || "localhost" },
  vite: {
    // 为 Tauri 命令输出提供更好的支持
    clearScreen: false,
    // 启用环境变量
    // 其他环境变量可以在如下网页中获知：
    // https://v2.tauri.app/reference/environment-variables/
    envPrefix: ["VITE_", "TAURI_"],
    server: {
      // Tauri需要一个确定的端口
      strictPort: true,
      // 开发期禁用缓存，避免 Tauri WebView 读取到损坏缓存
      headers: {
        "Cache-Control": "no-store",
        Pragma: "no-cache",
        Expires: "0",
      },
    },
    plugins: [tailwindcss()],
  },
  css: ["~/assets/css/tailwind.css"],
  ignore: ["**/src-tauri/**"],
});
