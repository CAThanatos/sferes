args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
min <- as.integer(args[2])
max <- as.integer(args[3])

cpt <- 1;
color <- rainbow(11);

# Ratio
output <- sprintf("preysRatioStags.png");
png(output);
while(cpt <= nbFiles) {
	filename = sprintf("refactDataRatio_run%d.dat", cpt);

	graph <- read.table(filename, sep=",", header=TRUE);
	#output <- sprintf("preysVite_run%d.png", cpt);
	#png(output);
	
	if(cpt == 1)
	{
		plot(graph$Evaluation, graph$RatioSStagsSolo, type="l", main="Ratio of stags hunted", xlab="Evaluations", ylab="Ratio", ylim=c(0,1));
		lines(graph$Evaluation, graph$RatioSStagsSolo, col="firebrick1");
	}
	else
	{
		lines(graph$Evaluation, graph$RatioSStagsSolo, col="firebrick1");
	}

	lines(graph$Evaluation, graph$RatioSStagsDuo, col="dodgerblue1");

	legend("topleft", c("Stags alone","Stags coop."),fill=c("firebrick1","dodgerblue1"));
	
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# NbStagsCoop
output <- sprintf("preysStagsDuo.png");
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
			plot(graph$Evaluation, graph$NbSStagsDuo, type="l", main="Number of stags hunted cooperatively", xlab="Evaluations", ylab="Number of stags");
		}
		else {
			plot(graph$Evaluation, graph$NbSStagsDuo, type="l", main="Number of stags hunted cooperatively", xlab="Evaluations", ylab="Number of stags", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbSStagsDuo, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbSStagsDuo, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();

# Ratio
output <- sprintf("preysStagsSolo.png");
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
			plot(graph$Evaluation, graph$NbSStagsSolo, type="l", main="Number of stags hunted alone", xlab="Evaluations", ylab="Number of stags");
		}
		else {
			plot(graph$Evaluation, graph$NbSStagsSolo, type="l", main="Number of stags hunted alone", xlab="Evaluations", ylab="Number of stags", ylim=c(min,max));
		}
		lines(graph$Evaluation, graph$NbSStagsSolo, col=color[cpt]);
	}
	else
	{
		lines(graph$Evaluation, graph$NbSStagsSolo, col=color[cpt]);
	}
	#dev.off();
	cpt <- cpt + 1;
}
dev.off();
