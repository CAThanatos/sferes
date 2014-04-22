args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
min <- as.integer(args[2])
max <- as.integer(args[3])

cpt <- 1;
color <- rainbow(11);

# Ratio
output <- sprintf("preysRatioHaresSStags.png");
png(output);
while(cpt <= nbFiles) {
	filename = sprintf("refactDataRatio_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);

	if(cpt == 1)
	{
		plot(graph$Evaluation, graph$RatioHares, type="l", main="Ratio of stags and hares hunted", xlab="Evaluations", ylab="Ratio", ylim=c(0,1));
		lines(graph$Evaluation, graph$RatioHares, col="firebrick1");
	}
	else
	{
		lines(graph$Evaluation, graph$RatioHares, col="firebrick1");
	}

	lines(graph$Evaluation, graph$RatioSStags, col="dodgerblue1");

	legend("topleft", c("Hares","Stags"),fill=c("firebrick1","dodgerblue1"));

	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# NbStagsSolo
output <- sprintf("preysStags.png");
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
			plot(graph$Evaluation, graph$NbSStags, type="l", main="Number of stags hunted", xlab="Evaluations", ylab="Number of stags");
		}
		else {
			plot(graph$Evaluation, graph$NbSStags, type="l", main="Number of stags hunted", xlab="Evaluations", ylab="Number of stags", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbSStags, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbSStags, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# Ratio
output <- sprintf("preysHares.png");
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
			plot(graph$Evaluation, graph$NbHares, type="l", main="Number of hares hunted", xlab="Evaluations", ylab="Number of hares");
		}
		else {
			plot(graph$Evaluation, graph$NbHares, type="l", main="Number of hares hunted", xlab="Evaluations", ylab="Number of hares", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbHares, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbHares, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();
