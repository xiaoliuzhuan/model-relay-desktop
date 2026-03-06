export type MtgaToastTone = "success" | "info" | "warning" | "error";

export type MtgaToastItem = {
  id: number;
  message: string;
  tone: MtgaToastTone;
};

const DEFAULT_TOAST_DURATION_MS = 1800;

export const useMtgaToast = () => {
  const items = useState<MtgaToastItem[]>("mtga-toast-items", () => []);
  const nextId = useState<number>("mtga-toast-next-id", () => 1);

  const removeToast = (id: number) => {
    items.value = items.value.filter((item) => item.id !== id);
  };

  const pushToast = (
    message: string,
    tone: MtgaToastTone = "success",
    durationMs = DEFAULT_TOAST_DURATION_MS,
  ) => {
    const id = nextId.value++;
    items.value = [...items.value, { id, message, tone }];
    window.setTimeout(() => {
      removeToast(id);
    }, durationMs);
  };

  return {
    items,
    pushToast,
    removeToast,
  };
};
