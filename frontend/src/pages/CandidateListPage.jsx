import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import CandidateCard from "../components/CandidateCard";
import CreateCandidateModal from "../components/CreateCandidateModal";
import HiringPipelineInfo from "../components/HiringPipelineInfo";
import Pagination from "../components/Pagination";
import GlassCard from "../components/layout/GlassCard";
import EmptyState from "../components/ui/EmptyState";
import GlassButton from "../components/ui/GlassButton";
import InputField from "../components/ui/InputField";
import PageHeader from "../components/ui/PageHeader";
import Spinner from "../components/ui/Spinner";
import { useCandidates } from "../hooks/useCandidates";
import useAuthStore from "../store/authStore";

const STATUS_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "new", label: "New" },
  { value: "reviewed", label: "Reviewed" },
  { value: "hired", label: "Hired" },
  { value: "rejected", label: "Rejected" },
];

const DEFAULT_LIMIT = 12;

function parseFilters(searchParams) {
  const offset = Number(searchParams.get("offset") || 0);
  const limit = Number(searchParams.get("limit") || DEFAULT_LIMIT);
  return {
    status: searchParams.get("status") || "",
    role_applied: searchParams.get("role_applied") || "",
    skill: searchParams.get("skill") || "",
    keyword: searchParams.get("keyword") || "",
    offset: Number.isFinite(offset) ? offset : 0,
    limit: Number.isFinite(limit) ? limit : DEFAULT_LIMIT,
  };
}

function toApiParams(filters) {
  const params = { offset: filters.offset, limit: filters.limit };
  if (filters.status) params.status = filters.status;
  if (filters.role_applied) params.role_applied = filters.role_applied;
  if (filters.skill) params.skill = filters.skill;
  if (filters.keyword) params.keyword = filters.keyword;
  return params;
}

function activeFilterCount(filters) {
  return [filters.status, filters.role_applied, filters.skill, filters.keyword].filter(Boolean).length;
}

export default function CandidateListPage() {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const isAdmin = useAuthStore((state) => state.user?.role === "admin");
  const [searchParams, setSearchParams] = useSearchParams();
  const filters = useMemo(() => parseFilters(searchParams), [searchParams]);
  const apiParams = useMemo(() => toApiParams(filters), [filters]);
  const { data, isLoading, isError, error } = useCandidates(apiParams);
  const activeFilters = activeFilterCount(filters);

  function updateFilter(key, value) {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.set("offset", "0");
    setSearchParams(next);
  }

  function clearFilters() {
    const next = new URLSearchParams();
    next.set("offset", "0");
    next.set("limit", String(filters.limit));
    setSearchParams(next);
  }

  function handlePageChange(nextOffset) {
    const next = new URLSearchParams(searchParams);
    next.set("offset", String(nextOffset));
    setSearchParams(next);
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Talent pipeline"
        title="Candidates"
        description="Browse the pipeline, filter by role or skill, and open profiles to score and summarize."
      >
        {!isLoading && data && (
          <span className="stat-badge">
            <span className="h-2 w-2 rounded-full bg-accent-success" />
            {data.total} total
          </span>
        )}
        {isAdmin && (
          <GlassButton onClick={() => setCreateOpen(true)} className="w-full sm:w-auto">
            Add Candidate
          </GlassButton>
        )}
      </PageHeader>

      <HiringPipelineInfo />

      <div className="filter-panel">
        <button
          type="button"
          className="filter-toggle"
          onClick={() => setFiltersOpen((open) => !open)}
          aria-expanded={filtersOpen}
        >
          <span className="flex items-center gap-2">
            Filters
            {activeFilters > 0 && (
              <span className="rounded-full bg-accent-primary/30 px-2 py-0.5 text-xs text-accent-glow">
                {activeFilters}
              </span>
            )}
          </span>
          <svg
            className={`h-5 w-5 transition-transform ${filtersOpen ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <div className={`p-4 sm:p-5 ${filtersOpen ? "block" : "hidden sm:block"}`}>
          <div className="mb-4 flex items-center justify-between gap-3">
            <p className="hidden text-sm font-semibold text-white sm:block">Search &amp; filters</p>
            {activeFilters > 0 && (
              <button
                type="button"
                onClick={clearFilters}
                className="text-xs font-semibold text-accent-glow hover:text-white"
              >
                Clear all filters
              </button>
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <InputField label="Status" htmlFor="filter-status">
              <div className="field">
                <select
                  id="filter-status"
                  value={filters.status}
                  onChange={(e) => updateFilter("status", e.target.value)}
                  className="field-input px-4"
                >
                  {STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value} className="bg-surface-800">
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </InputField>

            <InputField label="Role" htmlFor="filter-role">
              <div className="field">
                <input
                  id="filter-role"
                  type="text"
                  value={filters.role_applied}
                  onChange={(e) => updateFilter("role_applied", e.target.value)}
                  placeholder="e.g. Backend Engineer"
                  className="field-input px-4"
                />
              </div>
            </InputField>

            <InputField label="Skill" htmlFor="filter-skill">
              <div className="field">
                <input
                  id="filter-skill"
                  type="text"
                  value={filters.skill}
                  onChange={(e) => updateFilter("skill", e.target.value)}
                  placeholder="e.g. Python"
                  className="field-input px-4"
                />
              </div>
            </InputField>

            <InputField label="Keyword" htmlFor="filter-keyword">
              <div className="field">
                <input
                  id="filter-keyword"
                  type="search"
                  value={filters.keyword}
                  onChange={(e) => updateFilter("keyword", e.target.value)}
                  placeholder="Search name or email…"
                  className="field-input px-4"
                />
              </div>
            </InputField>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="glass-card animate-pulse">
              <div className="flex gap-4">
                <div className="h-12 w-12 rounded-2xl bg-white/10" />
                <div className="flex-1 space-y-3">
                  <div className="h-4 w-2/3 rounded bg-white/10" />
                  <div className="h-3 w-1/2 rounded bg-white/10" />
                  <div className="h-3 w-full rounded bg-white/10" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isError && (
        <GlassCard hover={false}>
          <p className="text-sm text-accent-danger">
            {error?.response?.data?.detail || "Failed to load candidates."}
          </p>
        </GlassCard>
      )}

      {!isLoading && !isError && (
        <>
          {data?.items?.length ? (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {data.items.map((candidate) => (
                <CandidateCard key={candidate.id} candidate={candidate} />
              ))}
            </div>
          ) : (
            <GlassCard hover={false}>
              <EmptyState
                title="No candidates found"
                description="Try adjusting your filters or clearing them to see the full pipeline."
                icon={
                  <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
                    />
                  </svg>
                }
              />
            </GlassCard>
          )}

          {data && data.total > 0 && (
            <Pagination
              offset={data.offset}
              limit={data.limit}
              total={data.total}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}

      <CreateCandidateModal open={createOpen} onClose={() => setCreateOpen(false)} />
    </div>
  );
}
