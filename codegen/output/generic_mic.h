#include <stdlib.h>
/* Struct's */
#define NUM_EVENTS 2
#define NUM_SUPERVISORS 1
#define EV_y 0
#define EV_x 1

void SCT_init();
void SCT_reset();
void SCT_add_callback( unsigned char event, void (*clbk)( void* ), unsigned char (*ci)( void* ), void* data );
void SCT_run_step();


// void SCT_set_decay_prob_event( unsigned char event, char factor );
// void SCT_decay_prob();
void SCT_set_decay_prob_event( unsigned char event, float init_decay, float decay );
void SCT_decay_prob();