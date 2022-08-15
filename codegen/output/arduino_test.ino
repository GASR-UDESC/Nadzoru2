
#define NUM_EVENTS 1
#define NUM_SUPERVISORS 1
#define EV_a 0


const unsigned char ev_controllable[1] = {0};
const unsigned char sup_events[1][1] = {{1}};
const unsigned long int sup_init_state[1] = {1};
unsigned long int sup_current_state[1] = {1};
const unsigned long int sup_data_pos[1] = {0};
const unsigned char sup_data[8] = {1, EV_a, 0, 1, 1, EV_a, 0, 0};
bool state = false;
bool state2 = false;
unsigned long counter = 0;

unsigned long previousMillis = 0;

void setup() {
    Serial.begin(115200);
    set_timer2_frequency(10000);
    pinMode(A1, INPUT);
    pinMode(10, OUTPUT);
    pinMode(11, OUTPUT);
    digitalWrite(10, state);
    digitalWrite(11, state2);
}

unsigned long int get_state_position(unsigned char supervisor, unsigned long int state){
    unsigned long int position;
    unsigned long int s;
    unsigned char en;
    position = sup_data_pos[supervisor];
    for(s=0; s<state; s++){
        en = sup_data[position];
        position += en*3 + 1;
    }
    return position;
}

void make_transition(unsigned char event){
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
                    sup_current_state[i] = ((unsigned long int)sup_data[position + 1])*256 + ((unsigned long int)sup_data[position + 2]);
                    break;
                }
                position += 3;
            }
        }
    }
}



/* IN_read */
unsigned char input_buffer[256];
unsigned char input_buffer_pnt_add = 0;
unsigned char input_buffer_pnt_get = 0;

unsigned char input_buffer_get(unsigned char *event){
    if(input_buffer_pnt_add == input_buffer_pnt_get){
        return 0;
    } else {
        *event = input_buffer[ input_buffer_pnt_get ];
        input_buffer_pnt_get++;
        return 1;
    }
}

void input_buffer_add(unsigned char event){
    input_buffer[input_buffer_pnt_add] = event;
    input_buffer_pnt_add++;
}

unsigned char input_buffer_check_empty(  ){
    return input_buffer_pnt_add == input_buffer_pnt_get;
}


unsigned char input_read_a(){
    // type your code for inputs
    if (digitalRead(A1)){
      return 0;
    }else {
      return 1;
    }

}
    

unsigned char input_read(unsigned char ev){
    unsigned char result = 0;
    switch(ev){
        case EV_a:
            result = input_read_a();
            break;}
    return result;
}
void callback_a(){
    Serial.println("callback_a");
    state = !state;
    digitalWrite(11, state);
    
}


void callback(char ev){
    Serial.println("callback");
    switch(ev){
        case EV_a:
            callback_a();
              
            break;
        }
}



void get_active_controllable_events(unsigned char *events){
    unsigned char i, j;

    /* Disable all non controllable events */
    for (i = 0; i < NUM_EVENTS; i++)
    {
        if (!ev_controllable[i])
        {
            events[i] = 0;
        }
    }

    /* Check disabled events for all supervisors */
    for (i = 0; i < NUM_SUPERVISORS; i++){
        unsigned long int position;
        unsigned char ev_disable[NUM_EVENTS], k;
        unsigned char num_transitions;
        for (k = 0; k < NUM_EVENTS; k++){
            ev_disable[k] = 1;
        }
        for (j = 0; j < NUM_EVENTS; j++){

            /*if supervisor don't have this event, it can't disable the event*/
            if (!sup_events[i][j]){
                ev_disable[j] = 0;
            }
        }
        /*if supervisor have a transition with the event in the current state, it can't disable the event */
        position = get_state_position(i, sup_current_state[i]);
        num_transitions = sup_data[position];
        position++;
        while (num_transitions--){
            ev_disable[sup_data[position]] = 0;
            position += ((unsigned long int)3);
        }

        /* Disable for current supervisor states */
        for(j=0; j<NUM_EVENTS; j++){
            if(ev_disable[j] == 1){
                events[j] = 0;
            }
        }
    }
}

/*choices*/
unsigned char last_events[1] = {0};
unsigned char get_next_controllable(unsigned char *event){
    unsigned char events[1] = {1};

    int count_actives, random_pos;
    unsigned char i;

    get_active_controllable_events(events);
    count_actives = 0;
    for (i = 0; i < 1; i++){
        if (events[i]){
            count_actives++;
        }
    }
    if (count_actives){
        random_pos = randomChar() % count_actives;
        for (i = 0; i < 1; i++){
            if (!random_pos && events[i]){
                *event = i;
                return 1;
            } else if (events[i]){
                random_pos--;
            }
        }
    }
    return 0;
}




unsigned char randomChar(){
    return random(255);
}



void loop() {
    
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= 10){
        previousMillis = currentMillis;
        unsigned char event;
        // clear buffer, executing all no controllable events
        while (input_buffer_get(&event))
        {
            Serial.println("input_buffer_get");
            make_transition(event);
            callback(event);
            
        }
        if (get_next_controllable(&event))
        {
          Serial.println("get_next_controlable");
            if (!input_buffer_check_empty())
              Serial.println("buffer_check_empty");
            make_transition(event);
            callback(event);
        }
    }
}





void set_timer2_frequency(unsigned long frequency){
    TCCR2A = 0;// set entire TCCR2A register to 0
    TCCR2B = 0;// same for TCCR2B
    TCNT2  = 0;//initialize counter value to 0

    unsigned long prescaler = 64;
    /*  set a prescaler value so that MAX(OCR2A)=255 for your desired frequency     *
     *  for prescaler = 64 && OCR2A = 1     -> frequency = 250 001 kHz              *
     *      prescaler = 64 && OCR2A = 255   -> frequency = 981 Hz                   */
    OCR2A = (F_CPU/(prescaler*frequency)) - 1;
    TCCR2A |= (1 << WGM21);
    Serial.print("OCR2A: ");
    Serial.println(OCR2A);
    switch (prescaler){
        case 1:
            TCCR2B |= (1 << CS20);
            break;
        case 8:
            TCCR2B |= (1 << CS21);
            break;
        case 32:
            TCCR2B |= (1 << CS22) | (1 << CS21);  
            break;
        case 64:
            TCCR2B |= (1 << CS22);
            Serial.print("TCCR2B: ");
            Serial.println(TCCR2B);
            break;
    }
    TIMSK2 |= (1 << OCIE2A);
}

ISR(TIMER2_COMPA_vect){
    //noInterrupts();
    unsigned char i;
    counter++;
    if(counter == 1000){
      counter = 0;
      state = !state;
      digitalWrite(10, state);
    }
    for(i = 0; i < NUM_EVENTS; i++){
        if(!ev_controllable[i]){
            if (input_read (i)){
                if(!last_events[i]){
                        input_buffer_add(i);
                        last_events[i] = 1;
                }
            } else {
                last_events[i] = 0;
            }
        }
   }
    //interrupts();
}
