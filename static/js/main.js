/**
 * Parichay — Resume Intelligence & Role Alignment Application
 * UI Reference: Figma Community Template (Dashboard Applicant Screens UI)
 * Manages file uploads, presets, live backend analysis, Chart.js radar, and reports.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Workspace & Studio
  const dropzone = document.getElementById("dropzone");
  const resumeInput = document.getElementById("resumeInput");
  const fileSelectedBox = document.getElementById("fileSelectedBox");
  const selectedFileName = document.getElementById("selectedFileName");
  const selectedFileSize = document.getElementById("selectedFileSize");
  const btnReplaceFile = document.getElementById("btnReplaceFile");
  const btnRemoveFile = document.getElementById("btnRemoveFile");
  const btnSampleResume = document.getElementById("btnSampleResume");
  const btnResetWorkspace = document.getElementById("btnResetWorkspace");

  const jdTextarea = document.getElementById("jdTextarea");
  const sampleChipsRow = document.getElementById("sampleChipsRow");
  
  const btnAnalyze = document.getElementById("btnAnalyze");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");
  const systemStatusText = document.getElementById("systemStatusText");

  const alertBanner = document.getElementById("alertBanner");
  const alertMessage = document.getElementById("alertMessage");

  // DOM Elements - Results Dashboard
  const dashboardSection = document.getElementById("dashboardSection");
  const btnResetAnalysis = document.getElementById("btnResetAnalysis");
  const btnPrintReport = document.getElementById("btnPrintReport");

  let currentFile = null;
  let radarChartInstance = null;
  let fullSkillsData = null;

  // Initialize Sample JDs from API
  fetchSampleJDs();
  initSidebarNav();

  // 1. Drag & Drop and File Input Handling
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
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    resumeInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  if (btnReplaceFile && resumeInput) {
    btnReplaceFile.addEventListener("click", () => {
      resumeInput.click();
    });
  }

  if (btnRemoveFile) {
    btnRemoveFile.addEventListener("click", (e) => {
      e.stopPropagation();
      clearSelectedFile();
    });
  }

  if (btnResetWorkspace) {
    btnResetWorkspace.addEventListener("click", () => {
      clearSelectedFile();
      if (jdTextarea) jdTextarea.value = "";
      hideAlert();
      if (dashboardSection) dashboardSection.style.display = "none";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // "Use Sample Resume" Trigger
  if (btnSampleResume) {
    btnSampleResume.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        const response = await fetch("/sample_data/sample_resume_swe.pdf");
        if (!response.ok) {
          throw new Error("Could not load sample PDF");
        }
        const blob = await response.blob();
        const sampleFile = new File([blob], "sample_resume_swe.pdf", { type: "application/pdf" });
        handleFileSelection(sampleFile);
        showAlert("Loaded verified candidate profile (Aarav Sharma — Software Engineer).", "info");
      } catch (err) {
        showAlert("Unable to auto-load sample PDF. Please select a PDF resume manually.", "error");
      }
    });
  }

  function handleFileSelection(file) {
    hideAlert();
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showAlert("Only PDF documents (.pdf) are supported. Please select a valid text-based PDF.", "error");
      return;
    }

    const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
    if (file.size > MAX_SIZE) {
      showAlert("The selected document exceeds the 5 MB maximum file limit. Please select a smaller PDF.", "error");
      return;
    }

    currentFile = file;
    if (selectedFileName) selectedFileName.textContent = file.name;
    if (selectedFileSize) selectedFileSize.textContent = formatBytes(file.size);
    
    if (dropzone) dropzone.style.display = "none";
    if (fileSelectedBox) fileSelectedBox.style.display = "flex";
  }

  function clearSelectedFile() {
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

  // 2. Fetch Sample Job Descriptions (Presets)
  async function fetchSampleJDs() {
    try {
      const res = await fetch("/api/sample-jds");
      const data = await res.json();
      if (data.success && data.sample_jds && sampleChipsRow) {
        sampleChipsRow.innerHTML = "";
        data.sample_jds.forEach((jd) => {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "preset-chip-btn";
          chip.textContent = jd.title;
          chip.title = `${jd.company_type} • ${jd.experience}`;
          chip.addEventListener("click", () => {
            if (jdTextarea) {
              jdTextarea.value = jd.description;
              showAlert(`Loaded role preset: "${jd.title}".`, "info");
            }
          });
          sampleChipsRow.appendChild(chip);
        });
      }
    } catch (e) {
      console.warn("Could not load sample JDs:", e);
    }
  }

  // Sidebar navigation active state handler
  function initSidebarNav() {
    const navItems = document.querySelectorAll(".sidebar-nav-item");
    navItems.forEach((item) => {
      item.addEventListener("click", () => {
        navItems.forEach((n) => n.classList.remove("active"));
        item.classList.add("active");
      });
    });
  }

  // 3. Form Submission & Analysis
  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", async () => {
      hideAlert();

      const jdText = jdTextarea ? jdTextarea.value.trim() : "";
      if (!currentFile) {
        showAlert("Please upload or attach a PDF resume to analyze alignment.", "error");
        return;
      }

      if (!jdText || jdText.split(/\s+/).length < 10) {
        showAlert("Please enter a comprehensive job description (at least 2-3 sentences) or select one of the role presets.", "error");
        return;
      }

      setLoadingState(true);

      const formData = new FormData();
      formData.append("resume", currentFile);
      formData.append("job_description", jdText);

      try {
        const response = await fetch("/api/analyze", {
          method: "POST",
          body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
          const errorMsg = result.message || "An unexpected error occurred during document processing.";
          showAlert(errorMsg, "error");
          return;
        }

        renderDashboard(result);

      } catch (err) {
        showAlert("Network connection error. Please verify the server is running and try again.", "error");
      } finally {
        setLoadingState(false);
      }
    });
  }

  function setLoadingState(isLoading) {
    if (isLoading) {
      if (btnAnalyze) btnAnalyze.disabled = true;
      if (btnSpinner) btnSpinner.style.display = "inline-block";
      if (btnText) btnText.textContent = "ANALYZING...";
      if (systemStatusText) systemStatusText.textContent = "Processing";
    } else {
      if (btnAnalyze) btnAnalyze.disabled = false;
      if (btnSpinner) btnSpinner.style.display = "none";
      if (btnText) btnText.textContent = "ANALYZE ALIGNMENT";
      if (systemStatusText) systemStatusText.textContent = "Ready";
    }
  }

  // 4. Render Analysis Dashboard (Figma Template Applicant Screens)
  function renderDashboard(data) {
    if (!dashboardSection) return;

    dashboardSection.style.display = "block";
    dashboardSection.scrollIntoView({ behavior: "smooth" });

    // Candidate Summary Header
    const candidateNameEl = document.getElementById("dashCandidateName");
    const candidateLinksEl = document.getElementById("dashCandidateLinks");
    if (candidateNameEl) {
      candidateNameEl.textContent = data.candidate.name || "Candidate Profile";
    }

    if (candidateLinksEl) {
      candidateLinksEl.innerHTML = "";
      
      if (data.candidate.email) {
        candidateLinksEl.innerHTML += `
          <span class="applicant-link-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            ${escapeHtml(data.candidate.email)}
          </span>
        `;
      }

      if (data.candidate.phone) {
        candidateLinksEl.innerHTML += `
          <span class="applicant-link-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
            </svg>
            ${escapeHtml(data.candidate.phone)}
          </span>
        `;
      }

      if (data.candidate.linkedin) {
        const url = data.candidate.linkedin.startsWith("http") ? data.candidate.linkedin : "https://" + data.candidate.linkedin;
        candidateLinksEl.innerHTML += `
          <span class="applicant-link-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
              <rect x="2" y="9" width="4" height="12"></rect>
              <circle cx="4" cy="4" r="2"></circle>
            </svg>
            <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          </span>
        `;
      }

      if (data.candidate.github) {
        const url = data.candidate.github.startsWith("http") ? data.candidate.github : "https://" + data.candidate.github;
        candidateLinksEl.innerHTML += `
          <span class="applicant-link-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
            <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">GitHub</a>
          </span>
        `;
      }

      candidateLinksEl.innerHTML += `
        <span class="applicant-link-pill">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          ${data.document_metrics.page_count} Page (${data.document_metrics.word_count} words)
        </span>
      `;
    }

    // Circular Score Badge
    const scoreValEl = document.getElementById("dashScoreVal");
    const tierBadgeEl = document.getElementById("dashTierBadge");
    const interpretationEl = document.getElementById("dashScoreInterpretation");

    animateNumber(scoreValEl, 0, data.alignment.score, 600);

    if (tierBadgeEl) {
      tierBadgeEl.textContent = data.alignment.fit_tier.toUpperCase();
    }

    if (interpretationEl) {
      if (data.alignment.score >= 75) {
        interpretationEl.textContent = "Strong overall alignment. The candidate's technical profile directly matches the primary competencies and domain expectations of this role, with clear evidence across multiple project and experience contexts.";
      } else if (data.alignment.score >= 55) {
        interpretationEl.textContent = "Moderate technical alignment. The profile demonstrates significant overlap with core tools, but several required technologies or domain concepts are missing from the resume.";
      } else {
        interpretationEl.textContent = "Limited alignment with posted requirements. Significant differences exist between the candidate's stated experience and the specific technical stack required for this position.";
      }
    }

    // 4-Pillar Score Cards
    renderBreakdownCards(data.alignment.score_breakdown.components);

    // Radar Chart
    renderRadarChart(data.alignment.score_breakdown.components);

    // Skills Matrix
    fullSkillsData = data.skills;
    setupSkillsTabs(data.skills);
    renderSkillsCluster("all");

    // Structural Health & Strengths
    renderAudit(data.audit, data.sections_detected);

    // Contextual AI Recommendations
    renderAdvisor(data.recommendations);
  }

  function renderBreakdownCards(components) {
    const listEl = document.getElementById("breakdownCardsList");
    if (!listEl) return;
    listEl.innerHTML = "";

    components.forEach((comp) => {
      const card = document.createElement("div");
      card.className = "pillar-box";
      card.innerHTML = `
        <div class="pillar-top">
          <span class="pillar-title">${escapeHtml(comp.name)}</span>
          <span class="pillar-score">${comp.contribution_points} pts</span>
        </div>
        <div class="pillar-meter">
          <div class="pillar-fill" style="width: ${Math.min(100, comp.achieved_percent)}%;"></div>
        </div>
        <p class="pillar-text">${escapeHtml(comp.description)}</p>
      `;
      listEl.appendChild(card);
    });
  }

  function renderRadarChart(components) {
    const canvas = document.getElementById("radarChart");
    if (!canvas) return;

    if (radarChartInstance) {
      radarChartInstance.destroy();
    }

    const labels = components.map((c) => c.name);
    const achievedData = components.map((c) => c.achieved_percent);
    const targetData = [100, 100, 100, 100];

    const ctx = canvas.getContext("2d");
    radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Candidate Evidence",
            data: achievedData,
            backgroundColor: "rgba(0, 123, 255, 0.16)",
            borderColor: "#007BFF",
            borderWidth: 2,
            pointBackgroundColor: "#007BFF",
            pointBorderColor: "#FFFFFF",
            pointRadius: 4
          },
          {
            label: "Target Role Baseline",
            data: targetData,
            backgroundColor: "rgba(176, 184, 196, 0.12)",
            borderColor: "#B0B8C4",
            borderWidth: 1.5,
            borderDash: [3, 3],
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: "#E2E6ED" },
            grid: { color: "#E2E6ED" },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: {
              display: false,
              stepSize: 25
            },
            pointLabels: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
                weight: "500"
              },
              color: "#4A5160"
            }
          }
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              font: {
                family: "'Inter', sans-serif",
                size: 11
              },
              boxWidth: 10,
              color: "#4A5160"
            }
          },
          tooltip: {
            backgroundColor: "#1E242E",
            titleFont: { family: "'Inter', sans-serif", size: 12 },
            bodyFont: { family: "'Inter', sans-serif", size: 12 },
            padding: 8,
            cornerRadius: 4
          }
        }
      }
    });
  }

  function setupSkillsTabs(skills) {
    const tabMatchedCount = document.getElementById("tabCountMatched");
    const tabMissingCount = document.getElementById("tabCountMissing");
    const tabUniqueCount = document.getElementById("tabCountUnique");

    if (tabMatchedCount) tabMatchedCount.textContent = skills.matched_technical.length;
    if (tabMissingCount) tabMissingCount.textContent = skills.missing_technical.length;
    if (tabUniqueCount) tabUniqueCount.textContent = skills.candidate_unique.length;

    const filterBtns = document.querySelectorAll(".figma-tab-btn");
    filterBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        filterBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        renderSkillsCluster(btn.dataset.tab);
      });
    });
  }

  function renderSkillsCluster(filter) {
    const container = document.getElementById("skillsClusterContainer");
    if (!container || !fullSkillsData) return;

    container.innerHTML = "";
    let items = [];

    if (filter === "all" || filter === "matched") {
      fullSkillsData.matched_technical.forEach((s) => {
        items.push({ name: s, type: "matched", label: "Matched" });
      });
      fullSkillsData.matched_soft.forEach((s) => {
        items.push({ name: s, type: "matched", label: "Soft Skill" });
      });
    }

    if (filter === "all" || filter === "missing") {
      fullSkillsData.missing_technical.forEach((s) => {
        items.push({ name: s, type: "missing", label: "Missing Requirement" });
      });
      fullSkillsData.missing_soft.forEach((s) => {
        items.push({ name: s, type: "missing", label: "Missing Soft" });
      });
    }

    if (filter === "all" || filter === "unique") {
      fullSkillsData.candidate_unique.forEach((s) => {
        items.push({ name: s, type: "unique", label: "Bonus Competency" });
      });
    }

    if (filter === "unverified" || (filter === "all" && fullSkillsData.unverified_skills.length > 0)) {
      fullSkillsData.unverified_skills.forEach((s) => {
        items.push({ name: s, type: "unverified", label: "Contextual Mention" });
      });
    }

    if (items.length === 0) {
      container.innerHTML = `<span style="font-size:0.82rem; color:var(--text-muted); font-style:italic;">No skills found under this filter.</span>`;
      return;
    }

    items.forEach((item) => {
      const pill = document.createElement("span");
      pill.className = `skill-tag-pill tag-${item.type}`;
      pill.innerHTML = `<strong>${escapeHtml(item.name)}</strong> <span class="pill-subtext">(${escapeHtml(item.label)})</span>`;
      container.appendChild(pill);
    });
  }

  function renderAudit(audit, sections) {
    const strengthsList = document.getElementById("resumeStrengthsList");
    const prioritiesList = document.getElementById("improvementPrioritiesList");

    if (strengthsList) {
      strengthsList.innerHTML = "";
      if (audit.strengths && audit.strengths.length > 0) {
        audit.strengths.forEach((str) => {
          const item = document.createElement("div");
          item.className = "audit-row-item";
          item.innerHTML = `
            <svg class="audit-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>${escapeHtml(str)}</span>
          `;
          strengthsList.appendChild(item);
        });
      } else {
        strengthsList.innerHTML = `<span style="font-size:0.82rem; color:var(--text-muted);">Standard profile coverage detected.</span>`;
      }
    }

    if (prioritiesList) {
      prioritiesList.innerHTML = "";
      if (audit.improvement_priorities && audit.improvement_priorities.length > 0) {
        audit.improvement_priorities.forEach((imp) => {
          const item = document.createElement("div");
          item.className = "priority-card";
          const pClass = imp.priority.toLowerCase();
          item.innerHTML = `
            <div class="priority-card-top">
              <span class="priority-badge p-${pClass}">${escapeHtml(imp.priority)} Priority</span>
            </div>
            <div class="priority-title">${escapeHtml(imp.area)}</div>
            <p class="priority-text">${escapeHtml(imp.details)}</p>
          `;
          prioritiesList.appendChild(item);
        });
      } else {
        prioritiesList.innerHTML = `<span style="font-size:0.82rem; color:var(--text-muted);">No critical structural gaps identified.</span>`;
      }
    }
  }

  function renderAdvisor(recommendations) {
    const engineBadge = document.getElementById("advisorEngineBadge");
    const execSummary = document.getElementById("advisorExecutiveSummary");
    const bulletContainer = document.getElementById("bulletEnhancementsList");
    const gapGrid = document.getElementById("gapMitigationGrid");
    const interviewList = document.getElementById("interviewPrepList");

    if (engineBadge) {
      engineBadge.textContent = recommendations.advisor_engine || "Parichay Advisor Engine";
    }

    if (execSummary) {
      execSummary.textContent = `“${recommendations.executive_summary}”`;
    }

    if (bulletContainer) {
      bulletContainer.innerHTML = "";
      if (recommendations.bullet_enhancements && recommendations.bullet_enhancements.length > 0) {
        recommendations.bullet_enhancements.forEach((enh) => {
          const entry = document.createElement("div");
          entry.className = "enhancement-card-entry";
          entry.innerHTML = `
            <div class="enhancement-head-text">${escapeHtml(enh.focus_area)}</div>
            <div class="enhancement-critique-text">${escapeHtml(enh.critique)}</div>
            <div class="enhancement-formula-box">
              <strong>Formula Action:</strong> ${escapeHtml(enh.recommended_action)}
            </div>
          `;
          bulletContainer.appendChild(entry);
        });
      }
    }

    if (gapGrid) {
      gapGrid.innerHTML = "";
      if (recommendations.gap_mitigation_plan && recommendations.gap_mitigation_plan.length > 0) {
        recommendations.gap_mitigation_plan.forEach((gap) => {
          const card = document.createElement("div");
          card.className = "gap-box-item";
          card.innerHTML = `
            <div class="gap-skill-header">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              ${escapeHtml(gap.missing_skill)}
            </div>
            <p class="gap-action-text">${escapeHtml(gap.concrete_action)}</p>
          `;
          gapGrid.appendChild(card);
        });
      }
    }

    if (interviewList) {
      interviewList.innerHTML = "";
      if (recommendations.interview_preparation_topics && recommendations.interview_preparation_topics.length > 0) {
        recommendations.interview_preparation_topics.forEach((topic, idx) => {
          const li = document.createElement("li");
          li.className = "interview-item";
          li.innerHTML = `
            <span class="interview-index-pill">0${idx + 1}</span>
            <span>${escapeHtml(topic)}</span>
          `;
          interviewList.appendChild(li);
        });
      }
    }
  }

  function animateNumber(element, start, end, duration) {
    if (!element) return;
    const range = end - start;
    let startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      element.textContent = Math.floor(progress * range + start);
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        element.textContent = end;
      }
    }

    window.requestAnimationFrame(step);
  }

  function showAlert(message, type = "error") {
    if (!alertBanner || !alertMessage) return;
    alertMessage.textContent = message;
    alertBanner.style.display = "flex";
    if (type === "error") {
      alertBanner.style.backgroundColor = "var(--missing-red-bg)";
      alertBanner.style.borderColor = "var(--missing-red-border)";
      alertBanner.style.color = "var(--missing-red)";
    } else {
      alertBanner.style.backgroundColor = "var(--figma-blue-subtle)";
      alertBanner.style.borderColor = "var(--figma-blue-border)";
      alertBanner.style.color = "var(--figma-blue)";
    }
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

  if (btnResetAnalysis) {
    btnResetAnalysis.addEventListener("click", () => {
      if (dashboardSection) dashboardSection.style.display = "none";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  if (btnPrintReport) {
    btnPrintReport.addEventListener("click", () => {
      window.print();
    });
  }
});
