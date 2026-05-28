# Foundry IQ Setup

Use one Azure AI Search index and one Foundry IQ knowledge base for the RDCCI Internal Fabric chatbot metadata.

Recommended names:

```text
AZURE_SEARCH_INDEX_NAME=rdcci-internal-chatbot-kb
AZURE_SEARCH_KNOWLEDGE_BASE_NAME=rdcci-internal-fabric-kb
```

The index stores metadata only. Do not index transactional rows or static KPI answers.

## Workbook Sheet Mapping

The workbook is treated as a metadata source for routing and terminology:

| Workbook sheet | Search document purpose |
| --- | --- |
| `Semantic Model` | Semantic model to table mapping |
| `Final-Columns with Lookup` | Dataflow Gen2 source table/column mapping |
| `Table Names` | Table names and business definitions across semantic models |
| `Tables & Attributes` | Source table attribute/column lists |
| `Final Data Tables` | Final curated table/column metadata |
| `Questions` | Approved sample questions and reference metadata |
| `Measures created in semantic models` | Measure names, date columns, and DAX formulas |
| `General Mapping for Chatbot` | Arabic/English business term to semantic model/measure mapping |

All documents include `doc_type`, `semantic_model`, `table_name`, and `column_name` where available. These fields let the backend and Foundry retrieve relevant context without splitting the project into multiple knowledge bases.

## Ingestion Flow

1. Extract metadata documents from the workbook into JSONL.
2. Create or update the Azure AI Search index with vector dimensions matching the embedding model.
3. Embed and upload JSONL documents to Azure AI Search.
4. Create one Foundry IQ knowledge base over the Search index.

With `text-embedding-3-large`, use:

```text
EMBEDDING_DIMENSIONS=3072
```

## Mac Workbook Path

On macOS, the easiest way to get the exact workbook path is:

1. Open Finder.
2. Locate the Excel workbook.
3. Right-click the workbook while holding `Option`.
4. Select `Copy "Final Data Tables for Subscription Model-V15.xlsx" as Pathname`.
5. Paste that path into the script command.

If the file is in Downloads, the path will usually look like:

```text
/Users/<your-user>/Downloads/Final Data Tables for Subscription Model-V15.xlsx
```

## Review Workbook Before Indexing

Run the inspection script first. It reads every sheet row-by-row, reports headers, sample rows, row counts, and whether each sheet should be indexed, skipped, or manually reviewed.

```bash
python scripts/inspect_workbook_for_indexing.py \
  --workbook "/absolute/path/to/Final Data Tables for Subscription Model-V15.xlsx" \
  --out docs/workbook_indexing_review.md
```

Review `docs/workbook_indexing_review.md` before uploading anything to Azure AI Search.

## Generate JSONL

After reviewing the workbook report, generate metadata JSONL:

```bash
python scripts/extract_kb_from_workbook.py \
  --workbook "/absolute/path/to/Final Data Tables for Subscription Model-V15.xlsx" \
  --out data/kb_docs/rdcci-internal_kb.jsonl
```

Then create the index and upload the documents:

```bash
python scripts/create_ai_search_index.py
python scripts/upload_kb_documents.py --file data/kb_docs/rdcci-internal_kb.jsonl
python scripts/create_foundry_iq_knowledge_base.py
```

# Foundry IQ Knowledge Base Setup

Use Foundry IQ as the chatbot's metadata knowledge base, not as the numeric answer source.

The index should contain:

- workbook table/column metadata
- semantic model names
- approved sample questions
- Arabic and English synonyms
- KPI/date-rule notes
- DAX-template hints

The index should not contain Lakehouse transaction rows.

## Build Steps

1. Fill `.env`.
2. Extract documents from the workbook.

```bash
python scripts/extract_kb_from_workbook.py \
  --workbook "/Users/mancunian_naz/Downloads/DDDM-DEV/Final Data Tables for Subscription Model-V15.xlsx" \
  --out data/kb_docs/rdcci-internal_kb.jsonl
```

3. Create the Azure AI Search index.

```bash
python scripts/create_ai_search_index.py
```

4. Upload vectorized metadata documents.

```bash
python scripts/upload_kb_documents.py --file data/kb_docs/rdcci-internal_kb.jsonl
```

5. Create or connect the Foundry IQ knowledge base.

```bash
python scripts/create_foundry_iq_knowledge_base.py
```

If the preview payload changes in your tenant, create the knowledge base in Microsoft Foundry portal:

- Open Microsoft Foundry.
- Enable the new Foundry experience.
- Go to Build > Knowledge.
- Connect the Azure AI Search service.
- Select the `rdcci-internal-chatbot-kb` index.
- Use semantic configuration `default`.
- Set output mode to extracted data if available.

## Agent Connection

In Foundry Agent Service, connect the agent to the Foundry IQ knowledge base and keep the backend function tool for actual semantic model execution.

Recommended agent instruction:

```text
You are an analytical assistant for RDCCI Internal Fabric semantic models.
Use the knowledge base only for metadata, terminology, routing, and citations.
Never invent numeric results.
For counts, comparisons, trends, or aggregations, call the backend semantic query tool.
Return Arabic answers for Arabic questions and English answers for English questions.
Always mention the semantic model used when returning numeric results.
```

## Microsoft Notes Verified

Microsoft describes Foundry IQ knowledge bases as Azure AI Search-backed objects that can be used from Foundry Agent Service or custom apps. Current docs also describe the Azure AI Search tool for Foundry agents as an index-grounding mechanism with citations, and note that private networking requires managed identity rather than key-based auth.
