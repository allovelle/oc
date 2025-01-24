import sys
from dataclasses import dataclass

C_SRC = """
int n = 20;
int r = 0;
r = 1;
while (n > 0) {
    r = r * n;
    n = n - 1;
}
"""

ASM_SRC = """
n: LONG(20)
r: LONG(0)
start:
    CMOVE(1, r0)
    ST(r0, r)
    BR(test)
loop:
    LD(r, r3)
    LD(n, r1)
    MUL(r1, r3, r3)
    ST(r3, r)
    LD(n, r1)
    SUBC(r1, 1, r1)
    ST(r1, n)
test:
    LD(n, r1)
    CMPLT(r31, r1, r2)
    BT(r2, loop)
done:
"""


@dataclass
class Label:
    label: str

    def __repr__(self) -> str:
        return f"Label({self.label})"


@dataclass
class Instruction:
    symbol: str
    args: list[str]

    def __repr__(self) -> str:
        return f"{self.symbol}({', '.join(self.args)})"


def parse_asm(src):
    def strips(s):
        return [i.strip() for i in s]

    for line in filter(lambda s: s, map(lambda s: s.strip(), src.splitlines())):
        if ":" in line:
            label, target = strips(line.split(":"))
            yield Label(label)
            if not target:
                continue
            line = target
        instruction = strips(line.replace("(", ",").replace(")", "").split(","))
        yield Instruction(instruction[0], instruction[1:])


def a3_to_arm_macos(instructions):
    "A3: Architecture Agnostic Assembly"
    # 1. Do first pass over instructions, gather all the labels and jumps
    # 2. Go back and fill in the holes
    # 3. Write resulting buffer to Mach-O ELF file

def main(args=None):
    args = args or []
    instructions = [*parse_asm(ASM_SRC)]
    [print(i) for i in instructions]
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
