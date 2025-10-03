# Component Map - Therapy Compliance Analyzer

## 🗺️ Visual Component Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THERAPY COMPLIANCE ANALYZER                       │
│                        PT | OT | SLP                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  MENU BAR                                                            │
├─────────────────────────────────────────────────────────────────────┤
│  📁 File  │  🔧 Tools  │  👁️ View  │  ⚙️ Admin  │  ❓ Help         │
│  ├─ Upload Document                                                  │
│  ├─ Upload Folder                                                    │
│  ├─ Export PDF                                                       │
│  ├─ Export HTML                                                      │
│  └─ Exit                                                             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  TAB WIDGET                                                          │
├─────────────────────────────────────────────────────────────────────┤
│  [📋 Analysis] [📊 Dashboard] [📄 Reports] [⚙️ Admin]              │
└─────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════╗
║  📋 ANALYSIS TAB                                                     ║
╠═════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  ANALYSIS SETUP                                               │  ║
║  ├──────────────────────────────────────────────────────────────┤  ║
║  │  Discipline: [PT ▼] [OT] [SLP]                               │  ║
║  │  [📄 Upload Document] [📁 Upload Folder] No document selected │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  ┌─────────────────────────┬────────────────────────────────────┐  ║
║  │  📄 DOCUMENT            │  📊 ANALYSIS RESULTS               │  ║
║  ├─────────────────────────┼────────────────────────────────────┤  ║
║  │                         │  Compliance Score: [████░░] 75%    │  ║
║  │  [Document text area]   │                                    │  ║
║  │                         │  ┌──────────────────────────────┐  │  ║
║  │  Paste or upload your   │  │ Issue | Severity | $ | Tip  │  │  ║
║  │  therapy documentation  │  ├──────────────────────────────┤  │  ║
║  │  here...                │  │ Missing signature | HIGH |   │  │  ║
║  │                         │  │ Goals not measurable | MED   │  │  ║
║  │                         │  │ Medical necessity | HIGH     │  │  ║
║  │                         │  └──────────────────────────────┘  │  ║
║  └─────────────────────────┴────────────────────────────────────┘  ║
║                                                                      ║
║  [🔍 Run Analysis] [⏹️ Stop] [💬 AI Chat] [📥 Export] [🗑️ Clear]  ║
║  [Progress Bar: ████████████████████████████] 100%                  ║
╚═════════════════════════════════════════════════════════════════════╝

╔═════════════════════════════════════════════════════════════════════╗
║  📊 DASHBOARD TAB                                                    ║
╠═════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────┬──────────────┬──────────────┐                    ║
║  │ Total        │ Average      │ Issues       │                    ║
║  │ Analyses     │ Score        │ Found        │                    ║
║  │              │              │              │                    ║
║  │    0         │    0%        │    0         │                    ║
║  └──────────────┴──────────────┴──────────────┘                    ║
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  COMPLIANCE TRENDS                                            │  ║
║  ├──────────────────────────────────────────────────────────────┤  ║
║  │  📈 Historical compliance trends                              │  ║
║  │  📊 Breakdown by discipline and issue type                    │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  [🔄 Refresh Dashboard]                                             ║
╚═════════════════════════════════════════════════════════════════════╝

╔═════════════════════════════════════════════════════════════════════╗
║  📄 REPORTS TAB                                                      ║
╠═════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  REPORT VIEWER                                                │  ║
║  ├──────────────────────────────────────────────────────────────┤  ║
║  │                                                               │  ║
║  │  Therapy Compliance Analysis Report                          │  ║
║  │  ═══════════════════════════════════════                     │  ║
║  │  Discipline: PT                                               │  ║
║  │  Compliance Score: 75%                                        │  ║
║  │  Total Financial Risk: $100                                   │  ║
║  │                                                               │  ║
║  │  Findings:                                                    │  ║
║  │  • Missing signature ($50)                                    │  ║
║  │  • Goals not measurable ($50)                                 │  ║
║  │                                                               │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  [📥 Export as PDF] [📥 Export as HTML] [📥 Export as JSON]        ║
╚═════════════════════════════════════════════════════════════════════╝

╔═════════════════════════════════════════════════════════════════════╗
║  ⚙️ ADMIN TAB (Admin Users Only)                                    ║
╠═════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │  ADMIN FUNCTIONS                                              │  ║
║  ├──────────────────────────────────────────────────────────────┤  ║
║  │  [👥 User Management]                                         │  ║
║  │  [📊 Team Analytics]                                          │  ║
║  │  [📋 Audit Logs]                                              │  ║
║  │  [🗄️ Database Maintenance]                                    │  ║
║  │  [⚙️ System Settings]                                         │  ║
║  │  [📚 Rubric Management]                                       │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚═════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│  STATUS BAR                                                          │
├─────────────────────────────────────────────────────────────────────┤
│  Ready - Select discipline and upload documentation                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💬 AI Chat Dialog (Popup Window)

```
┌─────────────────────────────────────────────────────────────┐
│  AI Chat Assistant                                      [X] │
├─────────────────────────────────────────────────────────────┤
│  💬 Chat History:                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ AI: Hello! I can help with compliance questions...   │ │
│  │                                                       │ │
│  │ You: How do I write measurable goals?                │ │
│  │                                                       │ │
│  │ AI: Goals should be SMART: Specific, Measurable,     │ │
│  │     Achievable, Relevant, Time-bound. Example:       │ │
│  │     "Patient will increase right shoulder flexion    │ │
│  │     from 90° to 120° within 3 weeks..."             │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Your Question:                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Type your question here...                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  [Send Message]                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌──────────────┐
│   USER       │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  1. SELECT DISCIPLINE (PT/OT/SLP)                    │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  2. UPLOAD DOCUMENT                                   │
│     • File dialog                                     │
│     • Load text                                       │
│     • Display in editor                               │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  3. CLICK "RUN ANALYSIS"                             │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  4. BACKGROUND WORKER                                 │
│     • AnalysisWorker thread                          │
│     • ComplianceAnalyzer.analyze()                   │
│     • Check rules for discipline                     │
│     • Calculate score                                │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  5. DISPLAY RESULTS                                   │
│     • Update score bar                                │
│     • Populate findings table                         │
│     • Generate HTML report                            │
│     • Show in Reports tab                             │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  6. USER ACTIONS                                      │
│     • Review findings                                 │
│     • Ask AI chat questions                           │
│     • Export report (PDF/HTML)                        │
│     • Clear and analyze next document                 │
└──────────────────────────────────────────────────────┘
```

---

## 🏗️ Class Structure

```
TherapyComplianceWindow (QMainWindow)
├── Menu Bar
│   ├── File Menu
│   ├── Tools Menu
│   ├── View Menu
│   ├── Admin Menu
│   └── Help Menu
│
├── Tab Widget
│   ├── Analysis Tab
│   │   ├── Controls Group
│   │   │   ├── Discipline Combo
│   │   │   └── Upload Buttons
│   │   ├── Splitter
│   │   │   ├── Document Text Edit
│   │   │   └── Results Group
│   │   │       ├── Score Bar
│   │   │       └── Results Table
│   │   └── Action Buttons
│   │
│   ├── Dashboard Tab
│   │   ├── Summary Cards
│   │   ├── Charts Group
│   │   └── Refresh Button
│   │
│   ├── Reports Tab
│   │   ├── Report Viewer
│   │   └── Export Buttons
│   │
│   └── Admin Tab
│       └── Admin Functions
│
├── Status Bar
│
└── Dialogs
    └── Chat Dialog

ComplianceAnalyzer
├── PT Rules (5 rules)
├── OT Rules (5 rules)
├── SLP Rules (5 rules)
├── analyze_compliance()
└── check_rule()

AnalysisWorker (QThread)
├── run()
├── finished signal
├── error signal
└── progress signal

ChatDialog (QWidget)
├── Chat History
├── Input Area
├── Send Button
└── generate_response()
```

---

## 📊 Feature Matrix

| Feature | PT | OT | SLP | Status |
|---------|----|----|-----|--------|
| Signature Check | ✅ | ✅ | ✅ | Complete |
| Goals Check | ✅ | ✅ | ✅ | Complete |
| Medical Necessity | ✅ | ✅ | ✅ | Complete |
| Skilled Services | ✅ | ❌ | ✅ | Complete |
| Progress Documentation | ✅ | ❌ | ✅ | Complete |
| Assistant Supervision | ❌ | ✅ | ❌ | Complete |
| Plan of Care | ❌ | ✅ | ✅ | Complete |
| **Total Rules** | **5** | **5** | **5** | **15** |

---

## 🎯 Button Locations

### Analysis Tab
```
Top Section:
  [📄 Upload Document] [📁 Upload Folder]

Bottom Section:
  [🔍 Run Analysis] [⏹️ Stop] [💬 AI Chat] [📥 Export] [🗑️ Clear]
```

### Dashboard Tab
```
Bottom Section:
  [🔄 Refresh Dashboard]
```

### Reports Tab
```
Bottom Section:
  [📥 Export as PDF] [📥 Export as HTML] [📥 Export as JSON]
```

### Admin Tab
```
Vertical Stack:
  [👥 User Management]
  [📊 Team Analytics]
  [📋 Audit Logs]
  [🗄️ Database Maintenance]
  [⚙️ System Settings]
  [📚 Rubric Management]
```

---

## 🔗 Component Connections

```
User Action → Button Click → Event Handler → Worker Thread → Analysis
                                                    ↓
                                              Results Signal
                                                    ↓
                                            Update UI Components
                                                    ↓
                                    [Score Bar] [Table] [Report]
```

---

This map shows every component, button, window, and feature in the application!
