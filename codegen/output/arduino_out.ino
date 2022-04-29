#include generic_mic.h
const unsigned char ev_controllable[4] = {1, 0, 0, 0};
const unsigned char sup_events[2][4] = {{1, 0, 0, 1}, {1, 1, 1, 0}};
const unsigned long int sup_init_state[2] = {2, 2};
unsigned long int sup_current_state[2] = {2, 2};
const unsigned long int sup_data_pos[2] = {0, 1};
const unsigned char sup_data[42] = {2, EV_a, 0, 1, EV_y, 0, 0, 1, EV_y, 0, 2, 2, EV_a, 0, 0, EV_y, 0, 2, 3, EV_c, 0, 2, EV_a, 0, 2, EV_b, 0, 0, 2, EV_a, 0, 0, EV_b, 0, 1, 2, EV_a, 0, 1, EV_b, 0, 0};


void setup() {
}


void loop() {
}