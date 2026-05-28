import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    endpoint = required("AZURE_SEARCH_ENDPOINT")
    api_key = required("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "rdcci-internal-chatbot-kb")
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String, retrievable=True),
            SearchableField(name="content", type=SearchFieldDataType.String, retrievable=True),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, retrievable=True),
            SimpleField(name="doc_type", type=SearchFieldDataType.String, filterable=True, facetable=True, retrievable=True),
            SimpleField(name="semantic_model", type=SearchFieldDataType.String, filterable=True, facetable=True, retrievable=True),
            SearchableField(name="table_name", type=SearchFieldDataType.String, filterable=True, retrievable=True),
            SearchableField(name="column_name", type=SearchFieldDataType.String, filterable=True, retrievable=True),
            SimpleField(name="language", type=SearchFieldDataType.String, filterable=True, retrievable=True),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=dimensions,
                vector_search_profile_name="default-vector-profile",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
            profiles=[
                VectorSearchProfile(
                    name="default-vector-profile",
                    algorithm_configuration_name="default-hnsw",
                )
            ],
        ),
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[
                            SemanticField(field_name="semantic_model"),
                            SemanticField(field_name="table_name"),
                            SemanticField(field_name="column_name"),
                        ],
                    ),
                )
            ]
        ),
    )

    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
    client.create_or_update_index(index)
    print(f"Created or updated Azure AI Search index: {index_name}")


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


if __name__ == "__main__":
    main()

