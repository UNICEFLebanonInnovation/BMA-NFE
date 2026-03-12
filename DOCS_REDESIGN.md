# BMA – NFE Sector: UI/UX Redesign Technical Specifications

This document outlines the design and architectural changes implemented during the system modernization. These patterns are designed to be reusable for any Django-based operational management system using Bootstrap 5.

---

## 1. Global Architecture & Layout
*   **Modern Sidebar Implementation:**
    *   Replaced legacy ArchitectUI sidebar with a lightweight, collapsible Bootstrap 5 sidebar.
    *   **Width:** 350px (optimized for large screens) with responsive hiding on mobile.
    *   **Hierarchy:** Flat navigation structure for primary modules; nested menus avoided to reduce cognitive load.
*   **Native RTL Support:**
    *   Implemented logical CSS properties (e.g., `margin-inline-start`, `text-align: start`) instead of hardcoded `left/right` values.
    *   Used `bootstrap.rtl.min.css` dynamically based on user language settings.

## 2. Design System (Branding & Foundations)
*   **Color Palette (UNICEF-Inspired):**
    *   **Primary:** `#003366` (Deep Blue) - Used for navigation, headers, and primary actions.
    *   **Secondary:** `#00ADEF` (Light Blue) - Used for info alerts and secondary indicators.
    *   **Success:** `#28a745` (Green) - Used for final submissions and active statuses.
    *   **Background:** `#F4F7F6` (Light Gray) - Used for main content areas to reduce glare.
*   **Typography:**
    *   Standardized on **Inter** (fallback to system sans-serif).
    *   **Font Weights:** 400 (Regular), 600 (Semibold), 700 (Bold).
    *   **Base size:** 14px (optimized for high-density operational data).

## 3. Form UX Patterns (Critical for High Accuracy)
*   **Intuitive Guidance:**
    *   **Placeholders:** Every text input has a descriptive example (e.g., `e.g. Ahmad`, `teacher@example.com`).
    *   **Help Text:** Standardized format instructions (e.g., `Format: XX-XXXXXX`) placed directly under the input.
*   **Logical Organization:**
    *   **Fieldsets:** Forms are broken down into logical sections (Identity, Contact, Assignment) using Django-crispy-forms `Fieldset`.
    *   **Visual Hierarchy:** Section headers are larger and bold; minor notes are small and muted.
*   **Wizard Workflow (NFE Registration):**
    *   Divided complex registration (80+ fields) into a **3-step linear wizard**:
        1. **Identity:** Basic bio and nationality.
        2. **Caregivers & Household:** Social/Economic data and primary contacts.
        3. **Review & Confirm:** A summary view of all data before final server submission.
    *   **Validation:** Step-by-step client-side validation prevents users from proceeding with errors.

## 4. Operational Data Tables
*   **High-Density Efficiency:**
    *   Reduced table cell padding (`py-2`) to maximize information visible on screen.
    *   **Sticky Headers:** Implemented `.sticky-top` on `<thead>` with high z-index to keep headers visible during long scrolls.
*   **Responsive Containers:**
    *   Wrapped all tables in `.table-responsive` to handle overflow on 14-inch screens.
    *   **Row Hover:** Sublte background change on hover for better row tracking in large datasets.

## 5. Beneficiary Profile & IA
*   **Information Decoupling:**
    *   Extracted Education History from general bio and moved to a dedicated tab.
    *   **Vertical Timelines:** Used for chronological data (Education rounds, assessments) to visualize progress over time.
*   **Actionable Dashboarding:**
    *   Profile headers now contain a summary "Mini-Dashboard" with key IDs, ages, and statuses.

## 6. Component Reusability Checklist
*   **Authentication UI:** Redesigned login and password management pages into a centered, narrow card layout to improve focus and professional feel.
*   **Buttons:** Standardized on `btn-primary` for "Save/Finish" and `btn-outline-secondary` for "Cancel/Back".
*   **Cards:** Standardized on `border-0 shadow-sm` for a modern "floating" feel.
*   **Icons:** Globally migrated to **Bootstrap Icons (BI)** for consistency and performance.
*   **Search Filters:** Migrated all search panels to Bootstrap **Offcanvas** elements to keep the main list view clean and focused.

## 7. Technical Implementation Notes
*   **CSS Entry Point:** `student_registration/static/css/redesign.css`
*   **JS Core Logic:** `student_registration/static/js/mscc/mscc.js` (Handles wizard, validation, and AJAX duplication checks).
*   **Base Template:** `student_registration/templates/base.html` (The "Golden Source" for layouts).
*   **Standard Table Template:** `student_registration/templates/django_tables2/bootstrap5.html`