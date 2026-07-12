# Keshava

Keshava is a small, Hindi/Sanskrit-keyword-inspired toy programming
language, implemented in Python. It supports variables, printing,
conditionals, while loops, and functions with return values.

## Project structure

```
Keshava/
├── main.py          # Runs the language
├── lexer.py         # Lexical analyzer (source code -> tokens)
├── parser.py        # Parser (tokens -> AST)
├── interpreter.py   # Tree-walking interpreter (executes the AST)
├── tokens.py         # Token / keyword definitions
├── ast_nodes.py      # AST node classes
├── grammar.txt        # Grammar rules
├── keshav.msm          # Example Keshava program
└── README.md           # This file
```

## Keywords

| Meaning   | Keyword       |
|-----------|---------------|
| Start     | Aarambha      |
| End       | Samaapti      |
| Print     | Likha         |
| If        | Yadi          |
| Else      | Anyathaa      |
| While     | Yaavat        |
| For       | Punah *(resermsm)* |
| Integer   | Sankhya       |
| String    | Paatha        |
| Boolean   | Satyam        |
| True      | Satya         |
| False     | Asatya        |
| Function  | Kriyaa        |
| Return    | Pratyaagaccha |
| Input     | Grahana *(resermsm)* |

`Punah` (for-loops) and `Grahana` (input) are recognized by the lexer
but do not yet have parser/interpreter support — see "Known
limitations" below.

## Running a program

```bash
python main.py keshav.msm
```

## Example

```
Aarambha

Sankhya age = 20

Paatha name = "Vivek"

Likha(name)

Yadi(age >= 18){
    Likha("Adult")
}
Anyathaa{
    Likha("Minor")
}

Samaapti
```

Output:

```
Vivek
Adult
```

## Language features

- **Variable declarations**: `Sankhya`, `Paatha`, `Satyam` for
  integers, strings, and booleans.
- **Assignment**: `age = age + 1`
- **Printing**: `Likha(expression)`
- **Conditionals**: `Yadi (...) { ... } Anyathaa { ... }`
- **Loops**: `Yaavat (...) { ... }`
- **Functions**: `Kriyaa name(params) { ... Pratyaagaccha value }`
- **Operators**: `+ - * / %`, comparisons `== != < > <= >=`
- **Comments**: `# this is a comment`

### Functions example

```
Aarambha

Kriyaa square(n){
    Pratyaagaccha n * n
}

Likha(square(5))

Samaapti
```

Output:

```
25
```

## Architecture

1. **`lexer.py`** turns the raw source text into a flat list of
   `(TOKEN_KIND, VALUE)` tuples using a single combined regular
   expression, mapping recognized identifiers to keyword tokens via
   `tokens.KEYWORDS`.
2. **`parser.py`** is a hand-written recursive-descent parser. It
   turns the token stream into an AST built from the classes in
   `ast_nodes.py` (`Program`, `VarDeclaration`, `If`, `While`,
   `Function`, `BinaryOp`, etc.). Expression parsing uses standard
   precedence climbing: comparison > addition/subtraction >
   multiplication/division/modulo > primary.
3. **`interpreter.py`** walks the AST directly (no bytecode/VM step).
   It keeps a chain of `Environment` scopes for variable lookup, and
   uses a `ReturnSignal` exception to unwind out of a function body
   when a `Pratyaagaccha` (return) statement executes.

## Known limitations

- `Punah` (for-loops) is tokenized but not implemented; use `Yaavat`
  (while) instead.
- `Grahana` (input) is tokenized but not implemented — there's no
  corresponding AST node or interpreter support yet.
- No `Viraama` (break) / `Anuvartaya` (continue) support yet.
- No arrays, floats, or nested/anonymous functions.
- Error messages are basic (raised as Python exceptions with a
  message), not line/column-accurate.

These are natural next extensions if you want to keep building the
language out.
