import re
from .constants import MAX_STEP_CHARS, MIN_STEP_LEN, MAX_STEPS

def _split_long_step(step, n=MAX_STEP_CHARS):
    """splits a long step into multiple steps, trying to respect sentence boundaries and punctuation."""
    if len(step) <= n:
        return [step]
    
    # strong punctuation: split on sentence boundaries
    parts = re.split(r'(?<=[.!?])\s+', step)
    if len(parts) >= 2:
        return _merge_to_limit(parts)
    
    # Fallback: split on commas or semicolons
    parts = re.split(r'(?<=[,;])\s+', step)
    if len(parts) >= 2:
        return _merge_to_limit(parts, n)
    
    # Fallback: hard split
    return _hard_split(step, n)

def _merge_to_limit(parts, max_chars=MAX_STEP_CHARS):
    """Merges parts into steps, ensuring each step does not exceed max_chars."""
    merged = []
    current = parts[0]
    for part in parts[1:]:
        candidate = current + ' ' + part
        if len(candidate) <= max_chars:
            current = candidate
        else:
            merged.append(current)
            current = part
    merged.append(current)
    return merged

def _hard_split(step, max_chars=MAX_STEP_CHARS):
    parts = []
    while len(step) > max_chars:
        cut = step.rfind(' ', 0, max_chars)
        if cut <= 0: 
            cut = max_chars
        parts.append(step[:cut].strip())
        step = step[cut:].strip()
        if not step:
            break
    if step:
        parts.append(step)
    return parts

def clean_step(s):
    s = re.sub(r'^(?:step\s*)?\d+[\s.\:\)]+\s*', '', s, flags=re.IGNORECASE).strip()
    s = re.split(r'\b(pro tips?|notes?|tips?)\b', s, flags=re.IGNORECASE)[0]
    s = re.sub(r'[^\S\n]+', ' ', s).strip()
    return s

def _normalize(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[^\S\n]+', ' ', text)
    text = text.replace('\\n', '\n')
    return text.strip()

def _try_numbered(text):
    """Strategy 1: explicit numbered steps (1. / 1) / 1: / Step 1)."""
    pattern = r'(?:^|\n)\s*(?:step\s+)?\d+[.\:\)]\s+'
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > MIN_STEP_LEN]
    return parts if len(parts) >= 2 else None

def _try_double_newline(text):
    """Strategy 2: double newlines."""
    if '\n\n' not in text:
        return None
    parts = re.split(r'\n{2,}', text)
    parts = [p.replace('\n', ' ').strip() for p in parts if p.strip() and len(p.strip()) > MIN_STEP_LEN]
    return parts if len(parts) >= 2 else None

def _try_single_newline(text):
    """Strategy 3: single newlines."""
    lines = text.split('\n')
    # Vale solo se la maggioranza delle righe è "sostanziosa"
    substantial = [l.strip() for l in lines if len(l.strip()) > MIN_STEP_LEN]
    if len(substantial) >= 2 and len(substantial) / max(len(lines), 1) > 0.6:
        return substantial
    return None

def _try_sentences(text):
    """Strategy 4 (fallback): split into sentences and merge to respect MAX_STEPS."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return [text]
    steps = sentences
    while len(steps) > MAX_STEPS:
        # merge the two shortest consecutive steps
        min_idx = min(range(len(steps) - 1), key=lambda i: len(steps[i]) + len(steps[i + 1]))
        steps[min_idx] = steps[min_idx] + ' ' + steps[min_idx + 1]
        steps.pop(min_idx + 1)
    return steps

def parse_steps(instructions):
    """Parses the instructions text into a list of clean steps."""
    if not instructions:
        return []

    text = _normalize(instructions)

    steps = (
        _try_numbered(text)
        or _try_double_newline(text)
        or _try_single_newline(text)
        or _try_sentences(text)
    )

    steps = [clean_step(s) for s in steps]
    steps = [s for s in steps if len(s) > MIN_STEP_LEN]

    split_steps = []
    if len(steps) < 10:
        for s in steps:
            split_steps.extend(_split_long_step(s))
        steps = split_steps
    
    if len(steps) < 3:
        steps = _try_sentences(text)
        steps = [clean_step(s) for s in steps if len(s) > MIN_STEP_LEN]

    if len(steps) > 25:
        print('max steps exceeded')
        steps = steps[:25]

    return steps