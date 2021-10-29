digraph finite_state_machine { 

	rankdir=LR; 
	node [shape = box, height = .001, width = .001, color = white, fontcolor = white, fontsize = 1]; 
	start;
	node [shape = doublecircle, color = black, fontcolor = black, fontsize = 18]; 
	0 1 2 4 5 7 8 9 ;
	node [shape = circle, color = black, fontcolor = black, fontsize = 18]; 
	3 6 ;
	start -> 0
	0 -> 6 [ label = "1", fontsize = 18];
	0 -> 5 [ label = "2", fontsize = 18];
	0 -> 1 [ label = "4", fontsize = 18];
	1 -> 9 [ label = "1", fontsize = 18];
	1 -> 9 [ label = "5", fontsize = 18];
	2 -> 3 [ label = "3", fontsize = 18];
	3 -> 6 [ label = "1", fontsize = 18];
	3 -> 4 [ label = "4", fontsize = 18];
	4 -> 9 [ label = "1", fontsize = 18];
	4 -> 6 [ label = "5", fontsize = 18];
	5 -> 0 [ label = "3", fontsize = 18];
	5 -> 9 [ label = "4", fontsize = 18];
	6 -> 5 [ label = "2", fontsize = 18];
	6 -> 9 [ label = "4", fontsize = 18];
	6 -> 0 [ label = "6", fontsize = 18];
	6 -> 7 [ label = "8", fontsize = 18];
	7 -> 8 [ label = "3", fontsize = 18];
	8 -> 9 [ label = "1", fontsize = 18];
	8 -> 8 [ label = "4", fontsize = 18];
	9 -> 9 [ label = "2", fontsize = 18];
	9 -> 9 [ label = "4", fontsize = 18];
	9 -> 0 [ label = "6", fontsize = 18];
	9 -> 2 [ label = "8", fontsize = 18];
}
