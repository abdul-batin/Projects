#!/usr/bin/env python3
"""Diagnostic: count compatible vs incompatible placements and their heights."""
import json
from collections import Counter

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#!/usr/bin/env python3
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import defaultdict, Counter
from datetime import datetime

def analyze_inversions(path):
    with open(path) as f:
        state = json.load(f)
    stacks = defaultdict(list)
    for c in state['containers']:
        p = c['position']
        key = (p['block'], p['bay'], p['row'])
        dt = c.get('departure_time', '')
        try:
            t = datetime.fromisoformat(dt).timestamp()
        except:
            t = 0
        stacks[key].append((p['tier'], t))

    total = 0; inverted = 0
    for key, tiers in stacks.items():
        tiers.sort()
        for i in range(len(tiers)-1):
            _, d1 = tiers[i]; _, d2 = tiers[i+1]
            total += 1
            if d1 < d2:  # lower tier leaves sooner = blocked by upper
                inverted += 1
    print(f"{path}: {total} pairs, {inverted} inverted ({100*inverted/total:.1f}%)")

analyze_inversions('data/train/initial_state.json')
analyze_inversions('data/test/initial_state.json')


