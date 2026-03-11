# BMA – NFE Sector: UI/UX Redesign Documentation

## 1. Information Architecture (IA)

### Core Modules
1.  **Dashboard (Landing Page):** Central hub for operational activity, quick actions, and high-level KPIs via Power BI integration.
2.  **NFE Registration:** 3-step streamlined wizard (Identity, Caregivers/Household, Review) for enrolling beneficiaries.
3.  **Beneficiary Management:**
    *   **Beneficiary List:** High-density data table with advanced filtering (Partner, Center, Program, Status).
    *   **Beneficiary Profile:** Multi-tab view (Personal Info, Education History, Services, Attendance).
4.  **Operational Tools:**
    *   **Attendance Tracking:** Monthly logs and daily export tools.
    *   **Center Management:** Management of physical locations, p-codes, and associated staff.
5.  **Analytics:** Integrated Power BI reporting for sector-wide monitoring.

### Navigation Structure
*   **Global Search:** Persistent search in top navigation for ID or Name.
*   **Sidebar (Collapsible):** Dashboard, Beneficiary List, New Registration, Attendance Reports, Center Management, Admin Settings.
*   **User Profile:** Right-aligned menu for account settings, password changes, and logout.

---

## 2. Design System Summary

### Typography Scale
*   **Primary Font:** Inter / System Sans-Serif.
*   **Headings:** Bold (700 weight), Primary Color (#003366 - UNICEF Blue variant).
*   **Body:** Regular (400 weight), #333333 for readability.
*   **Labels/Captions:** Semibold (600 weight), Uppercase for section headers.

### Spacing & Layout
*   **Base Unit:** 8px (Grid system: 8, 16, 24, 32, 48, 64).
*   **Containers:** Max-width fluid with standard gutters (g-4).
*   **Cards:** Bordered, shadow-sm, 0.5rem border-radius.

### Component Styles
*   **Buttons:**
    *   **Primary:** Solid blue, rounded-2, bold text.
    *   **Secondary/Outline:** For non-critical actions (Export, Edit).
    *   **Danger:** Reserved for Delete/Remove actions with confirmation.
*   **Forms:**
    *   **Inputs:** High-contrast borders, clear focus states.
    *   **Validation:** Real-time feedback with `is-invalid` classes and `invalid-feedback` text.
*   **Tables:**
    *   **Sticky Headers:** Crucial for large datasets.
    *   **Hover States:** Row highlighting for easier tracking.
    *   **Density:** Tight padding (py-2) for operational efficiency.

---

## 3. UX Improvements

### Bulk Operations
*   **Export:** Unified export dialog with format selection and background processing alerts.
*   **Import:** Standardized CSV/Excel templates with pre-validation logic.

### Duplicate Detection
*   **Real-time Check:** As user types Name/DOB in the registration form, a background AJAX call checks for matches and displays a "Potentially Registered" warning with a link to the existing profile.

### Connectivity Considerations
*   **Client-side Persistence:** Registration wizard steps are saved locally to prevent data loss on browser refresh.
*   **Optimistic UI:** Actions (like attendance marking) update the UI immediately while syncing in the background.

---

## 4. Developer Implementation Checklist (Bootstrap 5.3)

- [x] **Framework Upgrade:** Migrate legacy ArchitectUI/Bootstrap 4 classes to Bootstrap 5.3 native classes.
- [x] **Global CSS:** Implement UNICEF branding in `redesign.css`.
- [x] **Layout Template:** Use `base.html` with the new sidebar/topbar structure.
- [x] **RTL Support:** Ensure `html dir="rtl"` works correctly with Bootstrap 5's native RTL support.
- [x] **Sticky Headers:** Apply `.sticky-top` and high z-index to `thead` in `django_tables2`.
- [x] **Wizard Logic:** Use `mscc.js` for step transitions and validation.
- [x] **Icons:** Standardize on **Bootstrap Icons (BI)** for lightweight loading.
