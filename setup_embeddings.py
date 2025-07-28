import json
import os
from dotenv import load_dotenv
from app.vector_store.weaviate_client import WeaviateClient
from app.services.embedding_service import EmbeddingService


def setup_vector_store():
    """Setup and populate vector store with POI data"""

    # Load environment variables
    load_dotenv()

    print("Setting up vector store...")

    with WeaviateClient() as weaviate_client:
        embedding_service = EmbeddingService()

        # Create schema
        print("Creating Weaviate collection...")
        collection = weaviate_client.create_schema("BangladeshPOI")

        if collection is None:
            print("Failed to create collection. Exiting...")
            return 0

        # Load POI data
        print("Loading POI data...")
        poi_data_path = "data/points_of_interest_bangladesh.json"

        if not os.path.exists(poi_data_path):
            print(f"POI data file not found: {poi_data_path}")
            print("Please ensure the file exists and try again.")
            return 0

        try:
            with open(poi_data_path, "r", encoding="utf-8") as f:
                poi_data = json.load(f)
        except Exception as e:
            print(f"Error loading POI data: {e}")
            return 0

        print(f"Found {len(poi_data)} POIs to process")

        # Store POI data with embeddings
        print("Generating embeddings and storing in Weaviate...")
        stored_count = embedding_service.store_poi_data(weaviate_client, poi_data)

        # Verify storage
        total_objects = weaviate_client.get_object_count()
        print("\nSetup complete!")
        print(f"Total objects in Weaviate: {total_objects}")
        print(f"Successfully stored: {stored_count} POIs")

        weaviate_client.list_collections()

        return stored_count


if __name__ == "__main__":
    print("=" * 50)
    result = setup_vector_store()

    if result > 0:
        print("✅ Vector store setup completed successfully!")
    else:
        print("❌ Vector store setup failed!")
