digraph finite_state_machine { 

	rankdir=LR; 
	node [shape = box, height = .001, width = .001, color = white, fontcolor = white, fontsize = 1]; 
	start;
	node [shape = doublecircle, color = black, fontcolor = black, fontsize = 18]; 
	0 1 2 3 4 6 7 8 9 ;
	node [shape = circle, color = black, fontcolor = black, fontsize = 18]; 
	5 ;
	start -> 0
	0 -> 8 [ label = "1", fontsize = 18];
	0 -> 6 [ label = "2", fontsize = 18];
	0 -> 1 [ label = "4", fontsize = 18];
	1 -> 7 [ label = "1", fontsize = 18];
	1 -> 8 [ label = "5", fontsize = 18];
	2 -> 7 [ label = "3", fontsize = 18];
	3 -> 7 [ label = "1", fontsize = 18];
	3 -> 9 [ label = "5", fontsize = 18];
	4 -> 5 [ label = "3", fontsize = 18];
	5 -> 8 [ label = "1", fontsize = 18];
	5 -> 7 [ label = "4", fontsize = 18];
	6 -> 0 [ label = "3", fontsize = 18];
	6 -> 8 [ label = "4", fontsize = 18];
	7 -> 9 [ label = "1", fontsize = 18];
	7 -> 8 [ label = "2", fontsize = 18];
	7 -> 3 [ label = "4", fontsize = 18];
	8 -> 6 [ label = "2", fontsize = 18];
	8 -> 9 [ label = "4", fontsize = 18];
	8 -> 0 [ label = "6", fontsize = 18];
	8 -> 2 [ label = "8", fontsize = 18];
	9 -> 8 [ label = "2", fontsize = 18];
	9 -> 7 [ label = "4", fontsize = 18];
	9 -> 0 [ label = "6", fontsize = 18];
	9 -> 4 [ label = "8", fontsize = 18];
}
