
#line 1 "lexer.rl"
/*
 * Mara's main lexer.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "lexer.h"

#define YIELD(tokid) stream_push(stream, tokid, ts, te-ts-1)



#line 69 "lexer.rl"



#line 21 "lexer.c"
static const char _mara_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14
};

static const char _mara_key_offsets[] = {
	0, 0, 7, 32, 39, 42, 49, 52, 
	60, 68, 76, 83
};

static const char _mara_trans_keys[] = {
	33, 63, 95, 65, 90, 97, 122, 9, 
	32, 33, 40, 41, 45, 47, 63, 91, 
	93, 94, 95, 102, 105, 123, 125, 126, 
	37, 38, 42, 43, 65, 90, 97, 122, 
	33, 63, 95, 65, 90, 97, 122, 33, 
	63, 95, 33, 63, 95, 65, 90, 97, 
	122, 33, 63, 95, 45, 47, 94, 126, 
	37, 38, 42, 43, 33, 63, 95, 111, 
	65, 90, 97, 122, 33, 63, 95, 114, 
	65, 90, 97, 122, 33, 63, 95, 65, 
	90, 97, 122, 33, 63, 95, 110, 65, 
	90, 97, 122, 0
};

static const char _mara_single_lengths[] = {
	0, 3, 17, 3, 3, 3, 3, 4, 
	4, 4, 3, 4
};

static const char _mara_range_lengths[] = {
	0, 2, 4, 2, 0, 2, 0, 2, 
	2, 2, 2, 2
};

static const char _mara_index_offsets[] = {
	0, 0, 6, 28, 34, 38, 44, 48, 
	55, 62, 69, 75
};

static const char _mara_indicies[] = {
	0, 0, 0, 2, 3, 1, 4, 4, 
	0, 6, 7, 5, 5, 0, 8, 9, 
	5, 0, 10, 11, 12, 13, 5, 5, 
	5, 2, 3, 1, 15, 15, 15, 2, 
	2, 14, 15, 15, 15, 14, 17, 17, 
	17, 3, 3, 16, 17, 17, 17, 16, 
	5, 5, 5, 5, 5, 5, 18, 17, 
	17, 17, 19, 3, 3, 16, 17, 17, 
	17, 20, 3, 3, 16, 17, 17, 17, 
	21, 21, 16, 17, 17, 17, 22, 3, 
	3, 16, 0
};

static const char _mara_trans_targs[] = {
	1, 0, 3, 5, 2, 7, 2, 2, 
	2, 2, 8, 11, 2, 2, 2, 4, 
	2, 6, 2, 9, 10, 5, 10
};

static const char _mara_trans_actions[] = {
	0, 0, 0, 0, 11, 0, 13, 15, 
	17, 19, 0, 0, 21, 23, 27, 0, 
	25, 0, 29, 0, 1, 5, 3
};

static const char _mara_to_state_actions[] = {
	0, 0, 7, 0, 0, 0, 0, 0, 
	0, 0, 0, 0
};

static const char _mara_from_state_actions[] = {
	0, 0, 9, 0, 0, 0, 0, 0, 
	0, 0, 0, 0
};

static const char _mara_eof_trans[] = {
	0, 0, 0, 15, 15, 17, 17, 19, 
	17, 17, 17, 17
};

static const int mara_start = 2;
static const int mara_error = 0;

static const int mara_en_main = 2;


#line 72 "lexer.rl"

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

  
#line 202 "lexer.c"
	{
	cs = mara_start;
	ts = 0;
	te = 0;
	act = 0;
	}

#line 162 "lexer.rl"

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

    
#line 235 "lexer.c"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _mara_actions + _mara_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 4:
#line 1 "NONE"
	{ts = p;}
	break;
#line 256 "lexer.c"
		}
	}

	_keys = _mara_trans_keys + _mara_key_offsets[cs];
	_trans = _mara_index_offsets[cs];

	_klen = _mara_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (unsigned int)(_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _mara_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += (unsigned int)((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _mara_indicies[_trans];
_eof_trans:
	cs = _mara_trans_targs[_trans];

	if ( _mara_trans_actions[_trans] == 0 )
		goto _again;

	_acts = _mara_actions + _mara_trans_actions[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 30 "lexer.rl"
	{ kw_flag = FOR; printf("kw_flag = %d\n", kw_flag); }
	break;
	case 1:
#line 31 "lexer.rl"
	{ kw_flag = IN; printf("kw_flag = %d\n", kw_flag); }
	break;
	case 2:
#line 38 "lexer.rl"
	{kw_flag = 0;}
	break;
	case 5:
#line 49 "lexer.rl"
	{te = p+1;}
	break;
	case 6:
#line 64 "lexer.rl"
	{te = p+1;{ YIELD(LPAR); }}
	break;
	case 7:
#line 64 "lexer.rl"
	{te = p+1;{ YIELD(LPAR); }}
	break;
	case 8:
#line 65 "lexer.rl"
	{te = p+1;{ YIELD(LBKT); }}
	break;
	case 9:
#line 65 "lexer.rl"
	{te = p+1;{ YIELD(RBKT); }}
	break;
	case 10:
#line 66 "lexer.rl"
	{te = p+1;{ YIELD(LBRC); }}
	break;
	case 11:
#line 66 "lexer.rl"
	{te = p+1;{ YIELD(RBRC); }}
	break;
	case 12:
#line 50 "lexer.rl"
	{te = p;p--;{
    if (kw_flag) {
      YIELD(kw_flag);
    }
    else {
      YIELD(IDV);
    }
    kw_flag = 0;

  }}
	break;
	case 13:
#line 61 "lexer.rl"
	{te = p;p--;{ YIELD(IDT); }}
	break;
	case 14:
#line 62 "lexer.rl"
	{te = p;p--;{ YIELD(IDS); }}
	break;
#line 383 "lexer.c"
		}
	}

_again:
	_acts = _mara_actions + _mara_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 3:
#line 1 "NONE"
	{ts = 0;}
	break;
#line 396 "lexer.c"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _mara_eof_trans[cs] > 0 ) {
		_trans = _mara_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	}

	_out: {}
	}

#line 186 "lexer.rl"

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
