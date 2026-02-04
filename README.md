# Doc Publication Match

## Resources
- Providers data: https://download.cms.gov/nppes/NPI_Files.html
- Semantic Scholar: https://www.semanticscholar.org/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Taxonomy Code: https://taxonomy.nucc.org/
- Taxonomy Code CSV: https://www.nucc.org/index.php/code-sets-mainmenu-41/provider-taxonomy-mainmenu-40/csv-mainmenu-57

## Overview
This project processes large-scale provider data to match doctors with their research publications. The primary dataset is the NPI file provided by CMS, which contains comprehensive provider information.

## Logic and Workflow
The application follows a two-stage logic executed via `main.py`.

### 1. Data Preparation (First Run)
* **Start-up Check**: The script first checks if `results.csv` exists in the local directory. If missing, it initiates the processing logic.
* **Data Ingestion**: It reads the raw NPI data file (`npidata_pfile_*.csv`). 
    * *Note*: For testing and performance, the script is currently configured to process only a chunk of the raw data (first 20 rows).
* **Filtering**: The data is filtered to isolate individual providers (Entity Type Code = `1`), removing organizational records.
* **Taxonomy Enrichment**: 
    * The script uses the `nucc_taxonomy_251.csv` file to enrich the raw data.
    * It maps the specific **Taxonomy Codes** to their descriptive values: **Grouping**, **Classification**, **Specialization**, and **Display Name**.
    * This step transforms abstract codes into human-readable provider details.
* **Middleware Creation**: The processed and enriched data for the first 10 identified doctors is saved to `results.csv`. This file serves as the clean input for the next stage.
* **Completion**: The script terminates and requests a re-run.

### 2. Publication Matching (Second Run)
* **Start-up Check**: When `main.py` is run again, it detects the existing `results.csv` file.
* **Execution**: It loads the `results.csv` middleware file.
* **Search Strategy**: For each doctor in the list, it constructs a search query using the **Last Name** and **First Initial**.
* **External Querying**: The script queries the **PubMed API** to find relevant article IDs.
* **Validation & Matching**:
    * It fetches the details of potential articles.
    * A fuzzy matching algorithm (`rapidfuzz`) compares the author's name in the paper with the doctor's name.
    * It also checks for location matches (City) to increase confidence.
* **Results**: The final matching count for each doctor is output as a JSON list.

## Setup Instructions

### 1. Create Virtual Environment
Create a virtual environment to isolate dependencies:
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
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Configuration
Ensure that the file paths defined in `main.py` (e.g., for the NPI data and Taxonomy CSV) match the actual file locations on your system.

## Usage
Because the process is split into two logical steps, you must run the main script twice.

**Step 1: Generate Middleware Data**
Run the script to clean and enrich the raw NPI data.
```bash
python main.py
```
*Output: Generates `results.csv` and prompts to run again.*

**Step 2: Match Publications**
Run the script again to perform the publication search and matching.
```bash
python main.py
```
*Output: Displays the JSON results of matched publications.*