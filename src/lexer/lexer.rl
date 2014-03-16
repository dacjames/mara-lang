/*
 * Mara's main lexer.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "lexer.h"

#define YIELD(tokid) stream_push(stream, tokid, ts, te-ts-1)


%%{
  machine mara;

  # Symbols & Letters
  letter_small = [a-z];
  letter_big = [A-Z];
  letter_special = [_!?];
  letter = letter_small | letter_big;
  symbol = [\-+*/%^~&];  # TODO jump to eq state

  # colon = ':';
  # colcol = '::';

  # Reserved for future use.
  reserved = [|];

  # Keywords
  keyword = 'for' @{ kw_flag = FOR; printf("kw_flag = %d\n", kw_flag); }
          | 'in'  @{ kw_flag = IN; printf("kw_flag = %d\n", kw_flag); }
          ;

  # Identifiers
  idv = (letter_special* letter_small letter* letter_special*)
      | keyword
      | keyword
        letter+ >{kw_flag = 0;}
        letter_special*
      ;
  idt = letter_special* letter_big letter* letter_special*;
  ids = symbol+;


  expr = (idv | idt | ids);

  main := |*

  [ \t];
  idv {
    if (kw_flag) {
      YIELD(kw_flag);
    }
    else {
      YIELD(IDV);
    }
    kw_flag = 0;

  };

  idt { YIELD(IDT); };
  ids { YIELD(IDS); };

  '(' { YIELD(LPAR); }; ')' { YIELD(LPAR); };
  '[' { YIELD(LBKT); }; ']' { YIELD(RBKT); };
  '{' { YIELD(LBRC); }; '}' { YIELD(RBRC); };

  *|;
}%%

%% write data nofinal;

char * tok2str (Tok tok) {
  char * type;
  char * str;

  switch (tok.id) {
    case F:       type = "F";        break;
    case T:       type = "T";        break;
    case INT:     type = "INT";      break;
    case POINT:   type = "POINT";    break;
    case STRING:  type = "STRING";   break;
    case LPAR:    type = "LPAR";     break;
    case RPAR:    type = "RPAR";     break;
    case LBKT:    type = "LBKT";     break;
    case RBKT:    type = "RBKT";     break;
    case LBRC:    type = "LBRC";     break;
    case RBRC:    type = "RBRC";     break;
    case IDV:     type = "IDV";      break;
    case IDS:     type = "IDS";      break;
    case IDT:     type = "IDT";      break;
    case MATCH:   type = "MATCH";    break;
    case AS:      type = "AS";       break;
    case FOR:     type = "FOR";      break;
    case IN:      type = "IN";       break;
    case IF:      type = "IF";       break;
    case ELSE:    type = "ELSE";     break;
    case IMPORT:  type = "IMPORT";   break;
    case EXPORT:  type = "EXPORT";   break;
    case BIND:    type = "BIND";     break;
    case MODULE:  type = "MODULE";   break;
    case END:     type = "END";      break;
    default:      type = "Uknown Token";
  }
  str = (char *) malloc(strlen(type) + strlen(tok.value) + 5);
  sprintf(str, "(%s, %s)", type, tok.value);
  return str;
}


LexStream* stream_init(size_t size){
  LexStream * this;

  this = (LexStream *) malloc(sizeof(LexStream));
  this->stream = (Tok *) malloc(size * sizeof(Tok));
  this->len = 0;
  this->size = size;

  return this;
}

void stream_grow(LexStream * this) {
  this->stream = (Tok *) realloc(this->stream, this->size * sizeof(TokId) * 2);
  this->size *= 2;
}

void stream_push(LexStream * this, TokId tokid, char * value, size_t value_len){
  Tok tok;


  if (this->len == this->size) {
    stream_grow(this);
  }

  this->len += 1;

  tok = this->stream[this->len];
  tok.id = tokid;
  tok.value = (char *) malloc((value_len + 1) * sizeof(char));

  strncpy(tok.value, value, value_len + 1);   // + 1 to ensure that the value is null terminated;

  printf("%s\n", tok2str(tok));
}


#define BUFSIZE 128
#define STREAMSIZE 1024

LexStream lex(FILE* inf) {

  static char buf[BUFSIZE];
  int cs, act, have = 0, curline = 1;
  char *ts, *te = 0;
  int done = 0;
  LexStream * stream;
  int kw_flag = 0;

  stream = stream_init(STREAMSIZE);

  %% write init;

  while ( !done ) {
    char *p = buf + have
    char *pe;
    char *eof = 0;
    int len, space = BUFSIZE - have;

    if ( space == 0 ) {
      /* We've used up the entire buffer storing an already-parsed token
       * prefix that must be preserved. */
      fprintf(stderr, "OUT OF BUFFER SPACE\n" );
      exit(1);
    }

    len = fread( p, 1, space, inf );
    pe = p + len;

    /* Check if this is the end of file. */
    if ( len < space ) {
      eof = pe;
      done = 1;
    }

    %% write exec;

    // if ( cs == clang_error ) {
    //   fprintf(stderr, "PARSE ERROR\n" );
    //   break;
    // }

    if ( ts == 0 )
      have = 0;
    else {
      /* There is a prefix to preserve, shift it over. */
      have = pe - ts;
      memmove( buf, ts, have );
      te = buf + (te-ts);
      ts = buf;
    }
  }
  return *stream;
}

int main() {
  lex(stdin);
  return 0;
}
