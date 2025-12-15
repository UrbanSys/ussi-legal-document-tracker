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
