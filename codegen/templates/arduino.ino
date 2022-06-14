#include <Arduino.h>
#include generic_mic.h

{%- set n_events = events|count %}
{%- set n_automatons = automaton_list|count %}
{%- set n_data = data|count %}
#define NUM_EVENTS {{ n_events }}
#define NUM_SUPERVISORS {{ n_automatons }}
{%- for event in events %}
#define EV_{{event.name}} {{loop.index-1}}
{%- endfor %}


const unsigned char ev_controllable[{{ n_events }}] = {{ ev_controllable }};
const unsigned char sup_events[{{ n_automatons }}][{{ n_events }}] = {{ sup_event_map }};
const unsigned long int sup_init_state[{{ n_automatons }}] = {{ sup_init_state }};
unsigned long int sup_current_state[{{ n_automatons }}] = {{ sup_current_state }};
const unsigned long int sup_data_pos[{{ n_automatons }}] = {{ sup_data_pos }};
const unsigned char sup_data[{{ n_data }}] = {{ sup_data }};

unsigned long previousMillis = 0;

void setup() {
{# CHOICE: input method -#}
{% if input_fn  == generator.INPUT_MULTIPLEXED %} {# attachInterrupt(digitalPinToInterrupt(pin), interrupt_service_routine, mode) #}
    pinMode(ext_int_pin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ext_int_pin), ext_int, RISING );
{% elif input_fn  == generator.INPUT_TIMER %}
    set_timer2_frequency(1000);
{% endif -%}

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

{% for event in events -%}
    {%if not event.controllable%}
unsigned char input_read_{{ event.name }}(){
    // type your code for inputs
    return 0;
}
    {% endif %}
{%- endfor %}

unsigned char input_read(unsigned char ev){
    unsigned char result = 0;
    switch(ev){
    {%- for event in events -%}
        {%- if not event.controllable %}
        case EV_{{ event.name }}:
            result = input_read_{{ event.name }}();
            break;
        {%- endif -%}
    {%- endfor -%}
    }
    return result;
}

{%- for event in events %}
void callback_{{ event.name }}(){
    // type your code here
}
{% endfor %}

void callback(char ev){
    switch(ev){
        {% for event in events -%}
        case EV_{{ event.name }}:
            callback_{{ event.name }}();
            break;
        {% endfor -%}
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
unsigned char last_events[{{ n_events }}] = {{"{"}}{% for event in events %}0{{", " if not loop.last else""}}{%endfor%}};
unsigned char get_next_controllable(unsigned char *event){
    unsigned char events[{{ n_events }}] = {{"{"}}{% for event in events %}1{{", " if not loop.last else""}}{%endfor%}};

    int count_actives, random_pos;
    unsigned char i;

    get_active_controllable_events(events);
    count_actives = 0;
    for (i = 0; i < {{n_events}}; i++){
        if (events[i]){
            count_actives++;
        }
    }
    if (count_actives){
        random_pos = randomChar() % count_actives;
        for (i = 0; i < {{n_events}}; i++){
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


{# CHOICE: random number generator #}
{% if random_fn == generator.RANDOM_PSEUDOFIX %}
unsigned char randomChar(){
    return random(255);
}
{% elif random_fn == generator.RANDOM_PSEUDOAD %}
unsigned char seed_uses = 0;
unsigned char randomChar(){
    seed_uses++;
    if (seed_uses == 255){
        seed_uses = 0;
        randomSeed(analogRead({{ad_port}}))
    }
    return random(255);
}
{% elif random_fn == generator.RANDOM_AD %}
unsigned char randomChar(){
   return analogRead({{ad_port}})
}
{% elif random_fn == generator.RANDOM_PSEUDOTIME %}
unsigned char seed_uses = 0;
unsigned char randomChar(){
    seed_uses++;
    if (seed_uses == 255){
        seed_uses = 0;
        randomSeed(micros());
    }
    return random(255);
}
{% endif %}


void loop() {
    
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= 100){
        previousMillis = currentMillis;
         
        unsigned char event;
        // clear buffer, executing all no controllable events
        while (input_buffer_get(&event))
        {
            make_transition(event);
            callback(event);
        }
        if (get_next_controllable(&event))
        {
            if (!input_buffer_check_empty())
                return;
            make_transition(event);
            callback(event);
        }
    }
}



{# CHOICE: input method #}
{% if input_fn == generator.INPUT_TIMER %}
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
            break;
    }
    TIMSK2 |= (1 << OCIE2A);
}

ISR(TIMER2_COMPA_vect){
    //noInterrupts();
    unsigned char i;
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
{% elif input_fn  == generator.INPUT_MULTIPLEXED %}
void ext_int(){
    unsigned char i;
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
}
{% endif %}