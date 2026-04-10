import os
import glob
import re

files = glob.glob('frontend/src/**/*.jsx', recursive=True)

to_remove = [
    r'\bfont-mono\b',
    r'\btext-\[10px\]\b',
    r'\btext-\[11px\]\b',
    r'\buppercase\b',
    r'\btracking-widest\b',
    r'\btracking-wider\b',
    r'\b!font-mono\b',
    r'\b!uppercase\b',
    r'\b!tracking-widest\b',
    r'\b!text-\[10px\]\b',
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for pattern in to_remove:
        content = re.sub(pattern, '', content)
    
    # After removing, we might have multiple spaces or starting/ending spaces inside strings
    # But carefully only try to replace spaces inside className=" ... ", simplifying replacing double spaces with single
    # Actually, double spaces inside classes doesn't break React. Let's just write as is.
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)

print(f"Cleaned {len(files)} files.")
