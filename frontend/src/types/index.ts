// API Response Types
export interface EncumbranceAction {
  id: number;
  code: string;
  label: string;
}

export interface EncumbranceStatus {
  id: number;
  code: string;
  label: string;
}

export interface DocumentCategory {
  id: number;
  code: string;
  name: string;
}

export interface DocumentTaskStatus {
  id: number;
  code: string;
  label: string;
}

export interface Surveyor {
  id: number;
  name: string;
  ftp_number: string | null;
  city: string | null;
}

export interface Encumbrance {
  id: number;
  title_document_id: number;
  item_no: number;
  document_number: string | null;
  encumbrance_date: string | null;
  description: string | null;
  signatories: string | null;
  action_id: number | null;
  status_id: number | null;
  circulation_notes: string | null;
  legal_document_id: number | null;
  action?: EncumbranceAction | null;
  status?: EncumbranceStatus | null;
}

export interface TitleDocument {
  id: number;
  project_id: number;
  file_path: string;
  uploaded_by: string | null;
  uploaded_at: string;
  encumbrances: Encumbrance[];
}

export interface DocumentTask {
  id: number;
  project_id: number;
  category_id: number | null;
  item_no: number;
  doc_desc: string | null;
  copies_dept: string | null;
  signatories: string | null;
  condition_of_approval: string | null;
  circulation_notes: string | null;
  document_status_id: number | null;
  document_status?: DocumentTaskStatus | null;
  category?: DocumentCategory | null;
}

export interface Project {
  id: number;
  proj_num: string;
  name: string;
  municipality: string | null;
  surveyor_id: number | null;
  surveyor?: Surveyor | null;
  title_documents: TitleDocument[];
  document_tasks: DocumentTask[];
}

// Frontend Row Types
export interface EncumbranceRow {
  id: string;
  backend_id?: number;
  "Document #": string;
  Description: string;
  Signatories: string;
  action_id: number | null;
  "Circulation Notes": string;
  status_id: number | null;
}

export interface AgreementRow {
  id: string;
  backend_id?: number;
  "Document/Desc": string;
  "Copies/Dept": string;
  Signatories: string;
  "Condition of Approval": string;
  "Circulation Notes": string;
  status_id: number | null;
  item_no?: number;
  category_id?: number | null;
}

export interface PlanRow extends AgreementRow {}

// Tracker State Types
export interface TitleData {
  legal_desc: string;
  existing_encumbrances_on_title: EncumbranceRow[];
}

export interface TrackerState {
  header: {
    program_name: string;
    program_version: string;
    file_version: number;
  };
  project_number?: string;
  legal_desc: string;
  existing_encumbrances_on_title: EncumbranceRow[];
  new_agreements: AgreementRow[];
  plans: Record<string, PlanRow[]>;
  plan_order?: string[];
  titles: Record<string, TitleData>;
}

// API Payload Types
export interface CreateProjectPayload {
  proj_num: string;
  name: string;
  municipality: string;
  surveyor_id: number;
}

export interface EncumbranceCreatePayload {
  title_document_id: number;
  item_no: number;
  document_number?: string;
  description?: string;
  signatories?: string;
  circulation_notes?: string;
  action_id?: number | null;
  status_id?: number | null;
}

export interface EncumbranceUpdatePayload {
  document_number?: string;
  description?: string;
  signatories?: string;
  action_id?: number | null;
  circulation_notes?: string;
  status_id?: number | null;
}

export interface DocumentTaskCreatePayload {
  project_id: number;
  category_id: number | null;
  item_no: number;
  doc_desc?: string | null;
  copies_dept?: string | null;
  signatories?: string | null;
  condition_of_approval?: string | null;
  circulation_notes?: string | null;
}

export interface DocumentTaskUpdatePayload {
  doc_desc?: string | null;
  copies_dept?: string | null;
  signatories?: string | null;
  condition_of_approval?: string | null;
  circulation_notes?: string | null;
  category_id?: number | null;
}

export interface ImportTitleResponse {
  id: any;
  encumbrances: Encumbrance[] | undefined;
  existing_encumbrances_on_title?: Encumbrance[];
  inst_on_title?: Encumbrance[];
  instruments?: Encumbrance[];
  legal_desc?: string;
}

