import re

def extract_ids(path):
    ids = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('| `'):
                match = re.search(r'\| `([^`]+)`', line)
                if match:
                    ids.append(match.group(1))
    return ids

if __name__ == "__main__":
    ids = extract_ids('/workspace/RB4/missing_songs_investigation.md')
    print(",".join(ids))
