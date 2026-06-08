import InputField from "./InputField";

export default function GlassInput({
  id,
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  required = false,
  autoComplete,
  icon,
}) {
  return (
    <InputField label={label} htmlFor={id}>
      <div className="field">
        {icon && <span className="field-icon-left">{icon}</span>}
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          autoComplete={autoComplete}
          className={`field-input ${icon ? "field-input-icon-left" : ""}`}
        />
      </div>
    </InputField>
  );
}
