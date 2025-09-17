#include "generic_mic_public.h"

{%- set n_events = events|count %}
{%- set n_automatons = automaton_list|count %}
const unsigned char ev_controllable[{{ n_events }}] = {{ ev_controllable }};
const unsigned char ev_public[{{ n_events }}] = {{ ev_public }};
const unsigned char sup_events[{{ n_automatons }}][{{ n_events }}] = {{ sup_event_map }};
const unsigned long int sup_init_state[{{ n_automatons }}] = {{ sup_init_state }};
unsigned long int sup_current_state[{{ n_automatons }}] = {{ sup_current_state }};
const unsigned long int sup_data_pos[{{ n_automatons }}] = {{ sup_data_pos }};
const unsigned char sup_data[{{ n_data }}] = {{ sup_data }};

typedef struct Scallback {
    void (*callback)( void* data );
    unsigned char (*check_input) ( void* data );
    void* data;
} Tcallback;

Tcallback callback[ NUM_EVENTS ];

unsigned long int get_state_position( unsigned char supervisor, unsigned long int state ){
    unsigned long int position;
    unsigned long int s;
    unsigned long int en;
    position = sup_data_pos[ supervisor ];
    for(s=0; s<state; s++){
        en       = sup_data[position];
        position += en * 3 + 1;
    }
    return position;
}

void make_transition( unsigned char event ){
    unsigned char i;
    unsigned long int position;
    unsigned char num_transitions;

    for(i=0; i<NUM_SUPERVISORS; i++){
        if(sup_events[i][event]){
            position        = get_state_position(i, sup_current_state[i]);
            num_transitions = sup_data[position];
            position++;
            while(num_transitions--){
                if(sup_data[position] == event){
                    sup_current_state[i] = (sup_data[position + 1] * 256) + (sup_data[position + 2]);
                    break;
                }
                position+=3;
            }
        }
    }
}

unsigned char get_active_controllable_events( unsigned char *events ){
    unsigned char i,j;
    unsigned char count_actives = 0;

    /* Disable all non controllable events */
    for( i=0; i<NUM_EVENTS; i++ ){
        if( !ev_controllable[i] ){
            events[i] = 0;
        } else {
            events[i] = 1;
            count_actives++;
        }
    }

    /* Check disabled events for all supervisors */
    for(i=0; i<NUM_SUPERVISORS; i++){
        unsigned long int position;
        unsigned char ev_disable[NUM_EVENTS], k;
        unsigned char num_transitions;
        for(k=0; k<NUM_EVENTS;k++){
         ev_disable[k] = 1;
        }
        for( j=0; j<NUM_EVENTS; j++ ){

            /*if supervisor don't have this event, it can't disable the event*/
            if( !sup_events[i][j] ){
                ev_disable[j] = 0;
            }
        }
        /*if supervisor have a transition with the event in the current state, it can't disable the event */
        position = get_state_position(i, sup_current_state[i]);
        num_transitions = sup_data[position];
        position++;
        while(num_transitions--){
            ev_disable[ sup_data[position] ] = 0;
            position += 3;
        }

        /* Disable for current supervisor states */
        for( j=0; j<NUM_EVENTS; j++ ){
            if( ev_disable[j] == 1 && events[ j ] ){
                events[ j ] = 0;
                count_actives--;
            }
        }
    }
    
    return count_actives;
}

/* IN_read */
unsigned char input_buffer[256];
unsigned char input_buffer_pnt_add = 0;
unsigned char input_buffer_pnt_get = 0;

unsigned char input_buffer_pub[256];
unsigned char input_buffer_pub_pnt_add = 0;
unsigned char input_buffer_pub_pnt_get = 0;

unsigned char input_buffer_get( unsigned char *event ){
    if(input_buffer_pnt_add == input_buffer_pnt_get){
        return 0;
    } else {
        *event = input_buffer[ input_buffer_pnt_get ];
        input_buffer_pnt_get++;
        return 1;
    }
}

unsigned char input_buffer_pub_get(unsigned char *event){
    if(input_buffer_pub_pnt_add == input_buffer_pub_pnt_get){
        return 0;
    } else {
        *event = input_buffer_pub[ input_buffer_pub_pnt_get ];
        input_buffer_pub_pnt_get++;
        return 1;
    }
}

void input_buffer_add( unsigned char event ){
    input_buffer[ input_buffer_pnt_add ] = event;
    input_buffer_pnt_add++;
}

void input_buffer_pub_add(unsigned char event){
    input_buffer_pub[input_buffer_pub_pnt_add] = event;
    input_buffer_pub_pnt_add++;
}

unsigned char input_buffer_check_empty(){
    return input_buffer_pnt_add == input_buffer_pnt_get;
}

unsigned char input_buffer_pub_check_empty(){
    return input_buffer_pub_pnt_add == input_buffer_pub_pnt_get;
}

unsigned char input_read( unsigned char ev ){
    if( ev < NUM_EVENTS && callback[ ev ].check_input != NULL )
        return callback[ ev ].check_input( callback[ ev ].data );
    return 0;
}

unsigned char last_events[NUM_EVENTS];
void update_input(){
    unsigned char i;
    for(i=0;i<NUM_EVENTS;i++){
        if( !ev_controllable[i] ){  /* Check the UCEs only */
            if( input_read( i ) ){
                if( ev_public[i] ){ /* Check whether the UCE is public or private */
                    input_buffer_pub_add(i);
                } else {
                    input_buffer_add(i);
                }
            }
        }
    }
}

unsigned char get_next_uncontrollable_pub( unsigned char *event ){
    if( !input_buffer_pub_check_empty() ) {
        *event = input_buffer_pub[input_buffer_pub_pnt_get];
        input_buffer_pub_pnt_get++;
        return 1;
    }
    return 0;
}

/*choices*/
unsigned char get_next_controllable( unsigned char *event ){
    unsigned char events[NUM_EVENTS], i, count_actives;
    unsigned long int random_pos;
    
    count_actives = get_active_controllable_events( events );
    
    if( count_actives ){
        random_pos = rand() % count_actives;
        for(i=0; i<NUM_EVENTS; i++){
            if( !random_pos && events[i] ){
                *event = i;
                return 1;
            } else if( events[i] ){
                random_pos--;
            }
        }
    }
    return 0;
}


void execCallback( unsigned char ev ){
    if( ev < NUM_EVENTS && callback[ ev ].callback != NULL )
        callback[ ev ].callback( callback[ ev ].data );
}

//PUBLIC:

void SCT_init(){
    int i;
    for(i=0; i<NUM_EVENTS; i++){
        last_events[i] = 0;
        callback[i].callback    = NULL;
        callback[i].check_input = NULL;
        callback[i].data        = NULL;
    }
}

void SCT_reset(){
    int i;
    for(i=0; i<NUM_SUPERVISORS; i++){
        sup_current_state[i] = sup_init_state[i];
    }
    for(i=0; i<NUM_EVENTS; i++){
        last_events[i] = 0;
    }
}

void SCT_add_callback( unsigned char event, void (*clbk)( void* ), unsigned char (*ci)( void* ), void* data ){
        callback[ event ].callback    = clbk;
        callback[ event ].check_input = ci;
        callback[ event ].data        = data;
}

void SCT_run_step(){
    // AUTOMATA PLAYER
    update_input();
    unsigned char event;
    while( input_buffer_pub_get( &event ) ){//clear buffer, executing all public uncontrollable events (NCE)
        make_transition( event );
        execCallback( event );
    }
    while( input_buffer_get( &event ) ){//clear buffer, executing all no controllable events (NCE)
        make_transition( event );
        execCallback( event );
    }
    if( get_next_controllable( &event ) ){//find controllable event (CE)
        if( input_buffer_check_empty() ){ //Only execute CE if NCE input buffer is empty
            make_transition( event );
            execCallback( event );
        }
    }
}
