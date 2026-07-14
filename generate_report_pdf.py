"""generate_report_pdf.py - Generates a premium academic report PDF document for the examiner."""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

# Define Palette
PRIMARY = colors.HexColor("#6d28d9")   # Deep Purple
SECONDARY = colors.HexColor("#4c1d95") # Darker Purple
TEXT_COLOR = colors.HexColor("#1f2937")# Charcoal Gray
LIGHT_BG = colors.HexColor("#f3f4f6")  # Warm Gray
BORDER_COLOR = colors.HexColor("#e5e7eb")
ACCENT_GREEN = colors.HexColor("#059669")
ACCENT_RED = colors.HexColor("#dc2626")

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to calculate total page count dynamically and render headers/footers."""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return
        
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_COLOR)
        
        # Draw Header
        self.drawString(54, 750, "SmartRetry — Academic Project Report & Viva Reference Guide")
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential — For Examiner Reference & Evaluation Only")
        self.line(54, 52, 558, 52)
        
        self.restoreState()

def build_pdf(filename="static/SmartRetry_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#4b5563"),
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=SECONDARY,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=TEXT_COLOR,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e1b4b"),
        backColor=LIGHT_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_COLOR,
        alignment=TA_LEFT
    )

    dialogue_q_style = ParagraphStyle(
        'DialogueQ',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    dialogue_a_style = ParagraphStyle(
        'DialogueA',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_COLOR,
        leftIndent=12,
        spaceAfter=8
    )

    story = []

    # ================= PAGE 1: COVER PAGE =================
    story.append(Spacer(1, 100))
    story.append(Paragraph("SmartRetry Framework", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("A Selenium-Based Smart Retry Engine & AI-Driven Flaky Test Detection System", subtitle_style))
    story.append(Spacer(1, 120))
    
    # Metadata Block
    meta_data = [
        [Paragraph("<b>Domain:</b> Software Testing & Quality Assurance", table_body_style)],
        [Paragraph("<b>Core Stack:</b> Python, Flask, Selenium WebDriver, SQLite, Google GenAI SDK", table_body_style)],
        [Paragraph("<b>Version:</b> 1.2.0 (Stable Release with Gemini Integration)", table_body_style)],
        [Paragraph("<b>Target Audience:</b> Academic Examiners, System Architects, QA Engineers", table_body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 150))
    story.append(Paragraph("<b>Submitted for Evaluation:</b> Academic Project Viva-Voce Examination", subtitle_style))
    story.append(PageBreak())

    # ================= PAGE 2: EXEC PURPOSE, AIM, OBJECTIVES =================
    story.append(Paragraph("1. Project Abstract & Core Foundations", h1_style))
    
    story.append(Paragraph("<b>1.1 Problem Statement</b>", h2_style))
    story.append(Paragraph(
        "Modern CI/CD pipelines suffer from high regression overhead caused by <i>Flaky Tests</i>—test cases "
        "that exhibit non-deterministic behavior (passing and failing without changes in the source code). "
        "Standard test suites either fail completely when an element load is delayed or result in slow suite "
        "durations due to excessive static waits. Additionally, standard Selenium engines implicitly block on "
        "network operations, masking transition bugs and leading to false-positive pass results that hide authentic race conditions.",
        body_style
    ))

    story.append(Paragraph("<b>1.2 Project Aim</b>", h2_style))
    story.append(Paragraph(
        "To develop an intelligent web automation framework that dynamically executes test scripts, "
        "intercepts test failures mid-transition, attempts immediate smart retries with exponential backoffs, "
        "flags non-deterministic results as 'flaky', and leverages Large Language Models (Gemini API) "
        "to deliver root-cause diagnostics and recommendations.",
        body_style
    ))

    story.append(Paragraph("<b>1.3 Key Objectives</b>", h2_style))
    story.append(Paragraph(
        "• <b>Objective 1: Non-Deterministic Defect Isolation:</b> Bypass default page loading blocks via customized driver "
        "configurations, allowing the test suite to execute assertions during active element transition states.<br/>"
        "• <b>Objective 2: Self-Healing Retry Loop:</b> Implement a robust retry engine containing configurable attempts, delays, "
        "and backoff multipliers, automatically updating executions schema to isolate temporary environment errors.<br/>"
        "• <b>Objective 3: Low-Latency Cloud AI Integration:</b> Integrate the Google GenAI SDK (gemini-3.5-flash) to evaluate "
        "tracebacks, return real-time root causes, and output varying confidence scores under 2 seconds.<br/>"
        "• <b>Objective 4: Live Timezone-Aware Evaluation Dashboards:</b> Deliver a visual user interface presenting localized "
        "execution feeds (IST), status indicators, log terminals, and evidence screenshots per attempt.<br/>"
        "• <b>Objective 5: Concurrency & Transaction Management:</b> Prevent application conflicts and write locks during parallel test "
        "runs using SQLite Write-Ahead Logging (WAL) mode for high-throughput scaling.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 3: TECH STACK & ARCHITECTURE =================
    story.append(Paragraph("2. System Architecture & Technologies", h1_style))
    
    story.append(Paragraph("<b>2.1 Technologies & Tools</b>", h2_style))
    
    tech_data = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Tech/Tool Chosen</b>", table_header_style), Paragraph("<b>Engineering Rationale</b>", table_header_style)],
        [Paragraph("Backend Framework", table_body_style), Paragraph("Flask 3.0.3", table_body_style), Paragraph("Lightweight, minimal routing overhead, ideal for integrating system scripts.", table_body_style)],
        [Paragraph("Automation Engine", table_body_style), Paragraph("Selenium 4.22.0", table_body_style), Paragraph("Standard API wrapper for absolute control over Chromium instances.", table_body_style)],
        [Paragraph("Database", table_body_style), Paragraph("SQLite3 (WAL Mode)", table_body_style), Paragraph("Single-file deployment with write-ahead-logging to prevent concurrency bottlenecks.", table_body_style)],
        [Paragraph("LLM Core", table_body_style), Paragraph("Google GenAI (Gemini-3.5-flash)", table_body_style), Paragraph("Natively supports new AQ-auth keys, <2s latency, high schema compliance.", table_body_style)],
        [Paragraph("Report Engine", table_body_style), Paragraph("ReportLab 4.2.2", table_body_style), Paragraph("Used to compile dynamic system execution and analytical PDF outputs.", table_body_style)],
    ]
    
    tech_table = Table(tech_data, colWidths=[110, 140, 250])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2.2 Core System Architecture</b>", h2_style))
    story.append(Paragraph(
        "The following diagram represents the layout flow of the architecture:",
        body_style
    ))

    # Replaced ASCII Art with a beautiful, clean table diagram to prevent PDF warping
    flow_data = [
        [Paragraph("<b>Step 1: User Request</b>", table_header_style), Paragraph("User submits prompt or runs a test via the Flask Web Dashboard UI.", table_body_style)],
        [Paragraph("<b>Step 2: Engine Setup</b>", table_header_style), Paragraph("SmartRetry Engine starts Chrome with <b>page_load_strategy = 'none'</b>.", table_body_style)],
        [Paragraph("<b>Step 3: Test Execution</b>", table_header_style), Paragraph("Executes steps. If a step fails, it initiates the Exponential Retry Loop.", table_body_style)],
        [Paragraph("<b>Step 4: State Analysis</b>", table_header_style), Paragraph("Saves screenshots and attempts. Sets final status to Pass, Fail, or Flaky.", table_body_style)],
        [Paragraph("<b>Step 5: AI Diagnostics</b>", table_header_style), Paragraph("Google Gemini SDK reviews error trace, returning dynamic root cause & fix details.", table_body_style)],
    ]
    flow_table = Table(flow_data, colWidths=[130, 370])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), SECONDARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (1,0), (1,-1), colors.white),
        ('ROWBACKGROUNDS', (1,0), (1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(flow_table)
    story.append(PageBreak())

    # ================= PAGE 4: FORMULAS & ALGORITHMS =================
    story.append(Paragraph("3. Core Algorithms, Math & Implementation Details", h1_style))
    
    story.append(Paragraph("<b>3.1 Mathematical Formulas</b>", h2_style))
    
    story.append(Paragraph("<b>3.1.1 Exponential Backoff Retry Delay</b>", h2_style))
    story.append(Paragraph(
        "To prevent swamping the browser during resource transitions, the delay duration <i>d</i> "
        "before attempt <i>i</i> (where <i>i</i> is the retry attempt index, <i>i</i> ≥ 1) is computed as:",
        body_style
    ))
    # Corrected LaTeX display formulas to clean ReportLab Paragraph tags
    story.append(Paragraph("<b>d<sub>i</sub> = D<sub>base</sub> × M<sup>(i - 1)</sup></b>", ParagraphStyle('FormulaStyle', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=12, spaceAfter=8)))
    story.append(Paragraph(
        "Where <b>D<sub>base</sub></b> is the base retry delay (configured as <code>RETRY_DELAY_SECONDS</code> in <code>.env</code>, e.g., 0.5 seconds), "
        "and <b>M</b> is the growth factor (configured as <code>RETRY_BACKOFF_MULTIPLIER</code>, e.g., 1.0).",
        body_style
    ))

    story.append(Paragraph("<b>3.1.2 Flakiness Severity Score</b>", h2_style))
    story.append(Paragraph(
        "The system aggregates execution logs within a sliding window of size <i>N</i> (default 10) to determine "
        "whether a test case is unstable. The flaky rating score <i>S</i> is calculated as:",
        body_style
    ))
    story.append(Paragraph("<b>S = [ ( C<sub>flaky</sub> × 0.7 + C<sub>failed</sub> ) / N ] × 100</b>", ParagraphStyle('FormulaStyle2', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=12, spaceAfter=8)))
    story.append(Paragraph(
        "Where <b>C<sub>flaky</sub></b> is the number of executions that passed on retry attempts (status = 'flaky'), "
        "and <b>C<sub>failed</sub></b> is the number of executions that failed all attempts. If <b>S = 0</b>, the verdict is <b>stable</b>; "
        "if <b>0 &lt; S &lt; 40</b>, it is <b>flaky</b>; and if <b>S ≥ 40</b>, it is flagged as <b>chronic</b>.",
        body_style
    ))

    story.append(Paragraph("<b>3.2 Step Execution Implementation</b>", h2_style))
    story.append(Paragraph(
        "To allow genuine flaky failure detection on step verification, the Selenium webdriver <code>page_load_strategy</code> "
        "is set to <code>'none'</code>. When an assertion step is executed, the <code>step_executor</code> avoids standard implicitly blocking "
        "Selenium calls and executes an instant JavaScript query directly on the DOM:",
        body_style
    ))
    story.append(Paragraph(
        "current_html = driver.execute_script(\"return document.documentElement ? document.documentElement.innerHTML : ''\")\n"
        "assert input_value.lower() in current_html.lower(), f\"Text '{input_value}' not found on page\"",
        code_style
    ))
    story.append(PageBreak())

    # ================= PAGE 5: API DOCUMENTATION =================
    story.append(Paragraph("4. System API Documentation", h1_style))
    
    story.append(Paragraph("The backend communicates with the UI and AI systems via Flask Blueprints. Below is the API spec:", body_style))
    
    api_data = [
        [Paragraph("<b>Endpoint</b>", table_header_style), Paragraph("<b>Method</b>", table_header_style), Paragraph("<b>Description & Response Structure</b>", table_header_style)],
        [
            Paragraph("`/api/generate-steps`", table_body_style), 
            Paragraph("POST", table_body_style), 
            Paragraph("<b>AI Step Generator:</b> Accepts user prompts, sends context to Google Gemini API (gemini-3.5-flash) and returns a JSON payload containing the Selenium steps array.<br/>"
                      "<b>Response (JSON):</b><br/>"
                      "<code>{ 'steps': [{ 'action': 'open_url', 'input_value': '...', 'timeout': 10 }] }</code>", table_body_style)
        ],
        [
            Paragraph("`/api/executions`", table_body_style), 
            Paragraph("GET", table_body_style), 
            Paragraph("Retrieves the last 50 execution records containing status, durations, logs, and screenshots.", table_body_style)
        ],
        [
            Paragraph("`/api/stats`", table_body_style), 
            Paragraph("GET", table_body_style), 
            Paragraph("Returns summarized stats: <code>{ 'total': 20, 'passed': 12, 'failed': 5, 'flaky': 3 }</code>", table_body_style)
        ],
        [
            Paragraph("`/ai-analysis/analyze/<exec_id>`", table_body_style), 
            Paragraph("POST", table_body_style), 
            Paragraph("Triggers a dedicated Gemini model call to analyze the traceback and execution logs, storing a dynamic confidence rating (e.g. 95%) and root cause inside the SQLite database.", table_body_style)
        ]
    ]

    api_table = Table(api_data, colWidths=[150, 60, 290])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(api_table)
    story.append(PageBreak())

    # ================= PAGE 6: CHALLENGES FACED =================
    story.append(Paragraph("5. Engineering Challenges & Solutions", h1_style))
    
    challenges = [
        ("1. Local LLM Latency (Ollama)",
         "Originally, the backend called a locally running Ollama (llama3.1) instance to generate steps. However, local GPU/CPU constraints caused steps to take over 12 minutes to generate, leading to browser request timeouts.",
         "Replaced Ollama with the cloud-based <b>Google Gemini API</b> (gemini-3.5-flash) using the official <code>google-genai</code> SDK (supporting both AIza and AQ auth keys). This reduced generation latency from 12 minutes to under 2 seconds."),
        
        ("2. False-Positive Flaky Pass Verdicts",
         "Standard Selenium `driver.page_source` queries block execution and wait internally for the browser to finish rendering. Because of this block, tests always passed on attempt 1, failing to capture flaky network states.",
         "Set Chrome's <code>page_load_strategy</code> to <code>'none'</code> to prevent blocking. The framework now queries the DOM instantly using raw JavaScript <code>document.documentElement.innerHTML</code>, ensuring realistic transition failures."),
        
        ("3. Concurrency Database Locks",
         "Simultaneous runs on the SQLite backend caused database write locks, crashing test suites.",
         "Configured SQLite to run in **Write-Ahead Logging (WAL) Mode** and set an explicit 30-second database connection timeout to ensure thread-safety and smooth multi-user operations."),
        
        ("4. GitHub Push Security Scanning",
         "Committing API keys or credentials to public codebases triggers security blockages and compromises API quotas.",
         "Removed `.env` from tracked commits and amended git history. Added a secure `.env` mapping loaded via python-dotenv, ensuring the repository code contains no sensitive strings.")
    ]

    for title, problem, solution in challenges:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(f"<b>Problem:</b> {problem}", body_style))
        story.append(Paragraph(f"<b>Solution:</b> {solution}", body_style))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # ================= PAGE 7: EXAMINER Q&A VIVA SCRIPT =================
    story.append(Paragraph("6. Simulated Examiner Viva-Voce Script", h1_style))
    story.append(Paragraph("This transcript shows a simulated conversation demonstrating how to explain key details to project examiners:", body_style))
    
    viva_dialogue = [
        ("Examiner", "What is the core problem this project solves, and how does it differ from standard automation engines like Jenkins or TestNG?"),
        ("Candidate", "Standard test frameworks fail a test case immediately if a network delay occurs, or they require hardcoded sleep statements that slow down the entire execution. SmartRetry solves this by implementing an active retry mechanism with exponential backoffs. If a step fails, the framework immediately retries it. If it passes on subsequent attempts, it's flagged as 'flaky' so the developer knows the application has non-deterministic behavior, rather than failing the entire build."),
        
        ("Examiner", "How do you define a flaky test in your database, and what algorithm calculates this rating?"),
        ("Candidate", "When a test run executes, we keep track of how many retry attempts it takes. If a test case passes but its retry count is greater than 0, we update its status in the database to 'flaky'. To calculate the overall project flakiness, we query the last 10 executions and compute a weighted severity score: Flaky runs count for 70% weight, while permanent fails count for 100%. If this ratio exceeds 40%, the test is flagged as 'chronic' indicating a severe code design flaw."),
        
        ("Examiner", "I see you're using 'page_load_strategy = none'. Why is that critical for your flaky detection?"),
        ("Candidate", "By default, Selenium blocks the thread and waits for the page to fire the 'load' event before executing subsequent commands. If we left it on default, we could never detect flaky conditions because Selenium would wait for the elements to fully render. By setting the page load strategy to 'none', we make Chrome return control immediately. We then run an instant JavaScript DOM query. This allows the assertion to fail on attempt 1 during the network transition, but pass on attempt 2 after a brief retry delay, which is the exact definition of a flaky test."),
        
        ("Examiner", "How is AI integrated into the framework, and what models are used?"),
        ("Candidate", "AI is integrated in two parts: First, a Visual Test Builder which converts natural language (e.g., 'search for shoes on Amazon') into a JSON array of Selenium steps. Second, a Failure Diagnosis engine. We call the official Google GenAI SDK to communicate with 'gemini-3.5-flash'. Gemini analyzes the stack traces and logs to output a dynamic, varying confidence rating and root cause, all formatted as raw JSON.")
    ]

    for speaker, text in viva_dialogue:
        if speaker == "Examiner":
            story.append(Paragraph(f"<b>Q: {text}</b>", dialogue_q_style))
        else:
            story.append(Paragraph(f"A: {text}", dialogue_a_style))
    story.append(PageBreak())

    # ================= PAGE 8: SAMPLE VIVA QUESTIONS =================
    story.append(Paragraph("7. Quick-Reference Viva Questions", h1_style))
    
    quick_viva = [
        ("Q: Why choose Flask over Django for the project?",
         "A: Flask is micro-framework oriented, making it extremely easy to plug in script run loops, background threads, and direct SQLite databases without the overhead of complex Django ORM migrations."),
        
        ("Q: What is the purpose of WAL mode in SQLite?",
         "A: WAL (Write-Ahead Logging) allows concurrent reads to proceed without being blocked by ongoing write operations, which is crucial when Selenium scripts are writing logs while the user is loading the dashboard."),
        
        ("Q: What happens if Gemini API limit is exceeded?",
         "A: We implemented an automated fallback mechanism: if the GenAI API returns an HTTP 429 quota error, the framework catches the exception and falls back to a regex-based heuristic analysis engine so the dashboard remains fully functional."),
        
        ("Q: Can this framework be used in a headless CI/CD pipeline?",
         "A: Yes. In the `.env` configuration file, setting `HEADLESS=true` executes Chrome inside virtual memory (without rendering GUI), making it ready for integration with Jenkins, GitLab CI, or GitHub Actions.")
    ]

    for q, a in quick_viva:
        story.append(Paragraph(f"<b>{q}</b>", dialogue_q_style))
        story.append(Paragraph(a, dialogue_a_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_pdf()
    print("SUCCESS: PDF compiled.")
