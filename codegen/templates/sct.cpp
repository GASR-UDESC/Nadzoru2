#include "sct.h"
#include "yaml-cpp/yaml.h"

bool isNumber(const std::string& str)
{
    return str.find_first_not_of("0123456789") == std::string::npos;
}

/****************************************/
/*                 SCT                  */
/****************************************/

SCT::SCT(const std::string& yaml_path){

    srand((unsigned) time(NULL));

    /* Load SCT from YAML file */
    YAML::Node node = YAML::LoadFile(yaml_path);

    num_events        = node["num_events"].as<size_t>();
    num_supervisors   = node["num_supervisors"].as<size_t>();
    ev_controllable   = node["ev_controllable"].as<std::vector<size_t>>();
    sup_events        = node["sup_events"].as<std::vector<std::vector<size_t>>>();
    sup_init_state    = node["sup_init_state"].as<std::vector<size_t>>();
    sup_current_state = node["sup_current_state"].as<std::vector<size_t>>();
    sup_data_pos      = node["sup_data_pos"].as<std::vector<size_t>>();

    std::vector<std::string> event_strings = node["events"].as<std::vector<std::string>>();
    std::vector<std::string> data          = node["sup_data"].as<std::vector<std::string>>();

    /* Convert event names into corresponding numbers */
    for(size_t i = 0; i < event_strings.size(); i++)
        events[event_strings[i]] = i;

    for(const auto& val : data) {
        if(isNumber(val))
            sup_data.push_back(stoi(val));
        else
            sup_data.push_back(events[val]);    
    }

    // std::cout << yaml_path << std::endl;
    // std::cout << "num_events " << num_events << std::endl;
    // std::cout << "num_supervisors " << num_supervisors << std::endl;
    // for(const auto& ev : event_strings)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : ev_controllable)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : sup_events) {
    //     for (const auto& ev2 : ev)
    //         std::cout << ev2 << std::endl;
    //     std::cout << std::endl;
    // }
    // for(const auto& ev : sup_init_state)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : sup_current_state)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : sup_data_pos)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : data)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
    // for(const auto& ev : sup_data)
    //     std::cout << ev << std::endl;
    // std::cout << std::endl;
}

SCT::~SCT(){}

void SCT::run_step(){
    update_input(); // Get all uncontrollable events
    unsigned char event;

    /* Apply all the uncontrollable events */
    while ( get_next_uncontrollable( &event ) ){
        make_transition( event );
        exec_callback( event );
    }

    /* Apply the chosen controllable event */
    if( get_next_controllable( &event ) ){  /* Find and pick a controllable event (CE) */
        make_transition( event );
        exec_callback( event );
    }
}

std::string SCT::get_current_state_string() {
    std::ostringstream stream;
    stream.str("");
    stream << "sup:[";
    for(size_t i = 0; i < num_supervisors; i++) {
        stream << (int) sup_current_state[i]+1;
        if(i < num_supervisors - 1)
            stream << ",";
    }
    stream << "]";

    return stream.str();
}

unsigned char SCT::input_read( unsigned char ev ){
    if( ev < num_events && callback[ ev ].check_input != NULL )
        return callback[ ev ].check_input( callback[ ev ].data );
    return 0;
}

void SCT::update_input(){
    unsigned char i;
    for(i=0;i<num_events;i++){
        if( !ev_controllable[i] ){   /* Check the UCEs only */
            if( input_read( i ) ){
                input_buffer.push(i);
            }
        }
    }
}

unsigned long int SCT::get_state_position( unsigned char supervisor, unsigned long int state ){
    unsigned long int position;
    unsigned long int s;
    unsigned long int en;
    position = sup_data_pos[ supervisor ];  /* Jump to the start position of the supervisor */
    for(s=0; s<state; s++){                 /* Keep iterating until the state is reached */
        en       = sup_data[position];      /* The number of transitions in the state */
        position += en * 3 + 1;             /* Next state position (Number transitions * 3 + 1) */
    }
    return position;
}

void SCT::make_transition( unsigned char event ){
    unsigned char i;
    unsigned long int position;
    unsigned char num_transitions;

    /* Apply transition to each local supervisor */
    for(i=0; i<num_supervisors; i++){
        if(sup_events[i][event]){   /* Check if the given event is part of this supervisor */
            
            /* Current state info of supervisor */
            position        = get_state_position(i, sup_current_state[i]);
            num_transitions = sup_data[position];
            position++; /* Point to first transition */

            /* Find the transition for the given event */
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

void SCT::exec_callback( unsigned char ev ){
    if( ev < num_events && callback[ ev ].callback != NULL )
        callback[ ev ].callback( callback[ ev ].data );
}

unsigned char SCT::get_next_uncontrollable( unsigned char *event ){
    if( !input_buffer.empty() ) {
        *event = input_buffer.front();
        input_buffer.pop();
        return 1;
    }
    return 0;
}

unsigned char SCT::get_next_controllable( unsigned char *event ){
    unsigned char events[num_events], i, count_actives;
    unsigned long int random_pos;
    
    /* Get controllable events that are enabled -> events */
    count_actives = get_active_controllable_events( events );

    // DEBUG
    // std::cout << "count_actives: " << std::to_string(count_actives) << std::endl;
    // for(i = 0; i < num_events; i++) {
    //     if(events[i]) {
    //         std::cout << "event: " << std::to_string(i) << " active" << std::endl;
    //     }
    // }
    // DEBUG END

    if( count_actives ){                        /* If at least one event is enabled do */
        random_pos = rand() % count_actives;    /* Pick a random index (event) */
        for(i=0; i<num_events; i++){
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

unsigned char SCT::get_active_controllable_events( unsigned char *events ){
    unsigned char i,j;
    unsigned char count_actives = 0;

    /* Disable all non controllable events */
    for( i=0; i<num_events; i++ ){
        if( !ev_controllable[i] ){
            events[i] = 0;
        } else {
            events[i] = 1;
            count_actives++;
        }
    }

    /* Check if a controllable event is disabled in any of the supervisors */
    for(i=0; i<num_supervisors; i++){
        unsigned long int position;
        unsigned char ev_disable[num_events], k;
        unsigned char num_transitions;

        /* Init an array where all events are disabled */
        for(k=0; k < num_events;k++){
            ev_disable[k] = 1;  
        }

        /* Enable all events that are not part of this supervisor */
        for( j=0; j < num_events; j++ ){
            if( !sup_events[i][j] ){
                ev_disable[j] = 0;
            }
        }

        /* Get current state */
        position = get_state_position(i, sup_current_state[i]);
        num_transitions = sup_data[position];
        position++;

        /* Enable all events that have a transition from the current state */
        while(num_transitions--){
            ev_disable[ sup_data[position] ] = 0;
            position += 3;
        }

        /* Remove the controllable events to disable, leaving an array of enabled controllable events */
        for( j=0; j<num_events; j++ ){
            if( ev_disable[j] == 1 && events[ j ] ){
                events[ j ] = 0;
                count_actives--;
            }
        }
    }
    
    return count_actives;
}

/****************************************/
/*                SCTPub                */
/****************************************/

SCTPub::SCTPub(const std::string& yaml_path) : SCT(yaml_path) {
    YAML::Node node = YAML::LoadFile(yaml_path);
    ev_shared = node["ev_shared"].as<std::vector<size_t>>();

    // for(const auto& ev : ev_shared)
    //     std::cout << ev << std::endl;
}

SCTPub::~SCTPub(){}

void SCTPub::run_step() {
    update_input(); // Get all uncontrollable events
    unsigned char event;

    /* Apply all public uncontrollable events */
    while ( get_next_uncontrollable_pub( &event ) ){
        make_transition( event );
        exec_callback( event );
    }

    /* Apply all private uncontrollable events */
    while ( get_next_uncontrollable( &event ) ){
        make_transition( event );
        exec_callback( event );
    }

    /* Apply the chosen controllable event */
    if( get_next_controllable( &event ) ){  /* Find and pick a controllable event (CE) */
        make_transition( event );
        exec_callback( event );
    }
}

void SCTPub::update_input(){
    unsigned char i;
    for(i=0;i<num_events;i++){
        if( !ev_controllable[i] ){  /* Check the UCEs only */
            if( input_read( i ) ){
                if( ev_shared[i] ){ /* Check whether the UCE is public or private */
                    input_buffer_pub.push(i);
                } else {
                    input_buffer.push(i);
                }
            }
        }
    }
}

unsigned char SCTPub::get_next_uncontrollable_pub( unsigned char *event ){
    if( !input_buffer_pub.empty() ) {
        *event = input_buffer_pub.front();
        input_buffer_pub.pop();
        return 1;
    }
    return 0;
}
