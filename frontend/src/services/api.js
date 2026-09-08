/**
 * PAIMANA Frontend API Client
 * 
 * Centralized HTTP client for all backend API requests.
 * Handles error handling, response transformation, and environment-based URL configuration.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

/**
 * Centralized fetch wrapper with error handling
 * @param {string} endpoint - API endpoint (with or without leading /)
 * @param {object} options - fetch options (method, body, headers, etc.)
 * @returns {Promise<any>} - Parsed JSON response or error
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : "/" + endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    // Handle non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: `HTTP ${response.status}`,
      }));
      const error = new Error(errorData.detail || "API request failed");
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    // Parse and return JSON response
    return await response.json();
  } catch (error) {
    // Re-throw with additional context
    if (!error.status) {
      error.status = 0; // Network error or parse error
    }
    throw error;
  }
}

// ============================================================
// Dashboard Endpoints
// ============================================================

/**
 * Get dashboard summary with project counts and risk distribution
 */
export async function getDashboardSummary() {
  return fetchAPI("/dashboard/summary");
}

/**
 * Get state-wise risk aggregation for map display
 */
export async function getStateRisks() {
  return fetchAPI("/dashboard/state-risks");
}

// ============================================================
// Projects Endpoints
// ============================================================

/**
 * Get list of projects with optional filtering
 * @param {object} params - Query parameters
 *   - q: Search query (project name)
 *   - ministry: Filter by ministry
 *   - sector: Filter by sector
 *   - state: Filter by state
 *   - status: Filter by status (PLANNING, IN_PROGRESS, DELAYED, COMPLETED, ON_HOLD)
 *   - page: Page number (1-indexed)
 *   - page_size: Items per page
 */
export async function getProjects(params = {}) {
  const queryString = new URLSearchParams();
  
  // Map frontend parameter names to backend names if needed
  if (params.q) queryString.append("name", params.q);
  if (params.ministry) queryString.append("ministry", params.ministry);
  if (params.sector) queryString.append("sector", params.sector);
  if (params.state) queryString.append("state", params.state);
  if (params.status) queryString.append("status", params.status);
  if (params.page) queryString.append("page", params.page);
  if (params.page_size) queryString.append("page_size", params.page_size);

  const url = queryString.toString() ? `/projects?${queryString}` : "/projects";
  return fetchAPI(url);
}

/**
 * Get a single project by ID
 */
export async function getProject(projectId) {
  return fetchAPI(`/projects/${projectId}`);
}

/**
 * Create a new project
 */
export async function createProject(projectData) {
  return fetchAPI("/projects", {
    method: "POST",
    body: JSON.stringify(projectData),
  });
}

// ============================================================
// Milestones Endpoints
// ============================================================

/**
 * Get milestones for a project
 */
export async function getMilestones(projectId) {
  return fetchAPI(`/projects/${projectId}/milestones`);
}

/**
 * Create a milestone for a project
 */
export async function createMilestone(projectId, milestoneData) {
  return fetchAPI(`/projects/${projectId}/milestones`, {
    method: "POST",
    body: JSON.stringify(milestoneData),
  });
}

// ============================================================
// Progress Endpoints
// ============================================================

/**
 * Get progress reports for a project
 */
export async function getProgress(projectId) {
  return fetchAPI(`/projects/${projectId}/progress`);
}

/**
 * Create a new progress report for a project
 */
export async function createProgress(projectId, progressData) {
  return fetchAPI(`/projects/${projectId}/progress`, {
    method: "POST",
    body: JSON.stringify(progressData),
  });
}

// ============================================================
// Risk Score Endpoints
// ============================================================

/**
 * Get the latest risk score for a project
 */
export async function getRisk(projectId) {
  return fetchAPI(`/projects/${projectId}/risk`);
}

/**
 * Generate/update risk prediction for a project
 * This triggers ML inference and persists the RiskScore
 */
export async function generateRisk(projectId, riskData = {}) {
  return fetchAPI(`/projects/${projectId}/risk/predict`, {
    method: "POST",
    body: JSON.stringify(riskData),
  });
}

// ============================================================
// Alerts Endpoints
// ============================================================

/**
 * Get all alerts (with optional filtering)
 * @param {object} params - Query parameters
 *   - severity: CRITICAL, HIGH, MEDIUM, LOW
 *   - status: OPEN, ACKNOWLEDGED, RESOLVED, DISMISSED
 *   - alert_type: Filter by alert type
 */
export async function getAlerts(params = {}) {
  const queryString = new URLSearchParams();
  if (params.severity) queryString.append("severity", params.severity);
  if (params.status) queryString.append("status", params.status);
  if (params.alert_type) queryString.append("alert_type", params.alert_type);

  const url = queryString.toString() ? `/alerts?${queryString}` : "/alerts";
  return fetchAPI(url);
}

/**
 * Get alerts for a specific project
 */
export async function getProjectAlerts(projectId) {
  return fetchAPI(`/projects/${projectId}/alerts`);
}

/**
 * Create an alert for a project
 */
export async function createAlert(projectId, alertData) {
  return fetchAPI(`/projects/${projectId}/alerts`, {
    method: "POST",
    body: JSON.stringify(alertData),
  });
}

// ============================================================
// Health Check
// ============================================================

/**
 * Health check endpoint to verify backend connectivity
 */
export async function healthCheck() {
  return fetchAPI("/health", {
    headers: {}, // No Content-Type needed for health check
  }).catch(() => ({ status: "error" }));
}

// ============================================================
// Error utilities
// ============================================================

/**
 * User-friendly error message from API error
 */
export function getErrorMessage(error) {
  if (error.status === 0) {
    return "Network error. Please check your connection.";
  }
  if (error.status === 404) {
    return "Resource not found.";
  }
  if (error.status === 500) {
    return "Server error. Please try again later.";
  }
  return error.message || "An error occurred.";
}
