# Doc Publication Match

## Resources
- Providers data: https://download.cms.gov/nppes/NPI_Files.html
- Semantic Scholar: https://www.semanticscholar.org/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Taxonomy Code: https://taxonomy.nucc.org/
- Taxonomy Code CSV: https://www.nucc.org/index.php/code-sets-mainmenu-41/provider-taxonomy-mainmenu-40/csv-mainmenu-57

## Overview
This project contains a large dataset and is designed to process provider data for publication matching.

### Data Workflow
1. **Input Data**: The primary raw data source is `npidata_pfile_...csv` (Provider Data).
2. **Execution**: The `main.py` script is the entry point for the application.
3. **Middleware Generation**: The script processes the raw data to create `results.csv`.
4. **Publication Matching**: The `results.csv` file is subsequently processed to match doctors with their publications.

## Setup Instructions

### 1. Create Virtual Environment
Create a virtual environment to manage dependencies:
```bash
python -m venv env
```

### 2. Activate Virtual Environment

**Windows:**
```powershell
.\env\Scripts\activate
```

**Ubuntu/Linux:**
```bash
source env/bin/activate
```

### 3. Install Dependencies
Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Usage
To run the project and process the data:
```bash
python main.py
```