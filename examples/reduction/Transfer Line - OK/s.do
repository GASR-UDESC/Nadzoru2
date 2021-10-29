digraph finite_state_machine { 

	rankdir=LR; 
	node [shape = box, height = .001, width = .001, color = white, fontcolor = white, fontsize = 1]; 
	start;
	node [shape = doublecircle, color = black, fontcolor = black, fontsize = 18]; 
	0 2 5 9 10 13 17 18 21 24 ;
	node [shape = circle, color = black, fontcolor = black, fontsize = 18]; 
	1 3 4 6 7 8 11 12 14 15 16 19 20 22 23 ;
	start -> 0
	0 -> 1 [ label = "1", fontsize = 18];
	1 -> 2 [ label = "2", fontsize = 18];
	2 -> 3 [ label = "3", fontsize = 18];
	3 -> 4 [ label = "1", fontsize = 18];
	3 -> 5 [ label = "4", fontsize = 18];
	4 -> 6 [ label = "2", fontsize = 18];
	4 -> 7 [ label = "4", fontsize = 18];
	5 -> 7 [ label = "1", fontsize = 18];
	5 -> 8 [ label = "5", fontsize = 18];
	6 -> 9 [ label = "4", fontsize = 18];
	7 -> 9 [ label = "2", fontsize = 18];
	8 -> 0 [ label = "6", fontsize = 18];
	8 -> 10 [ label = "8", fontsize = 18];
	10 -> 11 [ label = "3", fontsize = 18];
	11 -> 12 [ label = "1", fontsize = 18];
	11 -> 13 [ label = "4", fontsize = 18];
	12 -> 14 [ label = "2", fontsize = 18];
	12 -> 15 [ label = "4", fontsize = 18];
	13 -> 15 [ label = "1", fontsize = 18];
	13 -> 16 [ label = "5", fontsize = 18];
	14 -> 17 [ label = "4", fontsize = 18];
	15 -> 17 [ label = "2", fontsize = 18];
	16 -> 0 [ label = "6", fontsize = 18];
	16 -> 18 [ label = "8", fontsize = 18];
	18 -> 19 [ label = "3", fontsize = 18];
	19 -> 20 [ label = "1", fontsize = 18];
	19 -> 21 [ label = "4", fontsize = 18];
	20 -> 22 [ label = "2", fontsize = 18];
	20 -> 23 [ label = "4", fontsize = 18];
	21 -> 23 [ label = "1", fontsize = 18];
	22 -> 24 [ label = "4", fontsize = 18];
	23 -> 24 [ label = "2", fontsize = 18];
}
