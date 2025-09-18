#include <stdlib.h>

{%- set n_events = events|count %}
{%- set n_automatons = automaton_list|count %}
/* Struct's */
#define NUM_EVENTS {{ n_events }}
#define NUM_SUPERVISORS {{ n_automatons }}

{%- for event in events %}
#define EV_{{event.name}} {{loop.index-1}}
{%- endfor %}

void SCT_init();
void SCT_reset();
void SCT_add_callback( unsigned char event, void (*clbk)( void* ), unsigned char (*ci)( void* ), void* data );
void SCT_run_step();
