param clients integer;
param equipments integer;
param coverdist integer;

set I := 1..clients by 1;

param weights{I};
param populations{I};

param a{I,I};

var y{I} binary;
var x{I} binary;

maximize z: sum{i in I} weights[i]*populations[i]*y[i];

subject to covering{i in I}:
	sum{j in I} a[i,j]*x[j] >= y[i];
	
subject to nequip:
	sum{j in I} x[j]=equipments;
	



