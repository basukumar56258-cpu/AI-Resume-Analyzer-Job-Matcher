# AI Resume Analyzer & Job Matcher

A local Streamlit application for reviewing a resume against a job description. It extracts supported skills, calculates a keyword-based match score, highlights gaps, and suggests practical resume improvements.

## Features

- Upload resumes in PDF or DOCX format
- Extract resume text and detect skills from the built-in skill list
- Compare detected resume skills with a pasted job description
- Show ATS-style keyword alignment, matched skills, and missing skills
- Generate rule-based recommendations and answer common match questions
- Review results in a responsive dashboard

## How Matching Works

The score is based on the supported skills detected in the job description:

```text
matched job skills / detected job skills * 100
```

This is a lightweight keyword comparison, not a prediction from a commercial ATS. The built-in skill list is intentionally limited and can be extended in `services/skill_extractor.py`.

The resume assistant uses local matching results and simple rules. No LLM provider or API key is required, and the app does not send resume content to an external AI service.

## Requirements

- Python 3.10 or newer
- pip

## Setup and Run

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

The app opens in your browser at the local Streamlit address. You can also start it directly with:

```bash
python -m streamlit run app/main.py
```

## Use the Analyzer

1. Upload a PDF or DOCX resume from the sidebar.
2. Paste the target job description into the dashboard.
3. Select **Match with Job** to calculate the score and refresh the analysis panels.
4. Review matched skills, missing skills, recommendations, and the local resume assistant.

## Run Tests

```bash
python -m pytest -q
```

## Project Structure

```text
AI-Resume-Analyzer-Job-Matcher/
├── app/
│   └── main.py                 # Streamlit dashboard and interactions
├── core/
│   ├── embeddings.py           # Embedding integration point
│   ├── llm.py                  # Optional LLM prompt integration point
│   └── prompts.py              # Prompt templates
├── data/
│   ├── job_descriptions/       # Sample job descriptions
│   └── skills.json             # Skill data
├── database/                   # Database integration point
├── parsers/
│   ├── pdf_parser.py           # PDF text extraction
│   ├── docx_parser.py          # DOCX text extraction
│   └── text_cleaner.py         # Text cleanup helpers
├── services/
│   ├── ats_scorer.py           # Match score calculation
│   ├── matcher.py              # Resume/job skill comparison
│   ├── recommendation.py       # Rule-based recommendations
│   └── skill_extractor.py      # Built-in skill detection
├── tests/                      # Pytest tests
├── utils/                      # Shared helpers and validators
├── requirements.txt
└── run.py                      # Application entry point
```

## Privacy and Limitations

- Resume analysis runs in the local Streamlit app; this project does not persist uploaded resumes to its database layer.
- Text-based PDFs are supported. Scanned/image-only PDFs may need OCR before their text can be analyzed.
- DOCX extraction currently reads paragraph text; complex tables and layout may not be fully represented.
- Skill extraction only recognizes entries in the built-in list, so it may miss equivalent terms or unlisted technologies.
- The ATS-style score is a keyword overlap estimate and does not guarantee a result from any third-party applicant tracking system.

## License

See [LICENSE](LICENSE).
