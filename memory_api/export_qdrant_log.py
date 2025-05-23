import argparse
import json
from qdrant_client import QdrantClient

def export_memories(output_file, host='localhost', port=6333, collection_name='memory'):
    client = QdrantClient(host=host, port=port, timeout=60.0)
    scroll_filter = {}

    total_exported = 0
    offset = None
    with open(output_file, 'w') as f:
        while True:
            for attempt in range(3):
                try:
                    result, next_page = client.scroll(
                        collection_name=collection_name,
                        filter=scroll_filter,
                        offset=offset,
                        with_payload=True,
                        with_vectors=True,
                        limit=100
                    )
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    print(f"[Warning] Scroll failed (attempt {attempt + 1}/3), retrying in 5s...")
                    import time
                    time.sleep(5)
            if not result:
                break
            for point in result:
                memory_entry = {
                    'id': point.id,
                    'payload': point.payload,
                    'vector': point.vector,
                }
                json.dump(memory_entry, f)
                f.write('\n')
                total_exported += 1
            offset = next_page

    print(f"Exported {total_exported} memory entries to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export memory entries from Qdrant to JSONL.")
    parser.add_argument("output", help="Output file path (e.g., memory_log.json)")
    parser.add_argument("--host", default="localhost", help="Qdrant host (default: localhost)")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port (default: 6333)")
    parser.add_argument("--collection", default="panai_memory", help="Collection name (default: panai_memory)")
    args = parser.parse_args()

    export_memories(args.output, args.host, args.port, args.collection)

if __name__ == "__main__":
    main()
