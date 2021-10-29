digraph finite_state_machine { 

	rankdir=LR; 
	node [shape = box, height = .001, width = .001, color = white, fontcolor = white, fontsize = 1]; 
	start;
	node [shape = doublecircle, color = black, fontcolor = black, fontsize = 18]; 
	0 ;
	node [shape = circle, color = black, fontcolor = black, fontsize = 18]; 
	1 ;
	start -> 0
	0 -> 1 [ label = "3", fontsize = 18];
	1 -> 0 [ label = "4", fontsize = 18];
}
