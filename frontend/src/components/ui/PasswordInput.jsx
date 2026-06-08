import { useState } from "react";
import InputField from "./InputField";

function EyeOpenIcon() {
  return (
    <svg className="h-[18px] w-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.75}
        d="M2.036 12.322a1 1 0 010-.644C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
      />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function EyeClosedIcon() {
  return (
    <svg className="h-[18px] w-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.75}
        d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c1.52 0 2.972-.29 4.288-.822m1.947 1.347A10.451 10.451 0 0021.066 12c-1.292-4.338-5.31-7.5-10.066-7.5-1.42 0-2.773.27-4.015.76M9.88 9.88l4.24 4.24M9.88 9.88L6.34 6.34m3.54 3.54l4.24 4.24m0 0l3.54 3.54M14.12 14.12l3.54 3.54"
      />
    </svg>
  );
}

export default function PasswordInput({
  id,
  label,
  value,
  onChange,
  placeholder,
  required = false,
  autoComplete = "current-password",
}) {
  const [visible, setVisible] = useState(false);

  return (
    <InputField label={label} htmlFor={id}>
      <div className="field">
        <input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          autoComplete={autoComplete}
          className="field-input field-input-action-right"
        />
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="field-action-right"
          aria-label={visible ? "Hide password" : "Show password"}
        >
          {visible ? <EyeClosedIcon /> : <EyeOpenIcon />}
        </button>
      </div>
    </InputField>
  );
}
