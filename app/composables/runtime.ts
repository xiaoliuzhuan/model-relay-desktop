export const getRuntimeTag = (): string => {
  if (typeof window === "undefined") {
    return "";
  }
  const runtime = window.__MTGA_RUNTIME__;
  if (typeof runtime === "string" && runtime.trim()) {
    return runtime.trim().toLowerCase();
  }
  const tauriCore = window.__TAURI__?.core;
  return tauriCore?.invoke ? "tauri" : "";
};

export const isTauriRuntime = (): boolean => getRuntimeTag() === "tauri";

export const isBundledRuntime = (): boolean => {
  if (typeof window === "undefined") {
    return false;
  }
  const runtime = window.__MTGA_RUNTIME__;
  if (runtime === "tauri" || runtime === "nuitka") {
    return true;
  }
  const protocol = window.location?.protocol?.replace(":", "");
  if (protocol === "tauri") {
    return true;
  }
  return window.location?.hostname === "tauri.localhost";
};
