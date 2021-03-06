args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
fitnessMin <- as.numeric(args[2])
fitnessMax <- as.numeric(args[3])
preysMin <- as.numeric(args[4])
preysMax <- as.numeric(args[5])

graph <- read.table("refactData.dat", sep=",", header=TRUE)
graph$Evaluation <- factor(graph$Evaluation)
attach(graph)
png("best.png")
if(fitnessMin == -1) {
		plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness")
} else {
	plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness", ylim=c(fitnessMin, fitnessMax))
}
dev.off()

cpt <- 1;
while(cpt <= nbFiles) {
	filename <- sprintf("refactData_run%d.dat", cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	output <- sprintf("best_run%d.png", cpt);
	png(output)

	if(fitnessMin == -1) {
		plot(graph$Evaluation, graph$Fitness, type="l", main="Best Fitness", xlab="Evaluations", ylab="Fitness")
	} else {
		plot(graph$Evaluation, graph$Fitness, type="l", main="Best Fitness", xlab="Evaluations", ylab="Fitness", ylim=c(fitnessMin, fitnessMax))
	}
	lines(graph$Evaluation, graph$Fitness,col="firebrick1");
	dev.off()

#	bind <- rbind(graph$NbHares, graph$NbBStagsDuo, graph$NbBStagsSolo)
#	output <- sprintf("preysSimple_run%d.png", cpt);
#	png(output)
	
#	if(preysMin == -1) {
#		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Repartition of preys hunted",col=c("green", "firebrick1", "dodgerblue1"))
#	} else {
#		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Repartition of preys hunted",col=c("green", "firebrick1", "dodgerblue1"), ylim=c(preysMin, preysMax))
#	}
#	legend("topleft", c("Hares","Stags cooperatively","Stags alone"),fill=c("green", "firebrick1", "dodgerblue1"))
#	dev.off()

	bind <- rbind(graph$NbHaresSolo, graph$NbHaresDuo, graph$NbSStagsSolo, graph$NbSStagsDuo, graph$NbBStagsSolo, graph$NbBStagsDuo)
	output <- sprintf("preys_run%d.png", cpt);
	png(output)
	
	if(preysMin == -1) {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Repartition of preys hunted",col=c("green", "green4", "firebrick1", "firebrick4", "dodgerblue1", "dodgerblue4"))
	} else {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Repartition of preys hunted",col=c("green", "green4", "firebrick1", "firebrick4", "dodgerblue1", "dodgerblue4"), ylim=c(preysMin, preysMax))
	}
#	legend("topleft", c("Hares alone", "Hares coop.","Small stags alone","Small stags coop.", "Big stags alone", "Big stags coop."),fill=c("green", "green4", "firebrick1", "firebrick4", "dodgerblue1", "dodgerblue4"))
	dev.off()	
	cpt <- cpt + 1;
}
