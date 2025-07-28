import weaviate
import os
from openai import OpenAI
from weaviate.classes.config import Configure


class WeaviateClient:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.openai_client = OpenAI()
        print("=" * 50)
        print(f"Weaviate client status: {self.client.is_ready()}")
        print("=" * 50)

    def close(self):
        if hasattr(self.client, "close"):
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_schema(self, class_name="BangladeshPOI"):
        """Create collection schema using Weaviate v4 API"""
        try:
            # Check if collection already exists
            if self.client.collections.exists(class_name):
                print(
                    f"Collection {class_name} already exists. Deleting and recreating..."
                )
                self.client.collections.delete(class_name)

            # Create collection with properties
            collection = self.client.collections.create(
                name=class_name,
                properties=[
                    weaviate.classes.config.Property(
                        name="content", data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="poi_name", data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="location", data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="category", data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="description",
                        data_type=weaviate.classes.config.DataType.TEXT,
                    ),
                    weaviate.classes.config.Property(
                        name="coordinates",
                        data_type=weaviate.classes.config.DataType.TEXT,
                    ),
                    weaviate.classes.config.Property(
                        name="full_data",
                        data_type=weaviate.classes.config.DataType.OBJECT,
                        nested_properties=[
                            weaviate.classes.config.Property(
                                name="example_nested_prop",
                                data_type=weaviate.classes.config.DataType.TEXT,
                            )
                        ],
                    ),
                ],
            )
            print(f"Created collection: {class_name}")
            return collection

        except Exception as e:
            print(f"Error creating schema: {e}")
            return None

    def search_similar(self, query_vector, class_name="BangladeshPOI", limit=5):
        """Search for similar POIs using vector similarity"""
        try:
            collection = self.client.collections.get(class_name)

            response = collection.query.near_vector(
                near_vector=query_vector, limit=limit, return_metadata=["distance"]
            )

            results = []
            for obj in response.objects:
                result = {
                    "content": obj.properties.get("content", ""),
                    "poi_name": obj.properties.get("poi_name", ""),
                    "location": obj.properties.get("location", ""),
                    "category": obj.properties.get("category", ""),
                    "description": obj.properties.get("description", ""),
                    "coordinates": obj.properties.get("coordinates", ""),
                    "full_data": obj.properties.get("full_data", {}),
                    "_additional": {
                        "distance": obj.metadata.distance if obj.metadata else None
                    },
                }
                results.append(result)

            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_object_count(self, class_name="BangladeshPOI"):
        """Get total number of stored objects"""
        try:
            collection = self.client.collections.get(class_name)
            response = collection.aggregate.over_all(total_count=True)
            return response.total_count
        except Exception as e:
            print(f"Count error: {e}")
            return 0

    def list_collections(self):
        """List all collections in Weaviate"""
        try:
            collections = self.client.collections.list_all()
            print("=" * 50)
            for collection_name in collections:  # Directly iterate through names
                print(f"- {collection_name}")
            print("=" * 50)
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
