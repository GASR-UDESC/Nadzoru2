#include generic_mic.h

{%- set n_events = events|count %}
{%- set n_automatons = automaton_list|count %}
{%- set n_data = data|count %}
const unsigned char ev_controllable[{{ n_events }}] = {{ ev_controllable }};
const unsigned char sup_events[{{ n_automatons }}][{{ n_events }}] = {{ sup_event_map }};
const unsigned long int sup_init_state[{{ n_automatons }}] = {{ sup_init_state }};
unsigned long int sup_current_state[{{ n_automatons }}] = {{ sup_current_state }};
const unsigned long int sup_data_pos[{{ n_automatons }}] = {{ sup_data_pos }};
const unsigned char sup_data[{{ n_data }}] = {{ sup_data }};


void setup() {
}


void loop() {
}
