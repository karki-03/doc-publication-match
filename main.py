import requests
import pandas as pd
from rapidfuzz import fuzz
import xml.etree.ElementTree as ET




def enrich_taxonomy_data(df, taxonomy_path):
    """
    Enriches the dataframe with taxonomy details (Grouping, Classification, Specialization, Display Name)
    for each of the 3 taxonomy codes.
    """
    try:
        # Load the taxonomy reference data
        taxonomy_df = pd.read_csv(taxonomy_path, usecols=['Code', 'Grouping', 'Classification', 'Specialization', 'Display Name'])
        
        # Dictionary to map suffixes to the taxonomy code columns in the main df
        taxonomy_columns = {
            '_1': 'Healthcare Provider Taxonomy Code_1',
            '_2': 'Healthcare Provider Taxonomy Code_2',
            '_3': 'Healthcare Provider Taxonomy Code_3'
        }
        
        for suffix, tax_col in taxonomy_columns.items():
            if tax_col in df.columns:
                # Prepare a temporary taxonomy dataframe for merging
                temp_tax = taxonomy_df.copy()
                # Rename columns to match the current iteration
                rename_map = {
                    'Code': tax_col,
                    'Grouping': f'Grouping{suffix}',
                    'Classification': f'Classification{suffix}',
                    'Specialization': f'Specialization{suffix}',
                    'Display Name': f'Display Name{suffix}'
                }
                temp_tax.rename(columns=rename_map, inplace=True)
                
                # Merge with the main dataframe
                df = df.merge(temp_tax, on=tax_col, how='left')
                
        return df
    except Exception as e:
        print(f"Error in enriching taxonomy data: {e}")
        return df

def clean_npi_data_and_enrich_taxonomy(npi_data_file_path, taxonomy_file_path):
    
    # Define the columns we want to extract
    # User requested: npi , provider first name, middle name and last name, prefix text, credential text, 
    # address (using Practice Location Address), healthcare provider taxonomy code 1
    required_columns = [
        "NPI",
        "Entity Type Code",  # Needed for filtering
        # Provider Name
        "Provider Last Name (Legal Name)",
        "Provider First Name",
        "Provider Middle Name",
        "Provider Name Prefix Text",
        "Provider Credential Text",
        # Provider Other Name
        "Provider Other Last Name",
        "Provider Other First Name",
        "Provider Other Middle Name",
        "Provider Other Name Prefix Text",
        "Provider Other Credential Text",
        # Mailing Address
        "Provider First Line Business Mailing Address",
        "Provider Business Mailing Address City Name",
        # Practice Location Address
        "Provider First Line Business Practice Location Address",
        "Provider Second Line Business Practice Location Address",
        "Provider Business Practice Location Address City Name",
        # Provider Information
        "Provider Sex Code",
        # Authorized Official
        "Authorized Official Last Name",
        "Authorized Official First Name",
        "Authorized Official Middle Name",
        "Authorized Official Title or Position",
        # Taxonomy 1
        "Healthcare Provider Taxonomy Code_1",
        "Provider License Number_1",
        "Provider License Number State Code_1",
        "Healthcare Provider Primary Taxonomy Switch_1",
        # Taxonomy 2
        "Healthcare Provider Taxonomy Code_2",
        "Provider License Number_2",
        "Provider License Number State Code_2",
        "Healthcare Provider Primary Taxonomy Switch_2",
        # Taxonomy 3
        "Healthcare Provider Taxonomy Code_3",
        "Provider License Number_3",
        "Provider License Number State Code_3",
        "Healthcare Provider Primary Taxonomy Switch_3"
    ]

    try:
        # Read only the first 20 rows as requested
        df = pd.read_csv(file_path, usecols=required_columns, nrows=20)

        # Filter for doctors (Entity Type Code = 1, which represents Individual providers, not organizations)
        # The user specified "no organization" (skip if Entity Type Code is 2)
        doctors_df = df[df['Entity Type Code'] == 1].copy()

        # Enrich with taxonomy details
        doctors_df = enrich_taxonomy_data(doctors_df, taxonomy_file_path)

        # Select the specific columns to display
        display_columns = [
            "NPI",
            "Provider First Name",
            "Provider Middle Name",
            "Provider Last Name (Legal Name)",
            "Provider Name Prefix Text",
            "Provider Credential Text",
            "Provider Other First Name",
            "Provider Other Middle Name",
            "Provider Other Last Name",
            "Provider Other Name Prefix Text",
            "Provider Other Credential Text",
            "Provider First Line Business Mailing Address",
            "Provider Business Mailing Address City Name",
            "Provider First Line Business Practice Location Address",
            "Provider Second Line Business Practice Location Address",
            "Provider Business Practice Location Address City Name",
            "Provider Sex Code",
            "Authorized Official First Name",
            "Authorized Official Middle Name",
            "Authorized Official Last Name",
            "Authorized Official Title or Position",
            "Healthcare Provider Taxonomy Code_1",
            "Provider License Number_1",
            "Provider License Number State Code_1",
            "Healthcare Provider Primary Taxonomy Switch_1",
            "Healthcare Provider Taxonomy Code_2",
            "Provider License Number_2",
            "Provider License Number State Code_2",
            "Healthcare Provider Primary Taxonomy Switch_2",
            "Healthcare Provider Taxonomy Code_3",
            "Provider License Number_3",
            "Provider License Number State Code_3",
            "Healthcare Provider Primary Taxonomy Switch_3",
            "Grouping_1",
            "Classification_1",
            "Specialization_1",
            "Display Name_1",
            "Grouping_2",
            "Classification_2",
            "Specialization_2",
            "Display Name_2",
            "Grouping_3",
            "Classification_3",
            "Specialization_3",
            "Display Name_3"
        ]
        
        result = doctors_df[display_columns]

        # Limit to 10 doctors (though with nrows=20, it's unlikely to exceed 10, but good practice)
        final_result = result.head(10)

        # Print the result
        # print(final_result.to_string(index=False))
        #store results in new csv file
        final_result.to_csv('d:\\Personal\\DNexus\\doc_pub_matching\\results.csv', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")

def search_pubmed(name_query):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": name_query,
        "retmode": "json",
        "retmax": 200
    }
    r = requests.get(url, params=params)

    # save text as file
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(str(r.json()))

    print("File saved ✅")
    return r.json()["esearchresult"]["idlist"]

def fetch_pubmed_details(pmids):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    r = requests.get(url, params=params)
    return r.text

def match_author(pubmed_xml, doctor):
    root = ET.fromstring(pubmed_xml)

    matched_papers = []

    for article in root.findall(".//PubmedArticle"):
        authors = article.findall(".//Author")
        affiliations = article.findall(".//Affiliation")

        aff_text = " ".join([a.text for a in affiliations if a.text])

        for a in authors:
            last = a.findtext("LastName", "").lower()
            first = a.findtext("ForeName", "").lower()

            name_score = fuzz.partial_ratio(doctor["last"].lower(), last)

            if doctor["city"] and doctor["city"].lower() in aff_text.lower():
                name_score += 20

            if name_score > 70:
                matched_papers.append(article)

    return matched_papers

def find_doctor_publications_no_key(doctor_record):
    first = doctor_record["Provider First Name"]
    last = doctor_record["Provider Last Name (Legal Name)"]
    city = doctor_record["Provider Business Practice Location Address City Name"]

    doctor = {"first": first, "last": last, "city": city}

    # Build PubMed search query
    query = f"{last} {first[0]}[Author]"

    pmids = search_pubmed(query)
    if not pmids:
        return {
            "doctor": f"{first} {last}",
            "matched_publications": 0
        }


    xml_data = fetch_pubmed_details(pmids)
    matched = match_author(xml_data, doctor)

    return {
        "doctor": f"{first} {last}",
        "matched_publications": len(matched)
    }

if __name__ == "__main__":
    # Define the file path
    # check if  results.csv file exists in this directory
    import os

    file_name = "results.csv"
    is_npi_data_cleaned = False
    if os.path.isfile(file_name):
        print("results.csv exists in current directory ✅")
        is_npi_data_cleaned = True

    else:
        print("results.csv NOT found ❌")
        print("Starting to process the original NPI file")

    

    if is_npi_data_cleaned is False:
        file_path = 'd:\\Personal\\DNexus\\doc_pub_matching\\npidata_pfile_20260105-20260111.csv'
        taxonomy_file_path = 'd:\\Personal\\DNexus\\doc_pub_matching\\nucc_taxonomy_251.csv'

        clean_npi_data_and_enrich_taxonomy(npi_data_file_path=file_path, taxonomy_file_path=taxonomy_file_path)
        # the output is a file saved as results.csv
        # we only process this file once and use it for further process
        print("Processing is complete. Run `python main.py` again")
    else:
        # read output csv and loop over the doctors data

        results_csv_path = 'd:\\Personal\\DNexus\\doc_pub_matching\\results.csv'

        # Read only the first 20 rows as requested
        import json
        # Read the results CSV
        results_df = pd.read_csv(results_csv_path)
        
        publication_results = []

        # Loop over the dataframe rows
        for index, row in results_df.iterrows():
            print(f"Finding data for {str(row["Provider First Name"]) if pd.notna(row["Provider First Name"]) else ""} {str(row["Provider Last Name (Legal Name)"]) if pd.notna(row["Provider Last Name (Legal Name)"]) else ""}  - {str(row["Display Name_1"]) if pd.notna(row["Display Name_1"]) else ""}")
            doctor_record = {
                "Provider First Name": str(row["Provider First Name"]) if pd.notna(row["Provider First Name"]) else "",
                "Provider Last Name (Legal Name)": str(row["Provider Last Name (Legal Name)"]) if pd.notna(row["Provider Last Name (Legal Name)"]) else "",
                "Provider Business Practice Location Address City Name": str(row["Provider Business Practice Location Address City Name"]) if pd.notna(row["Provider Business Practice Location Address City Name"]) else ""
            }
            
            # Find publications
            result = find_doctor_publications_no_key(doctor_record)
            
            # Add NPI for reference
            if "NPI" in row:
                result['NPI'] = row['NPI']
            
            publication_results.append(result)
            
        print(json.dumps(publication_results, indent=4))