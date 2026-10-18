#  ScopeGuard AI

**Protect your scope. Keep your cool.**

ScopeGuard AI is a freelancer-focused tool that compares a client's new request with the original project agreement. It helps freelancers identify potentially out-of-scope work, find relevant agreement wording, prepare clarifying questions, and draft professional responses.

The application uses a local large language model through Ollama, alongside rule-based checks and evidence verification.

> **Disclaimer:** ScopeGuard AI provides business decision support, not legal advice. Its classifications are suggestions, not definitive legal or contractual determinations.

##  Features

- ** PDF agreement upload:** Extract text from text-based PDF agreements.
- ** Text input:** Paste an agreement directly into the application.
- ** Scope classification:** Categorize requests as:
  - `INCLUDED` — available evidence suggests the work is included.
  - `POTENTIALLY ADDITIONAL` — wording suggests the work may be excluded or require a scope change.
  - `UNCLEAR` — the available evidence is insufficient to make a confident assessment.
- ** Evidence verification:** Check whether a quoted sentence appears in the original agreement before presenting it as verified evidence.
- ** Clarifying questions:** Generate questions to resolve ambiguity with a client.
- ** Professional replies:** Prepare polite responses for discussing scope changes.
- ** Local AI inference:** Use Ollama with Gemma 3 1B for AI analysis.
- ** Neo-Brutalism interface:** A bold, accessible Streamlit interface.

##  How It Works

1. Upload a PDF agreement or paste its text.
2. Enter the client's new request.
3. ScopeGuard extracts the agreement text and searches for relevant passages.
4. Rule-based checks look for explicit inclusion or exclusion language.
5. If the rules find no clear match, the application asks the configured Ollama model to analyze the request.
6. The application checks whether the model's proposed evidence quotation can be verified against the agreement.
7. The result includes a classification, explanation, available evidence, clarifying questions, and a suggested client reply.

### Classification Flow

```text
Agreement + Client Request
            |
            v
    Extract Agreement Text
            |
            v
    Rule-Based Scope Checks
            |
       +----+----+
       |         |
  Clear match   No clear match
       |         |
       |         v
       |    Local Ollama Model
       |         |
       +----+----+
            |
            v
    Verify Evidence Quote
            |
            v
 Classification + Questions
       + Suggested Reply
```

**Important:** A matching sentence or verified quotation does not by itself establish the full contractual meaning. Context, exceptions, amendments, and other clauses may change the interpretation.

##  Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| Ollama | Local model inference |
| Gemma 3 1B | Language model for scope analysis |
| PyMuPDF | PDF text extraction |
| Requests | Communication with the local Ollama API |
| `unittest` | Automated tests |

##  Project Structure

```text
scopeguard-ai/
├── app.py
├── scopeguard.py
├── test_scopeguard.py
├── requirements.txt
├── README.md
└── .gitignore
```

- `app.py` — Streamlit UI, PDF handling, analysis pipeline, and results.
- `scopeguard.py` — Shared scope-matching and evidence-verification utilities.
- `test_scopeguard.py` — Unit tests for the shared utility functions.
- `requirements.txt` — Python dependencies.
- `.gitignore` — Files and directories that should not be committed.

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python 3.11 or another version compatible with your dependencies.
- Git.
- Ollama.
- The Gemma 3 1B model.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/scopeguard-ai.git
cd scopeguard-ai
```

Replace `YOUR-USERNAME` with your GitHub username and adjust the repository name if necessary.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can invoke the environment's Python executable directly instead.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Your `requirements.txt` should contain:

```text
streamlit
requests
PyMuPDF
```

### 4. Install and start Ollama

Install Ollama using its official download page:

https://ollama.com/download

Download the model:

```powershell
ollama pull gemma3:1b
```

Start Ollama if it is not already running, then verify the model is available:

```powershell
ollama list
```

The application currently expects the Ollama API at:

```text
http://localhost:11434/api/generate
```

If the `ollama` command is not recognized in PowerShell, verify the installation and PATH configuration.

### 5. Run the application

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually:

```text
http://localhost:8501
```

## 🧪 Running Tests

Run the unit tests from the project directory:

```powershell
python -m unittest -v test_scopeguard
```

The tests cover basic scope matching and evidence verification.

Additional integration tests should verify PDF extraction, all three classifications, malformed model responses, and behavior when Ollama is unavailable.

##  Example

**Agreement**

> The project includes a five-page website. Payment gateway integration is not included in this project.

**Client request**

> Please add payment gateway integration.

**Expected assessment**

- Classification: `POTENTIALLY ADDITIONAL`
- Evidence: The sentence explicitly excluding payment gateway integration.
- Suggested next step: Clarify requirements and agree on any scope, cost, and timeline changes before proceeding.

This example illustrates the intended behavior. Actual results depend on the agreement text and application implementation.

##  Privacy and Security

- In local mode, agreement text is sent to the configured local Ollama API for model analysis.
- PDF contents and client requests may contain confidential business information. Use documents you are authorized to process.
- Avoid logging or committing private agreements, API credentials, or client data.
- Evidence verification checks textual correspondence; it does not prove that an interpretation is legally correct.
- A hosted deployment may send data to a remote model service depending on its architecture. Review the hosting and model provider's privacy practices before using confidential agreements.

##  Deployment

The current configuration uses a local Ollama endpoint. It works when the application and Ollama are accessible in the same environment.

**Deploying the Streamlit application to Render alone is not sufficient.** The hosted app cannot normally access Ollama running on your personal computer through `localhost`.

Before deploying, choose one of these approaches:

1. Run the application and Ollama together in a suitably configured hosted environment.
2. Configure a securely hosted inference endpoint and update the application to use it.
3. Keep the application local for a local-first demonstration.

Do not expose the Ollama API publicly without appropriate access controls. For a hosted deployment, configure endpoint details and credentials through environment variables or a secure secrets mechanism rather than committing them to Git.

##  Future Improvements

- More robust semantic matching between requests and deliverables.
- Better handling of exceptions, amendments, and contradictory clauses.
- OCR support for scanned PDFs.
- Additional regression and end-to-end tests.
- Improved evidence highlighting with agreement page references.
- Exportable analysis reports.
- Copy-to-clipboard functionality.
- Secure hosted inference and deployment.
- User feedback to improve the quality of scope assessments.

##  Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Run the automated tests.
5. Open a pull request explaining the change and how it was tested.

Please avoid committing confidential agreements, generated secrets, or local environment files.

##  License

Choose a license before publishing the repository. For example, the MIT License permits broad reuse with attribution. Add a `LICENSE` file containing the license terms you select.

---

**ScopeGuard AI — clearer scope conversations, better-informed decisions.**
