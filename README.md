# DAB API Client (Terms)

A Python client to fetch terms from the DAB Terms API. This repository contains a minimal client for retrieving controlled vocabulary terms (e.g., instruments) from the Blue-Cloud/GeoDAB service using a token and view.

Package name: dab_api_client
Top-level module: DAB_TERMS_API


## Features
- Retrieve terms from the DAB Terms API with a single call
- Simple object model: Term and Terms containers
- Small dependency footprint (requests)


## Installation
The package is not published on PyPI yet. You can install it from source:

- Using pip and a local path
  - pip install .

- Or in editable/development mode
  - pip install -e .

Requirements:
- Python 3.7+
- requests

If using the provided test/example that performs semantic analysis, you will also need a separate dependency my_semantic_analyzer (not included in this repo).


## Quick start
Below is a minimal example illustrating how to fetch terms.

```python
from DAB_TERMS_API.DAB_API import TermsAPI

# Provided by the Blue-Cloud/GeoDAB environment
token = "blue-cloud-terms-maris-bv"
view = "blue-cloud-terms"

# What type of terms to fetch and how many
term_type = "instrument"
max_terms = 20

api = TermsAPI(token=token, view=view)
terms = api.get_terms(type=term_type, max=max_terms)

# Iterate the received terms
for term in terms.get_terms():
    print(term.get_value(), term.get_count())
```


## API Reference (light)
- class Term(count: int, value: str)
  - get_count() -> int
  - get_value() -> str

- class Terms()
  - get_terms() -> list[Term]

- class TermsAPI(token: str, view: str)
  - get_terms(type: str, max: int) -> Terms
    - Calls: https://gs-service-preproduction.geodab.eu/gs-service/services/essi/token/{token}/view/{view}/terms-api/terms?type={type}&max={max}

Notes:
- The API currently prints some debug information (counts and sample outputs) to stdout.
- The Terms container simply stores the raw list of Term objects in the attribute terms and exposes it via get_terms().


## Example with semantic analyzer (optional)
The included test.py shows how to integrate the fetched terms with an external semantic analyzer library. That library is not part of this package; install and configure it separately if you intend to use that workflow.

```python
from DAB_TERMS_API.DAB_API import TermsAPI
from my_semantic_analyzer.semantic_analyzer import *

api = TermsAPI(token="blue-cloud-terms-maris-bv", view="blue-cloud-terms")
terms = api.get_terms(type="instrument", max=20)

analyzer = SemanticAnalyzer()
terms_to_analyze = [t.get_value().replace('(', '').replace(')', '') for t in terms.get_terms()]

match_types = [Matchtype("exactMatch")]
match_properties = [MatchProperty("altLabel"), MatchProperty("prefLabel")]

results = analyzer.analyzeTerms(terms_to_analyze, match_types, match_properties)
print("Matches:", len(results.get_matches()))
```


## Development
- Code lives in DAB_TERMS_API/DAB_API.PY
- Packaging metadata is defined in setup.py (project name: dab_api_client)
- Long description is sourced from this README.md

To run the example/test (after installing deps):
- python test.py


## License
license="GPL-3.0".


## Project Links
- Source: https://github.com/ESSI-Lab/Blue-Cloud-Hackathon-2025/tree/main


## Helper scripts to create a virtual environment
If you prefer an automated setup, this repo includes simple helpers:
- Windows (PowerShell):
  - ./create_venv.ps1
- macOS/Linux (bash):
  - ./create_venv.sh

Both scripts will create .venv, upgrade pip, and (if present) install dependencies from requirments.txt.
