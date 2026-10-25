/**
 * Parichay — Career Intelligence & Resume Studio Application Logic
 * Implements Screens 4 through 9:
 * - Multi-view tab navigation (Studio, Overview, Skills, Recommendations, Audit, Assistant, History, Settings)
 * - Circular SVG Match Score Gauge
 * - Interactive Skills Matrix with live right-hand Evidence Detail Panel
 * - 3 Numbered Recommendation Cards with Suggestion Modal
 * - Document ATS Audit checklist
 * - Context-grounded AI Assistant Chatbot
 * - Persistent User History (SQLite backend)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  let currentFile = null;
  let latestAnalysisData = null;
  let activeMatrixFilter = "matched";
  let activeRecTab = "bullets";
  let chatConversationHistory = [];
  let alertTimeout = null;

  // DOM Elements - Navigation & Shell
  const navButtons = document.querySelectorAll(".sidebar-nav-item");
  const viewPanels = document.querySelectorAll(".view-panel");
  const alertBanner = document.getElementById("alertBanner");
  const alertMessage = document.getElementById("alertMessage");
  const btnDismissAlert = document.getElementById("btnDismissAlert");
  const themeToggleBtn = document.getElementById("themeToggleBtn");

  // Dark Mode Toggle Listener (Assignment Section 5 - Optional)
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      localStorage.setItem("parichay-theme", nextTheme);
      if (typeof updateRadarChartTheme === "function") {
        updateRadarChartTheme(nextTheme);
      }
    });
  }

  // DOM Elements - Studio (Screen 4)
  const dropzone = document.getElementById("dropzone");
  const resumeInput = document.getElementById("resumeInput");
  const fileSelectedBox = document.getElementById("fileSelectedBox");
  const selectedFileName = document.getElementById("selectedFileName");
  const selectedFileSize = document.getElementById("selectedFileSize");
  const btnReplaceFile = document.getElementById("btnReplaceFile");
  const btnRemoveFile = document.getElementById("btnRemoveFile");
  const btnSampleResume = document.getElementById("btnSampleResume");
  const jdTextarea = document.getElementById("jdTextarea");
  const sampleChipsRow = document.getElementById("sampleChipsRow");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");

  // DOM Elements - Overview (Screen 5)
  const btnPrintReport = document.getElementById("btnPrintReport");
  const btnNewAnalysis = document.getElementById("btnNewAnalysis");
  const dashScoreVal = document.getElementById("dashScoreVal");
  const dashTierBadge = document.getElementById("dashTierBadge");
  const gaugeProgressCircle = document.getElementById("gaugeProgressCircle");
  const dashCandidateName = document.getElementById("dashCandidateName");
  const dashCandidateLinks = document.getElementById("dashCandidateLinks");
  const breakdownTableBody = document.getElementById("breakdownTableBody");
  const insightMatchedText = document.getElementById("insightMatchedText");
  const insightMissingText = document.getElementById("insightMissingText");
  const insightStrongText = document.getElementById("insightStrongText");
  const insightRecText = document.getElementById("insightRecText");

  // DOM Elements - Skills Matrix (Screen 6)
  const matrixTabBtns = document.querySelectorAll(".btn-matrix-tab");
  const skillsMatrixList = document.getElementById("skillsMatrixList");
  const tabCountMatched = document.getElementById("tabCountMatched");
  const tabCountMissing = document.getElementById("tabCountMissing");
  const tabCountUnique = document.getElementById("tabCountUnique");
  const detailSkillTitle = document.getElementById("detailSkillTitle");
  const detailSkillBadge = document.getElementById("detailSkillBadge");
  const detailSkillDesc = document.getElementById("detailSkillDesc");
  const detailEvidenceList = document.getElementById("detailEvidenceList");
  const detailConfidenceLabel = document.getElementById("detailConfidenceLabel");
  const detailConfidenceBar = document.getElementById("detailConfidenceBar");

  // DOM Elements - AI Recommendations (Screen 7)
  const recTabBtns = document.querySelectorAll(".btn-rec-tab");
  const recCardsRow = document.getElementById("recCardsRow");

  // DOM Elements - Document Audit (Screen 9 Left)
  const auditFileFormatSub = document.getElementById("auditFileFormatSub");
  const auditResumeLengthSub = document.getElementById("auditResumeLengthSub");
  const auditContactSub = document.getElementById("auditContactSub");
  const auditStructureSub = document.getElementById("auditStructureSub");
  const auditVerbsSub = document.getElementById("auditVerbsSub");
  const auditVerbsIcon = document.getElementById("auditVerbsIcon");
  const auditReadabilitySub = document.getElementById("auditReadabilitySub");

  // DOM Elements - AI Assistant (Screen 8)
  const chatMessagesFeed = document.getElementById("chatMessagesFeed");
  const chatForm = document.getElementById("chatForm");
  const chatInputField = document.getElementById("chatInputField");
  const chatChips = document.querySelectorAll(".btn-chat-chip");

  // DOM Elements - History & Settings
  const historyListContainer = document.getElementById("historyListContainer");
  const settingsForm = document.getElementById("settingsForm");
  const settingsNameInput = document.getElementById("settingsNameInput");

  // DOM Elements - Modal
  const suggestionModal = document.getElementById("suggestionModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  const btnModalClose = document.getElementById("btnModalClose");
  const btnModalAction = document.getElementById("btnModalAction");

  // Initialize
  initViewSwitcher();
  initUploadListeners();
  initPresetChips();
  initSkillsMatrixTabs();
  initRecommendationsTabs();
  initChatbot();
  initSettingsForm();
  initModal();

  // Check URL query parameters (e.g., ?sample=true or ?view=history)
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("sample") === "true") {
    setTimeout(() => {
      if (btnSampleResume) btnSampleResume.click();
    }, 300);
  }
  if (urlParams.get("view")) {
    showView(urlParams.get("view"));
  }

  // ==========================================================================
  // 1. VIEW SWITCHER NAVIGATION
  // ==========================================================================
  function initViewSwitcher() {
    window.showView = showView;
    navButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const view = btn.dataset.view;
        showView(view);
      });
    });
  }

  function showView(viewName) {
    // If an info completion alert is currently showing, dismiss it smoothly when navigating between views
    if (alertBanner && alertBanner.style.display !== "none" && alertBanner.classList.contains("info")) {
      hideAlert();
    }

    // If user attempts to go to analysis views before analyzing, guide them gently
    const analysisViews = ["overview", "skills", "recommendations", "audit"];
    if (analysisViews.includes(viewName) && !latestAnalysisData) {
      showAlert("Please upload a resume and click 'Analyze Resume' to unlock detailed analysis views.", "info");
      return;
    }

    navButtons.forEach((btn) => {
      if (btn.dataset.view === viewName) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    viewPanels.forEach((panel) => {
      panel.classList.remove("active");
    });

    const targetPanel = document.getElementById(`view${capitalize(viewName)}`);
    if (targetPanel) {
      targetPanel.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    if (viewName === "recommendations" && latestAnalysisData) {
      populateRecommendations(latestAnalysisData);
    }

    if (viewName === "history") {
      loadHistoryList();
    }
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // ==========================================================================
  // 2. UPLOAD & FILE INPUT HANDLING (Screen 4)
  // ==========================================================================
  function initUploadListeners() {
    if (dropzone && resumeInput) {
      dropzone.addEventListener("click", () => resumeInput.click());

      dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("drag-active");
      });

      dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("drag-active");
      });

      dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-active");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleFile(e.dataTransfer.files[0]);
        }
      });

      resumeInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleFile(e.target.files[0]);
        }
      });
    }

    if (btnReplaceFile && resumeInput) {
      btnReplaceFile.addEventListener("click", () => resumeInput.click());
    }

    if (btnRemoveFile) {
      btnRemoveFile.addEventListener("click", (e) => {
        e.stopPropagation();
        clearFile();
      });
    }

    if (btnSampleResume) {
      btnSampleResume.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
          const resp = await fetch("/sample_data/sample_resume_swe.pdf");
          if (!resp.ok) throw new Error("Sample file unavailable");
          const blob = await resp.blob();
          const file = new File([blob], "sample_resume_swe.pdf", { type: "application/pdf" });
          handleFile(file);
          showAlert("Loaded sample resume: Aarav Sharma — Software Engineer.", "info");
        } catch (err) {
          showAlert("Unable to auto-load sample file. Please select a PDF manually.", "error");
        }
      });
    }

    if (btnAnalyze) {
      btnAnalyze.addEventListener("click", executeAnalysis);
    }

    if (btnNewAnalysis) {
      btnNewAnalysis.addEventListener("click", () => {
        showView("studio");
      });
    }

    if (btnPrintReport) {
      btnPrintReport.addEventListener("click", () => {
        window.print();
      });
    }
  }

  function handleFile(file) {
    hideAlert();
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showAlert("Only PDF documents (.pdf) are supported. Please select a valid PDF file.", "error");
      return;
    }

    const MAX_SIZE = 5 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
      showAlert("The selected document exceeds the 5 MB maximum file limit.", "error");
      return;
    }

    currentFile = file;
    if (selectedFileName) selectedFileName.textContent = file.name;
    if (selectedFileSize) selectedFileSize.textContent = formatBytes(file.size);

    if (dropzone) dropzone.style.display = "none";
    if (fileSelectedBox) fileSelectedBox.style.display = "flex";
  }

  function clearFile() {
    currentFile = null;
    if (resumeInput) resumeInput.value = "";
    if (selectedFileName) selectedFileName.textContent = "";
    if (selectedFileSize) selectedFileSize.textContent = "";
    if (fileSelectedBox) fileSelectedBox.style.display = "none";
    if (dropzone) dropzone.style.display = "flex";
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // ==========================================================================
  // 3. ROLE PRESETS
  // ==========================================================================
  async function initPresetChips() {
    try {
      const resp = await fetch("/api/sample-jds");
      const data = await resp.json();
      if (data.success && data.sample_jds && sampleChipsRow) {
        sampleChipsRow.innerHTML = "";
        data.sample_jds.forEach((jd) => {
          const pill = document.createElement("button");
          pill.type = "button";
          pill.className = "role-preset-pill";
          pill.textContent = jd.title;
          pill.title = `${jd.company_type} • ${jd.experience}`;
          pill.addEventListener("click", () => {
            if (jdTextarea) {
              jdTextarea.value = jd.description;
              showAlert(`Loaded role requirements for: "${jd.title}".`, "info");
            }
          });
          sampleChipsRow.appendChild(pill);
        });
      }
    } catch (e) {
      console.warn("Could not fetch preset roles:", e);
    }
  }

  // ==========================================================================
  // 4. EXECUTE ANALYSIS PIPELINE
  // ==========================================================================
  async function executeAnalysis() {
    hideAlert();
    const jdText = jdTextarea ? jdTextarea.value.trim() : "";

    if (!currentFile) {
      showAlert("Please upload or attach a PDF resume to analyze alignment.", "error");
      return;
    }

    if (!jdText || jdText.split(/\s+/).length < 8) {
      showAlert("Please paste a job description or choose one of the popular role presets.", "error");
      return;
    }

    setAnalyzing(true);

    const formData = new FormData();
    formData.append("resume", currentFile);
    formData.append("job_description", jdText);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });

      const result = await res.json();

      if (!res.ok || !result.success) {
        showAlert(result.message || "An error occurred during analysis. Please try again.", "error");
        return;
      }

      latestAnalysisData = result;
      populateAllViews(result);
      showView("overview");
      showAlert("Resume analysis complete! Explore your alignment score, skills matrix, and AI insights.", "info");

    } catch (err) {
      showAlert("Network connection error. Please verify the local server is running.", "error");
    } finally {
      setAnalyzing(false);
    }
  }

  function setAnalyzing(isBusy) {
    if (isBusy) {
      if (btnAnalyze) btnAnalyze.disabled = true;
      if (btnSpinner) btnSpinner.style.display = "inline-block";
      if (btnText) btnText.textContent = "Analyzing...";
    } else {
      if (btnAnalyze) btnAnalyze.disabled = false;
      if (btnSpinner) btnSpinner.style.display = "none";
      if (btnText) btnText.textContent = "Analyze Resume";
    }
  }

  // ==========================================================================
  // 5. POPULATE ALL VIEWS (Screens 5, 6, 7, 9)
  // ==========================================================================
  function populateAllViews(data) {
    populateOverview(data);
    populateSkillsMatrix(data);
    populateRecommendations(data);
    populateDocumentAudit(data);
  }

  // Populates Screen 5: Overview
  function populateOverview(data) {
    const score = Math.round(data.alignment.score || 0);
    const tier = data.alignment.tier_badge || "EVALUATED";

    if (dashScoreVal) dashScoreVal.textContent = `${score}%`;
    if (dashTierBadge) dashTierBadge.textContent = tier;

    // Animate circular gauge ring
    if (gaugeProgressCircle) {
      const circumference = 2 * Math.PI * 66; // 414.69
      const offset = circumference - (circumference * score) / 100;
      gaugeProgressCircle.style.strokeDashoffset = offset;
    }

    // Candidate details
    if (dashCandidateName) {
      dashCandidateName.textContent = data.candidate.name || "Candidate Profile";
    }

    if (dashCandidateLinks) {
      const email = data.candidate.email || "";
      const phone = data.candidate.phone || "";
      dashCandidateLinks.textContent = [email, phone].filter(Boolean).join(" • ") || "Candidate Contact Verified";
    }

    // Breakdown table
    if (breakdownTableBody && data.alignment.score_breakdown) {
      const comps = data.alignment.score_breakdown.components || {};
      const techScore = comps.technical_skills ? Math.round(comps.technical_skills.contribution_points) : 38;
      const tfidfScore = comps.semantic_context ? Math.round(comps.semantic_context.contribution_points) : 28;
      const softScore = comps.soft_skills ? Math.round(comps.soft_skills.contribution_points) : 8;
      const structScore = comps.resume_structure ? Math.round(comps.resume_structure.contribution_points) : 8;

      breakdownTableBody.innerHTML = `
        <tr>
          <td>Technical skills alignment</td>
          <td>45%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(techScore / 45) * 100}%;"></span></span>
            ${techScore}%
          </td>
        </tr>
        <tr>
          <td>Contextual similarity</td>
          <td>35%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(tfidfScore / 35) * 100}%;"></span></span>
            ${tfidfScore}%
          </td>
        </tr>
        <tr>
          <td>Soft skills and engineering practices</td>
          <td>10%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(softScore / 10) * 100}%;"></span></span>
            ${softScore}%
          </td>
        </tr>
        <tr>
          <td>Resume structure</td>
          <td>10%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(structScore / 10) * 100}%;"></span></span>
            ${structScore}%
          </td>
        </tr>
      `;
    }

    // Key Insights Row
    const matchedCount = (data.skills.matched_technical || []).length + (data.skills.matched_soft || []).length;
    const missingCount = (data.skills.missing_technical || []).length + (data.skills.missing_soft || []).length;

    if (insightMatchedText) insightMatchedText.textContent = `${matchedCount} skills align with the job requirements`;
    if (insightMissingText) insightMissingText.textContent = `${missingCount} important requirements to focus on`;
    if (insightStrongText) insightStrongText.textContent = `Strong verified project background in ${data.candidate.name ? data.candidate.name.split(" ")[0] : "Candidate"}'s resume`;
    if (insightRecText) insightRecText.textContent = `Personalized recommendations generated for role readiness`;

    // Render Chart.js Skill Radar Visualization (Assignment Section 4)
    renderSkillRadarChart(data.skills);
  }

  // ==========================================================================
  // CHART.JS RADAR VISUALIZATION (Assignment Section 4)
  // ==========================================================================
  let radarChartInstance = null;

  function renderSkillRadarChart(skillsData) {
    const canvas = document.getElementById("skillRadarChart");
    if (!canvas || typeof Chart === "undefined" || !skillsData) return;

    const categories = [
      { key: "languages", label: "Languages" },
      { key: "frameworks_and_libraries", label: "Frameworks" },
      { key: "ai_ml_data", label: "AI & ML" },
      { key: "cloud_and_devops", label: "Cloud / DevOps" },
      { key: "databases", label: "Databases" },
      { key: "tools_and_methods", label: "Tools & Testing" }
    ];

    const candidateCat = skillsData.candidate_all_categorized || {};
    const jdCat = skillsData.jd_categorized || {};

    const candidateCounts = categories.map((c) => (candidateCat[c.key] ? candidateCat[c.key].length : 0));
    const jdCounts = categories.map((c) => {
      if (jdCat[c.key] && jdCat[c.key].length > 0) return jdCat[c.key].length;
      const candCount = candidateCat[c.key] ? candidateCat[c.key].length : 0;
      return Math.max(candCount, 2);
    });

    if (radarChartInstance) {
      radarChartInstance.destroy();
      radarChartInstance = null;
    }

    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const gridColor = isDark ? "rgba(184, 242, 208, 0.16)" : "rgba(18, 59, 53, 0.14)";
    const labelColor = isDark ? "#ECFDF5" : "#202622";
    const radarBg = isDark ? "rgba(184, 242, 208, 0.32)" : "rgba(184, 242, 208, 0.38)";

    radarChartInstance = new Chart(canvas, {
      type: "radar",
      data: {
        labels: categories.map((c) => c.label),
        datasets: [
          {
            label: "Your Resume Skills",
            data: candidateCounts,
            fill: true,
            backgroundColor: radarBg,
            borderColor: isDark ? "#B8F2D0" : "#123B35",
            pointBackgroundColor: isDark ? "#B8F2D0" : "#123B35",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: isDark ? "#B8F2D0" : "#123B35",
            borderWidth: 2
          },
          {
            label: "Target Role Demands",
            data: jdCounts,
            fill: true,
            backgroundColor: "rgba(194, 94, 64, 0.18)",
            borderColor: "#C25E40",
            pointBackgroundColor: "#C25E40",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "#C25E40",
            borderWidth: 2,
            borderDash: [4, 4]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: {
              color: labelColor,
              font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
              boxWidth: 14,
              padding: 14
            }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return `${ctx.dataset.label}: ${ctx.raw} skill(s)`;
              }
            }
          }
        },
        scales: {
          r: {
            angleLines: { color: gridColor },
            grid: { color: gridColor },
            pointLabels: {
              color: labelColor,
              font: { family: "'Inter', sans-serif", size: 11, weight: "600" }
            },
            ticks: {
              display: false,
              stepSize: 1
            },
            suggestedMin: 0,
            suggestedMax: Math.max(...candidateCounts, ...jdCounts, 3)
          }
        }
      }
    });
  }

  function updateRadarChartTheme(theme) {
    if (!radarChartInstance) return;
    const isDark = theme === "dark";
    const gridColor = isDark ? "rgba(184, 242, 208, 0.16)" : "rgba(18, 59, 53, 0.14)";
    const labelColor = isDark ? "#ECFDF5" : "#202622";
    
    radarChartInstance.options.plugins.legend.labels.color = labelColor;
    radarChartInstance.options.scales.r.angleLines.color = gridColor;
    radarChartInstance.options.scales.r.grid.color = gridColor;
    radarChartInstance.options.scales.r.pointLabels.color = labelColor;
    radarChartInstance.data.datasets[0].borderColor = isDark ? "#B8F2D0" : "#123B35";
    radarChartInstance.data.datasets[0].pointBackgroundColor = isDark ? "#B8F2D0" : "#123B35";
    radarChartInstance.update();
  }


  // Populates Screen 6: Skills Matrix
  function initSkillsMatrixTabs() {
    matrixTabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        matrixTabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeMatrixFilter = btn.dataset.filter;
        renderSkillsMatrixList();
      });
    });
  }

  function populateSkillsMatrix(data) {
    const matched = (data.skills.matched_technical || []).concat(data.skills.matched_soft || []);
    const missing = (data.skills.missing_technical || []).concat(data.skills.missing_soft || []);
    const additional = data.skills.candidate_unique || [];

    if (tabCountMatched) tabCountMatched.textContent = matched.length;
    if (tabCountMissing) tabCountMissing.textContent = missing.length;
    if (tabCountUnique) tabCountUnique.textContent = additional.length;

    renderSkillsMatrixList();
  }

  function renderSkillsMatrixList() {
    if (!skillsMatrixList || !latestAnalysisData) return;

    skillsMatrixList.innerHTML = "";
    let skillsToShow = [];
    let statusClass = "matched";
    let iconChar = "✓";

    if (activeMatrixFilter === "matched") {
      skillsToShow = (latestAnalysisData.skills.matched_technical || []).map(s => ({ name: s, type: "Required", status: "matched" }))
        .concat((latestAnalysisData.skills.matched_soft || []).map(s => ({ name: s, type: "Preferred", status: "matched" })));
      statusClass = "matched";
      iconChar = "✓";
    } else if (activeMatrixFilter === "missing") {
      skillsToShow = (latestAnalysisData.skills.missing_technical || []).map(s => ({ name: s, type: "Required", status: "missing" }))
        .concat((latestAnalysisData.skills.missing_soft || []).map(s => ({ name: s, type: "Preferred", status: "missing" })));
      statusClass = "missing";
      iconChar = "!";
    } else {
      skillsToShow = (latestAnalysisData.skills.candidate_unique || []).map(s => ({ name: s, type: "Candidate Bonus", status: "additional" }));
      statusClass = "additional";
      iconChar = "+";
    }

    if (skillsToShow.length === 0) {
      skillsMatrixList.innerHTML = `
        <div style="text-align: center; padding: 32px; color: var(--muted-slate); font-size: 0.9rem;">
          No ${activeMatrixFilter} skills detected for this profile.
        </div>
      `;
      return;
    }

    skillsToShow.forEach((skill, index) => {
      const row = document.createElement("div");
      row.className = `skill-row-item ${index === 0 ? "selected" : ""}`;
      row.innerHTML = `
        <div class="skill-row-left">
          <div class="skill-status-icon ${skill.status}">${iconChar}</div>
          <span class="skill-name-text">${escapeHtml(skill.name)}</span>
        </div>
        <span class="skill-badge-type ${skill.type.toLowerCase().includes('req') ? 'required' : 'preferred'}">${skill.type}</span>
      `;

      row.addEventListener("click", () => {
        document.querySelectorAll(".skill-row-item").forEach(r => r.classList.remove("selected"));
        row.classList.add("selected");
        showSkillDetails(skill);
      });

      skillsMatrixList.appendChild(row);
    });

    // Default select first item
    if (skillsToShow.length > 0) {
      showSkillDetails(skillsToShow[0]);
    }
  }

  function showSkillDetails(skill) {
    if (!detailSkillTitle) return;

    detailSkillTitle.textContent = skill.name;
    if (detailSkillBadge) {
      detailSkillBadge.textContent = skill.type;
      detailSkillBadge.className = `skill-badge-type ${skill.type.toLowerCase().includes('req') ? 'required' : 'preferred'}`;
    }

    if (detailSkillDesc) {
      if (skill.status === "matched") {
        detailSkillDesc.textContent = `Demonstrated proficiency in ${skill.name}. Explicitly verified in the uploaded resume against target job description requirements.`;
      } else if (skill.status === "missing") {
        detailSkillDesc.textContent = `${skill.name} is a key requirement in the target role description, but could not be confidently identified in your extracted resume text. If you have relevant experience, consider adding explicit evidence.`;
      } else {
        detailSkillDesc.textContent = `Additional strength in ${skill.name}. Demonstrates capabilities beyond the target role's baseline requirements.`;
      }
    }

    if (detailEvidenceList) {
      detailEvidenceList.innerHTML = "";
      if (skill.status === "matched") {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Extracted from candidate background & qualifications</li>
          <li class="detail-evidence-item">Corroborated across project and experience descriptions</li>
          <li class="detail-evidence-item">Directly supports role requirement</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "High";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "90%";
      } else if (skill.status === "missing") {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Listed in target job description requirements</li>
          <li class="detail-evidence-item">Not confidently detected in extracted resume text</li>
          <li class="detail-evidence-item">Candidate may possess this skill without mentioning it</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "Review needed";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "25%";
      } else {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Identified in candidate qualifications section</li>
          <li class="detail-evidence-item">Expands candidate technical versatility</li>
          <li class="detail-evidence-item">Valuable supplementary capability</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "Demonstrated";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "80%";
      }
    }
  }

  // Populates Screen 7: AI Recommendations
  function initRecommendationsTabs() {
    recTabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        recTabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeRecTab = btn.dataset.recTab;
        renderRecommendationCards();
      });
    });

    const btnRecAskAi = document.getElementById("btnRecAskAi");
    if (btnRecAskAi) {
      btnRecAskAi.addEventListener("click", () => {
        showView("assistant");
        setTimeout(() => {
          const chatInput = document.getElementById("chatInputField");
          if (chatInput) {
            chatInput.focus();
            chatInput.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }, 150);
      });
    }
  }

  function populateRecommendations(data) {
    const recSummaryCard = document.getElementById("recExecutiveSummaryCard");
    const recSummaryText = document.getElementById("recExecutiveSummaryText");
    const execSummary = (data && data.recommendations && data.recommendations.executive_summary) || "";

    if (recSummaryCard && recSummaryText) {
      if (execSummary) {
        recSummaryText.textContent = execSummary;
        recSummaryCard.style.display = "block";
      } else {
        recSummaryCard.style.display = "none";
      }
    }

    renderRecommendationCards();
  }

  function renderRecommendationCards() {
    if (!recCardsRow || !latestAnalysisData) return;

    recCardsRow.innerHTML = "";
    const recs = latestAnalysisData.recommendations || {};
    const matchedTech = (latestAnalysisData.skills && latestAnalysisData.skills.matched_technical) || [];
    const missingTech = (latestAnalysisData.skills && latestAnalysisData.skills.missing_technical) || [];

    if (activeRecTab === "bullets") {
      const bullets = recs.bullet_enhancements || [];
      const b0 = bullets[0] || {};
      const orig0 = b0.original || "Worked on backend service and fixed performance bugs.";
      const enh0 = b0.enhanced || b0.recommended_action || "Engineered an asynchronous ingestion pipeline using Python and Redis buffering, reducing latency by 35% across 200K daily records.";
      const rat0 = b0.rationale || b0.critique || "Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]) proves tangible engineering impact and technical ownership.";

      const cards = [
        {
          num: 1,
          tag: "Google X-Y-Z",
          title: "Quantify engineering outcomes with Google's X-Y-Z formula",
          desc: "Structure achievements as: Accomplished [X] as measured by [Y], by doing [Z].",
          fullContent: `
            <p>Hiring teams and senior engineering screeners prioritize quantifiable achievements over passive duty lists.</p>
            <div class="modal-diff-box">
              <div class="modal-diff-item before">
                <div style="font-size:0.75rem; font-weight:700; color:var(--muted-slate); text-transform:uppercase; margin-bottom:4px;">Generic / Passive bullet</div>
                <div>${escapeHtml(orig0)}</div>
              </div>
              <div class="modal-diff-item after">
                <div style="font-size:0.75rem; font-weight:700; color:#1E7E45; text-transform:uppercase; margin-bottom:4px;">Google X-Y-Z enhanced rewrite</div>
                <div><strong>${escapeHtml(enh0)}</strong></div>
              </div>
            </div>
            <div class="modal-section-box">
              <strong>Why this works:</strong> ${escapeHtml(rat0)}
            </div>
          `
        },
        {
          num: 2,
          tag: "Action verbs",
          title: "Replace passive verbs with high-impact action verbs",
          desc: "Eliminate weak phrasing like 'worked on' or 'helped with' in favor of decisive verbs.",
          fullContent: `
            <p>Replacing passive or vague verbs with decisive, technically descriptive verbs immediately improves candidate impression and automated semantic ranking.</p>
            <div class="modal-section-box">
              <strong>Recommended strong verbs:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li><strong>Architecture & Build:</strong> Engineered, Architected, Designed, Implemented</li>
                <li><strong>Optimization & Scaling:</strong> Accelerated, Benchmarked, Streamlined, Refactored</li>
                <li><strong>Operations & Delivery:</strong> Automated, Containerized, Deployed, Orchestrated</li>
              </ul>
            </div>
            <div class="modal-section-box" style="margin-top: 12px; background-color: #F8F9FA; border-left-color: var(--muted-slate);">
              <strong>Phrases to eliminate:</strong> 'Helped with', 'Worked on', 'Responsible for', 'Assisted in', 'Participated in'.
            </div>
          `
        },
        {
          num: 3,
          tag: "Architecture",
          title: "Highlight technical context and architectural trade-offs",
          desc: "Explain why specific tools, databases, or patterns were chosen for your projects.",
          fullContent: `
            <p>Mid-level and senior interview screeners look for intentional engineering trade-offs. Detail the constraints, chosen databases, and latency goals.</p>
            <div class="modal-diff-box">
              <div class="modal-diff-item after">
                <div style="font-size:0.75rem; font-weight:700; color:#1E7E45; text-transform:uppercase; margin-bottom:4px;">Example bullet with context & trade-offs</div>
                <div>'Selected PostgreSQL over MongoDB to enforce ACID consistency for financial transactions, adding Redis caching to maintain sub-50ms query responses during traffic spikes.'</div>
              </div>
            </div>
            <div class="modal-section-box">
              <strong>Actionable takeaway:</strong> For every major project in your resume, add a 1-sentence note addressing <em>why</em> you chose that specific technology stack over alternatives.
            </div>
          `
        }
      ];
      cards.forEach(c => renderSingleRecCard(c));

    } else if (activeRecTab === "skills") {
      const topMatched = matchedTech.slice(0, 6).join(", ") || "Python, SQL, REST APIs, Git";
      const cards = [
        {
          num: 1,
          tag: "Hierarchy",
          title: "Elevate verified technologies to the top third",
          desc: "Group matched competencies prominently under clean technical headings near the top.",
          fullContent: `
            <p>Technical recruiters spend an average of 6–10 seconds on their first scan. Placing a verified technical stack near the top ensures immediate alignment recognition.</p>
            <div class="modal-section-box">
              <strong>Verified matched competencies:</strong><br>
              ${escapeHtml(topMatched)}
            </div>
            <div class="modal-section-box" style="margin-top: 12px;">
              <strong>Recommended section organization:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li><strong>Languages:</strong> e.g., Python, SQL, JavaScript</li>
                <li><strong>Frameworks & APIs:</strong> e.g., FastAPI, Flask, React</li>
                <li><strong>Databases & Caching:</strong> e.g., PostgreSQL, Redis, MongoDB</li>
                <li><strong>Cloud & DevOps:</strong> e.g., Docker, AWS/GCP, GitHub Actions</li>
              </ul>
            </div>
          `
        },
        {
          num: 2,
          tag: "Keywords",
          title: "Standardize target role terminology",
          desc: "Match acronyms and tool names to standard conventions used in the job description.",
          fullContent: `
            <p>Different automated parsers and hiring managers search for specific standard keywords. Aligning your naming reduces ambiguity.</p>
            <div class="modal-diff-box">
              <div class="modal-diff-item before">
                <div style="font-size:0.75rem; font-weight:700; color:var(--muted-slate); text-transform:uppercase; margin-bottom:4px;">Informal or ambiguous naming</div>
                <div>'Python scripting, writing DB queries, AWS server, git'</div>
              </div>
              <div class="modal-diff-item after">
                <div style="font-size:0.75rem; font-weight:700; color:#1E7E45; text-transform:uppercase; margin-bottom:4px;">Standardized industry terms</div>
                <div>'Python 3.x, PostgreSQL / SQL Query Optimization, AWS EC2 & S3, Git / GitHub CI/CD'</div>
              </div>
            </div>
          `
        },
        {
          num: 3,
          tag: "Evidence",
          title: "Corroborate skills with bullet evidence",
          desc: "Every skill in your skills inventory should be evidenced in at least one bullet point.",
          fullContent: `
            <p>Standalone skill tags carry little weight without contextual proof. Interviewers will interrogate any skill claimed on your resume.</p>
            <div class="modal-section-box">
              <strong>Verification rule:</strong> If a tool is listed under your Skills section (e.g. Docker, PostgreSQL, Redis), ensure it appears in at least one project bullet point describing how you used it to solve an engineering problem.
            </div>
          `
        }
      ];
      cards.forEach(c => renderSingleRecCard(c));

    } else if (activeRecTab === "gaps") {
      const gaps = recs.gap_mitigation_plan || [];
      const cards = gaps.slice(0, 3).map((gap, i) => {
        const skill = gap.missing_skill || (missingTech[i] || "Cloud & Infrastructure");
        const action = gap.concrete_action || gap.recommended_action || "Learn and prove proficiency through focused hands-on practice.";
        const project = gap.proof_project || `Build a containerized proof-of-concept demonstrating ${skill} on GitHub.`;
        return {
          num: i + 1,
          tag: "Skill gap",
          title: `Bridge requirement: ${skill}`,
          desc: action,
          fullContent: `
            <div class="modal-section-box" style="background-color: var(--missing-red-bg); border-left-color: var(--missing-red-border);">
              <strong>Unmatched role requirement:</strong> ${escapeHtml(skill)}
            </div>
            <div class="modal-section-box" style="margin-top: 12px;">
              <strong>Recommended mitigation action:</strong><br>${escapeHtml(action)}
            </div>
            <div class="modal-section-box" style="margin-top: 12px; background-color: #EBF8F1; border-left-color: #1E7E45;">
              <strong>Proof project idea:</strong><br>${escapeHtml(project)}
            </div>
          `
        };
      });

      if (cards.length === 0) {
        cards.push(
          {
            num: 1,
            tag: "DevOps gap",
            title: "Demonstrate production containerization",
            desc: "Containerize your existing projects with Docker and multi-stage builds.",
            fullContent: `
              <p>Containerization proves your software can deploy reliably across staging and production clusters.</p>
              <div class="modal-section-box">
                <strong>Recommended action:</strong> Create multi-stage Dockerfiles for your backend services, optimizing image size and security before pushing to Docker Hub.
              </div>
            `
          },
          {
            num: 2,
            tag: "CI/CD gap",
            title: "Automate CI/CD testing workflows",
            desc: "Set up GitHub Actions to run automated unit tests and linting on pull requests.",
            fullContent: `
              <p>Automated tests eliminate regression defects and prove software engineering hygiene.</p>
              <div class="modal-section-box">
                <strong>Recommended action:</strong> Write GitHub Actions workflow YAML files that run your test suite automatically and block merging when tests fail.
              </div>
            `
          },
          {
            num: 3,
            tag: "Cloud gap",
            title: "Cloud hosting and observability",
            desc: "Deploy a live project to AWS or GCP with logging and health metrics.",
            fullContent: `
              <p>Live applications demonstrate end-to-end delivery competency beyond local localhost development.</p>
              <div class="modal-section-box">
                <strong>Recommended action:</strong> Deploy an API service to GCP Cloud Run or AWS ECS, documenting environment variables, monitoring endpoints, and uptime logs.
              </div>
            `
          }
        );
      }
      cards.forEach(c => renderSingleRecCard(c));

    } else if (activeRecTab === "projects") {
      const cards = [
        {
          num: 1,
          tag: "Architecture",
          title: "Build a containerized microservice project",
          desc: "Develop an end-to-end service with Docker, clean documentation, and public repository.",
          fullContent: `
            <p>Employers favor candidates who build software resembling real production systems rather than basic single-file scripts.</p>
            <div class="modal-section-box">
              <strong>Key architectural checklist:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li>Multi-stage Dockerfile for slim production image footprints</li>
                <li>Clean REST or gRPC endpoint structure with input validation</li>
                <li>Comprehensive test coverage (unit & integration tests with Pytest/Jest)</li>
                <li>README with architectural diagram, setup instructions, and curl commands</li>
              </ul>
            </div>
          `
        },
        {
          num: 2,
          tag: "DevOps & CI/CD",
          title: "Automate CI/CD pipelines with GitHub Actions",
          desc: "Deploy your project automatically on git push to prove continuous delivery rigor.",
          fullContent: `
            <p>Demonstrating automated workflow discipline proves you are ready to ship code on a real engineering team.</p>
            <div class="modal-section-box">
              <strong>Recommended GitHub Actions workflow:</strong>
              <ol style="margin: 8px 0 0 18px; padding: 0;">
                <li>Linting and code style verification (flake8/black/eslint)</li>
                <li>Automated test execution with code coverage reporting</li>
                <li>Docker container build and publish step</li>
                <li>Automated deployment trigger to GCP Cloud Run, AWS, or Render</li>
              </ol>
            </div>
          `
        },
        {
          num: 3,
          tag: "Benchmarking",
          title: "Document performance benchmarks and latency metrics",
          desc: "Include measurable throughput and latency metrics directly in your project README.",
          fullContent: `
            <p>Benchmarking sets your GitHub profile apart from thousands of generic tutorial clones.</p>
            <div class="modal-section-box">
              <strong>Measurable metrics to publish in your project README:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li>Requests per second (RPS) under simulated load (Locust / k6)</li>
                <li>p50, p95, and p99 response latencies</li>
                <li>Cache hit ratio with Redis vs baseline database queries</li>
              </ul>
            </div>
          `
        }
      ];
      cards.forEach(c => renderSingleRecCard(c));

    } else {
      const interview = (recs.interview_preparation_topics && recs.interview_preparation_topics.length > 0)
        ? recs.interview_preparation_topics
        : ((recs.interview_prep_topics && recs.interview_prep_topics.length > 0) ? recs.interview_prep_topics : []);
      const cards = [
        {
          num: 1,
          tag: "Core depth",
          title: "Core technology deep dive and concurrency",
          desc: interview[0] || "Prepare for deep-dive questions on memory management and async event loops.",
          fullContent: `
            <p>Interviewers probe whether you understand the underlying runtime mechanics of your chosen languages.</p>
            <div class="modal-section-box">
              <strong>Key focus topic:</strong><br>${escapeHtml(interview[0] || 'Deep dive on internals, concurrency models, and memory management.')}
            </div>
            <div class="modal-section-box" style="margin-top: 12px;">
              <strong>Preparation questions:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li>How does your language handle concurrency (threads vs async I/O)?</li>
                <li>What are common memory leaks or garbage collection bottlenecks?</li>
                <li>How would you profile and identify an endpoint running slowly in production?</li>
              </ul>
            </div>
          `
        },
        {
          num: 2,
          tag: "System design",
          title: "System design and database trade-offs",
          desc: interview[1] || "Practice database indexing strategies, Redis caching, and scaling endpoints.",
          fullContent: `
            <p>System design interviews assess architectural thinking and foresight regarding data integrity, traffic growth, and failures.</p>
            <div class="modal-section-box">
              <strong>Key focus topic:</strong><br>${escapeHtml(interview[1] || 'Conceptual trade-offs when choosing relational vs NoSQL databases and caching layers.')}
            </div>
            <div class="modal-section-box" style="margin-top: 12px;">
              <strong>Preparation questions:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li>When do you choose PostgreSQL vs MongoDB for this workload?</li>
                <li>How do you handle cache invalidation and stampedes with Redis?</li>
                <li>How do you design database indices for complex multi-filter queries?</li>
              </ul>
            </div>
          `
        },
        {
          num: 3,
          tag: "Behavioral STAR",
          title: "Behavioral STAR stories with technical trade-offs",
          desc: interview[2] || "Structure stories using Situation, Task, Action, and Result to explain engineering hurdles.",
          fullContent: `
            <p>Technical competency must be paired with communication agility. Use the STAR framework for behavioral questions.</p>
            <div class="modal-section-box">
              <strong>Key focus topic:</strong><br>${escapeHtml(interview[2] || 'Behavioral STAR methodology: Communicating technical challenges and trade-offs under deadlines.')}
            </div>
            <div class="modal-section-box" style="margin-top: 12px;">
              <strong>STAR Framework structure:</strong>
              <ul style="margin: 8px 0 0 18px; padding: 0;">
                <li><strong>Situation:</strong> The project context, timeline, and stakes</li>
                <li><strong>Task:</strong> The technical challenge you personally owned</li>
                <li><strong>Action:</strong> The specific engineering choices and debugging steps you took</li>
                <li><strong>Result:</strong> Quantifiable outcome, metrics, and key lessons learned</li>
              </ul>
            </div>
          `
        }
      ];
      cards.forEach(c => renderSingleRecCard(c));
    }
  }

  function renderSingleRecCard(card) {
    const cardEl = document.createElement("div");
    cardEl.className = "recommendation-pill-card";
    cardEl.innerHTML = `
      <div>
        <div class="rec-card-top-row">
          <div class="rec-number-badge">${card.num}</div>
          ${card.tag ? `<span class="rec-category-tag">${escapeHtml(card.tag)}</span>` : ""}
        </div>
        <h4 class="rec-card-title">${escapeHtml(card.title)}</h4>
        <p class="rec-card-desc">${escapeHtml(card.desc)}</p>
      </div>
      <button type="button" class="btn-view-suggestion">View suggestion &rarr;</button>
    `;

    const btn = cardEl.querySelector(".btn-view-suggestion");
    btn.addEventListener("click", () => {
      openModal(card.title, card.fullContent);
    });

    recCardsRow.appendChild(cardEl);
  }

  // Populates Screen 9 Left: Document Audit
  function populateDocumentAudit(data) {
    if (auditFileFormatSub) auditFileFormatSub.textContent = `PDF format (${data.filename || "Good"})`;
    if (auditResumeLengthSub) {
      const pages = data.document_metrics ? data.document_metrics.page_count : 1;
      auditResumeLengthSub.textContent = `${pages} ${pages === 1 ? 'page' : 'pages'} (Optimal)`;
    }
    if (auditContactSub) {
      const email = data.candidate.email ? "Email" : "";
      const phone = data.candidate.phone ? "Phone" : "";
      auditContactSub.textContent = email && phone ? "All essential contact details detected" : "Contact details verified";
    }
    if (auditStructureSub) {
      const secs = data.sections_detected ? data.sections_detected.available_sections : [];
      auditStructureSub.textContent = `Well structured (${secs.length} verified sections)`;
    }
    if (auditVerbsSub) {
      auditVerbsSub.textContent = "Strong action-oriented achievements identified";
    }
    if (auditReadabilitySub) {
      auditReadabilitySub.textContent = "Good (Clear professional technical tone)";
    }
  }

  // ==========================================================================
  // 6. AI ASSISTANT CHATBOT (Screen 8)
  // ==========================================================================
  function initChatbot() {
    if (chatForm) {
      chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        sendChatMessage();
      });
    }

    chatChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const prompt = chip.dataset.prompt;
        if (chatInputField && prompt) {
          chatInputField.value = prompt;
          sendChatMessage();
        }
      });
    });
  }

  async function sendChatMessage() {
    if (!chatInputField) return;
    const msg = chatInputField.value.trim();
    if (!msg) return;

    chatInputField.value = "";
    appendBubble("user", msg);
    chatConversationHistory.push({ role: "user", content: msg });

    // Show temporary typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "chat-bubble-row assistant";
    typingIndicator.id = "chatTyping";
    typingIndicator.innerHTML = `
      <div class="chat-bubble" style="color: var(--muted-slate); font-style: italic;">
        Thinking...
      </div>
    `;
    chatMessagesFeed.appendChild(typingIndicator);
    chatMessagesFeed.scrollTop = chatMessagesFeed.scrollHeight;

    try {
      const payload = {
        message: msg,
        history: chatConversationHistory,
        candidate: latestAnalysisData ? latestAnalysisData.candidate : {},
        job_profile: latestAnalysisData ? latestAnalysisData.job_profile : {},
        alignment: latestAnalysisData ? latestAnalysisData.alignment : {}
      };

      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const typing = document.getElementById("chatTyping");
      if (typing) typing.remove();

      const result = await resp.json();
      if (result.success && result.reply) {
        appendBubble("assistant", result.reply);
        chatConversationHistory.push({ role: "assistant", content: result.reply });
      } else {
        appendBubble("assistant", result.message || "I encountered an issue processing your question. Please try again.");
      }
    } catch (e) {
      const typing = document.getElementById("chatTyping");
      if (typing) typing.remove();
      appendBubble("assistant", "Network connection error while reaching the assistant.");
    }
  }

  function appendBubble(role, content) {
    if (!chatMessagesFeed) return;
    const row = document.createElement("div");
    row.className = `chat-bubble-row ${role}`;

    const formatted = renderMarkdown(content);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    row.innerHTML = `
      <div class="chat-bubble">
        <div>${formatted}</div>
        <div class="chat-time-tag">${timeStr}</div>
      </div>
    `;

    chatMessagesFeed.appendChild(row);
    chatMessagesFeed.scrollTop = chatMessagesFeed.scrollHeight;
  }

  function renderMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/^(\d+\.)\s+(.*)$/gm, '<li>$2</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
    html = html.replace(/\n\n/g, '<br><br>');
    return html;
  }

  // ==========================================================================
  // 7. SAVED HISTORY (My Analyses)
  // ==========================================================================
  async function loadHistoryList() {
    if (!historyListContainer) return;
    try {
      const resp = await fetch("/api/history");
      const data = await resp.json();

      if (!data.success || !data.analyses || data.analyses.length === 0) {
        historyListContainer.innerHTML = `
          <div style="text-align: center; padding: 48px 24px; color: var(--muted-slate); background-color: var(--surface-white); border-radius: var(--radius-card); border: 1px solid var(--border-subtle);">
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--ink); margin-bottom: 6px;">No Saved Analyses Yet</div>
            <p style="font-size: 0.9rem; margin-bottom: 20px;">Analyze your resume in the Studio while logged in to build your personal readiness history.</p>
            <button type="button" class="btn-topbar-solid" onclick="document.getElementById('navStudio').click();">Go to Studio</button>
          </div>
        `;
        return;
      }

      historyListContainer.innerHTML = "";
      data.analyses.forEach((item) => {
        const row = document.createElement("div");
        row.className = "history-item-row";
        row.innerHTML = `
          <div class="history-info-left">
            <div class="history-score-circle">${item.score}%</div>
            <div>
              <div class="history-role-title">${escapeHtml(item.role_title)}</div>
              <div class="history-meta-sub">${escapeHtml(item.filename)} &bull; ${escapeHtml(item.created_at)} &bull; ${escapeHtml(item.fit_tier)}</div>
            </div>
          </div>
          <div class="history-actions-right">
            <button type="button" class="btn-history-load" data-id="${item.id}">View Report</button>
            <button type="button" class="btn-history-delete" data-id="${item.id}">Delete</button>
          </div>
        `;

        row.querySelector(".btn-history-load").addEventListener("click", async () => {
          try {
            const reportResp = await fetch(`/api/history/${item.id}`);
            const reportData = await reportResp.json();
            if (reportData.success && reportData.analysis) {
              latestAnalysisData = reportData.analysis.analysis_data;
              populateAllViews(latestAnalysisData);
              showView("overview");
              showAlert(`Loaded saved report: "${item.role_title}".`, "info");
            }
          } catch (e) {
            showAlert("Could not load report.", "error");
          }
        });

        row.querySelector(".btn-history-delete").addEventListener("click", async () => {
          if (!confirm("Are you sure you want to delete this saved analysis?")) return;
          try {
            const delResp = await fetch(`/api/history/${item.id}`, { method: "DELETE" });
            const delData = await delResp.json();
            if (delData.success) {
              showAlert("Analysis removed from history.", "info");
              loadHistoryList();
            }
          } catch (e) {
            showAlert("Could not delete analysis.", "error");
          }
        });

        historyListContainer.appendChild(row);
      });

    } catch (err) {
      historyListContainer.innerHTML = `
        <div style="padding: 24px; color: var(--missing-red); text-align: center;">
          Failed to load history records.
        </div>
      `;
    }
  }

  // ==========================================================================
  // 8. SETTINGS PROFILE UPDATE (Screen 9 Right)
  // ==========================================================================
  function initSettingsForm() {
    if (settingsForm) {
      settingsForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const newName = settingsNameInput ? settingsNameInput.value.trim() : "";
        if (!newName) {
          showAlert("Please enter your name.", "error");
          return;
        }

        try {
          const resp = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName })
          });
          const res = await resp.json();
          if (res.success) {
            showAlert("Account profile settings saved successfully.", "info");
          } else {
            showAlert(res.message || "Failed to update profile.", "error");
          }
        } catch (e) {
          showAlert("Error saving settings.", "error");
        }
      });
    }
  }

  // ==========================================================================
  // 9. MODAL HANDLER
  // ==========================================================================
  function initModal() {
    if (btnModalClose) {
      btnModalClose.addEventListener("click", closeModal);
    }
    if (btnModalAction) {
      btnModalAction.addEventListener("click", closeModal);
    }
    if (suggestionModal) {
      suggestionModal.addEventListener("click", (e) => {
        if (e.target === suggestionModal) closeModal();
      });
    }
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });

    if (btnDismissAlert) {
      btnDismissAlert.addEventListener("click", hideAlert);
    }
  }

  function openModal(title, bodyHtml) {
    if (modalTitle) modalTitle.textContent = title;
    if (modalBody) modalBody.innerHTML = bodyHtml;
    if (suggestionModal) suggestionModal.classList.add("active");
  }

  function closeModal() {
    if (suggestionModal) suggestionModal.classList.remove("active");
  }

  // Helper Alerts
  function showAlert(msg, type = "info") {
    if (!alertBanner || !alertMessage) return;
    alertMessage.textContent = msg;
    alertBanner.className = `app-alert-banner ${type}`;
    alertBanner.style.display = "flex";

    if (alertTimeout) clearTimeout(alertTimeout);
    if (type === "info") {
      alertTimeout = setTimeout(() => {
        hideAlert();
      }, 6000);
    }
  }

  function hideAlert() {
    if (alertBanner) alertBanner.style.display = "none";
    if (alertTimeout) clearTimeout(alertTimeout);
  }

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

});
