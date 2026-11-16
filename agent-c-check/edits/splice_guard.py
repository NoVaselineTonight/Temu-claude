import sys

coach, block = sys.argv[1], sys.argv[2]
lines = open(coach, encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('_INAPP_RE = re.compile('))
end = next(i for i in range(start, len(lines)) if lines[i].startswith('_QUESTION_START = re.compile('))
new = open(block, encoding='utf-8').read().rstrip('\n').split('\n')
lines[start:end] = new
out = '\n'.join(lines)
assert '\x08' not in out and '�' not in out, 'still corrupted'
open(coach, 'w', encoding='utf-8').write(out)
print('replaced lines', start + 1, 'to', end, 'with', len(new), 'lines')
