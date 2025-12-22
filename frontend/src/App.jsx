import { useEffect, useMemo, useRef, useState } from "react";
import EncumbranceTable from "./components/EncumbranceTable.jsx";
import AgreementsTable from "./components/AgreementsTable.jsx";
import PlanSection from "./components/PlanSection.jsx";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

import {
  saveTracker,
  importTitle as importTitleApi,
  generateDocuments,
  fetchProjectByNumber,
  fetchSurveyors,
  createProject,
  updateEncumbrance,
  fetchEncumbranceActions,
  fetchEncumbranceStatuses,
  fetchDocumentCategories,
  createDocumentCategory,
  fetchDocumentTasks,
  createDocumentTask,
  updateDocumentTask,
  deleteDocumentTask,
  exportProjectToExcel,
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
  action_id: encActions[0]?.id ?? null,
  "Circulation Notes": "",
  status_id: encStatuses[0]?.id ?? null,
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
];

const buildDefaultTracker = () => ({
  header: { ...PROGRAM_METADATA },
  legal_desc: "",
  existing_encumbrances_on_title: [], // start blank
  new_agreements: [createAgreementRow()],                 // start blank
  plans: { "SUB1": seedPlanRows() },  // default SUB1 plan
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
      return saved ? JSON.parse(saved) : ["SUB1"];
    } catch {
      return ["SUB1"];
    }
  });
  const [tracker, setTracker] = useState(() => buildDefaultTracker());
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [selectedPlanType, setSelectedPlanType] = useState("");
  const [isAddingNewPlanType, setIsAddingNewPlanType] = useState(false);
  const [newPlanTypeCode, setNewPlanTypeCode] = useState("");
  const [newPlanTypeName, setNewPlanTypeName] = useState("");
  const [newTitleName, setNewTitleName] = useState("");
  const fileInputRef = useRef(null);
  const [projectNumber, setProjectNumber] = useState("");
  const [surveyors, setSurveyors] = useState([]);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [newProjectData, setNewProjectData] = useState({
    proj_num: "",
    name: "",
    municipality: "",
    surveyor_id: 0,
  });
  const encumbranceSaveTimers = useRef({});
  const documentTaskSaveTimers = useRef({});
  const [encActions, setEncActions] = useState([]);
  const [encStatuses, setEncStatuses] = useState([]);
  const [docCategories, setDocCategories] = useState([]);
  const [currentProjectId, setCurrentProjectId] = useState(null);

  const buildEncumbrancePayload = (row) => ({
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
    const loadLookups = async () => {
      try {
        const [actions, statuses, categories] = await Promise.all([
          fetchEncumbranceActions(),
          fetchEncumbranceStatuses(),
          fetchDocumentCategories(),
        ]);
        setEncActions(actions);
        setEncStatuses(statuses);
        setDocCategories(categories);
      } catch (err) {
        console.error("Failed to load lookups:", err);
      }
    };

    loadLookups();
  }, []);


  const handleProjectNotFound = (projNum) => {
    setNewProjectData({ proj_num: projNum, name: `Project ${projNum}`, municipality: "", surveyor_id: 0 });
    setShowCreateProjectModal(true);
  };

  // Helper: Map backend DocumentTask to frontend row format
  const mapTaskToRow = (task) => ({
    id: uniqueId(),
    backend_id: task.id,
    "Document/Desc": task.doc_desc || "",
    "Copies/Dept": task.copies_dept || "",
    Signatories: task.signatories || "",
    "Condition of Approval": task.condition_of_approval || "",
    "Circulation Notes": task.circulation_notes || "",
    Status: task.document_status?.label || STATUS_OPTIONS[0],
    item_no: task.item_no,
    category_id: task.category_id,
  });

  // Helper: Build payload for creating/updating a DocumentTask
  const buildDocumentTaskPayload = (row, projectId, categoryId, itemNo) => ({
    project_id: projectId,
    category_id: categoryId,
    item_no: itemNo,
    doc_desc: row["Document/Desc"] || null,
    copies_dept: row["Copies/Dept"] || null,
    signatories: row.Signatories || null,
    condition_of_approval: row["Condition of Approval"] || null,
    circulation_notes: row["Circulation Notes"] || null,
  });

  // Helper: Organize document tasks into new_agreements and plans
  const organizeDocumentTasks = (tasks, categories) => {
    const newAgreements = [];
    const plans = {};

    tasks.forEach((task) => {
      const row = mapTaskToRow(task);
      if (task.category_id === null) {
        // New Agreements
        newAgreements.push(row);
      } else {
        // Plans - group by category code
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

  const handleLoadProject = async () => {
    if (!projectNumber.trim()) return;
    setLoading(true);
    setStatus("Loading project...");
    try {
      const project = await fetchProjectByNumber(projectNumber.trim());
      if (!project) {
        setStatus(`Project ${projectNumber} not found.`);
        return;
      }

      // Store project ID for document task operations
      setCurrentProjectId(project.id);

      // Map project titles and encumbrances into tracker
      const titles = {};
      if (project.title_documents?.length > 0) {
        project.title_documents.forEach((td) => {
          titles[`TITLE-${td.id}`] = {
            legal_desc: "",
            existing_encumbrances_on_title: td.encumbrances?.map((e) => ({
              id: uniqueId(),
              backend_id: e.id,
              "Document #": e.document_number || "",
              Description: e.description || "",
              Signatories: e.signatories || "",
              action_id: e.action_id,
              "Circulation Notes": e.circulation_notes || "",
              status_id: e.status_id,
            })) || [],
          };
        });
      }

      // Fetch document tasks (plans & new agreements) from backend
      const documentTasks = await fetchDocumentTasks(project.id);
      const { newAgreements, plans } = organizeDocumentTasks(documentTasks, docCategories);

      // If no new agreements exist, create default empty row
      const finalNewAgreements = newAgreements.length > 0 ? newAgreements : [createAgreementRow()];
      
      // Build plan order from existing plans
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
      setStatus(`Project ${projectNumber} loaded successfully.`);
    } catch (error) {
      console.error(error);
      setStatus(`Failed to load project: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };



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
    updateTracker((prev) => {
      const updatedRow = { ...prev.new_agreements[index], [field]: value };
      // Auto-save to backend if row has backend_id
      debounceSaveDocumentTask(updatedRow, null, index + 1);
      return {
        new_agreements: prev.new_agreements.map((row, idx) =>
          idx === index ? updatedRow : row,
        ),
      };
    });
  };

  const handlePlanFieldChange = (planName, index, field, value) => {
    updateTracker((prev) => {
      const planRows = prev.plans?.[planName] ?? [];
      const updatedRow = { ...planRows[index], [field]: value };
      // Find category_id for this plan
      const category = docCategories.find((c) => c.code === planName);
      // Auto-save to backend if row has backend_id
      debounceSaveDocumentTask(updatedRow, category?.id, index + 1);
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: planRows.map((row, idx) =>
            idx === index ? updatedRow : row,
          ),
        },
      };
    });
  };

  // Debounced save for document tasks (plans & new agreements)
  const debounceSaveDocumentTask = (row, categoryId, itemNo) => {
    const taskId = row.backend_id;
    if (!taskId || !currentProjectId) return; // Skip if no backend_id or project

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

  const addAgreementRow = async () => {
    const newRow = createAgreementRow();
    
    // Create in backend if project exists
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
    
    // Delete from backend if has backend_id
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

  const addPlanRow = async (planName) => {
    const newRow = createPlanRow();
    const category = docCategories.find((c) => c.code === planName);
    const planRows = tracker.plans?.[planName] ?? [];

    // Create in backend if project exists
    if (currentProjectId && category) {
      try {
        const payload = buildDocumentTaskPayload(newRow, currentProjectId, category.id, planRows.length + 1);
        const created = await createDocumentTask(payload);
        newRow.backend_id = created.id;
      } catch (err) {
        console.error("Failed to create plan row in backend:", err);
      }
    }

    updateTracker((prev) => {
      const existingRows = prev.plans?.[planName] ?? [];
      return {
        plans: {
          ...(prev.plans ?? {}),
          [planName]: [...existingRows, newRow],
        },
      };
    });
  };

  const removePlanRow = async (planName) => {
    const planRows = tracker.plans?.[planName] ?? [];
    if (planRows.length === 0) return;

    const lastRow = planRows[planRows.length - 1];

    // Delete from backend if has backend_id
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

  const removePlan = async (planName) => {
    const planRows = tracker.plans?.[planName] ?? [];

    // Delete all rows from backend
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

  // keep planOrder in sync when plan removed
  useEffect(() => {
    // remove any planOrder entries that no longer exist in tracker.plans
    setPlanOrder((prev) => prev.filter((name) => typeof tracker.plans?.[name] !== "undefined"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tracker.plans]);

  const handleCreatePlan = async () => {
    let category;
    let planCode;

    if (isAddingNewPlanType) {
      // Create new category first
      const code = newPlanTypeCode.trim().toUpperCase();
      const name = newPlanTypeName.trim();
      
      if (!code || !name) {
        setStatus("Please enter both code and name for the new plan type.");
        return;
      }

      // Check if code already exists
      if (docCategories.find((c) => c.code === code)) {
        setStatus(`Plan type "${code}" already exists. Please select it from the dropdown.`);
        return;
      }

      try {
        category = await createDocumentCategory(code, name);
        setDocCategories((prev) => [...prev, category]);
        planCode = code;
      } catch (err) {
        setStatus(`Failed to create plan type: ${err.message}`);
        return;
      }
    } else {
      // Use selected category from dropdown
      if (!selectedPlanType) {
        setStatus("Please select a plan type.");
        return;
      }
      category = docCategories.find((c) => c.code === selectedPlanType);
      planCode = selectedPlanType;
    }

    // Check if plan already exists
    if (tracker.plans?.[planCode]) {
      setStatus(`Plan ${planCode} already exists for this project.`);
      return;
    }

    // Create initial rows
    const initialRows = seedPlanRows();

    // Create rows in backend if project exists
    if (currentProjectId) {
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

    // add to ordering
    setPlanOrder((prev) => {
      if (prev.includes(planCode)) return prev;
      return [...prev, planCode];
    });

    // Reset form
    setSelectedPlanType("");
    setIsAddingNewPlanType(false);
    setNewPlanTypeCode("");
    setNewPlanTypeName("");
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
    const projNum = tracker.project_number?.trim();
    if (!projNum) return;

    setLoading(true);
    setStatus("Loading project...");

    try {
      const project = await fetchProjectByNumber(projNum);

      if (project) {
        // Store project ID for document task operations
        setCurrentProjectId(project.id);

        // Map project data into tracker
        const titles = {};
        project.title_documents?.forEach(td => {
          titles[`TITLE-${td.id}`] = {
            legal_desc: "",
            existing_encumbrances_on_title: td.encumbrances?.map(e => ({
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

        // Fetch document tasks (plans & new agreements) from backend
        const documentTasks = await fetchDocumentTasks(project.id);
        const { newAgreements, plans } = organizeDocumentTasks(documentTasks, docCategories);

        // If no new agreements exist, create default empty row
        const finalNewAgreements = newAgreements.length > 0 ? newAgreements : [createAgreementRow()];
        
        // Build plan order from existing plans
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
      if (err.message.includes("404")) {
        handleProjectNotFound(projNum);
        setStatus(`Project ${projNum} not found. Please enter details to create a new project.`);
      } else {
        setStatus(`Failed to load project: ${err.message}`);
        console.error(err);
      }
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
      setStatus(`Export failed: ${error.message}`);
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

  const debounceSaveEncumbrance = (row) => {
    const encId = row.backend_id;
    if (!encId) return; // new rows not yet saved on backend

    // Clear existing timer
    if (encumbranceSaveTimers.current[encId]) {
      clearTimeout(encumbranceSaveTimers.current[encId]);
    }

    // Set new debounce timer
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
            onChange={(e) =>
              updateTracker(() => ({ project_number: e.target.value }))
            }
            placeholder="Enter project #..."
          />
          <button
            type="button"
            onClick={reloadTracker}
            disabled={loading || !(tracker.project_number?.trim())}
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
              onChange={(e) => setNewProjectData((prev) => ({ ...prev, municipality: e.target.value }))}
              placeholder="Municipality..."
            />
          </div>
          <div className="bar-field">
            <label>Surveyor</label>
            <select
              value={newProjectData.surveyor_id}
              onChange={(e) => setNewProjectData((prev) => ({ ...prev, surveyor_id: Number(e.target.value) }))}
            >
              <option value={0}>Select...</option>
              {surveyors.map((s) => (
                <option key={s.id} value={s.id}>{s.name} ({s.city})</option>
              ))}
            </select>
          </div>
          <div className="bar-actions">
            <button onClick={async () => {
              try {
                const project = await createProject(newProjectData);
                setShowCreateProjectModal(false);
                setTracker(prev => ({ ...prev, project_number: project.proj_num }));
                reloadTracker();
              } catch (err) {
                alert("Failed to create project: " + err.message);
              }
            }}>
              Create
            </button>
            <button className="btn-secondary" onClick={() => setShowCreateProjectModal(false)}>Cancel</button>
          </div>
        </section>
      )}


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
        <div className="status-line">
          {loading ? "Working..." : status || ""}
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
                                    <p className="empty-row">Import Title (PDF) to populate existing encumbrances on title.</p>
                                  ) : (
                                    titleEntries.map(([titleName, titleData]) => (
                                      <EncumbranceTable
                                        key={titleName}
                                        name={titleName} 
                                        rows={titleData.existing_encumbrances_on_title ?? []}
                                        actions={encActions}
                                        statuses={encStatuses}
                                        onFieldChange={(name, index, field, value) => {
                                          updateTracker((prev) => {
                                            const updatedTitles = { ...prev.titles };
                                            const rows = updatedTitles[titleName].existing_encumbrances_on_title;

                                            const updatedRow = {
                                              ...rows[index],
                                              [field]: value,
                                            };
                                            
                                            updatedTitles[titleName] = {
                                              ...updatedTitles[titleName],
                                              existing_encumbrances_on_title: rows.map((row, i) =>
                                                i === index ? { ...row, [field]: value } : row
                                              ),
                                            };
                                            debounceSaveEncumbrance(updatedRow);
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
                                        onRemoveTitle={(name) => {
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
                                        .filter((c) => !tracker.plans?.[c.code]) // Hide already added plans
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
                                      onChange={(e) => setNewPlanTypeCode(e.target.value.toUpperCase())}
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
