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
  existing_encumbrances_on_title: [], // start blank
  new_agreements: [createAgreementRow()],                 // start blank
  plans: {},                          // no plans initially
  titles: {},                          // no titles initially
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
    try {
      const saved = localStorage.getItem("sectionOrder");
      return saved ? JSON.parse(saved) : ["encumbrances", "agreements", "plans"];
    } catch {
      return ["encumbrances", "agreements", "plans"];
    }
  });

  // planOrder: persisted ordering of plan groups (SUB1, URW1, etc)
  const [planOrder, setPlanOrder] = useState(() => {
    try {
      const saved = localStorage.getItem("planOrder");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [tracker, setTracker] = useState(() => buildDefaultTracker());
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [newPlanName, setNewPlanName] = useState("");
  const [newTitleName, setNewTitleName] = useState("");
  const fileInputRef = useRef(null);

  // planEntries follow planOrder and filter out removed plans
  const planEntries = useMemo(() => {
    const plans = tracker.plans ?? {};
    return planOrder.filter((name) => plans[name]).map((name) => [name, plans[name]]);
  }, [tracker.plans, planOrder]);

  // Memoized titles entries
  const titleEntries = useMemo(() => {
    const titles = tracker.titles ?? {};
    return Object.entries(titles);
  }, [tracker.titles]);


  // persist sectionOrder and planOrder when they change
  useEffect(() => {
    try {
      localStorage.setItem("sectionOrder", JSON.stringify(sectionOrder));
    } catch {}
  }, [sectionOrder]);

  useEffect(() => {
    try {
      localStorage.setItem("planOrder", JSON.stringify(planOrder));
    } catch {}
  }, [planOrder]);

  useEffect(() => {
  if (tracker?.plans) {
    const existingNames = Object.keys(tracker.plans);
    const fromBackend = tracker.plan_order ?? existingNames;

    // Filter out deleted plans + keep order
    const synced = fromBackend.filter(name => existingNames.includes(name));

    // Append any new plans not in order list
    const extras = existingNames.filter(name => !synced.includes(name));

    setPlanOrder([...synced, ...extras]);
  }
}, [tracker.plans, tracker.plan_order]);


  // load tracker once on mount
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const payload = await fetchTracker();
        if (!cancelled) {
          if (payload) {
            setTracker(payload);
            // ensure planOrder includes backend plans (append any missing ones)
            const backendKeys = Object.keys(payload.plans ?? {});
            setPlanOrder((prev) => {
              const merged = Array.from(new Set([...prev, ...backendKeys]));
              // keep only keys that exist in the payload
              return merged.filter((k) => (payload.plans ?? {})[k]);
            });
            setStatus("Tracker loaded from backend.");
          } else {
            const defaultTracker = buildDefaultTracker();
            setTracker(defaultTracker);
            setPlanOrder(Object.keys(defaultTracker.plans ?? {}));
            setStatus("Backend unavailable. Using local template data.");
          }
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
          const defaultTracker = buildDefaultTracker();
          setTracker(defaultTracker);
          setPlanOrder(Object.keys(defaultTracker.plans ?? {}));
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
  }, []);

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
      delete updatedPlans[planName]; // remove whole plan
      return {
        plans: updatedPlans,
      };
    });

  // keep planOrder in sync when plan removed
  useEffect(() => {
    // remove any planOrder entries that no longer exist in tracker.plans
    setPlanOrder((prev) => prev.filter((name) => typeof tracker.plans?.[name] !== "undefined"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tracker.plans]);

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

    // add to ordering
    setPlanOrder((prev) => {
      if (prev.includes(cleaned)) return prev;
      return [...prev, cleaned];
    });

    setNewPlanName("");
  };

  const handleCreateTitle = () => {
    const cleaned = newTitleName.trim().toUpperCase();
    if (!cleaned) return;

    updateTracker((prev) => {
      // Make sure tracker has a titles object
      const titles = prev.titles ?? {};

      if (titles[cleaned]) {
        // title already exists, do nothing
        return {};
      }

      // Add a new title with empty/default fields
      return {
        titles: {
          ...titles,
          [cleaned]: {
            legal_desc: "",
            existing_encumbrances_on_title: Array.from({ length: 3 }, () =>
              createEncumbranceRow()
            ),
            new_agreements: [createAgreementRow()],
            plans: {},
          },
        },
      };
    });

    setNewTitleName("");
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
        // ensure planOrder includes backend plans
        const backendKeys = Object.keys(payload.plans ?? {});
        setPlanOrder((prev) => Array.from(new Set([...prev, ...backendKeys])));
      } else {
        const defaultTracker = buildDefaultTracker();
        setTracker(defaultTracker);
        setPlanOrder(Object.keys(defaultTracker.plans ?? {}));
        setStatus("Backend unavailable. Using local template data.");
      }
    } catch (error) {
      console.error(error);
      const defaultTracker = buildDefaultTracker();
      setTracker(defaultTracker);
      setPlanOrder(Object.keys(defaultTracker.plans ?? {}));
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

  // Unified onDragEnd for both SECTION and PLAN types
  const onDragEnd = (result) => {
    if (!result.destination) return;

    if (result.type === "SECTION") {
      const items = Array.from(sectionOrder);
      const [moved] = items.splice(result.source.index, 1);
      items.splice(result.destination.index, 0, moved);
      setSectionOrder(items);
      return;
    }

    if (result.type === "PLAN") {
      const items = Array.from(planOrder);
      const [moved] = items.splice(result.source.index, 1);
      items.splice(result.destination.index, 0, moved);
      setPlanOrder(items);
      return;
    }

    if (result.type === "ENCUMBRANCE_ROW") {
      updateTracker((prev) => {
        const rows = Array.from(prev.existing_encumbrances_on_title);
        const [moved] = rows.splice(result.source.index, 1);
        rows.splice(result.destination.index, 0, moved);
        return { existing_encumbrances_on_title: rows };
      });
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
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="sections" type="SECTION">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {sectionOrder.map((sec, index) => (
                  <Draggable key={sec} draggableId={sec} index={index}>
                    {(providedSection, snapshotSection) => (
                      <div
                        ref={providedSection.innerRef}
                        {...providedSection.draggableProps}
                        {...providedSection.dragHandleProps}
                        className="section-wrapper"
                        style={{
                          marginBottom: 12,
                          ...providedSection.draggableProps.style,
                        }}
                      >
                        {sec === "encumbrances" && (
                          <section className="plan-section">
                            <div className="plan-header">
                              <h2>Existing Encumbrances on Title</h2>
                              <div className="plan-new">
                                <input
                                  value={newTitleName}
                                  onChange={(e) => setNewTitleName(e.target.value)}
                                  placeholder="Title Number"
                                />
                                <button
                                  type="button"
                                  onClick={handleCreateTitle}
                                  disabled={!newTitleName.trim()}
                                >
                                  + Title
                                </button>
                              </div>
                            </div>

                            <Droppable droppableId="encumbrances" type="ENCUMBRANCE_ROW">
                              {(provided) => (
                                <div ref={provided.innerRef} {...provided.droppableProps}>
                                  {titleEntries.length === 0 ? (
                                    <p className="empty-row">No titles defined yet.</p>
                                  ) : (
                                    titleEntries.map(([titleName, titleData]) => (
                                      <EncumbranceTable
                                        key={titleName}
                                        name={titleName} 
                                        rows={titleData.existing_encumbrances_on_title ?? []}
                                        actionOptions={ACTION_OPTIONS}
                                        statusOptions={STATUS_OPTIONS}
                                        onFieldChange={(name, index, field, value) => {
                                          updateTracker((prev) => {
                                            const updatedTitles = { ...prev.titles };
                                            updatedTitles[titleName].existing_encumbrances_on_title[index][field] = value;
                                            return { titles: updatedTitles };
                                          });
                                        }}
                                        onAddRow={(name) => {
                                          updateTracker((prev) => {
                                            const rows = prev.titles[titleName].existing_encumbrances_on_title ?? [];
                                            return {
                                              titles: {
                                                ...prev.titles,
                                                [titleName]: {
                                                  ...prev.titles[titleName],
                                                  existing_encumbrances_on_title: [...rows, createEncumbranceRow()],
                                                },
                                              },
                                            };
                                          });
                                        }}
                                        onRemoveRow={(name) => {
                                          updateTracker((prev) => {
                                            const rows = prev.titles[titleName].existing_encumbrances_on_title ?? [];
                                            return {
                                              titles: {
                                                ...prev.titles,
                                                [titleName]: {
                                                  ...prev.titles[titleName],
                                                  existing_encumbrances_on_title: rows.slice(
                                                    0,
                                                    Math.max(rows.length - 1, 0)
                                                  ),
                                                },
                                              },
                                            };
                                          });
                                        }}
                                        onRemovePlan={(name) => {
                                          // remove the entire title
                                          updateTracker((prev) => {
                                            const updatedTitles = { ...prev.titles };
                                            delete updatedTitles[titleName];
                                            return { titles: updatedTitles };
                                          });
                                        }}
                                      />
                                    )))}

                                  {provided.placeholder}
                                </div>
                              )}
                            </Droppable>
                          </section>
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

                            <Droppable droppableId="plans" type="PLAN">
                              {(providedPlans) => (
                                <div ref={providedPlans.innerRef} {...providedPlans.droppableProps}>
                                  {planEntries.length === 0 ? (
                                    <p className="empty-row">No plans defined yet.</p>
                                  ) : (
                                    planEntries.map(([planName, rows], pIndex) => (
                                      <Draggable key={planName} draggableId={planName} index={pIndex}>
                                        {(providedPlan, snapshotPlan) => (
                                          <div
                                            ref={providedPlan.innerRef}
                                            {...providedPlan.draggableProps}
                                            {...providedPlan.dragHandleProps}
                                            style={{
                                              marginBottom: "1rem",
                                              ...providedPlan.draggableProps.style,
                                            }}
                                          >
                                            <PlanSection
                                              name={planName}
                                              rows={rows}
                                              statusOptions={STATUS_OPTIONS}
                                              onFieldChange={handlePlanFieldChange}
                                              onAddRow={addPlanRow}
                                              onRemoveRow={removePlanRow}
                                              onRemovePlan={(name) => {
                                                // remove plan from tracker and order
                                                removePlan(name);
                                                setPlanOrder((prev) => prev.filter((n) => n !== name));
                                              }}
                                            />
                                          </div>
                                        )}
                                      </Draggable>
                                    ))
                                  )}
                                  {providedPlans.placeholder}
                                </div>
                              )}
                            </Droppable>
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
