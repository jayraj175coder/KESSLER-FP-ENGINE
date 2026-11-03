# KESSLER FP ENGINE — AI Usage & Engineering Transparency Disclosure

> **Candidate:** Jayraj Sanas  
> **Position:** Software Engineer Intern (Data & Development)  
> **Company:** DeepLogic AI

---

## 1. Disclosure Statement

In accordance with modern software engineering best practices and DeepLogic AI's assessment guidelines, this document provides an honest, transparent breakdown of how generative AI was utilized during the development of the **KESSLER FP ENGINE**.

---

## 2. Tools & Models Used

- **AI Assistant**: Claude 3.7 Sonnet / Antigravity Agent
- **Local Tooling**: Python 3.11, PyMuPDF, jsonschema, pytest
- **Development Mode**: Interactive pair programming, coordinate inspection, and automated test-driven development (TDD).

---

## 3. Division of Responsibility

| Task Domain | Human Engineering Responsibility | AI Assistance Responsibility |
|---|---|---|
| **Architectural Design** | Defined the Strategy pattern for layout fingerprinting (`detector.py`), separation of concern across `core/`, `parsers/`, and `validation/`. | Assisted in drafting initial Python dataclass scaffolding. |
| **PDF Inspection & Coordinate Analysis** | Formulated the mathematical bucketing strategy ($x$ coordinate thresholding and $y$ clustering). | Analyzed raw PyMuPDF word coordinate dumps across PDFs to propose initial coordinate intervals. |
| **Edge Case Diagnosis** | Discovered the column boundary issue on amounts $\ge$ 1,000 EUR in INV-04 (`COL_RAB_MAX` tuning) and identified the printer transposition error on Pos 7. | Automated unit tests to confirm boundary corrections. |
| **Financial Validation (V1–V7)** | Conceptualized the 7-step reconciliation audit trail mirroring ERP accounts payable reconciliation pipelines. | Implemented test fixtures and Markdown table report formatting in `report_generator.py`. |
| **Code Verification** | Audited every generated regex, checked schema field requirements, and ensured 100% test pass rate. | Executed test runs and highlighted diffs against `INV-01_expected_output.json`. |

---

## 4. Key Takeaways & Human Learnings

1. **AI is an Accelerator, Not a Substitute for Ground Truth**:
   When initial regex parsers were run, they easily confused the `Rab. %` and `Gesamt €` columns when amounts exceeded 1,000 EUR. Only careful inspection of actual word bounding boxes resolved the bug.
2. **Deterministic Document Intelligence vs LLM Hallucinations**:
   Financial documents require 100% precision. Using an LLM to "read" PDF text and generate JSON directly produces subtle hallucinations on numbers and dates. Using deterministic Python parsers with PyMuPDF ensures that every number in the output matches the document text byte-for-byte.
3. **Understanding Every Line**:
   Every function, regular expression, and data structure in this repository was vetted and understood so that it can be explained clearly during technical interviews.
