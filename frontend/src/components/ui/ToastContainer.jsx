import useToastStore from "../../store/toastStore";

const VARIANT_CLASS = {
  success: "toast-success",
  error: "toast-error",
  info: "toast-info",
};

export default function ToastContainer() {
  const toasts = useToastStore((state) => state.toasts);
  const removeToast = useToastStore((state) => state.removeToast);

  if (!toasts.length) return null;

  return (
    <div className="toast-stack" aria-live="polite" aria-atomic="true">
      {toasts.map((item) => (
        <div key={item.id} className={`toast-item ${VARIANT_CLASS[item.variant] || VARIANT_CLASS.info}`}>
          <p className="toast-message">{item.message}</p>
          <button type="button" className="toast-dismiss" onClick={() => removeToast(item.id)} aria-label="Dismiss">
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
