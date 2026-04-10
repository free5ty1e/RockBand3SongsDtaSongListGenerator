import os

def main():
    candidates_path = '/workspace/RB4/output/patch_4_candidates.txt'
    if not os.path.exists(candidates_path):
        return

    with open(candidates_path, 'r') as f:
        candidates = [line.strip() for line in f if line.strip()]

    missing_requests = [c for c in candidates if c.startswith('request_')]
    
    results = []
    for r in sorted(missing_requests):
        title = r.replace('request_', '').replace('_', ' ').title() + ' (Crowd Request)'
        results.append(f'| `{r}` | {title} | Update PKG | `patch_main_ps4_4.ark` | Pending |')
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
