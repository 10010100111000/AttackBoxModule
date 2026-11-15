"""Generate a small genuine single-page PDF using only Python stdlib."""
import sys
from pathlib import Path

def pdf_escape(value):
    return value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

lines = [
    ("Password Policy", 20),
    ("Overview", 14),
    ("All accounts must use a secure and unique password.", 11),
    ("Do not share credentials with other employees.", 11),
    ("Change temporary passwords when you first sign in.", 11),
    ("Default password for new starters: funnel123#!#", 11),
]
stream = ['BT', '1 0 0 1 55 770 Tm']
for i, (line, size) in enumerate(lines):
    if i:
        stream.append('0 -38 Td' if i <= 2 else '0 -27 Td')
    stream.append(f'/F1 {size} Tf ({pdf_escape(line)}) Tj')
stream.append('ET')
content = '\n'.join(stream).encode('ascii')
objects = [
    b'<< /Type /Catalog /Pages 2 0 R >>',
    b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>',
    b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    b'<< /Length '+str(len(content)).encode()+b' >>\nstream\n'+content+b'\nendstream',
]
out=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
offsets=[0]
for index, obj in enumerate(objects, 1):
    offsets.append(len(out))
    out += f'{index} 0 obj\n'.encode()+obj+b'\nendobj\n'
xref=len(out)
out += f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
for offset in offsets[1:]:
    out += f'{offset:010d} 00000 n \n'.encode()
out += f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
Path(sys.argv[1]).write_bytes(out)
