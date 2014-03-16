
typedef enum {
  F       = 0,
  T       = 1,
  INT     = 2,
  POINT   = 3,
  STRING  = 4,

  LPAR    = 11,
  RPAR    = 12,
  LBKT    = 13,
  RBKT    = 14,
  LBRC    = 15,
  RBRC    = 16,

  IDV     = 21,
  IDS     = 22,
  IDT     = 23,

  MATCH   = 101,
  AS      = 102,
  FOR     = 103,
  IN      = 104,
  IF      = 105,
  ELSE    = 106,
  IMPORT  = 107,
  EXPORT  = 108,
  BIND    = 109,
  MODULE  = 110,
  END     = 111
} TokId;

typedef struct {
  TokId id;
  char* value;
  int line;
  int column;
} Tok;

typedef struct {
  Tok* stream;
  size_t len;
  size_t size;
} LexStream;

LexStream lex(FILE* inf);
