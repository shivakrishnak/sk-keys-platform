import os

files_to_fix = [
    'technical-mastery/tier-7-frontend/RCT-react/RCT-051 - XSS Prevention in React (dangerouslySetInnerHTML).md',
    'technical-mastery/tier-7-frontend/RCT-react/RCT-052 - Authentication Patterns in React (JWT, Session, OAuth).md',
    'technical-mastery/tier-7-frontend/RCT-react/RCT-053 - State Management Architecture (Zustand, Jotai, Signals).md',
    'technical-mastery/tier-7-frontend/RCT-react/RCT-055 - Over-Rendering Anti-Pattern (Unnecessary Re-renders).md',
    'technical-mastery/tier-7-frontend/RCT-react/RCT-057 - Scheduler Internals (Lane Model, Priority Queues).md',
    'technical-mastery/tier-7-frontend/RCT-react/RCT-060 - React Native Architecture (New Architecture, Fabric).md',
]

FENCE_OPEN = '```'

def fix_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    result = []
    in_fence = False
    fence_has_liquid = False
    fence_lines = []
    for line in lines:
        stripped = line.strip()
        if not in_fence and stripped.startswith(FENCE_OPEN):
            in_fence = True
            fence_has_liquid = False
            fence_lines = [line]
        elif in_fence:
            fence_lines.append(line)
            if '{{' in line:
                fence_has_liquid = True
            if stripped == FENCE_OPEN:
                in_fence = False
                if fence_has_liquid:
                    result.append('{% raw %}')
                    result.extend(fence_lines)
                    result.append('{% endraw %}')
                else:
                    result.extend(fence_lines)
                fence_lines = []
        else:
            if '{{' in line:
                result.append(line.replace('{{', '{%- raw -%}{{').replace('}}', '}}{%- endraw -%}'))
            else:
                result.append(line)
    if fence_lines:
        result.extend(fence_lines)
    new_content = '\n'.join(result)
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        return True
    return False

for fpath in files_to_fix:
    try:
        changed = fix_file(fpath)
        print(('Fixed' if changed else 'No change') + ': ' + os.path.basename(fpath))
    except Exception as e:
        print('ERROR: ' + fpath + ': ' + str(e))
