/**
 * Parichay — Editorial Career Intelligence Web Application
 * Handles file uploads, sample dataset injection, live backend analysis,
 * interactive Chart.js visualizations, and report exports.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const resumeInput = document.getElementById("resumeInput");
  const fileSelectedBox = document.getElementById("fileSelectedBox");
  const selectedFileName = document.getElementById("selectedFileName");
  const selectedFileSize = document.getElementById("selectedFileSize");
  const btnRemoveFile = document.getElementById("btnRemoveFile");
  const btnSampleResume = document.getElementById("btnSampleResume");

  const jdTextarea = document.getElementById("jdTextarea");
  const sampleChipsRow = document.getElementById("sampleChipsRow");
  
  const btnAnalyze = document.getElementById("btnAnalyze");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");

  const alertBanner = document.getElementById("alertBanner");
  const alertMessage = document.getElementById("alertMessage");

  const dashboardSection = document.getElementById("dashboardSection");
  const btnResetAnalysis = document.getElementById("btnResetAnalysis");
  const btnPrintReport = document.getElementById("btnPrintReport");

  let currentFile = null;
  let radarChartInstance = null;
  let fullSkillsData = null;

  // Initialize Sample JDs from API
  fetchSampleJDs();

  // 1. Drag & Drop File Handling
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

  btnRemoveFile.addEventListener("click", (e) => {
    e.stopPropagation();
    clearSelectedFile();
  });

  // "Use Sample Resume" Helper
  if (btnSampleResume) {
    btnSampleResume.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        const response = await fetch("/sample_data/sample_resume_swe.pdf");
        if (!response.ok) {
          // If direct static fetch fails, fetch via API or blob
          throw new Error("Could not load sample PDF");
        }
        const blob = await response.blob();
        const sampleFile = new File([blob], "sample_resume_swe.pdf", { type: "application/pdf" });
        handleFileSelection(sampleFile);
        showAlert("Loaded sample software engineering resume.", "success");
      } catch (err) {
        // Fallback: create mock file with valid PDF bytes
        showAlert("Unable to auto-load sample PDF. Please select a PDF resume manually.", "error");
      }
    });
  }

  function handleFileSelection(file) {
    hideAlert();
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showAlert("Only PDF files (.pdf) are supported. Please select a valid PDF document.", "error");
      return;
    }

    const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
    if (file.size > MAX_SIZE) {
      showAlert("The selected file is too large (max 5 MB). Please select a smaller PDF.", "error");
      return;
    }

    currentFile = file;
    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatBytes(file.size);
    
    dropzone.style.display = "none";
    fileSelectedBox.style.display = "flex";
  }

  function clearSelectedFile() {
    currentFile = null;
    resumeInput.value = "";
    selectedFileName.textContent = "";
    selectedFileSize.textContent = "";
    fileSelectedBox.style.display = "none";
    dropzone.style.display = "flex";
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // 2. Sample Job Descriptions
  async function fetchSampleJDs() {
    try {
      const res = await fetch("/api/sample-jds");
      const data = await res.json();
      if (data.success && data.sample_jds && sampleChipsRow) {
        sampleChipsRow.innerHTML = "";
        data.sample_jds.forEach((jd) => {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "sample-chip";
          chip.textContent = jd.title;
          chip.title = `${jd.company_type} • ${jd.experience}`;
          chip.addEventListener("click", () => {
            jdTextarea.value = jd.description;
            showAlert(`Loaded example job description for "${jd.title}".`, "info");
          });
          sampleChipsRow.appendChild(chip);
        });
      }
    } catch (e) {
      console.warn("Could not load sample JDs:", e);
    }
  }

  // 3. Form Submission & Analysis
  btnAnalyze.addEventListener("click", async () => {
    hideAlert();

    const jdText = jdTextarea.value.trim();
    if (!currentFile) {
      showAlert("Please upload your PDF resume to begin analysis.", "error");
      return;
    }

    if (!jdText || jdText.split(/\s+/).length < 10) {
      showAlert("Please enter a comprehensive job description (at least 2-3 sentences) or select one of the example roles.", "error");
      return;
    }

    // Set Loading State
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
        const errorMsg = result.message || "An unexpected error occurred during analysis.";
        showAlert(errorMsg, "error");
        return;
      }

      // Render Results Dashboard
      renderDashboard(result);

    } catch (err) {
      showAlert("Network connection error. Please verify the server is running and try again.", "error");
    } finally {
      setLoadingState(false);
    }
  });

  function setLoadingState(isLoading) {
    if (isLoading) {
      btnAnalyze.disabled = true;
      btnSpinner.style.display = "inline-block";
      btnText.textContent = "Analyzing Qualifications...";
    } else {
      btnAnalyze.disabled = false;
      btnSpinner.style.display = "none";
      btnText.textContent = "Analyze Resume Alignment";
    }
  }

  // 4. Render Dashboard View
  function renderDashboard(data) {
    // Reveal Dashboard
    dashboardSection.style.display = "block";
    dashboardSection.scrollIntoView({ behavior: "smooth" });

    // Candidate Info
    const candidateNameEl = document.getElementById("dashCandidateName");
    const candidateLinksEl = document.getElementById("dashCandidateLinks");
    candidateNameEl.textContent = data.candidate.name || "Candidate";

    candidateLinksEl.innerHTML = "";
    if (data.candidate.email) {
      candidateLinksEl.innerHTML += `<span class="contact-item">✉ ${data.candidate.email}</span>`;
    }
    if (data.candidate.phone) {
      candidateLinksEl.innerHTML += `<span class="contact-item">☎ ${data.candidate.phone}</span>`;
    }
    if (data.candidate.linkedin) {
      candidateLinksEl.innerHTML += `<span class="contact-item">🔗 <a href="${data.candidate.linkedin.startsWith('http') ? data.candidate.linkedin : 'https://' + data.candidate.linkedin}" target="_blank">LinkedIn</a></span>`;
    }
    if (data.candidate.github) {
      candidateLinksEl.innerHTML += `<span class="contact-item">💻 <a href="${data.candidate.github.startsWith('http') ? data.candidate.github : 'https://' + data.candidate.github}" target="_blank">GitHub</a></span>`;
    }
    candidateLinksEl.innerHTML += `<span class="contact-item">📄 ${data.document_metrics.page_count} Page (${data.document_metrics.word_count} words)</span>`;

    // Alignment Score & Tier
    const scoreValEl = document.getElementById("dashScoreVal");
    const tierBadgeEl = document.getElementById("dashTierBadge");
    
    animateNumber(scoreValEl, 0, data.alignment.score, 600);

    tierBadgeEl.textContent = data.alignment.fit_tier;
    tierBadgeEl.className = `fit-tier-badge tier-${data.alignment.tier_badge}`;

    // 4-Component Breakdown
    renderBreakdownCards(data.alignment.score_breakdown.components);

    // Chart.js Radar Visualization
    renderRadarChart(data.alignment.score_breakdown.components, data.alignment.score);

    // Skills Matrix
    fullSkillsData = data.skills;
    setupSkillsTabs(data.skills);
    renderSkillsCluster("all");

    // Grounded AI Advisor
    renderAdvisor(data.recommendations);

    // Audit / Health
    renderAudit(data.audit, data.sections_detected);
  }

  function renderBreakdownCards(components) {
    const listEl = document.getElementById("breakdownCardsList");
    listEl.innerHTML = "";

    components.forEach((comp) => {
      const card = document.createElement("div");
      card.className = "component-card";
      card.innerHTML = `
        <div class="component-card-top">
          <span class="component-card-name">${comp.name}</span>
          <span class="component-card-weight">${comp.achieved_percent}% achieved (${comp.contribution_points} pts)</span>
        </div>
        <div class="component-progress-bar">
          <div class="component-progress-fill" style="width: ${Math.min(100, comp.achieved_percent)}%;"></div>
        </div>
        <p class="component-card-desc">${comp.description}</p>
      `;
      listEl.appendChild(card);
    });
  }

  function renderRadarChart(components, overallScore) {
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
            backgroundColor: "rgba(24, 72, 160, 0.18)",
            borderColor: "#1848A0",
            borderWidth: 2,
            pointBackgroundColor: "#1848A0",
            pointBorderColor: "#FFFFFF",
            pointRadius: 4
          },
          {
            label: "Target Role Baseline",
            data: targetData,
            backgroundColor: "rgba(218, 214, 204, 0.1)",
            borderColor: "#DCD6CC",
            borderWidth: 1.5,
            borderDash: [4, 4],
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: "#E8E4DC" },
            grid: { color: "#E8E4DC" },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: {
              display: false,
              stepSize: 25
            },
            pointLabels: {
              font: {
                family: "'Plus Jakarta Sans', sans-serif",
                size: 11,
                weight: "500"
              },
              color: "#52525B"
            }
          }
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              font: {
                family: "'Plus Jakarta Sans', sans-serif",
                size: 12
              },
              boxWidth: 12,
              color: "#52525B"
            }
          },
          tooltip: {
            backgroundColor: "#18181B",
            titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            padding: 10,
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

    const tabBtns = document.querySelectorAll(".skill-tab-btn");
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        tabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const category = btn.dataset.tab;
        renderSkillsCluster(category);
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
        items.push({ name: s, type: "missing", label: "Missing in Resume" });
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
      container.innerHTML = `<span style="font-size:0.86rem; color:var(--text-muted); font-style:italic;">No skills found in this view.</span>`;
      return;
    }

    items.forEach((item) => {
      const tag = document.createElement("span");
      tag.className = `skill-badge skill-${item.type}`;
      tag.innerHTML = `<strong>${item.name}</strong> <small style="opacity:0.75; font-size:0.72rem;">(${item.label})</small>`;
      container.appendChild(tag);
    });
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

    // Bullet enhancements
    if (bulletContainer) {
      bulletContainer.innerHTML = "";
      if (recommendations.bullet_enhancements && recommendations.bullet_enhancements.length > 0) {
        recommendations.bullet_enhancements.forEach((enh) => {
          const card = document.createElement("div");
          card.className = "enhancement-card";
          card.innerHTML = `
            <div class="enhancement-focus">${enh.focus_area}</div>
            <div class="enhancement-critique">Observation: ${enh.critique}</div>
            <div class="enhancement-action"><strong>Recommended Action:</strong> ${enh.recommended_action}</div>
          `;
          bulletContainer.appendChild(card);
        });
      }
    }

    // Gap mitigation
    if (gapGrid) {
      gapGrid.innerHTML = "";
      if (recommendations.gap_mitigation_plan && recommendations.gap_mitigation_plan.length > 0) {
        recommendations.gap_mitigation_plan.forEach((gap) => {
          const card = document.createElement("div");
          card.className = "gap-card";
          card.innerHTML = `
            <div class="gap-skill-title">⚡ ${gap.missing_skill}</div>
            <p class="gap-action-text">${gap.concrete_action}</p>
          `;
          gapGrid.appendChild(card);
        });
      }
    }

    // Interview prep topics
    if (interviewList) {
      interviewList.innerHTML = "";
      if (recommendations.interview_preparation_topics && recommendations.interview_preparation_topics.length > 0) {
        recommendations.interview_preparation_topics.forEach((topic, idx) => {
          const li = document.createElement("li");
          li.className = "interview-topic-item";
          li.innerHTML = `
            <span class="bullet-num">Q${idx + 1}</span>
            <span>${topic}</span>
          `;
          interviewList.appendChild(li);
        });
      }
    }
  }

  function renderAudit(audit, sections) {
    const strengthsList = document.getElementById("resumeStrengthsList");
    const prioritiesList = document.getElementById("improvementPrioritiesList");

    if (strengthsList) {
      strengthsList.innerHTML = "";
      if (audit.strengths && audit.strengths.length > 0) {
        audit.strengths.forEach((str) => {
          const item = document.createElement("div");
          item.className = "audit-item";
          item.innerHTML = `<span style="color:var(--state-matched-text); font-weight:bold;">✔</span> <span>${str}</span>`;
          strengthsList.appendChild(item);
        });
      } else {
        strengthsList.innerHTML = `<span style="font-size:0.86rem; color:var(--text-muted);">Standard profile coverage.</span>`;
      }
    }

    if (prioritiesList) {
      prioritiesList.innerHTML = "";
      if (audit.improvement_priorities && audit.improvement_priorities.length > 0) {
        audit.improvement_priorities.forEach((imp) => {
          const item = document.createElement("div");
          item.className = "audit-item";
          const pClass = imp.priority.toLowerCase();
          item.innerHTML = `
            <span class="audit-badge priority-${pClass}">${imp.priority}</span>
            <div><strong>${imp.area}:</strong> ${imp.details}</div>
          `;
          prioritiesList.appendChild(item);
        });
      } else {
        prioritiesList.innerHTML = `<span style="font-size:0.86rem; color:var(--text-muted);">No critical structural gaps identified.</span>`;
      }
    }
  }

  // Animate numeric score
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

  // Feedback Helpers
  function showAlert(message, type = "error") {
    alertMessage.textContent = message;
    alertBanner.style.display = "flex";
    if (type === "error") {
      alertBanner.className = "alert-banner alert-error";
    } else {
      alertBanner.className = "alert-banner";
      alertBanner.style.backgroundColor = "var(--cobalt-subtle)";
      alertBanner.style.borderColor = "var(--cobalt-border)";
      alertBanner.style.color = "var(--cobalt)";
    }
  }

  function hideAlert() {
    alertBanner.style.display = "none";
  }

  // Secondary Controls
  if (btnResetAnalysis) {
    btnResetAnalysis.addEventListener("click", () => {
      dashboardSection.style.display = "none";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  if (btnPrintReport) {
    btnPrintReport.addEventListener("click", () => {
      window.print();
    });
  }
});
