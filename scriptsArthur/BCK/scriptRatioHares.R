args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
min <- as.integer(args[2])
max <- as.integer(args[3])

cpt <- 1;
color <- rainbow(11);

# Ratio
output <- sprintf("preysRatioHares.png");
png(output);
while(cpt <= nbFiles) {
	filename = sprintf("refactDataRatio_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);

	if(cpt == 1)
	{
		plot(graph$Evaluation, graph$RatioHaresSolo, type="l", main="Ratio of hares hunted", xlab="Evaluations", ylab="Ratio", ylim=c(0,1));
		lines(graph$Evaluation, graph$RatioHaresSolo, col="firebrick1");
	}
	else
	{
		lines(graph$Evaluation, graph$RatioHaresSolo, col="firebrick1");
	}

	lines(graph$Evaluation, graph$RatioHaresDuo, col="dodgerblue1");

	legend("topleft", c("Hares solo","Hares duo"),fill=c("firebrick1","dodgerblue1"));

	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# NbStagsSolo
output <- sprintf("preysHaresSolo.png");
png(output);
cpt <- 1;
while(cpt <= nbFiles) {
	filename = sprintf("refactData_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);

	if(cpt == 1)
	{
		if(min == -1) {
			plot(graph$Evaluation, graph$NbHaresSolo, type="l", main="Number of hares hunted solo", xlab="Evaluations", ylab="Number of hares");
		}
		else {
			plot(graph$Evaluation, graph$NbHaresSolo, type="l", main="Number of hares hunted solo", xlab="Evaluations", ylab="Number of agres", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbHaresSolo, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbHaresSolo, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# Ratio
output <- sprintf("preysHaresDuo.png");
png(output);
cpt <- 1;
while(cpt <= nbFiles) {
	filename = sprintf("refactData_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);

	if(cpt == 1)
	{
		if(min == -1) {
			plot(graph$Evaluation, graph$NbHaresDuo, type="l", main="Number of hares hunted coop", xlab="Evaluations", ylab="Number of hares");
		}
		else {
			plot(graph$Evaluation, graph$NbHaresDuo, type="l", main="Number of hares hunted coop", xlab="Evaluations", ylab="Number of hares", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbHaresDuo, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbHaresDuo, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();
