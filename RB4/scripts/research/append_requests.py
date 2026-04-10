import os

def main():
    with open('/workspace/RB4/output/request_rows.txt', 'r') as f:
        new_rows = f.readlines()
    
    with open('/workspace/RB4/output/existing_requests.txt', 'r') as f:
        existing_content = f.read()
    
    final_rows = []
    for row in new_rows:
        # Extract song ID from row: | `id` | ...
        parts = row.split('|')
        if len(parts) > 1:
            song_id = parts[1].strip().replace('`', '')
            if song_id not in existing_content:
                final_rows.append(row)
    
    if final_rows:
        with open('/workspace/RB4/missing_songs_investigation.md', 'a') as f:
            f.write(''.join(final_rows))
        print(f"Added {len(final_rows)} new request songs.")
    else:
        print("No new request songs to add.")

if __name__ == "__main__":
    main()
