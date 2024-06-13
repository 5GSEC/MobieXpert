/*
 * pb_runtime.h
 *
 *   Copyright (c) Computer Sciences Laboratory, SRI International 1995. 
 *   See the file COPYING in this directory for information on the
 *   conditions under which this software can be copied.
 *   This software comes with NO WARRANTY.
 */

/* 	$Id: pb_runtime.h,v 1.1 1999/05/13 23:43:56 raghavan Exp $	 */

#include <string.h>

#ifdef __STDC__

#define malloc malloc_kludge
#define free free_kludge
#include <stdlib.h>
#undef malloc
#undef free

#endif


#define ASSERT_FCT 1
#define NEGATE_FCT 2
#define SELECT_BND 3
#define INITIALIZE 4

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#ifndef min
#define min(x,y) (x<y?x:y)
#endif

#ifndef max
#define max(x,y) (x>y?x:y)
#endif

struct mark {
        char *symbol;
        struct mark *next;
};


struct factlist {
  struct fact *fact;
  struct factlist *next;
  struct factlist *prev;
};


struct factheader {
  struct factlist **fl;
  struct factheader *next;
  struct factheader *prev;
};


struct bind {
  struct rulelist *rule;
  struct factlist *facts;
};


struct bindlist {
  struct bind *binding;
  struct bindlist *next;
  struct bindlist *prev;
};


struct rulelist {
  void (*ante1)();
  void (*concl)();
  char *name;                    /* Rule name. */
  struct factheader *fh;         /* Facts this rule has bound to. */
  struct bindlist *bestbinding;  /* Best binding with which to fire. */
  int repeat;                    /* Rule repeatability. */
  int rank;                      /* Rule priority. */
  int active;                    /* Can the rule currently fire? */
  long ante_secs;                /* Cumulative seconds spent executing antecedent. */
  long ante_usecs;               /* Cumulative microseconds spent executing antecedent. */
  long conc_secs;                /* Cumulative seconds spent executing conclusion. */
  long conc_usecs;               /* Cumulative microseconds spent executing conclusion. */
  long rule_firings;             /* Number of times consequent was executed. */
  char *text;                    /* Rule text. */ 
  char *sourcefile;              /* Full path name of rule source. */
  struct rulelist *next;
  struct rulelist *prev;
};

extern struct rulelist *pb_rules;
extern int pb_tsnum;

struct factlist *new_factlistnode();
struct bindlist *new_bindlistnode();
struct factlist *nthfact();
struct factlist *remove_fact();
struct factlist *in_factlist();

void engine(), negate(), pb_xmonitor(), push_bindlist(), push_factlist(), 
  push_mark(), remove_mark(), ui_message();

void add_to_list(), remove_from_list(), xfbinding(), remove_all_marks(), clear_binding();

struct mark *new_mark();
extern struct mark *pb_fact_ml();
int marktest();

void pb_ante_timein();
void pb_conc_timein();
void pb_ante_timeout();
void pb_conc_timeout();
void pb_output_times();
void pb_set_status();
void pb_reset_status();

char *pb_format_time();
