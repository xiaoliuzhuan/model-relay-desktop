export {};

declare global {
  interface Window {
    __MTGA_RUNTIME__?: string;
    __TAURI__?: {
      core?: {
        invoke?: unknown;
      };
    };
  }
}
