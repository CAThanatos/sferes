args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
min <- as.integer(args[2])
max <- as.integer(args[3])

cpt <- 1;
color <- rainbow(11);

# Ratio
output <- sprintf("preysRatioHaresBtags.png");
png(output);
while(cpt <= nbFiles) {
	filename = sprintf("refactDataRatio_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);
	
	if(cpt == 1)
	{
		plot(graph$Evaluation, graph$RatioBStags, type="l", main="Ratio of hares and big stags hunted", xlab="Evaluations", ylab="Ratio", ylim=c(0,1));
		lines(graph$Evaluation, graph$RatioBStags, col="firebrick1");
	}
	else
	{
		lines(graph$Evaluation, graph$RatioBStags, col="firebrick1");
	}

	lines(graph$Evaluation, graph$RatioHares, col="dodgerblue1");

	legend("topleft", c("Big stags","hares"),fill=c("firebrick1","dodgerblue1"));

	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# NbStagsCoop
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

# Ratio
output <- sprintf("preysBStags.png");
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
			plot(graph$Evaluation, graph$NbBStags, type="l", main="Number of big stags hunted", xlab="Evaluations", ylab="Number of big stags");
		}
		else {
			plot(graph$Evaluation, graph$NbBStags, type="l", main="Number of big stags hunted", xlab="Evaluations", ylab="Number of big stags", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbBStags, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbBStags, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();
