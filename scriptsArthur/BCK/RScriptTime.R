args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])

cpt <- 1;
while(cpt <= nbFiles) {
	filename <- sprintf("refactDataTime_run%d.dat", cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$TimeOnHares, graph$TimeOnSStags, graph$TimeOnBStags)
	output <- sprintf("preysTime_run%d.png", cpt);
	png(output)
	
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE, names=levels(graph$Evaluation), xlab="Evaluations", ylab="Time spent", main="Repartition of time spent on preys", col=c("green", "firebrick1", "dodgerblue1"))

	dev.off()	
	cpt <- cpt + 1;
}
