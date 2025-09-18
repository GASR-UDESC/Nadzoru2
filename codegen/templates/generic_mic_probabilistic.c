#include "generic_mic_probabilistic.h"

{%- set n_events = events|count %}
{%- set n_automatons = automaton_list|count %}
{%- set n_data = data|count %}
{%- set n_data_prob = data_prob|count %}
const unsigned char ev_controllable[{{ n_events }}] = {{ ev_controllable }};
const unsigned char sup_events[{{ n_automatons }}][{{ n_events }}] = {{ sup_event_map }};
const unsigned long int sup_init_state[{{ n_automatons }}] = {{ sup_init_state }};
unsigned long int sup_current_state[{{ n_automatons }}] = {{ sup_current_state }};
const unsigned long int sup_data_pos[{{ n_automatons }}] = {{ sup_data_pos }};
const unsigned char sup_data[{{ n_data }}] = {{ sup_data }};
unsigned long int sup_data_prob_pos[{{ n_automatons }}] = {{ sup_data_prob_pos }};
float sup_data_prob[{{ n_data_prob }}] = {{ sup_data_prob }};

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

unsigned long int get_state_position_prob( unsigned char supervisor, unsigned long int state ) {
    unsigned long int s, en;
    unsigned long int prob_position = sup_data_prob_pos[ supervisor ];  /* Jump to the start position of the supervisor */
    for(s=0; s<state; s++){                                             /* Keep iterating until the state is reached */
        en            =  sup_data_prob[prob_position];                  /* The number of controllable events in the state */
        prob_position += en + 1;                                        /* Next controllable event's probability position */
    }
    return prob_position;
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

float get_active_controllable_events_prob( float *events ){
    unsigned char i,j;
    float count_actives = 0;

    /* Disable all non controllable events */
    for( i=0; i<NUM_EVENTS; i++ ){
        if( ev_controllable[i] ){
            events[i] = 1.0;
        } else {
            events[i] = 0;
        }
    }

    /* Check disabled events for all supervisors */
    for(i=0; i<NUM_SUPERVISORS; i++){
        unsigned long int position;
        unsigned char num_transitions;
        unsigned char ev_disable[NUM_EVENTS];
        unsigned long int position_prob;

        for( j=0; j<NUM_EVENTS; j++ ){
            if( sup_events[i][j] ){
                /* Unless this event has a transition in the current state, this event will be disabled*/
                ev_disable[j] = 1;
            } else {
                /*if supervisor don't have this event, it can't disable the event*/
                ev_disable[j] = 0;
            }
        }

        /*if supervisor have a transition with the event in the current state, it can't disable the event */
        position             = get_state_position(i, sup_current_state[i]); //Points to the byte that indicate the number of 3-bytes parts (each part describle one transition)
        position_prob        = get_state_position_prob(i, sup_current_state[i]); //Points to the first probability
        num_transitions      = sup_data[position];
        position++;
        position_prob++;

        while(num_transitions--){
            unsigned char event = sup_data[position];
            if( ev_controllable[ event ] && sup_events[i][ event ] ){
                ev_disable[ event ] = 0; /*Transition with this event, do not disable it, just calculate its probability contribution*/
                events[ event ] = events[ event ] * sup_data_prob[position_prob];

                position_prob++;
            }
            position += 3;
        }

        for( j=0; j<NUM_EVENTS; j++ ){
            if( ev_disable[j] == 1 ){
                events[ j ] = 0;
            }
        }
    }

    /* Sum the probabilities */
    for( j=0; j<NUM_EVENTS; j++ ){
        count_actives += events[ j ];
    }
    return count_actives;
}

/* IN_read */
unsigned char input_buffer[256];
unsigned char input_buffer_pnt_add = 0;
unsigned char input_buffer_pnt_get = 0;

unsigned char input_buffer_get( unsigned char *event ){
    if(input_buffer_pnt_add == input_buffer_pnt_get){
        return 0;
    } else {
        *event = input_buffer[ input_buffer_pnt_get ];
        input_buffer_pnt_get++;
        return 1;
    }
}

void input_buffer_add( unsigned char event ){
    input_buffer[ input_buffer_pnt_add ] = event;
    input_buffer_pnt_add++;
}

unsigned char input_buffer_check_empty(){
    return input_buffer_pnt_add == input_buffer_pnt_get;
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
        if( !ev_controllable[i]){
            if(  input_read( i ) ){
                if( !last_events[i] ){
                    input_buffer_add( i );
                    last_events[i] = 1;
                }
            } else {
                last_events[i] = 0;
            }
        }
    }
}

/*choices*/
unsigned char get_next_controllable(unsigned char *event){
    float events[NUM_EVENTS], random_sum = 0;

    unsigned char i;

    float prob_sum = get_active_controllable_events_prob(events);

    if (prob_sum > 0.0001){ /* If at least one event is enabled do */
        float random_value = (float) rand() / RAND_MAX * prob_sum; /* Pick a random index (event) */

        for (i = 0; i < NUM_EVENTS; i++){
            random_sum += events[i]; /* Add probability of each event until the random value is reached */
            if ( (random_value < random_sum) && ev_controllable[ i ] ){
                *event = i;
                return 1;
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
    //AUTOMATA PLAYER
    update_input();
    unsigned char event;
    while( input_buffer_get( &event ) ){//clear buffer, executing all no controllable events (NCE)
        make_transition( event );
        execCallback( event );
    }
    if( get_next_controllable( &event ) ){//find controllable event (CE)
        //if( input_buffer_check_empty() ){ //Only execute CE if NCE input buffer is empty
        make_transition( event );
        execCallback( event );
        //}
    }
}
