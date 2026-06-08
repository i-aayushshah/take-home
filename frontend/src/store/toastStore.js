import { create } from "zustand";

let nextId = 0;

const useToastStore = create((set) => ({
  toasts: [],
  addToast: (message, variant = "success") => {
    const id = ++nextId;
    set((state) => ({
      toasts: [...state.toasts, { id, message, variant }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((toast) => toast.id !== id),
      }));
    }, 4200);
    return id;
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),
}));

export function toast(message, variant = "success") {
  return useToastStore.getState().addToast(message, variant);
}

export default useToastStore;
