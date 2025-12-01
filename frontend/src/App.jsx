import { useEffect, useMemo, useRef, useState } from "react";
import EncumbranceTable from "./components/EncumbranceTable.jsx";
import AgreementsTable from "./components/AgreementsTable.jsx";
import PlanSection from "./components/PlanSection.jsx";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

import {
  fetchTracker,
  saveTracker,
  importTitle as importTitleApi,
  generateDocuments,
} from "./services/docTrackerApi.js";
import "./App.css";

const ACTION_OPTIONS = [
  "No Action Required",
  "Consent",
  "Partial Discharge",
  "Full Discharge",
];

const STATUS_OPTIONS = [
  "---",
  "Prepared",
  "Complete",
  "No Action Required",
  "Client for Execution",
  "City for Execution",
  "Third party for Execution",
];

const PROGRAM_METADATA = {
  program_name: "USSI DOCUMENT TRACKER",
  program_version: "V.3.0", 
  file_version: 1,
};



const uniqueId = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
? crypto.randomUUID()
: `${Date.now()}-${Math.random()}`;

const createEncumbranceRow = () => ({
  id: uniqueId(),
  "Document #": "",
  Description: "",
  Signatories: "",
  Action: ACTION_OPTIONS[0],
  "Circulation Notes": "",
  Status: STATUS_OPTIONS[0],
});

const createAgreementRow = () => ({
  id: uniqueId(),
  "Document/Desc": "",
  "Copies/Dept": "",
  Signatories: "",
  "Condition of Approval": "",
  "Circulation Notes": "",
  Status: STATUS_OPTIONS[0],
});

const createPlanRow = (desc = "") => ({
  id: uniqueId(),
  "Document/Desc": desc,
  "Copies/Dept": "",
  Signatories: "",
  "Condition of Approval": "",
  "Circulation Notes": "",
  Status: STATUS_OPTIONS[0],
});

const seedPlanRows = () => [
  createPlanRow("Surveyor's Affidavit"),
  createPlanRow("Consent"),
  createPlanRow(""),
];

const buildDefaultTracker = () => ({
  header: { ...PROGRAM_METADATA },
  legal_desc: "",
  existing_encumbrances_on_title: Array.from({ length: 3 }, () =>
    createEncumbranceRow(),
),
new_agreements: [createAgreementRow()],
plans: {
  SUB1: seedPlanRows(),
  URW1: seedPlanRows(),
  ODRW1: seedPlanRows(),
},
});

function mapInstrumentsToRows(insts) {
  if (!insts) {
    return [];
  }
  return insts.map((inst) => ({
    id: uniqueId(),
    "Document #": inst["Document #"] ?? inst.reg_number ?? "",
    Description: inst["Description"] ?? inst.name ?? "",
    Signatories: inst["Signatories"] ?? inst.signatories ?? "",
    Action: inst.Action ?? inst.action ?? ACTION_OPTIONS[0],
    "Circulation Notes": inst["Circulation Notes"] ?? inst.notes ?? "",
    Status: inst.Status ?? inst.status ?? STATUS_OPTIONS[0],
  }));
}

function App() {
  const [sectionOrder, setSectionOrder] = useState(() => {
  const saved = localStorage.getItem("sectionOrder");
    return saved ? JSON.parse(saved) : ["encumbrances", "agreements", "plans"];
  });

  const [tracker, setTracker] = useState(() => buildDefaultTracker());
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [newPlanName, setNewPlanName] = useState("");
  const fileInputRef = useRef(null);
  
  const planEntries = useMemo(
    () => Object.entries(tracker.plans ?? {}),
    [tracker.plans],
  );
  
  useEffect(() => {
    localStorage.setItem("sectionOrder", JSON.stringify(sectionOrder));
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const payload = await fetchTracker();
        if (!cancelled) {
          if (payload) {
            setTracker(payload);
            setStatus("Tracker loaded from backend.");
          } else {
            setTracker(buildDefaultTracker());
            setStatus("Backend unavailable. Using local template data.");
          }
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
          setTracker(buildDefaultTracker());
          setStatus("Unable to reach backend. Using local template data.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [sectionOrder]);

  const updateTracker = (transform) => {
    setTracker((prev) => ({
      ...prev,
      header: prev.header ?? { ...PROGRAM_METADATA },
      ...transform(prev),
    }));
  };

  const handleEncFieldChange = (index, field, value) => {
    updateTracker((prev) => ({
      existing_encumbrances_on_title: prev.existing_encumbrances_on_title.map(
        (row, idx) => (idx === index ? { ...row, [field]: value } : row),
      ),
    }));
  };

  const handleAgreementFieldChange = (index, field, value) => {
    updateTracker((prev) => ({
      new_agreements: prev.new_agreements.map((row, idx) =>
        idx === index ? { ...row, [field]: value } : row,
      ),
    }));
  };

  const handlePlanFieldChange = (planName, index, field, value) => {
    updateTracker((prev) => {
      const planRows = prev.plans?.[planName] ?? [];
      const updatedRows = planRows.map((row, idx) =>
        idx === index ? { ...row, [field]: value } : row,
      );
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: updatedRows,
        },
      };
    });
  };

  const addEncRow = () =>
    updateTracker((prev) => ({
      existing_encumbrances_on_title: [
        ...prev.existing_encumbrances_on_title,
        createEncumbranceRow(),
      ],
    }));

  const removeEncRow = () =>
    updateTracker((prev) => ({
      existing_encumbrances_on_title:
        prev.existing_encumbrances_on_title.slice(
          0,
          Math.max(prev.existing_encumbrances_on_title.length - 1, 0),
        ),
    }));

  const addAgreementRow = () =>
    updateTracker((prev) => ({
      new_agreements: [...prev.new_agreements, createAgreementRow()],
    }));

  const removeAgreementRow = () =>
    updateTracker((prev) => ({
      new_agreements: prev.new_agreements.slice(
        0,
        Math.max(prev.new_agreements.length - 1, 0),
      ),
    }));

  const addPlanRow = (planName) =>
    updateTracker((prev) => {
      const planRows = prev.plans?.[planName] ?? [];
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: [...planRows, createPlanRow()],
        },
      };
    });

  const removePlanRow = (planName) =>
    updateTracker((prev) => {
      const planRows = prev.plans?.[planName] ?? [];
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: planRows.slice(0, Math.max(planRows.length - 1, 0)),
        },
      };
    });

  const removePlan = (planName) =>
    updateTracker((prev) => {
      const updatedPlans = { ...prev.plans };
      delete updatedPlans[planName]; // <-- remove the whole plan

      return {
        plans: updatedPlans
      };
    });

  const handleCreatePlan = () => {
    const cleaned = newPlanName.trim().toUpperCase();
    if (!cleaned) {
      return;
    }
    updateTracker((prev) => {
      if (prev.plans?.[cleaned]) {
        return {};
      }
      return {
        plans: {
          ...(prev.plans ?? {}),
          [cleaned]: seedPlanRows(),
        },
      };
    });
    setNewPlanName("");
  };

  const triggerFilePicker = () => {
    fileInputRef.current?.click();
  };

  const handleImportTitle = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setLoading(true);
    try {
      const payload = await importTitleApi(file);
      const importedRows =
        payload?.existing_encumbrances_on_title ??
        payload?.inst_on_title ??
        payload?.instruments;
      if (importedRows && importedRows.length > 0) {
        updateTracker((prev) => ({
          existing_encumbrances_on_title: mapInstrumentsToRows(importedRows),
          legal_desc: payload?.legal_desc ?? prev.legal_desc,
        }));
        setStatus(
          `Imported ${importedRows.length} instruments from title certificate.`,
        );
      } else {
        setStatus("Import finished, but no instruments were returned.");
      }
    } catch (error) {
      setStatus(`Unable to import title: ${error.message}`);
    } finally {
      setLoading(false);
      if (event.target) {
        event.target.value = "";
      }
    }
  };

  const reloadTracker = async () => {
    setLoading(true);
    try {
      const payload = await fetchTracker();
      if (payload) {
        setTracker(payload);
        setStatus("Tracker reloaded from backend.");
      } else {
        setTracker(buildDefaultTracker());
        setStatus("Backend unavailable. Using local template data.");
      }
    } catch (error) {
      console.error(error);
      setTracker(buildDefaultTracker());
      setStatus("Unable to load tracker data. Using template data.");
    } finally {
      setLoading(false);
    }
  };

  const persistTracker = async () => {
    setLoading(true);
    try {
      const ok = await saveTracker(tracker);
      setStatus(
        ok
          ? "Tracker saved successfully."
          : "Unable to save tracker. See server logs.",
      );
    } finally {
      setLoading(false);
    }
  };

  const runDocumentGeneration = async () => {
    setLoading(true);
    try {
      await generateDocuments({
        tracker,
        legal_desc: tracker.legal_desc,
      });
      setStatus("Document generation requested successfully.");
    } catch (error) {
      setStatus(`Document generation failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">USSI</p>
          <h1>{PROGRAM_METADATA.program_name}</h1>
          <p className="subhead">{PROGRAM_METADATA.program_version}</p>
        </div>
        <div className="header-meta">
          <label className="field">
            <span>Legal Description</span>
            <textarea
              value={tracker.legal_desc ?? ""}
              onChange={(e) =>
                updateTracker(() => ({ legal_desc: e.target.value }))
              }
              placeholder="Enter legal description..."
            />
          </label>
        </div>
      </header>

      <section className="toolbar">
        <div className="toolbar__group">
          <button onClick={triggerFilePicker} disabled={loading}>
            Import Title (PDF)
          </button>
          <button onClick={persistTracker} disabled={loading}>
            Save Tracker
          </button>
          <button onClick={reloadTracker} disabled={loading}>
            Reload Tracker
          </button>
          <button onClick={runDocumentGeneration} disabled={loading}>
            Generate Documents
          </button>
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            onChange={handleImportTitle}
            style={{ display: "none" }}
          />
        </div>
        <div className="status-line">
          {loading ? "Working..." : status || "Ready."}
        </div>
      </section>

      <section className="sections">
        <DragDropContext
          onDragEnd={(result) => {
            if (!result.destination) return;

            const items = Array.from(sectionOrder);
            const [moved] = items.splice(result.source.index, 1);
            items.splice(result.destination.index, 0, moved);
            setSectionOrder(items);
          }}
        >
          <Droppable droppableId="sections">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {sectionOrder.map((sec, index) => (
                  <Draggable key={sec} draggableId={sec} index={index}>
                    {(provided) => (
                      <div
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        ref={provided.innerRef}
                        className="section-wrapper"
                      >
                        {sec === "encumbrances" && (
                          <EncumbranceTable
                            rows={tracker.existing_encumbrances_on_title ?? []}
                            actionOptions={ACTION_OPTIONS}
                            statusOptions={STATUS_OPTIONS}
                            onFieldChange={handleEncFieldChange}
                            onAddRow={addEncRow}
                            onRemoveRow={removeEncRow}
                          />
                        )}
                        {sec === "agreements" && (
                          <AgreementsTable
                            rows={tracker.new_agreements ?? []}
                            statusOptions={STATUS_OPTIONS}
                            onFieldChange={handleAgreementFieldChange}
                            onAddRow={addAgreementRow}
                            onRemoveRow={removeAgreementRow}
                          />
                        )}
                        {sec === "plans" && (
                          <section className="plan-section">
                            <div className="plan-header">
                              <h2>Plans</h2>
                              <div className="plan-new">
                                <input
                                  value={newPlanName}
                                  onChange={(e) => setNewPlanName(e.target.value)}
                                  placeholder="Plan label (e.g., SUB2)"
                                />
                                <button
                                  type="button"
                                  onClick={handleCreatePlan}
                                  disabled={!newPlanName.trim()}
                                >
                                  + Plan
                                </button>
                              </div>
                            </div>
                            {planEntries.length === 0 ? (
                              <p className="empty-row">No plans defined yet.</p>
                            ) : (
                              planEntries.map(([planName, rows]) => (
                                <PlanSection
                                  key={planName}
                                  name={planName}
                                  rows={rows}
                                  statusOptions={STATUS_OPTIONS}
                                  onFieldChange={handlePlanFieldChange}
                                  onAddRow={addPlanRow}
                                  onRemoveRow={removePlanRow}
                                  onRemovePlan={removePlan}
                                />
                              ))
                            )}
                          </section>
                        )}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </section>
    </div>
  );
}

export default App;
