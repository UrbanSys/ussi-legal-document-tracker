import { useEffect, useMemo, useRef, useState, ChangeEvent } from "react";
import EncumbranceTable from "./components/EncumbranceTable";
import AgreementsTable from "./components/AgreementsTable";
import PlanSection from "./components/PlanSection";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";

import type {
  EncumbranceRow,
  AgreementRow,
  PlanRow,
  TitleData,
  TrackerState,
  EncumbranceAction,
  EncumbranceStatus,
  DocumentCategory,
  Surveyor,
  DocumentTask,
  DocumentTaskStatus,
} from "./types";

import {
  importTitle as importTitleApi,
  deleteTitle,
  generateDocuments,
  fetchProjectByNumber,
  fetchSurveyors,
  createProject,
  createEncumbrance,
  updateEncumbrance,
  deleteEncumbrance,
  fetchEncumbranceActions,
  fetchEncumbranceStatuses,
  fetchDocumentCategories,
  createDocumentCategory,
  fetchDocumentTasks,
  createDocumentTask,
  updateDocumentTask,
  deleteDocumentTask,
  exportProjectToExcel,
  blankTitle,
  fetchDocumentStatuses,
} from "./services/docTrackerApi";
import "./App.css";

const PROGRAM_METADATA = {
  program_name: "USSI DOCUMENT TRACKER",
  program_version: "V.4.0",
  file_version: 1,
};

const uniqueId = (): string =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random()}`;

// These need to be functions that capture current state
const createEncumbranceRow = (encActions: EncumbranceAction[], encStatuses: EncumbranceStatus[]): EncumbranceRow => ({
  id: uniqueId(),
  "Document #": "",
  Description: "",
  Signatories: "",
  action_id: encActions[0]?.id ?? null,
  "Circulation Notes": "",
  status_id: encStatuses[0]?.id ?? null,
});

const createAgreementRow = (statusOptions: DocumentTaskStatus[]): AgreementRow => ({
  id: uniqueId(),
  "Document/Desc": "",
  "Copies/Dept": "",
  Signatories: "",
  "Condition of Approval": "",
  "Circulation Notes": "",
  status_id: statusOptions[0]?.id ?? null,
});

const createPlanRow = (statusOptions: DocumentTaskStatus[], desc = ""): PlanRow => ({
  id: uniqueId(),
  "Document/Desc": desc,
  "Copies/Dept": "",
  Signatories: "",
  "Condition of Approval": "",
  "Circulation Notes": "",
  status_id: statusOptions[0]?.id ?? null,
});


const seedPlanRows = (statusOptions: DocumentTaskStatus[]): PlanRow[] => [
  createPlanRow(statusOptions,"Surveyor's Affidavit"),
  createPlanRow(statusOptions,"Consent"),
];

const buildDefaultTracker = (): TrackerState => ({
  header: { ...PROGRAM_METADATA },
  legal_desc: "",
  existing_encumbrances_on_title: [],
  new_agreements: [],
  plans: {},
  titles: {},
});

interface BackendInstrument {
  "Document #"?: string;
  reg_number?: string;
  Description?: string;
  name?: string;
  Signatories?: string;
  signatories?: string;
  Action?: string;
  action?: string;
  "Circulation Notes"?: string;
  notes?: string;
  Status?: string;
  status?: string;
}

function mapInstrumentsToRows(insts: BackendInstrument[] | null | undefined): EncumbranceRow[] {
  if (!insts) {
    return [];
  }
  return insts.map((inst) => ({
    id: uniqueId(),
    "Document #": inst["Document #"] ?? inst.reg_number ?? "",
    Description: inst["Description"] ?? inst.name ?? "",
    Signatories: inst["Signatories"] ?? inst.signatories ?? "",
    action_id: null,
    "Circulation Notes": inst["Circulation Notes"] ?? inst.notes ?? "",
    status_id: null,
  }));
}

interface NewProjectData {
  proj_num: string;
  name: string;
  municipality: string;
  surveyor_id: number;
}

function App() {
  const [sectionOrder, setSectionOrder] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem("sectionOrder");
      return saved ? JSON.parse(saved) : ["encumbrances", "agreements", "plans"];
    } catch {
      return ["encumbrances", "agreements", "plans"];
    }
  });

  const [planOrder, setPlanOrder] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem("planOrder");
      return saved ? JSON.parse(saved) : ["SUB1"];
    } catch {
      return ["SUB1"];
    }
  });

  const [tracker, setTracker] = useState<TrackerState>(() => buildDefaultTracker());
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [selectedPlanType, setSelectedPlanType] = useState("");
  const [isAddingNewPlanType, setIsAddingNewPlanType] = useState(false);
  const [newPlanTypeCode, setNewPlanTypeCode] = useState("");
  const [newPlanTypeName, setNewPlanTypeName] = useState("");
  const [newTitleName, setNewTitleName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [surveyors, setSurveyors] = useState<Surveyor[]>([]);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [newProjectData, setNewProjectData] = useState<NewProjectData>({
    proj_num: "",
    name: "",
    municipality: "",
    surveyor_id: 0,
  });
  const encumbranceSaveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const documentTaskSaveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const [encActions, setEncActions] = useState<EncumbranceAction[]>([]);
  const [docStatuses, setDocStatuses] = useState<DocumentTaskStatus[]>([]);
  const [encStatuses, setEncStatuses] = useState<EncumbranceStatus[]>([]);
  const [docCategories, setDocCategories] = useState<DocumentCategory[]>([]);
  const [currentProjectId, setCurrentProjectId] = useState<number | null>(null);

  const buildEncumbrancePayload = (row: EncumbranceRow) => ({
    document_number: row["Document #"],
    description: row.Description,
    signatories: row.Signatories,
    action_id: row.action_id,
    circulation_notes: row["Circulation Notes"],
    status_id: row.status_id,
  });

  useEffect(() => {
    const loadSurveyors = async () => {
      try {
        const data = await fetchSurveyors();
        setSurveyors(data);
      } catch (err) {
        console.error("Failed to fetch surveyors:", err);
      }
    };
    loadSurveyors();
  }, []);

  useEffect(() => {
    if (docStatuses.length > 0 && tracker.new_agreements.length === 1 && tracker.plans.SUB1.length === 2) {
      // Rebuild default rows with real status IDs
      setTracker(buildDefaultTracker());
    }
  }, [docStatuses]);

  useEffect(() => {
    const loadLookups = async () => {
      try {
        const [actions, statuses, categories,dstatuses] = await Promise.all([
          fetchEncumbranceActions(),
          fetchEncumbranceStatuses(),
          fetchDocumentCategories(),
          fetchDocumentStatuses()
        ]);
        setEncActions(actions);
        setEncStatuses(statuses);
        setDocCategories(categories);
        setDocStatuses(dstatuses)
      } catch (err) {
        console.error("Failed to load lookups:", err);
      }
    };

    loadLookups();
  }, []);

  const handleProjectNotFound = (projNum: string) => {
    setNewProjectData({
      proj_num: projNum,
      name: `Project ${projNum}`,
      municipality: "",
      surveyor_id: 0,
    });
    setShowCreateProjectModal(true);
  };

  const mapTaskToRow = (task: DocumentTask): AgreementRow => ({
    id: uniqueId(),
    backend_id: task.id,
    "Document/Desc": task.doc_desc || "",
    "Copies/Dept": task.copies_dept || "",
    Signatories: task.signatories || "",
    "Condition of Approval": task.condition_of_approval || "",
    "Circulation Notes": task.circulation_notes || "",
    status_id: task.document_status?.id || 0,
    item_no: task.item_no,
    category_id: task.category_id,
  });

  const buildDocumentTaskPayload = (
    row: AgreementRow | PlanRow,
    projectId: number,
    categoryId: number | null,
    itemNo: number
  ) => ({
    project_id: projectId,
    category_id: categoryId,
    item_no: itemNo,
    doc_desc: row["Document/Desc"] || null,
    copies_dept: row["Copies/Dept"] || null,
    signatories: row.Signatories || null,
    condition_of_approval: row["Condition of Approval"] || null,
    circulation_notes: row["Circulation Notes"] || null,
  });

  const organizeDocumentTasks = (
    tasks: DocumentTask[],
    categories: DocumentCategory[]
  ): { newAgreements: AgreementRow[]; plans: Record<string, PlanRow[]> } => {
    const newAgreements: AgreementRow[] = [];
    const plans: Record<string, PlanRow[]> = {};

    tasks.forEach((task) => {
      const row = mapTaskToRow(task);
      if (task.category_id === null) {
        newAgreements.push(row);
      } else {
        const category = categories.find((c) => c.id === task.category_id);
        const planKey = category?.code || `PLAN-${task.category_id}`;
        if (!plans[planKey]) {
          plans[planKey] = [];
        }
        plans[planKey].push(row);
      }
    });

    return { newAgreements, plans };
  };

  const planEntries = useMemo(() => {
    const plans = tracker.plans ?? {};
    return planOrder.filter((name) => plans[name]).map((name) => [name, plans[name]] as [string, PlanRow[]]);
  }, [tracker.plans, planOrder]);

  const titleEntries = useMemo(() => {
    const titles = tracker.titles ?? {};
    return Object.entries(titles);
  }, [tracker.titles]);

  useEffect(() => {
    try {
      localStorage.setItem("sectionOrder", JSON.stringify(sectionOrder));
    } catch {
      // Ignore localStorage errors
    }
  }, [sectionOrder]);

  useEffect(() => {
    try {
      localStorage.setItem("planOrder", JSON.stringify(planOrder));
    } catch {
      // Ignore localStorage errors
    }
  }, [planOrder]);

  useEffect(() => {
    if (tracker?.plans) {
      const existingNames = Object.keys(tracker.plans);
      const fromBackend = tracker.plan_order ?? existingNames;

      const synced = fromBackend.filter((name) => existingNames.includes(name));
      const extras = existingNames.filter((name) => !synced.includes(name));

      setPlanOrder([...synced, ...extras]);
    }
  }, [tracker.plans, tracker.plan_order]);

  const updateTracker = (transform: (prev: TrackerState) => Partial<TrackerState>) => {
    setTracker((prev) => ({
      ...prev,
      header: prev.header ?? { ...PROGRAM_METADATA },
      ...transform(prev),
    }));
  };

  const handleAgreementFieldChange = (index: number, field: string, value: string) => {
    updateTracker((prev) => {
      const updatedRow = { ...prev.new_agreements[index], [field]: value };
      debounceSaveDocumentTask(updatedRow, null, index + 1);
      return {
        new_agreements: prev.new_agreements.map((row, idx) =>
          idx === index ? updatedRow : row
        ),
      };
    });
  };

  const handlePlanFieldChange = (planName: string, index: number, field: string, value: string) => {
    updateTracker((prev) => {
      const planRows = prev.plans?.[planName] ?? [];
      const updatedRow = { ...planRows[index], [field]: value };
      const category = docCategories.find((c) => c.code === planName);
      debounceSaveDocumentTask(updatedRow, category?.id ?? null, index + 1);
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: planRows.map((row, idx) => (idx === index ? updatedRow : row)),
        },
      };
    });
  };

  const debounceSaveDocumentTask = (row: AgreementRow | PlanRow, categoryId: number | null, itemNo: number) => {
    const taskId = row.backend_id;
    if (!taskId || !currentProjectId) return;

    const key = `task-${taskId}`;
    if (documentTaskSaveTimers.current[key]) {
      clearTimeout(documentTaskSaveTimers.current[key]);
    }

    documentTaskSaveTimers.current[key] = setTimeout(async () => {
      try {
        const payload = buildDocumentTaskPayload(row, currentProjectId, categoryId, itemNo);
        await updateDocumentTask(taskId, payload);
      } catch (err) {
        console.error(`Failed to autosave document task ${taskId}`, err);
      }
    }, 500);
  };

  const addAgreementRow = async () => {
    const newRow = createAgreementRow(docStatuses);

    if (currentProjectId) {
      try {
        const payload = buildDocumentTaskPayload(newRow, currentProjectId, null, tracker.new_agreements.length + 1);
        const created = await createDocumentTask(payload);
        newRow.backend_id = created.id;
      } catch (err) {
        console.error("Failed to create agreement row in backend:", err);
      }
    }

    updateTracker((prev) => ({
      new_agreements: [...prev.new_agreements, newRow],
    }));
  };

  const removeAgreementRow = async () => {
    const rows = tracker.new_agreements;
    if (rows.length === 0) return;

    const lastRow = rows[rows.length - 1];

    if (lastRow.backend_id) {
      try {
        await deleteDocumentTask(lastRow.backend_id);
      } catch (err) {
        console.error("Failed to delete agreement row from backend:", err);
      }
    }

    updateTracker((prev) => ({
      new_agreements: prev.new_agreements.slice(0, Math.max(prev.new_agreements.length - 1, 0)),
    }));
  };

  const addPlanRow = async (planName: string) => {
    const newRow = createPlanRow(docStatuses);
    const category = docCategories.find((c) => c.code === planName);
    const planRows = tracker.plans?.[planName] ?? [];

    if (currentProjectId && category) {
      try {
        const payload = buildDocumentTaskPayload(newRow, currentProjectId, category.id, planRows.length + 1);
        const created = await createDocumentTask(payload);
        newRow.backend_id = created.id;  // <-- assign backend_id here
      } catch (err) {
        console.error("Failed to create plan row in backend:", err);
      }
    }

    updateTracker((prev) => ({
      plans: {
        ...(prev.plans ?? {}),
        [planName]: [...planRows, newRow],
      },
    }));
  };


  const removePlanRow = async (planName: string) => {
    const planRows = tracker.plans?.[planName] ?? [];
    if (planRows.length === 0) return;

    const lastRow = planRows[planRows.length - 1];

    if (lastRow.backend_id) {
      try {
        await deleteDocumentTask(lastRow.backend_id);
      } catch (err) {
        console.error("Failed to delete plan row from backend:", err);
      }
    }

    updateTracker((prev) => {
      const rows = prev.plans?.[planName] ?? [];
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: rows.slice(0, Math.max(rows.length - 1, 0)),
        },
      };
    });
  };

  const removePlan = async (planName: string) => {
    const planRows = tracker.plans?.[planName] ?? [];

    for (const row of planRows) {
      if (row.backend_id) {
        try {
          await deleteDocumentTask(row.backend_id);
        } catch (err) {
          console.error(`Failed to delete plan row ${row.backend_id}:`, err);
        }
      }
    }

    updateTracker((prev) => {
      const updatedPlans = { ...prev.plans };
      delete updatedPlans[planName];
      return {
        plans: updatedPlans,
      };
    });
  };

  useEffect(() => {
    setPlanOrder((prev) => prev.filter((name) => typeof tracker.plans?.[name] !== "undefined"));
  }, [tracker.plans]);

  const handleCreatePlan = async () => {
    let category: DocumentCategory | undefined;
    let planCode: string;

    if (isAddingNewPlanType) {
      const code = newPlanTypeCode.trim().toUpperCase();
      const name = newPlanTypeName.trim();

      if (!code || !name) {
        setStatus("Please enter both code and name for the new plan type.");
        return;
      }

      if (docCategories.find((c) => c.code === code)) {
        setStatus(`Plan type "${code}" already exists. Please select it from the dropdown.`);
        return;
      }

      try {
        category = await createDocumentCategory(code, name);
        setDocCategories((prev) => [...prev, category!]);
        planCode = code;
      } catch (err) {
        setStatus(`Failed to create plan type: ${(err as Error).message}`);
        return;
      }
    } else {
      if (!selectedPlanType) {
        setStatus("Please select a plan type.");
        return;
      }
      category = docCategories.find((c) => c.code === selectedPlanType);
      planCode = selectedPlanType;
    }

    if (tracker.plans?.[planCode]) {
      setStatus(`Plan ${planCode} already exists for this project.`);
      return;
    }

    const initialRows = seedPlanRows(docStatuses);

    if (currentProjectId && category) {
      for (let i = 0; i < initialRows.length; i++) {
        try {
          const payload = buildDocumentTaskPayload(initialRows[i], currentProjectId, category.id, i + 1);
          const created = await createDocumentTask(payload);
          initialRows[i].backend_id = created.id;
        } catch (err) {
          console.error("Failed to create plan row in backend:", err);
        }
      }
    }

    updateTracker((prev) => ({
      plans: {
        ...(prev.plans ?? {}),
        [planCode]: initialRows,
      },
    }));

    setPlanOrder((prev) => {
      if (prev.includes(planCode)) return prev;
      return [...prev, planCode];
    });

    setSelectedPlanType("");
    setIsAddingNewPlanType(false);
    setNewPlanTypeCode("");
    setNewPlanTypeName("");
  };

  const handleCreateTitle = async () => {
    const cleaned = newTitleName.trim().toUpperCase();
    if (!cleaned || !currentProjectId) return;

    setLoading(true);

    try {
      const created = await blankTitle(currentProjectId, cleaned);

      const titleKey = `TITLE-${created.id}`;

      updateTracker((prev) => ({
        titles: {
          ...(prev.titles ?? {}),
          [titleKey]: {
            legal_desc: "",
            existing_encumbrances_on_title: [],
          },
        },
      }));

      setStatus(`Title ${cleaned} created.`);
      setNewTitleName("");
    } catch (err) {
      console.error("Failed to create blank title:", err);
      setStatus("Failed to create title.");
    } finally {
      setLoading(false);
    }
  };


  const triggerFilePicker = () => {
    fileInputRef.current?.click();
  };

  const handleImportTitle = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    if (!currentProjectId) {
      setStatus("Please load a project first before importing a title.");
      return;
    }
    setLoading(true);
    try {
      const payload = await importTitleApi(currentProjectId,file);
      console.log("Imported payload:", payload);
      const importedRows =
        payload?.existing_encumbrances_on_title ??
        payload?.inst_on_title ??
        payload?.encumbrances ??
        payload?.instruments;
      if (importedRows && importedRows.length > 0) {
        updateTracker((prev) => ({
          existing_encumbrances_on_title: mapInstrumentsToRows(importedRows as BackendInstrument[]),
          legal_desc: payload?.legal_desc ?? prev.legal_desc,
        }));
        await reloadTracker();
        setStatus(`Imported ${importedRows.length} instruments from title certificate.`);
      } else {
        setStatus("Import finished, but no instruments were returned.");
      }
    } catch (error) {
      setStatus(`Unable to import title: ${(error as Error).message}`);
    } finally {
      setLoading(false);
      if (event.target) {
        event.target.value = "";
      }
    }
  };

  const reloadTracker = async () => {
    const projNum = tracker.project_number?.trim();
    if (!projNum) return;

    setLoading(true);
    setStatus("Loading project...");

    try {
      const project = await fetchProjectByNumber(projNum);

      if (project) {
        setCurrentProjectId(project.id);

        const titles: Record<string, TitleData> = {};
        project.title_documents?.forEach((td) => {
          titles[`TITLE-${td.id}`] = {
            legal_desc: "",
            existing_encumbrances_on_title:
              td.encumbrances?.map((e) => ({
                id: uniqueId(),
                backend_id: e.id,
                "Document #": e.document_number || "",
                Description: e.description || "",
                Signatories: e.signatories || "",
                action_id: e.action_id ?? null,
                "Circulation Notes": e.circulation_notes || "",
                status_id: e.status_id ?? null,
              })) || [],
          };
        });

        const documentTasks = await fetchDocumentTasks(project.id);
        const { newAgreements, plans } = organizeDocumentTasks(documentTasks, docCategories);

        let finalNewAgreements = newAgreements;
        if (newAgreements.length === 0) {
          const defaultRow = createAgreementRow(docStatuses);
          try {
            const payload = buildDocumentTaskPayload(defaultRow, project.id, null, 1);
            const created = await createDocumentTask(payload);
            defaultRow.backend_id = created.id;
          } catch (err) {
            console.error("Failed to create default agreement row:", err);
          }
          finalNewAgreements = [defaultRow];
        }

        const existingPlanKeys = Object.keys(plans);

        setTracker({
          header: { ...PROGRAM_METADATA },
          project_number: project.proj_num,
          legal_desc: "",
          existing_encumbrances_on_title: [],
          new_agreements: finalNewAgreements,
          plans,
          titles,
        });
        setPlanOrder(existingPlanKeys);
        setStatus(`Project ${projNum} loaded successfully.`);
      }
    } catch (err) {
      if ((err as Error).message.includes("404")) {
        handleProjectNotFound(projNum);
        setStatus(`Project ${projNum} not found. Please enter details to create a new project.`);
      } else {
        setStatus(`Failed to load project: ${(err as Error).message}`);
        console.error(err);
      }
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
      setStatus(`Document generation failed: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = async () => {
    if (!currentProjectId) {
      setStatus("Please load a project first.");
      return;
    }

    setLoading(true);
    setStatus("Exporting to Excel...");
    try {
      const filename = await exportProjectToExcel(currentProjectId);
      setStatus(`Exported successfully: ${filename}`);
    } catch (error) {
      setStatus(`Export failed: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const onDragEnd = (result: DropResult) => {
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
        rows.splice(result.destination!.index, 0, moved);
        return { existing_encumbrances_on_title: rows };
      });
    }
  };

  const debounceSaveEncumbrance = (row: EncumbranceRow) => {
    const encId = row.backend_id;
    if (!encId) return;

    if (encumbranceSaveTimers.current[encId]) {
      clearTimeout(encumbranceSaveTimers.current[encId]);
    }

    encumbranceSaveTimers.current[encId] = setTimeout(async () => {
      try {
        await updateEncumbrance(encId, buildEncumbrancePayload(row));
      } catch (err) {
        console.error(`Failed to autosave encumbrance ${encId}`, err);
      }
    }, 500);
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <h1>USSI Document Tracker</h1>
          <span className="version">{PROGRAM_METADATA.program_version}</span>
        </div>
        <div className="header-project">
          <label>Project</label>
          <input
            type="text"
            value={tracker.project_number ?? ""}
            onChange={(e) => updateTracker(() => ({ project_number: e.target.value }))}
            placeholder="Enter project #..."
          />
          <button
            type="button"
            onClick={reloadTracker}
            disabled={loading || !tracker.project_number?.trim()}
          >
            Load
          </button>
        </div>
      </header>

      {showCreateProjectModal && (
        <section className="create-project-bar">
          <span className="bar-title">New Project</span>
          <div className="bar-field">
            <label>Name</label>
            <input
              type="text"
              value={newProjectData.name}
              onChange={(e) => setNewProjectData((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="Project name..."
            />
          </div>
          <div className="bar-field">
            <label>Municipality</label>
            <input
              type="text"
              value={newProjectData.municipality}
              onChange={(e) =>
                setNewProjectData((prev) => ({ ...prev, municipality: e.target.value }))
              }
              placeholder="Municipality..."
            />
          </div>
          <div className="bar-field">
            <label>Surveyor</label>
            <select
              value={newProjectData.surveyor_id}
              onChange={(e) =>
                setNewProjectData((prev) => ({ ...prev, surveyor_id: Number(e.target.value) }))
              }
            >
              <option value={0}>Select...</option>
              {surveyors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.city})
                </option>
              ))}
            </select>
          </div>
          <div className="bar-actions">
            <button
              onClick={async () => {
                try {
                  const project = await createProject(newProjectData);
                  setShowCreateProjectModal(false);
                  setTracker((prev) => ({ ...prev, project_number: project.proj_num }));
                  reloadTracker();
                } catch (err) {
                  alert("Failed to create project: " + (err as Error).message);
                }
              }}
            >
              Create
            </button>
            <button className="btn-secondary" onClick={() => setShowCreateProjectModal(false)}>
              Cancel
            </button>
          </div>
        </section>
      )}

      <section className="toolbar">
        <div className="toolbar__group">
          <button onClick={triggerFilePicker} disabled={loading}>
            Import Title (PDF)
          </button>
          <button onClick={reloadTracker} disabled={loading}>
            Reload Tracker
          </button>
          <button onClick={runDocumentGeneration} disabled={loading}>
            Generate Documents
          </button>
          <button
            onClick={handleExportExcel}
            disabled={loading || !currentProjectId}
            title={!currentProjectId ? "Load a project first" : "Export to Excel"}
          >
            Export to Excel
          </button>
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            onChange={handleImportTitle}
            style={{ display: "none" }}
          />
        </div>
        <div className="status-line">{loading ? "Working..." : status || ""}</div>
      </section>

      <section className="sections">
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="sections" type="SECTION">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {sectionOrder.map((sec, index) => (
                  <Draggable key={sec} draggableId={sec} index={index}>
                    {(providedSection) => (
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
                              {(providedEnc) => (
                                <div ref={providedEnc.innerRef} {...providedEnc.droppableProps}>
                                  {titleEntries.length === 0 ? (
                                    <p className="empty-row">
                                      Import Title (PDF) to populate existing encumbrances on title.
                                    </p>
                                  ) : (
                                    titleEntries.map(([titleName, titleData]) => (
                                      <EncumbranceTable
                                        key={titleName}
                                        name={titleName}
                                        rows={titleData.existing_encumbrances_on_title ?? []}
                                        actions={encActions}
                                        statuses={encStatuses}
                                        onFieldChange={(
                                          _name: string,
                                          rowIndex: number,
                                          field: string,
                                          value: string | number
                                        ) => {
                                          updateTracker((prev) => {
                                            const updatedTitles = { ...prev.titles };
                                            const rows =
                                              updatedTitles[titleName].existing_encumbrances_on_title;

                                            const updatedRow = {
                                              ...rows[rowIndex],
                                              [field]: value,
                                            };

                                            updatedTitles[titleName] = {
                                              ...updatedTitles[titleName],
                                              existing_encumbrances_on_title: rows.map((row, i) =>
                                                i === rowIndex ? { ...row, [field]: value } : row
                                              ),
                                            };
                                            debounceSaveEncumbrance(updatedRow);
                                            return { titles: updatedTitles };
                                          });
                                        }}
                                        onAddRow={async () => {
                                          const newRow = createEncumbranceRow(encActions, encStatuses);
                                          const titleDocId = parseInt(
                                            titleName.replace("TITLE-", ""),
                                            10
                                          );

                                          if (titleDocId) {
                                            try {
                                              const rows =
                                                tracker.titles[titleName]
                                                  ?.existing_encumbrances_on_title ?? [];
                                              const created = await createEncumbrance({
                                                title_document_id: titleDocId,
                                                item_no: rows.length + 1,
                                                document_number: "",
                                                description: "",
                                                signatories: "",
                                                circulation_notes: "",
                                              });
                                              newRow.backend_id = created.id;
                                            } catch (err) {
                                              console.error("Failed to create encumbrance:", err);
                                            }
                                          }

                                          updateTracker((prev) => {
                                            const rows =
                                              prev.titles[titleName].existing_encumbrances_on_title ??
                                              [];
                                            return {
                                              titles: {
                                                ...prev.titles,
                                                [titleName]: {
                                                  ...prev.titles[titleName],
                                                  existing_encumbrances_on_title: [...rows, newRow],
                                                },
                                              },
                                            };
                                          });
                                        }}
                                        onRemoveRow={async () => {
                                          const rows =
                                            tracker.titles[titleName]?.existing_encumbrances_on_title ??
                                            [];
                                          if (rows.length === 0) return;

                                          const lastRow = rows[rows.length - 1];

                                          if (lastRow.backend_id) {
                                            try {
                                              await deleteEncumbrance(lastRow.backend_id);
                                            } catch (err) {
                                              console.error("Failed to delete encumbrance:", err);
                                            }
                                          }

                                          updateTracker((prev) => {
                                            const currentRows =
                                              prev.titles[titleName].existing_encumbrances_on_title ??
                                              [];
                                            return {
                                              titles: {
                                                ...prev.titles,
                                                [titleName]: {
                                                  ...prev.titles[titleName],
                                                  existing_encumbrances_on_title: currentRows.slice(
                                                    0,
                                                    Math.max(currentRows.length - 1, 0)
                                                  ),
                                                },
                                              },
                                            };
                                          });
                                        }}
                                        onRemoveTitle={async () => {
                                          const titleDocId = parseInt(titleName.replace("TITLE-", ""), 10);
                                          if (!titleDocId) return;

                                          setLoading(true);
                                          try {
                                            await deleteTitle(titleDocId); // <-- call your new API function
                                            updateTracker((prev) => {
                                              const updatedTitles = { ...prev.titles };
                                              delete updatedTitles[titleName];
                                              return { titles: updatedTitles };
                                            });
                                            setStatus(`Title ${titleName} deleted successfully.`);
                                          } catch (err) {
                                            console.error("Failed to delete title:", err);
                                            setStatus(`Failed to delete title ${titleName}.`);
                                          } finally {
                                            setLoading(false);
                                          }
                                        }}
                                      />
                                    ))
                                  )}

                                  {providedEnc.placeholder}
                                </div>
                              )}
                            </Droppable>
                          </section>
                        )}

                        {sec === "agreements" && (
                          <AgreementsTable
                            rows={tracker.new_agreements ?? []}
                            statusOptions={docStatuses}
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
                                {!isAddingNewPlanType ? (
                                  <>
                                    <select
                                      value={selectedPlanType}
                                      onChange={(e) => {
                                        if (e.target.value === "__NEW__") {
                                          setIsAddingNewPlanType(true);
                                          setSelectedPlanType("");
                                        } else {
                                          setSelectedPlanType(e.target.value);
                                        }
                                      }}
                                    >
                                      <option value="">Select plan type...</option>
                                      {docCategories
                                        .filter((c) => !tracker.plans?.[c.code])
                                        .map((cat) => (
                                          <option key={cat.id} value={cat.code}>
                                            {cat.name} ({cat.code})
                                          </option>
                                        ))}
                                      <option value="__NEW__">+ Add New Plan Type...</option>
                                    </select>
                                    <button
                                      type="button"
                                      onClick={handleCreatePlan}
                                      disabled={!selectedPlanType}
                                    >
                                      + Plan
                                    </button>
                                  </>
                                ) : (
                                  <>
                                    <input
                                      value={newPlanTypeCode}
                                      onChange={(e) =>
                                        setNewPlanTypeCode(e.target.value.toUpperCase())
                                      }
                                      placeholder="Code (e.g., URW)"
                                      style={{ width: "100px" }}
                                    />
                                    <input
                                      value={newPlanTypeName}
                                      onChange={(e) => setNewPlanTypeName(e.target.value)}
                                      placeholder="Name (e.g., Utility Right of Way)"
                                      style={{ width: "200px" }}
                                    />
                                    <button
                                      type="button"
                                      onClick={handleCreatePlan}
                                      disabled={!newPlanTypeCode.trim() || !newPlanTypeName.trim()}
                                    >
                                      Create & Add
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => {
                                        setIsAddingNewPlanType(false);
                                        setNewPlanTypeCode("");
                                        setNewPlanTypeName("");
                                      }}
                                      className="btn-secondary"
                                    >
                                      Cancel
                                    </button>
                                  </>
                                )}
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
                                        {(providedPlan) => (
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
                                              statusOptions={docStatuses}
                                              onFieldChange={handlePlanFieldChange}
                                              onAddRow={() => addPlanRow(planName)}
                                              onRemoveRow={() => removePlanRow(planName)}
                                              onRemovePlan={(name) => {
                                                removePlan(name);
                                                setPlanOrder((prev) =>
                                                  prev.filter((n) => n !== name)
                                                );
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

