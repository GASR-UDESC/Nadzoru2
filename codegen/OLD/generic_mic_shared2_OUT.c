#include "generic_mic_shared2.h"
#include <shefpuck/router_bt.h>

    const unsigned char     ev_shared[8] = { 0,0,0,0,1,1,0,0 };
    const unsigned char     ev_controllable[8] = { 1,1,1,1,0,0,1,0 };
    const unsigned char     sup_events[4][8] = { { 1,1,1,1,0,0,0,0 },{ 1,1,0,0,1,1,0,0 },{ 0,0,1,1,0,0,1,1 },{ 1,1,1,1,1,1,0,0 } };
    const unsigned long int sup_init_state[4]     = { 0,0,0,0 };
    unsigned long int       sup_current_state[4]  = { 0,0,0,0 };
    const unsigned long int sup_data_pos[4] = { 0,20,40,55 };
    const unsigned char     sup_data[ 113 ] = { 3,EV_onLoffR,0,0,EV_rR,0,1,EV_rL,0,0,3,EV_onRoffL,0,1,EV_rR,0,1,EV_rL,0,0,3,EV_onLoffR,0,0,EV__rL,0,1,EV__rR,0,0,3,EV__rL,0,1,EV_onRoffL,0,1,EV__rR,0,0,1,EV_tstart,0,1,1,EV_tout,0,2,2,EV_rR,0,0,EV_rL,0,0,4,EV__rL,0,1,EV_rL,0,2,EV__rR,0,1,EV_rR,0,2,4,EV__rL,0,1,EV_rL,0,3,EV__rR,0,1,EV_rR,0,3,4,EV__rL,0,3,EV_rL,0,2,EV__rR,0,3,EV_rR,0,2,6,EV__rL,0,3,EV_rL,0,3,EV_onLoffR,0,3,EV__rR,0,3,EV_rR,0,3,EV_onRoffL,0,3 };



typedef struct Scallback {
    void (*callback)( void* data );
    unsigned char (*check_input) ( void* data );
    void* data;
    unsigned char globalMap;
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

void sendSharedEvent( unsigned char event ){
    if( ev_shared[event] ){
        if( !rbt_is_sending() ){
            RBTMsg msg;
            char data[2];
            data[0] = 'E';
            data[1] = (char) event;
            rbt_msg_set_command( &msg, "brod" );
            rbt_msg_set_source( &msg, "0000" );
            rbt_msg_set_data( &msg, data, 2 );
            rbt_send( &msg );
        }
    }
}

void sendMapSharedEvent( unsigned char controllable_event ){
    if( callback[ controllable_event ].globalMap != 255 ){
        sendSharedEvent( callback[ controllable_event ].globalMap );//use the mapped event, which must be global (shared)
    }
}

/*returns 1 if nw event, 0 otherwise*/
int getSharedEvent( unsigned char *event ){
    if( !rbt_msg_empty() ){
        RBTMsg msg;
        rbt_msg_pop_back( &msg );
        if( msg.data[0] == 'E' ){
            *event = (unsigned char) msg.data[1];
            return 1;
        }
    }
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
        callback[ event ].globalMap   = 255; //NULL FLAG
}

void SCT_add_global_map( unsigned char controllable_event, unsigned char uncontrollable_event ){
    callback[ controllable_event ].globalMap = uncontrollable_event;
}

void SCT_run_step(){
    //AUTOMATA PLAYER
    update_input();
    rbt_update();
    unsigned char event;
    while( getSharedEvent( &event ) ){
        make_transition( event );
        execCallback( event );
    }
    while( input_buffer_get( &event ) ){//clear buffer, executing all no controllable events (NCE)
        make_transition( event );
        execCallback( event );
        sendSharedEvent( event ); //SEND EVENT
        rbt_update();
    }
    if( get_next_controllable( &event ) ){//find controllable event (CE)
        //if( input_buffer_check_empty() ){ //Only execute CE if NCE input buffer is empty
        make_transition( event );
        execCallback( event );
        sendMapSharedEvent( event ); //SEND EVENT
        rbt_update();
        //}
    }
    //rbt_update();
}
