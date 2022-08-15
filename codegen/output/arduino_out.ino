#include generic_mic.h
const unsigned char ev_controllable[2] = {1, 0};
const unsigned char sup_events[1][2] = {{1, 1}};
const unsigned long int sup_init_state[1] = {1};
unsigned long int sup_current_state[1] = {1};
const unsigned long int sup_data_pos[1] = {0};
const unsigned char sup_data[18] = {2, EV_x, 0, 2, EV_y, 0, 0, 2, EV_x, 0, 0, EV_y, 0, 1, 1, EV_y, 0, 1};


void setup() {
}


void loop() {
}