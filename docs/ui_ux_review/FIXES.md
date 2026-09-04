# UI/UX review — what was fixed

Companion to `README.md` (the review itself). Six commits, `7a8aae7`..`6ce60ac`.

Everything below was verified against the app running locally with seeded data
for all five roles (superuser, centre, partner, UNICEF, ALP school), in English
and Arabic, at desktop and mobile widths.

## How it was verified

Five repeatable checks, run after every change:

| Check | What it asserts | Result |
| --- | --- | --- |
| URL sweep | all 210 routes, as each of 5 roles | no 5xx except the two noted below |
| Broken-page smoke | the 24 URLs the review found broken | 24/24 |
| Edit-form smoke | 8 edit pages open unbound, no errors | 8/8 |
| Access control | 11 anonymous / wrong-role / GET-delete attempts | 11/11 refused |
| Navigation | every sidebar link, per role | 0 dead ends |

Plus `manage.py check` clean, a headless-browser pass over 22 pages (no
JavaScript errors), and the project's own test suite: **9 tests failed before
this work and the same 9 fail after** — no regression, and none of them was in
scope.

## What was fixed

**Crashes.** The django-braces `GroupRequiredMixin` clashes with Django 5's
`AccessMixin.handle_no_permission`, so 66+ views returned 500 instead of 403 to
a user in the wrong group; replaced with a compatible mixin. A template tag
delegated to a name it never imported, taking down three list pages. Serializers
referenced four fields that no longer exist on their models. 45 object lookups
took an id from the URL and raised `DoesNotExist` — a 500 — for any id that
didn't exist. Attendance crashed without a month parameter, and export history
crashed on `localtime()` with `USE_TZ` off.

**Every form script was dead.** jQuery 3 removed the `.load()` event shorthand.
Thirteen scripts open with `$(window).load(fn)`, which throws under jQuery 3.7,
so none of their setup ran: the bridging form and its four assessments, the
school forms, three teacher forms, and the registration pages. All their
conditional fields, validation and score calculations were inert.

**The registration wizard lost data.** Edit views bound the form with the stored
record, so opening a child for editing showed "Registration Failed" and a dozen
errors before any input. `child_fe_unique_id` was a `ChoiceField` with no
choices, rejecting everything typed into it. A dead `#id_type` selector meant a
branch never ran and its `else` wiped the Formal Education ID on every change.
`checkArabicOnly` deleted every non-Arabic character on blur without a word to
the user. The name validator rejected hyphens and apostrophes, so "Abdul-Rahman"
could not be saved. The stepper was decoration, Reset sat beside Submit, the
search spinner never stopped, and the duplicate warning's link opened a modal
that did not exist.

**Arabic never reached the UI.** Labels were built with `gettext` at import time,
so every form label, table header and filter was resolved once in English and
frozen. Switched 27 modules to `gettext_lazy` — MSCC's registration form goes
from 0 to 77 of 77 labels in Arabic. 28 translated strings had never been
compiled into the `.mo`. JavaScript had no route to the catalogue at all
(`window.gettext` was undefined); added `JavaScriptCatalog` and a `djangojs`
catalogue for the 45 strings the scripts translate.

**Access control.** Two attendance endpoints had no access check whatsoever —
anyone reachable could POST attendance for any centre. Six delete endpoints
accepted GET from any signed-in account, so an `<img src>` was enough to destroy
a record. The push-token endpoint was `csrf_exempt` while rebinding the caller's
token. The landing page computed every figure over the whole database and listed
every organisation's exports.

**Wrong numbers.** The dropout indicator compared attended days against a flat 45
regardless of whether the round had finished, reporting 100% (all 29 of 29
children on the current data). Centre disability counts treated "never recorded"
as "has a disability". CLM attendance stored `Yes`/`No` but read `yes`, so
attended days always came back 0. The ALP dashboard's chart script 404'd, and
its data endpoint answered with keys nothing reads.

**Layout.** `.sidebar` is a flex item with no `flex-shrink`, so any page wider
than the viewport squeezed it to ~50px and wrapped its labels a letter at a
time.

## Left undone, and why

**Five export endpoints still return 500.** `/clm/bridging-export-all/`,
`/clm/bridging-school-export-data/<id>/`, `/locations/export/`,
`/locations/export-center-background/`, `/schools/school-export-background/` and
`/students/teacher-export/` all query hand-maintained SQL views —
`vw_bridging_extract`, `vw_bridging_data`, `vw_center_data` and 13 others. **No
migration creates any of them**, so they exist only in databases where somebody
made them by hand, and a freshly migrated environment cannot run exports at all.
Writing those definitions means reproducing schema that only the production
database has; they should be captured from there into a migration.

**163 UI strings have no Arabic translation.** Most belong to third-party apps
(django-celery-beat and friends), but a handful are this project's own — four
school-profile labels among them. They are missing from `django.po` entirely,
not mistranslated, so they need a translator rather than a code change. The 17
new JavaScript strings were written to match the terminology already in the
catalogue and are worth a native reviewer's eye.

**`EducationService.education_program` and `MSCCAttendance.education_program`
disagree.** Attendance offers ABLN Level 1/2, ABLN Catch-up and BLN Catch-up;
registration does not, and registration offers four ALP levels that attendance
does not. A child in an ABLN programme therefore has attendance recorded against
a programme their registration cannot name. Which list is correct is a programme
decision, not a code one.

**The 9 pre-existing test failures** are in the ALP school-profile, pivot
dashboard, teacher dashboard and tables tests. They fail identically before and
after this work and were outside the review's scope.

**"Analytics default filters show zeros" could not be reproduced.** The
analytics summary returns real figures with no parameters, and the Advanced
Analytics page is commented out of the navigation, so it is unreachable.
