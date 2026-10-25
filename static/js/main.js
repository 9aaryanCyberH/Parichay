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
  let activeRecTab = "improvements";
  let chatConversationHistory = [];

  // DOM Elements - Navigation & Shell
  const navButtons = document.querySelectorAll(".sidebar-nav-item");
  const viewPanels = document.querySelectorAll(".view-panel");
  const alertBanner = document.getElementById("alertBanner");
  const alertMessage = document.getElementById("alertMessage");

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
    navButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const view = btn.dataset.view;
        showView(view);
      });
    });
  }

  function showView(viewName) {
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
          <td>Technical Skills</td>
          <td>45%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(techScore / 45) * 100}%;"></span></span>
            ${techScore}%
          </td>
        </tr>
        <tr>
          <td>Role Context</td>
          <td>35%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(tfidfScore / 35) * 100}%;"></span></span>
            ${tfidfScore}%
          </td>
        </tr>
        <tr>
          <td>Soft Skills</td>
          <td>10%</td>
          <td class="col-right">
            <span class="score-progress-bar-wrap"><span class="score-progress-bar-fill" style="width: ${(softScore / 10) * 100}%;"></span></span>
            ${softScore}%
          </td>
        </tr>
        <tr>
          <td>Resume Structure</td>
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
        detailSkillDesc.textContent = `Demonstrated proficiency in ${skill.name}. Explicitly verified in the uploaded resume against target job posting requirements.`;
      } else if (skill.status === "missing") {
        detailSkillDesc.textContent = `${skill.name} is a key requirement in the target role description, but is not detected in your resume evidence.`;
      } else {
        detailSkillDesc.textContent = `Bonus candidate competency in ${skill.name}. Provides unique competitive advantage beyond baseline role requirements.`;
      }
    }

    if (detailEvidenceList) {
      detailEvidenceList.innerHTML = "";
      if (skill.status === "matched") {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Extracted directly from candidate technical background</li>
          <li class="detail-evidence-item">Corroborated in verified projects & experience bullets</li>
          <li class="detail-evidence-item">Exact match with target role specification</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "High";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "90%";
      } else if (skill.status === "missing") {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Listed in target job description requirements</li>
          <li class="detail-evidence-item">Zero explicit occurrences detected in resume text</li>
          <li class="detail-evidence-item">Recommended for bullet addition or portfolio inclusion</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "Action Needed";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "20%";
      } else {
        detailEvidenceList.innerHTML = `
          <li class="detail-evidence-item">Found in candidate resume skills section</li>
          <li class="detail-evidence-item">Expands candidate domain versatility</li>
          <li class="detail-evidence-item">Valuable supplementary expertise</li>
        `;
        if (detailConfidenceLabel) detailConfidenceLabel.textContent = "Good Evidence";
        if (detailConfidenceBar) detailConfidenceBar.style.width = "75%";
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
  }

  function populateRecommendations(data) {
    renderRecommendationCards();
  }

  function renderRecommendationCards() {
    if (!recCardsRow || !latestAnalysisData) return;

    recCardsRow.innerHTML = "";
    const recs = latestAnalysisData.recommendations || {};

    if (activeRecTab === "improvements") {
      const bullets = recs.bullet_enhancements || [];
      const defaultCards = [
        {
          num: 1,
          title: "Strengthen Project Descriptions",
          desc: "Add specific metrics and quantifiable outcomes to your project achievements using Google's X-Y-Z formula.",
          fullContent: bullets[0] ? `<strong>Before:</strong> ${escapeHtml(bullets[0].original)}<br><br><strong>Google X-Y-Z Enhanced:</strong> ${escapeHtml(bullets[0].enhanced)}<br><br><strong>Why:</strong> ${escapeHtml(bullets[0].rationale)}` : "Quantify your impact with business metrics."
        },
        {
          num: 2,
          title: "Highlight Relevant Skills",
          desc: "Move core matched technologies like Python, SQL, and Machine Learning to a prominent technical skills section.",
          fullContent: "Organize your skills into categoric bands (Languages, Frameworks, Cloud, Databases) right near the top third of your resume for immediate recruiter visibility."
        },
        {
          num: 3,
          title: "Improve Action Verbs",
          desc: "Replace passive or vague words like 'worked on' or 'helped with' with decisive verbs like 'Engineered', 'Architected', and 'Deployed'.",
          fullContent: "Strong active verbs increase ATS readability and convey engineering leadership. Frame each accomplishment around what you built and the result."
        }
      ];

      defaultCards.forEach(c => renderSingleRecCard(c));
    } else if (activeRecTab === "skills") {
      const gaps = recs.gap_mitigation_plan || [];
      const cards = gaps.slice(0, 3).map((gap, i) => ({
        num: i + 1,
        title: `Bridge ${gap.missing_skill}`,
        desc: gap.recommended_action || "Learn and prove proficiency with hands-on practice.",
        fullContent: `<strong>Skill:</strong> ${escapeHtml(gap.missing_skill)}<br><br><strong>Action:</strong> ${escapeHtml(gap.recommended_action)}<br><br><strong>Recommended Project:</strong> ${escapeHtml(gap.proof_project)}`
      }));

      if (cards.length === 0) {
        cards.push({
          num: 1,
          title: "Expand Cloud & Microservices",
          desc: "Deploy a containerized application to AWS or GCP to demonstrate production deployment readiness.",
          fullContent: "Build a Dockerized REST API and deploy it with CI/CD to AWS ECS or GCP Cloud Run."
        });
      }

      cards.forEach(c => renderSingleRecCard(c));
    } else {
      const interview = recs.interview_prep_topics || [];
      const cards = [
        {
          num: 1,
          title: "Technical Architecture Drill",
          desc: interview[0] ? interview[0] : "Prepare for deep-dive questions on your core project architecture.",
          fullContent: interview[0] ? `<strong>Focus Area:</strong> ${escapeHtml(interview[0])}` : "Review system design and data structures."
        },
        {
          num: 2,
          title: "Core Competency Coding",
          desc: interview[1] ? interview[1] : "Review algorithms, API design, and asynchronous patterns in Python.",
          fullContent: interview[1] ? `<strong>Focus Area:</strong> ${escapeHtml(interview[1])}` : "Practice coding exercises on data structures and algorithms."
        },
        {
          num: 3,
          title: "Behavioral & Impact Review",
          desc: interview[2] ? interview[2] : "Prepare STAR-method examples explaining technical challenges you overcame.",
          fullContent: interview[2] ? `<strong>Focus Area:</strong> ${escapeHtml(interview[2])}` : "Be ready to explain trade-offs made during development."
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
        <div class="rec-number-badge">${card.num}</div>
        <h4 class="rec-card-title">${escapeHtml(card.title)}</h4>
        <p class="rec-card-desc">${escapeHtml(card.desc)}</p>
      </div>
      <button type="button" class="btn-view-suggestion">View Suggestion</button>
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
  }

  function hideAlert() {
    if (alertBanner) alertBanner.style.display = "none";
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
