# BMA – NFE Sector UI/UX Redesign Proposal

## 1. Information Architecture (IA)

The proposed architecture streamlines the user journey by grouping operational tasks into logical modules.

### Modules & Navigation
- **Dashboard (Landing Page)**: Central hub for overview and quick actions.
- **Registration**: Focused, distraction-free environment for adding new beneficiaries.
- **Beneficiaries (Management)**: Searchable database of all registered students/children.
- **Operations**:
    - **Attendance**: Daily and monthly tracking interfaces.
    - **Centers & Schools**: Management of physical locations.
    - **Teachers**: Staff records and assignments.
- **Analytics & Reporting**:
    - **Standard Reports**: Pre-defined exports.
    - **Pivot Builder**: Custom data analysis.
    - **Insights**: Visual dashboards (PowerBI/D3 integrations).
- **Admin**: User roles, permissions, reference data (Governorates, Cazas, etc.), and Audit Logs.

### User Flow: New Registration
1. `Dashboard` -> `Quick Action: Register New`
2. `Step 1: Identity` (Real-time duplicate check)
3. `Step 2: Caregiver Info`
4. `Step 3: Vulnerability/Education Status`
5. `Step 4: Summary & Confirmation`
6. `Success Screen` -> `Option to Print Card or Register Another`

---

## 2. Wireframe-level Layouts

### Login
- **Layout**: Centered minimal card.
- **Components**: Logo, Username/Email, Password (with toggle visibility), "Remember Me", Login Button.
- **UX**: Clear error messages below inputs; "Forgotten Password" link prominent.

### Landing Page (Dashboard)
- **Top Row**: 3-4 Metric Cards (Total Active Students, Attendance Rate this week, Pending Exports).
- **Primary Area**: "Quick Action" Tiles (Large icons: Register, Attendance, Search).
- **Secondary Area**: "Recent Activity" feed and "My Tasks" (e.g., "3 cases need follow-up").

### NFE Registration Form (Wizard)
- **Top**: Horizontal Stepper (Identity -> Caregivers -> Vulnerability -> Review).
- **Body**: 2-column grid for related fields.
- **Sidebar (Contextual)**: Real-time "Potential Duplicates" panel that updates as the name/DOB is typed.
- **Footer**: Sticky bar with [Back], [Save Draft], [Next].

### Beneficiary Profile Page
- **Header**: High-level summary (Photo, Name, ID, Status: Active/Inactive, Primary Phone).
- **Tabs**:
    - **Overview**: Personal info summary.
    - **Enrollment**: History of rounds and programs.
    - **Attendance**: Calendar view or list of absences.
    - **Services**: History of received support/interventions.
- **Actions**: Edit, Deactivate, Transfer, Print ID.

### Case / Enrollment Tracking Page
- **Layout**: Full-width data table with "Quick Filter" chips at the top.
- **Components**: Status badges (e.g., "Active", "Dropped Out", "Graduated"), Priority icons, Date of last interaction.
- **UX**: Search bar that supports Student ID, Name, or Caregiver Phone. Infinite scroll or clear pagination.

### Reporting / Insights Page
- **Layout**: Dashboard grid of "Data Widgets."
- **Components**: High-level aggregate numbers at the top, followed by interactive charts (Bar charts for age distribution, Line charts for enrollment trends).
- **UX**: "Export to Excel/PDF" buttons prominent on every widget. Ability to filter the entire dashboard by Center or Date Range.

### Admin / Settings Page
- **Layout**: Left-hand sub-navigation for categories (Users, Roles, Reference Data, System Logs).
- **Components**: Permission matrix for role management; CRUD interfaces for reference data (e.g., list of Cazas).
- **UX**: Searchable audit log showing system-wide changes.

---

## 3. Design System Summary

### Typography
- **Primary Font**: Inter (Variable font for optimal legibility at all sizes).
- **Scale**:
    - H1: 32px (Bold)
    - H2: 24px (Semibold)
    - Body: 16px (Regular)
    - Caption: 13px (Medium)

### Spacing & Grid
- **Base Unit**: 8px.
- **Margins**: 24px on desktop, 16px on mobile.
- **Container**: Max-width 1440px for readability on large monitors.

### Components (Bootstrap 5 Based)
- **Buttons**:
    - Primary: Solid UNICEF Blue (#0097D7), 4px border-radius.
    - Secondary: Outlined blue or light gray.
    - Danger: Red (#D93025) for destructive actions.
- **Forms**:
    - Top-aligned labels.
    - Inputs: 48px height for touch-friendliness.
    - Validation: Inline error text in red; green border for valid required fields.
- **Tables**:
    - Dense/Normal toggle.
    - Sticky headers.
    - Zebra striping (light gray).
    - **Row Actions**: A single "Kebab" (vertical three dots) menu at the end of each row for secondary actions.

- **Navigation**:
    - **Top Bar**: Fixed height (64px), contains the logo (left), global search (center), and user profile/notifications (right).
    - **Sidebar**: Collapsible (240px expanded to 64px icon-only). Items are grouped by category with clear icons. Active state uses a high-contrast sidebar indicator.

- **Empty States**:
    - **Pattern**: Centered illustration (minimalist), clear headline, and a primary CTA.
    - **Example**: "No beneficiaries found. [Register New Student]".

---

## 4. UX Improvements

### Bulk Operations
- **Pattern**: Checkboxes on every table row.
- **Interaction**: Upon selection, a "Selection Bar" appears at the bottom with actions (Bulk Export, Bulk Edit, Change Status).

### Duplicate Detection
- **Pattern**: Non-blocking search.
- **UX**: As the user types Name + DOB, the system queries the database. If a match > 80% is found, a subtle alert appears: *"Found 2 similar records. [View Details]"*.

### Offline/Low Connectivity
- **Pattern**: "Save as Draft" using browser `localStorage`.
- **UX**: If the connection drops, a "Work Offline" indicator appears. Data is synced automatically once back online.

### Audit Trail
- **Pattern**: Sidebar "History" panel on all record pages.
- **UX**: Shows *Who, What, When* for the last 10 changes.

---

## 5. Sample Component Patterns

### Global Search
- **Behavior**: Command + K (Mac) or Ctrl + K (Windows) opens a modal search.
- **Scope**: Search for Students by ID/Name, Centers, or Navigation items.

### Filter Panel
- **Behavior**: Slides out from the right (Offcanvas).
- **UX**: Allows filtering complex tables without cluttering the main view. Includes a "Clear All" button.

### Confirmation Dialogs
- **Behavior**: Standard Bootstrap Modal.
- **UX**: Destructive actions (e.g., Delete) require typing "DELETE" or the record ID to confirm.

---

## 6. Implementation Checklist (Dev-Ready)

### Technical Prerequisites
- [ ] Upgrade to **Bootstrap 5.3** (utilize CSS variables).
- [ ] Migrate from **jQuery** to **Vanilla JS** for core interactions.
- [ ] Use **django-crispy-forms** with `crispy-bootstrap5`.

### Step-by-Step implementation
1. **Layout Overhaul**: Create `templates/base_redesign.html` using a Flexbox-based Sidebar/Main structure.
2. **RTL Implementation**: Use `bootstrap.rtl.min.css` and set `dir="rtl"` based on language context.
3. **Template Refactoring**:
    - Convert `main_card` wrappers to standard BS5 `.card`.
    - Replace `smartwizard` with a native BS5 Stepper component.
4. **Form Logic**: Move `reorganizeForm` logic from `mscc.js` into modular JS controllers (e.g., Stimulus or Alpine.js for lightweight reactivity).
5. **Assets**: Standardize icons using **Lucide Icons** (SVG-based, lightweight).

---

## Recommended Next Steps
1. **Interactive Prototype**: Create a Figma prototype focusing on the Registration Wizard.
2. **Usability Testing**: Conduct 5-10 tests with operators (both low and high tech-literacy).
3. **Phased Rollout**: Implement the new Landing Page and Navigation first, keeping old forms in a "Legacy" tab to minimize disruption.
