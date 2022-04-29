#include <stdlib.h>
/* Struct's */
#define NUM_EVENTS 4
#define NUM_SUPERVISORS 2
#define EV_a 0
#define EV_b 1
#define EV_c 2
#define EV_y 3

void SCT_init();
void SCT_reset();
void SCT_add_callback( unsigned char event, void (*clbk)( void* ), unsigned char (*ci)( void* ), void* data );
void SCT_run_step();


// void SCT_set_decay_prob_event( unsigned char event, char factor );
// void SCT_decay_prob();
void SCT_set_decay_prob_event( unsigned char event, float init_decay, float decay );
void SCT_decay_prob();