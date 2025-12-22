const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `API request failed (${response.status} ${response.statusText}): ${text}`,
    );
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export async function fetchTracker() {
  try {
    return await request("/tracker");
  } catch (error) {
    console.warn("Falling back to local tracker data:", error.message);
    return null;
  }
}

export async function saveTracker(trackerState) {
  try {
    await request("/tracker", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(trackerState),
    });
    return true;
  } catch (error) {
    console.error("Unable to persist tracker:", error.message);
    return false;
  }
}

export async function importTitle(file) {
  const formData = new FormData();
  formData.append("file", file);
  try {
    return await request("/import-title", {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    console.error("Import title failed:", error.message);
    throw error;
  }
}

export async function generateDocuments(payload) {
  try {
    return await request("/documents/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error("Document generation failed:", error.message);
    throw error;
  }
}

export async function fetchProjectByNumber(projNum) {
  if (!projNum) throw new Error("Project number is required");
  return await request(`/projects/by-number/${encodeURIComponent(projNum)}`);
}

export async function fetchSurveyors() {
  return await request("/projects/surveyors", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
}

export async function createProject(projectData) {
  try {
    return await request("/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectData),
    });
  } catch (error) {
    console.error("Project creation failed:", error.message);
    throw error;
  }
}

export async function updateEncumbrance(encumbranceId, payload) {
  if (!encumbranceId) {
    throw new Error("Encumbrance ID is required");
  }

  return await request(`/titles/encumbrances/${encumbranceId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchEncumbranceActions() {
  return request("/lookups/encumbrance-actions");
}

export async function fetchEncumbranceStatuses() {
  return request("/lookups/encumbrance-statuses");
}

// Document Categories (for plan types)
export async function fetchDocumentCategories() {
  return request("/documents/category");
}

export async function createDocumentCategory(code, name) {
  return request("/documents/category", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, name }),
  });
}

// Document Tasks (Plans & New Agreements)
export async function fetchDocumentTasks(projectId) {
  if (!projectId) throw new Error("Project ID is required");
  return request(`/documents?project_id=${projectId}&limit=1000`);
}

export async function createDocumentTask(payload) {
  return request("/documents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateDocumentTask(taskId, payload) {
  if (!taskId) throw new Error("Task ID is required");
  return request(`/documents/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteDocumentTask(taskId) {
  if (!taskId) throw new Error("Task ID is required");
  return request(`/documents/${taskId}`, {
    method: "DELETE",
  });
}

// Export project to Excel
export async function exportProjectToExcel(projectId) {
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