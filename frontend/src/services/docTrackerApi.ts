import type {
  Project,
  Surveyor,
  Encumbrance,
  EncumbranceAction,
  EncumbranceStatus,
  DocumentCategory,
  DocumentTask,
  CreateProjectPayload,
  EncumbranceCreatePayload,
  EncumbranceUpdatePayload,
  DocumentTaskCreatePayload,
  DocumentTaskUpdatePayload,
  ImportTitleResponse,
} from '../types';

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `API request failed (${response.status} ${response.statusText}): ${text}`,
    );
  }
  if (response.status === 204) {
    return null as T;
  }
  return response.json();
}

export async function deleteTitle(titleId: number): Promise<null> {
  if (!titleId) throw new Error("Title ID is required");
  try {
    return request<null>(`/titles/${titleId}`, {
    method: "DELETE",
  });
  } catch (error) {
    console.error("Delete title failed:", (error as Error).message);
    throw error;
  }
}

export async function importTitle(projectId: number, file: File): Promise<ImportTitleResponse> {
  const formData = new FormData();
  formData.append("file", file);
  try {
    return await request<ImportTitleResponse>(                                                                                                                                                                                                                                                                                                                                                                                                                                         `/titles?project_id=${projectId}`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    console.error("Import title failed:", (error as Error).message);
    throw error;
  }
}

export async function generateDocuments(payload: { tracker: unknown; legal_desc: string }): Promise<unknown> {
  try {
    return await request("/documents/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error("Document generation failed:", (error as Error).message);
    throw error;
  }
}

export async function fetchProjectByNumber(projNum: string): Promise<Project> {
  if (!projNum) throw new Error("Project number is required");
  return await request<Project>(`/projects/by-number/${encodeURIComponent(projNum)}`);
}

export async function fetchSurveyors(): Promise<Surveyor[]> {
  return await request<Surveyor[]>("/projects/surveyors", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
}

export async function createProject(projectData: CreateProjectPayload): Promise<Project> {
  try {
    return await request<Project>("/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectData),
    });
  } catch (error) {
    console.error("Project creation failed:", (error as Error).message);
    throw error;
  }
}

export async function createEncumbrance(payload: EncumbranceCreatePayload): Promise<Encumbrance> {
  return await request<Encumbrance>("/titles/encumbrances", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateEncumbrance(encumbranceId: number, payload: EncumbranceUpdatePayload): Promise<Encumbrance> {
  if (!encumbranceId) {
    throw new Error("Encumbrance ID is required");
  }

  return await request<Encumbrance>(`/titles/encumbrances/${encumbranceId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteEncumbrance(encumbranceId: number): Promise<null> {
  if (!encumbranceId) {
    throw new Error("Encumbrance ID is required");
  }

  return await request<null>(`/titles/encumbrances/${encumbranceId}`, {
    method: "DELETE",
  });
}

export async function fetchEncumbranceActions(): Promise<EncumbranceAction[]> {
  return request<EncumbranceAction[]>("/lookups/encumbrance-actions");
}

export async function fetchEncumbranceStatuses(): Promise<EncumbranceStatus[]> {
  return request<EncumbranceStatus[]>("/lookups/encumbrance-statuses");
}

// Document Categories (for plan types)
export async function fetchDocumentCategories(): Promise<DocumentCategory[]> {
  return request<DocumentCategory[]>("/documents/category");
}

export async function createDocumentCategory(code: string, name: string): Promise<DocumentCategory> {
  return request<DocumentCategory>("/documents/category", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, name }),
  });
}

// Document Tasks (Plans & New Agreements)
export async function fetchDocumentTasks(projectId: number): Promise<DocumentTask[]> {
  if (!projectId) throw new Error("Project ID is required");
  return request<DocumentTask[]>(`/documents?project_id=${projectId}&limit=1000`);
}

export async function createDocumentTask(payload: DocumentTaskCreatePayload): Promise<DocumentTask> {
  return request<DocumentTask>("/documents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateDocumentTask(taskId: number, payload: DocumentTaskUpdatePayload): Promise<DocumentTask> {
  if (!taskId) throw new Error("Task ID is required");
  return request<DocumentTask>(`/documents/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteDocumentTask(taskId: number): Promise<null> {
  if (!taskId) throw new Error("Task ID is required");
  return request<null>(`/documents/${taskId}`, {
    method: "DELETE",
  });
}

// Export project to Excel
export async function exportProjectToExcel(projectId: number): Promise<string> {
  if (!projectId) throw new Error("Project ID is required");
  
  const url = `${API_BASE}/projects/${projectId}/export-excel`;
  const response = await fetch(url);
  
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Export failed (${response.status}): ${text}`);
  }
  
  // Get filename from Content-Disposition header or use default
  const contentDisposition = response.headers.get("Content-Disposition");
  let filename = "document_tracking.xlsx";
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="(.+)"/);
    if (match) filename = match[1];
  }
  
  // Download the file
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
  
  return filename;
}

