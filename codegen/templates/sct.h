#ifndef SCT_H
#define SCT_H

#include <stdlib.h>
#include <ctime>
#include <queue>
#include <map>
#include <functional>
#include <iostream>

/* Structure to store member functions */
struct Scallback {
    std::function<void(void* data)> callback;
    std::function<unsigned char(void* data)> check_input;
    void* data;
};

/****************************************/
/*                 SCT                  */
/****************************************/

class SCT {

public:

    /* Class constructor */
    SCT(const std::string& yaml_path);

    /* Class destructor */
    virtual ~SCT();

    /* Add callback function for a controllable event */
    template<typename Class>
    void add_callback(Class* p, std::string event, void (Class::*clbk)( void* ), void* empty_ci, void* data) {
        if (events.find(event) == events.end()) {
            std::cerr << "ERROR: encountered unknown event " << event << std::endl;
            exit(1);
        }
        using namespace std::placeholders; //for _1, _2, _3...
        callback[events[event]].callback    = std::bind(clbk, p, _1);
        callback[events[event]].check_input = nullptr;
        callback[events[event]].data        = data;
    }

    /* Add callback function for an uncontrollable event */
    template<typename Class>
    void add_callback(Class* p, std::string event, void* clbk, unsigned char (Class::*ci)( void* ), void* data) {
        if (events.find(event) == events.end()) {
            std::cerr << "ERROR: encountered unknown event " << event << std::endl;
            exit(1);
        }
        using namespace std::placeholders; //for _1, _2, _3...
        callback[events[event]].callback    = nullptr;
        callback[events[event]].check_input = std::bind(ci, p, _1);
        callback[events[event]].data        = data;
    }

    /* Add callback function for an uncontrollable event, while also triggering some robot function (e.g. turn LEDs on) */
    template<typename Class>
    void add_callback(Class* p, std::string event, void (Class::*clbk)( void* ), unsigned char (Class::*ci)( void* ), void* data) {            
        if (events.find(event) == events.end()) {
            std::cerr << "ERROR: encountered unknown event " << event << std::endl;
            exit(1);
        }
        using namespace std::placeholders; //for _1, _2, _3...
        callback[events[event]].callback    = std::bind(clbk, p, _1);
        callback[events[event]].check_input = std::bind(ci, p, _1);
        callback[events[event]].data        = data;
    }

    /* Run the generator player to execute the next action */
    virtual void run_step();

    virtual std::string get_current_state_string();

    /* Map used to convert an event name into its corresponding number */
    std::map<std::string, size_t> events;

protected:

    /* Return whether an uncontrollable event has occured */
    virtual unsigned char input_read( unsigned char ev );

    /* Add uncontrollable events that have occured to the buffer */
    virtual void update_input();

    /* Given the supervisor and its state, return the position of the current state in the data structure */
    virtual unsigned long int get_state_position( unsigned char supervisor, unsigned long int state );

    /* Apply the transition from current state */
    virtual void make_transition( unsigned char event );

    /* Execute callback function */
    virtual void exec_callback( unsigned char ev );

    /* Return a uncontrollale event from the input buffer */
    virtual unsigned char get_next_uncontrollable( unsigned char *event );

    /* Choose a controllale event from the list of enabled controllable events */ 
    virtual unsigned char get_next_controllable( unsigned char *event );

    /* Return all the enabled controllable events */
    virtual unsigned char get_active_controllable_events( unsigned char *events );

    /* Map of callback functions */
    std::map<unsigned char, Scallback> callback;

    /* Buffer to record the occurances of uncontrollable events */
    std::queue<unsigned char> input_buffer;

    /* Supervisors */
    size_t                           num_events;
    size_t                           num_supervisors;
    std::vector<size_t>              ev_controllable;
    std::vector<std::vector<size_t>> sup_events;
    std::vector<size_t>              sup_init_state;
    std::vector<size_t>              sup_current_state;
    std::vector<size_t>              sup_data_pos;
    std::vector<size_t>              sup_data;

};

/****************************************/
/*                SCTPub                */
/****************************************/

class SCTPub : virtual public SCT {

public:

    /* Class constructor */
    SCTPub(const std::string& yaml_path);

    /* Class destructor */
    virtual ~SCTPub();

    /* Run the generator player to execute the next action */
    virtual void run_step();

protected:

    /* Add uncontrollable events that have occured to the buffer */
    virtual void update_input();

    /* Return a public uncontrollale event from the input buffer */
    virtual unsigned char get_next_uncontrollable_pub( unsigned char *event );

    /* Buffer to store public uncontrollable events */
    std::queue<unsigned char> input_buffer_pub;

    /* Public event info of supervisors */
    std::vector<size_t> ev_public;

};

#endif