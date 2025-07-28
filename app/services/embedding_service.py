from openai import OpenAI
import json
import re


class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
        self.model = "text-embedding-3-small"

    def get_embedding(self, text):
        try:
            text = str(text).strip()
            if not text:
                return None
            response = self.client.embeddings.create(input=text, model=self.model)
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return None

    def prepare_poi_content(self, poi):
        """Create searchable content from POI data"""
        content_parts = []

        # Add name
        if poi.get("name"):
            content_parts.append(poi["name"])

        # Add description
        if poi.get("description"):
            content_parts.append(poi["description"])

        # Add category/type
        if poi.get("category"):
            content_parts.append(f"Category: {poi['category']}")
        if poi.get("type"):
            content_parts.append(f"Type: {poi['type']}")

        # Add location info
        if poi.get("location"):
            content_parts.append(f"Location: {poi['location']}")
        if poi.get("district"):
            content_parts.append(f"District: {poi['district']}")
        if poi.get("division"):
            content_parts.append(f"Division: {poi['division']}")

        return " | ".join(content_parts)

    def store_poi_data(self, weaviate_client, poi_data):
        """Store POI data with embeddings in Weaviate using v4 API"""
        successful_stores = 0
        collection = weaviate_client.client.collections.get("BangladeshPOI")

        # Prepare batch data
        batch_data = []

        for i, poi in enumerate(poi_data):
            try:
                content = self.prepare_poi_content(poi)
                if not content:
                    print(f"No content for POI {i}: {poi}")
                    continue

                embedding = self.get_embedding(content)
                if embedding is None:
                    print(f"No embedding for POI {i}: {poi}")
                    continue

                coordinates = ""
                if poi.get("latitude") and poi.get("longitude"):
                    coordinates = f"{poi['latitude']}, {poi['longitude']}"

                # Prepare data object for batch insertion
                data_object = {
                    "content": content,
                    "poi_name": poi.get("name", ""),
                    "location": poi.get("location", ""),
                    "category": poi.get("category", poi.get("type", "")),
                    "description": poi.get("description", ""),
                    "coordinates": coordinates,
                    "full_data": poi,
                }

                batch_data.append({"properties": data_object, "vector": embedding})

                # Process in batches of 100
                if len(batch_data) >= 100:
                    self._insert_batch(collection, batch_data)
                    successful_stores += len(batch_data)
                    batch_data = []
                    print(f"Processed {successful_stores}/{len(poi_data)} POIs...")

            except Exception as e:
                print(f"Error preparing POI {i}|{poi}: {e}")
                continue

        # Insert remaining batch data
        if batch_data:
            self._insert_batch(collection, batch_data)
            successful_stores += len(batch_data)

        print(f"Successfully stored {successful_stores}/{len(poi_data)} POIs")
        return successful_stores

    def _insert_batch(self, collection, batch_data):
        """Insert a batch of data into Weaviate"""
        try:
            with collection.batch.dynamic() as batch:
                for item in batch_data:
                    batch.add_object(
                        properties=item["properties"], vector=item["vector"]
                    )
        except Exception as e:
            print(f"Batch insert error: {e}")
