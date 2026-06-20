# bin_to_vba

Converts a raw shellcode binary into a self-contained Office VBA macro that allocates executable memory and runs the payload in-process.

> **For authorized security testing and research only.**

## How it works

1. Reads the binary shellcode file.
2. Splits the bytes into fixed-size `Array()` chunks, each wrapped in a `FillBuf` Sub to stay under VBA's 1 KB line limit.
3. Generates `VirtualAlloc` + `RtlMoveMemory` + `CreateThread` calls via `Declare PtrSafe` (64-bit Office compatible).
4. Writes a `.vba` file (or prints to stdout) ready to paste into the Office macro editor.

## Usage

```
python3 bin_to_vba.py <shellcode.bin> [options]

positional:
  shellcode.bin          Raw binary shellcode

options:
  -o, --output FILE      Write output to FILE instead of stdout
  --chunk N              Bytes per Array() call (default: 50)
  --chunks-per-sub M     Array() calls per Sub (default: 10)
```

## Examples

```bash
# print to stdout
python3 bin_to_vba.py shellcode.bin

# write to file
python3 bin_to_vba.py shellcode.bin -o macro.vba

# larger chunks (fewer subs generated)
python3 bin_to_vba.py shellcode.bin --chunk 100 --chunks-per-sub 20
```

## Output structure

```
[WinAPI declares]
Sub FillBuf0(buf() As Byte) ... End Sub
Sub FillBuf1(buf() As Byte) ... End Sub
...
Function MyMacro()
  ReDim buf(N)
  FillBuf0 buf
  FillBuf1 buf
  ...
  VirtualAlloc / RtlMoveMemory / CreateThread
End Function
Sub Document_Open() / Sub AutoOpen()
```

## Requirements

- Python 3.6+
- No external dependencies
