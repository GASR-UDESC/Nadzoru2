digraph finite_state_machine { 

	rankdir=LR; 
	node [shape = box, height = .001, width = .001, color = white, fontcolor = white, fontsize = 1]; 
	start;
	node [shape = doublecircle, color = black, fontcolor = black, fontsize = 18]; 
	0 1 2 ;
	start -> 0
	0 -> 0 [ label = "6", fontsize = 18];
	0 -> 1 [ label = "8", fontsize = 18];
	1 -> 0 [ label = "6", fontsize = 18];
	1 -> 2 [ label = "8", fontsize = 18];
}
