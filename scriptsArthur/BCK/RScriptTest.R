graph <- read.table("refactData.dat", sep=",", header=TRUE)
graph$Evaluation <- factor(graph$Evaluation)
attach(graph)
png("best.png")
plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness")
dev.off()

cpt <- 1;
while(cpt < 12) {
	filename <- sprintf("refactData_run%d.dat", cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	output <- sprintf("best_run%d.png", cpt);
	png(output)
	plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness")
	dev.off()

	bind <- rbind(graph$NbHares, graph$NbSStagsDuo, graph$NbSStagsSolo, graph$NbBStagsDuo, graph$NbBStagsSolo)
	output <- sprintf("preys_run%d.png", cpt);
	png(output)
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Proportion of preys hunted",col=gray.colors(5))
	legend("topleft", c("NbHares","NbSStagsDuo","$NbSStagsSolo","NbBStagsDuo","NBSStagsSolo"),fill=gray.colors(5))
	dev.off()
	
	cpt <- cpt + 1;
}
