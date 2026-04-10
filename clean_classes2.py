import os
import glob

files = glob.glob('frontend/src/**/*.jsx', recursive=True)

to_remove = [
    'font-mono ',
    'text-[10px] ',
    'text-[11px] ',
    'uppercase ',
    'tracking-widest ',
    'tracking-wider ',
    '!font-mono ',
    '!uppercase ',
    '!tracking-widest ',
    '!text-[10px] '
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for text in to_remove:
        content = content.replace(text, '')
    
    # ensure it gets edge instances not followed by space (end of string)
    for text in to_remove:
        content = content.replace(" " + text.strip() + "\"", "\"")
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)

print(f"Cleaned {len(files)} files.")
