import { useEffect, useState } from "react";
import Modal from "./ui/Modal";
import { useParseResume } from "../hooks/useParseResume";
import { useUpdateProfile } from "../hooks/useUpdateProfile";

export default function ParseResumeModal({ open, onClose, candidateId }) {
  const { mutate: parse, data, isPending, isError, error, reset } = useParseResume(candidateId);
  const { mutate: saveProfile, isPending: saving, isError: saveError, error: saveErr } = useUpdateProfile(candidateId);

  const [skills, setSkills] = useState("");
  const [description, setDescription] = useState("");
  const [experienceJson, setExperienceJson] = useState("[]");

  useEffect(() => {
    if (!open) {
      reset();
      return undefined;
    }
    parse(undefined, {
      onSuccess: (result) => {
        setSkills((result.skills || []).join(", "));
        setDescription(result.description || "");
        setExperienceJson(JSON.stringify(result.work_experience || [], null, 2));
      },
    });
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  function handleSave() {
    let workExperience = [];
    try {
      workExperience = JSON.parse(experienceJson);
    } catch {
      return;
    }
    const skillList = skills.split(",").map((s) => s.trim()).filter(Boolean);
    saveProfile(
      {
        skills: skillList,
        description: description.trim() || null,
        work_experience: workExperience,
      },
      { onSuccess: () => onClose() }
    );
  }

  const parsing = isPending && !data;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Review parsed resume"
      description="Edit extracted fields before saving to the candidate profile."
      size="lg"
      footer={
        <div className="modal-actions">
          <button type="button" className="modal-btn-secondary" onClick={onClose} disabled={saving}>
            Cancel
          </button>
          <button type="button" className="modal-btn-primary" onClick={handleSave} disabled={parsing || saving}>
            {saving ? "Saving…" : "Save to profile"}
          </button>
        </div>
      }
    >
      {parsing && <p className="text-sm text-white/60">Parsing resume with AI…</p>}

      {isError && (
        <p className="modal-error">{error?.response?.data?.detail || "Failed to parse resume."}</p>
      )}

      {data && (
        <div className="modal-form space-y-4">
          <label className="modal-field">
            <span className="modal-label">Skills</span>
            <input value={skills} onChange={(e) => setSkills(e.target.value)} className="modal-input" />
          </label>

          <label className="modal-field">
            <span className="modal-label">Description</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="modal-input modal-textarea"
            />
          </label>

          <label className="modal-field">
            <span className="modal-label">
              Work experience
              <span className="modal-hint">JSON array</span>
            </span>
            <textarea
              value={experienceJson}
              onChange={(e) => setExperienceJson(e.target.value)}
              rows={8}
              className="modal-input modal-textarea font-mono text-xs"
            />
          </label>

          {saveError && (
            <p className="modal-error">{saveErr?.response?.data?.detail || "Failed to save profile."}</p>
          )}
        </div>
      )}
    </Modal>
  );
}
