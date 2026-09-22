# QA Test Agent and Data Validation & Quality Implementation Plan

## 1. Purpose

This document is the approved starting specification for implementing a QA and
data-quality capability for the MSCC `Child` and `Registration` records. The
implementation will be delivered incrementally and will contain three related
components:

1. a deterministic data-quality rules engine;
2. continuous duplicate-beneficiary detection; and
3. a QA test-generation and maintenance agent.

The first release will operate in **monitor-only mode**. It will report quality
problems and possible duplicates without blocking saves, changing beneficiary
data, merging records, or deleting records.

## 2. Approved product decisions

| Decision | Approved direction |
| --- | --- |
| Initial beneficiary scope | MSCC `Child` and `Registration` |
| Initial operating mode | Monitor only |
| Cross-partner reviewer | Dedicated `DATA_QUALITY_REVIEWER` group |
| Initial interface language | English first |
| Internationalization | All new user-facing text must be translation-ready from the first implementation |
| Arabic interface | Add after the English workflow stabilizes |
| Reviewer identity visibility | `DATA_QUALITY_REVIEWER` members may see complete identity and phone values without masking |
| Duplicate execution | Continuous backend checks for new and materially updated records |
| Duplicate scope | Same-partner, geographic, and cross-partner candidate generation |
| Automatic merge/delete | Excluded |
| General Celery task tests | Excluded |
| Export tests | Included, including export business logic invoked by background tasks |
| Test styles | Python `unittest`, Django `TestCase`, and pytest |

### 2.1 Approved reviewer privacy boundary

Members of `DATA_QUALITY_REVIEWER` may see complete identity and phone values
without masking in the reviewer interface. This permission is limited to that
dedicated group and authorized administrators; membership alone must not grant
permission to edit, merge, delete, or reassign beneficiary records.

Ordinary partner users must not gain access to complete cross-partner identity
or phone values. Access to duplicate evidence and every review decision must be
auditable. Permission tests must verify both the approved reviewer access and
the denial of access to unauthorized users.

## 3. Responsibilities

### 3.1 Product supervisor

The product supervisor will:

- approve each business rule, its severity, scope, and eventual blocking state;
- provide representative valid and invalid business examples;
- approve what counts as a duplicate and what is only supporting evidence;
- nominate pilot partners, geographic areas, exports, and reviewers;
- approve which users may view and resolve cross-partner cases;
- classify reviewer outcomes and approve remediation procedures;
- review each increment and request changes before the next increment starts;
- decide which monitored rules may later become blocking.

### 3.2 Implementation agent

The implementation agent will:

- analyze models, forms, serializers, views, permissions, imports, and exports;
- design and implement versioned deterministic rules;
- implement issue, run, candidate, decision, and audit persistence;
- implement efficient normalization and duplicate candidate generation;
- enforce same-partner and cross-partner authorization boundaries;
- implement `unittest`, Django `TestCase`, pytest, authorization, regression,
  duplicate, and export tests;
- run checks, review diffs, and document assumptions;
- provide screenshots for visible web changes;
- commit every completed increment and prepare a pull request;
- report test results, limitations, pending decisions, and recommended next work.

## 4. Functional architecture

The capability should be implemented as a dedicated Django application rather
than adding more unrelated responsibilities to the existing `child` or `mscc`
applications. The provisional application name is `data_quality`; the name will
be finalized before its first migration.

```text
data_quality
├── models.py             Quality runs, issues, candidates, and decisions
├── rules/                Versioned deterministic rule implementations
├── matching/             Normalization, blocking, comparison, and scoring
├── services.py           Orchestration independent of HTTP and task runners
├── permissions.py        Reviewer and cross-partner authorization
├── admin.py              Initial operational review interface
├── management/commands/  Manual audit and historical backfill entry points
└── tests/                Unit, integration, permission, and regression tests
```

Business behavior must live in callable services. Forms, serializers,
management commands, and any asynchronous trigger should call those services
rather than implement separate copies of a rule.

## 5. Initial data-quality design

### 5.1 Rule result contract

Every rule evaluation should return structured information containing:

- stable rule code and rule version;
- subject type and record identifier;
- result (`pass`, `fail`, `not_applicable`, or `error`);
- severity;
- affected fields;
- safe, structured evidence;
- translation-ready message code and parameters;
- evaluation timestamp.

Rule execution errors must be recorded separately from data failures. A broken
rule must not incorrectly classify a beneficiary as having invalid data.

### 5.2 Initial rule lifecycle

Rules will support these states:

- `DRAFT`: implemented or proposed but not executed operationally;
- `MONITORING`: evaluated and reported without blocking;
- `ACTIVE_WARNING`: visible warning that does not block a save;
- `ACTIVE_BLOCKING`: may reject an invalid write after separate approval;
- `DISABLED`: retained historically but not evaluated.

All first-release rules will be `MONITORING`.

### 5.3 Proposed first rule catalog

The product supervisor must approve the exact applicability and wording of each
rule before it is activated:

| Code | Proposed rule | Initial severity |
| --- | --- | --- |
| `DQ-BIRTH-001` | Complete birth-date components must form a real date | Error |
| `DQ-BIRTH-002` | Birth date must not be in the future | Error |
| `DQ-ID-001` | Populated identity value and confirmation must match | Error |
| `DQ-PHONE-001` | Populated phone value and confirmation must match | Error |
| `DQ-NATIONALITY-001` | Other nationality requires explanatory text | Warning |
| `DQ-DISABILITY-001` | Other disability requires explanatory text | Warning |
| `DQ-CHILDREN-001` | No children implies a zero or empty count | Warning |
| `DQ-CHILDREN-002` | Having children requires a positive count | Warning |
| `DQ-CASH-001` | `None` cannot be selected with another cash programme | Warning |
| `DQ-RELATION-001` | Registration partner and center relationship must be valid | Error |
| `DQ-RELATION-002` | Registration must refer to an existing child | Error |

Existing historical records will be scanned without being changed. A finding
will be deduplicated by subject, rule, rule version, and open status so repeated
scans do not flood the review queue.

## 6. Duplicate-beneficiary design

### 6.1 Continuous behavior

Duplicate candidate generation will be triggered after a `Child` is created or
after a material matching field changes. It must not make record creation depend
on an external AI service. An execution failure must not lose the submitted
record.

Material fields initially include:

- child first, father, and last names;
- mother or caregiver name components;
- gender;
- birth-date components;
- nationality;
- identity and case-number fields;
- primary and secondary phone values;
- partner and center on the related registration;
- P-Code and other available geographic relationships.

Changing a material field must invalidate or re-evaluate affected open
candidates. A confirmed non-duplicate pair may be reconsidered only after a
material change or matching-version change, and the previous decision must
remain in the audit history.

### 6.2 Candidate generation

Candidate generation must use blocking to avoid comparing every new child with
every existing child. Initial candidate routes are:

1. exact normalized identity or case number;
2. exact normalized phone plus supporting demographic evidence;
3. normalized or phonetic name bucket plus birth-date evidence;
4. same-partner name and demographic bucket;
5. same-geographic-area name and demographic bucket;
6. cross-partner bucket requiring stronger identity or demographic evidence.

Arabic and English normalization will be deterministic, versioned, and tested.
The original values will remain unchanged. Transliteration and phonetic
similarity will generate candidates, not declare duplicates.

### 6.3 Evidence and confidence

Each candidate must store explainable field comparisons and the matcher version.
The first implementation will use configurable deterministic weights rather
than a trained opaque model. Confidence levels are:

- `HIGH`: strong identity evidence or multiple agreeing demographic signals;
- `MEDIUM`: strong name/date/geographic similarity requiring review;
- `LOW`: weak supporting similarity, retained without flooding the main queue.

Thresholds will be finalized using reviewed pilot examples. Candidate scores
must never automatically merge, delete, or reassign a record.

### 6.4 Cross-partner access

- Only authenticated members of `DATA_QUALITY_REVIEWER`, authorized
  administrators, and explicitly approved service code may query complete
  cross-partner candidate evidence.
- Partner users may be informed that a possible cross-partner duplicate needs
  central review, but must not thereby receive the other partner's complete
  beneficiary record.
- Review access and decisions must be logged.
- Query-level filtering and object-level permission tests are both required.

### 6.5 Review outcomes

The initial outcomes are:

- confirmed duplicate;
- not a duplicate;
- related household member;
- insufficient evidence;
- deferred for investigation.

Remediation and record merging are outside the first implementation. A
confirmed duplicate is an audited finding for authorized staff to resolve using
an approved operating procedure.

## 7. QA test-agent scope

### 7.1 Included

- pure Python `unittest` coverage for normalization, rules, and scoring;
- Django `TestCase` coverage for models and database behavior;
- pytest fixtures and parametrized cases;
- Factory Boy factories for users, partners, centers, children, and
  registrations;
- form, serializer, view, API, permission, and object-scope tests;
- deterministic-rule and duplicate candidate tests;
- same-partner and cross-partner authorization tests;
- export permissions, filters, schemas, row counts, encoding, file validity,
  duplicate rows, and formula-injection tests;
- regression tests for every confirmed defect;
- test suggestions based on changed application behavior.

Generated tests are proposals subject to engineering review. The agent must not
weaken assertions merely to obtain a passing result or approve its own changes.

### 7.2 Excluded

- general Celery broker, worker routing, retry, and queue-infrastructure tests;
- automatic production deployment;
- automatic business-rule changes;
- automatic beneficiary modification, merging, or deletion.

Export business logic remains testable directly even when production invokes it
through a background task.

## 8. Delivery phases

The schedule assumes incremental supervision and review rather than maximum
parallel development. Estimates are planning ranges and will be updated after
the discovery baseline.

| Phase | Duration | Implementation output | Product input or approval |
| --- | ---: | --- | --- |
| 0. Discovery and specification | 3–5 days | This specification, code-path inventory, initial rules, permission model | Approve scope and clarify rule questions |
| 1. QA foundation | 5–7 days | Test structure, factories, `unittest`, Django and pytest baseline, coverage | Prioritize critical workflows |
| 2. Quality core | 7–10 days | Quality run, issue, rule, audit models and monitor-only service | Approve statuses, severities, and reviewers |
| 3. Initial rules | 7–10 days | First approved rules, manual audit, form/API consistency tests | Approve each rule and remediation text |
| 4. Normalization | 7–10 days | Versioned Arabic/English name, phone, identity, and date normalization | Supply representative variations |
| 5. Candidate generation | 10–15 days | Continuous same-partner, geographic, and cross-partner candidates | Review candidate examples |
| 6. Scoring and review UI | 10–15 days | Explainable score, review queue, outcomes, permissions, audit | Approve the review workflow |
| 7. Export QA | 7–10 days | Critical export contract, permission, filter, content, and safety tests | Rank exports and approve expected output |
| 8. QA agent automation | 7–10 days | Change analysis, test suggestions, focused execution, regression workflow | Approve release gates and report format |
| 9. Pilot and tuning | 10 days | Pilot metrics, threshold tuning, performance and defect fixes | Select pilot and classify results |
| 10. Production rollout | 5–10 days | Approved rule activation, controlled backfill, monitoring, runbooks | Approve blocking rules and operating owners |

The recommended supervised production timeline is approximately 18–20 weeks.
The first monitor-only deterministic rules should be available around week 6,
continuous candidate generation around week 11, and the reviewer workflow
around week 14.

## 9. Pull-request sequence

Each increment will be independently reviewable and will include focused tests:

1. specification and decision record;
2. QA test foundation and factories;
3. quality models, permissions, and rule registry;
4. initial deterministic rules;
5. beneficiary normalization;
6. continuous duplicate candidate generation;
7. duplicate scoring and reviewer interface;
8. export QA tests;
9. QA test-agent workflow;
10. pilot fixes and performance tuning;
11. rollout configuration and operational documentation.

Visible UI changes require screenshots. No phase may introduce automatic merges
or activate blocking rules without explicit product approval.

## 10. Quality gates for every increment

Before an increment is proposed for review, the implementation agent will run,
as applicable:

- focused unit and integration tests;
- the relevant Django test suite;
- Django system checks;
- migration consistency checks;
- formatting or lint checks supported by the repository;
- authorization tests when data visibility changes;
- an inspected final diff and clean working tree after commit.

Test reports must distinguish an implementation failure from an environment
limitation. A pull request must state scope, exclusions, migrations, security
impact, tests, and remaining work.

## 11. Phase 0 completion and next action

The supplied product decisions, including complete identity and phone
visibility for authorized `DATA_QUALITY_REVIEWER` members, are recorded in this
document. Phase 0 is complete enough to begin the non-behavioral QA foundation.

**Phase 1: QA foundation is implemented.** It provides shared factories for the
initial MSCC domain, dedicated reviewer test setup, `unittest`, Django
`TestCase`, pytest-compatible tests, coverage execution, and documented test
commands. It does not change production validation, duplicate behavior, or
user-facing screens.

**Phase 2: quality core is implemented.** It adds versioned rule metadata,
monitor-only runs and findings, an append-only audit history, a deterministic
rule registry, reviewer permissions, and a service that creates, refreshes,
resolves, or reopens findings without changing the evaluated beneficiary.

The next implementation increment is **Phase 3: initial deterministic rules**.
It will implement the first approved MSCC `Child` and `Registration` rules and a
manual audit command on top of the quality core.
