args <- commandArgs(trailingOnly=TRUE)
fitnessMin <- as.numeric(args[1])
fitnessMax <- as.numeric(args[2])
preysMin <- as.numeric(args[3])
preysMax <- as.numeric(args[4])

filename <- "refactData_run1.dat";
print(filename);
	
graph <- read.table(filename, sep=",", header=TRUE)
output <- "best_test.png";
png(output)

if(fitnessMin == -1) {
	plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness")
} else {
	plot(graph$Evaluation, graph$Fitness, main="Best Fitness", xlab="Evaluations", ylab="Fitness", ylim=c(fitnessMin, fitnessMax))
}
dev.off()

bind <- rbind(graph$NbHares, graph$NbBStagsDuo, graph$NbBStagsSolo)
output <- "preysSimple_test.png";
png(output)

if(preysMin == -1) {
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Proportion of preys hunted",col=gray.colors(3))
} else {
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Proportion of preys hunted",col=gray.colors(3), ylim=c(preysMin, preysMax))
}

legend("topleft", c("Lièvres","Cerfs à deux","Cerfs seuls"),fill=gray.colors(3))
dev.off()

bind <- rbind(graph$NbHares, graph$NbSStagsSolo, graph$NbSStagsDuo, graph$NbBStagsSolo, graph$NbBStagsDuo)
output <- "preys_test.png";
png(output)

if(preysMin == -1) {
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Proportion of preys hunted",col=gray.colors(5))
} else {
	barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Preys Hunted",main="Proportion of preys hunted",col=gray.colors(5), ylim=c(preysMin, preysMax))
}

legend("topleft", c("Hares","Small stags alone","Small stags coop.", "Big stags alone", "Big stags coop."),fill=gray.colors(5))
dev.off()
