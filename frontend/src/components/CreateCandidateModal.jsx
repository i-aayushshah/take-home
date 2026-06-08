import { useState } from "react";
import Modal from "./ui/Modal";
import { useCreateCandidate } from "../hooks/useCreateCandidate";

export default function CreateCandidateModal({ open, onClose }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [roleApplied, setRoleApplied] = useState("");
  const [skills, setSkills] = useState("");
  const [description, setDescription] = useState("");
  const { mutate, isPending, isError, error } = useCreateCandidate();

  function handleClose() {
    if (!isPending) onClose();
  }

  function handleSubmit(event) {
    event.preventDefault();
    mutate(
      {
        name: name.trim(),
        email: email.trim(),
        role_applied: roleApplied.trim(),
        skills: skills.split(",").map((item) => item.trim()).filter(Boolean),
        description: description.trim() || null,
      },
      {
        onSuccess: () => {
          setName("");
          setEmail("");
          setRoleApplied("");
          setSkills("");
          setDescription("");
          onClose();
        },
      }
    );
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Add candidate"
      description="Enter application details to add someone to the pipeline."
      size="lg"
      footer={
        <div className="modal-actions">
          <button type="button" className="modal-btn-secondary" onClick={handleClose} disabled={isPending}>
            Cancel
          </button>
          <button type="submit" form="create-candidate-form" className="modal-btn-primary" disabled={isPending}>
            {isPending ? "Creating…" : "Create candidate"}
          </button>
        </div>
      }
    >
      <form id="create-candidate-form" onSubmit={handleSubmit} className="modal-form">
        <fieldset className="modal-fieldset">
          <legend className="modal-legend">Contact</legend>
          <div className="modal-field-grid">
            <label className="modal-field">
              <span className="modal-label">Full name</span>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoFocus
                placeholder="Jane Smith"
                className="modal-input"
              />
            </label>

            <label className="modal-field">
              <span className="modal-label">Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="jane@company.com"
                className="modal-input"
              />
            </label>
          </div>
        </fieldset>

        <fieldset className="modal-fieldset">
          <legend className="modal-legend">Application</legend>
          <div className="modal-field-stack">
            <label className="modal-field">
              <span className="modal-label">Role applied</span>
              <input
                value={roleApplied}
                onChange={(e) => setRoleApplied(e.target.value)}
                required
                placeholder="Frontend Engineer"
                className="modal-input"
              />
            </label>

            <label className="modal-field">
              <span className="modal-label">
                Skills
                <span className="modal-hint">comma-separated</span>
              </span>
              <input
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                required
                placeholder="React, TypeScript, Node.js"
                className="modal-input"
              />
            </label>

            <label className="modal-field">
              <span className="modal-label">
                Notes
                <span className="modal-hint">optional</span>
              </span>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="Brief background or context for reviewers…"
                className="modal-input modal-textarea"
              />
            </label>
          </div>
        </fieldset>

        {isError && (
          <p className="modal-error">{error?.response?.data?.detail || "Failed to create candidate."}</p>
        )}
      </form>
    </Modal>
  );
}
