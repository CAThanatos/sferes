args <- commandArgs(trailingOnly=TRUE)
numRun <- as.integer(args[1])
nbTrials <- as.integer(args[2])
setting <- as.integer(args[3])

if(setting == 1 || setting == 2 || setting == 4)
{
	output <- sprintf("CoopHare_run%d.png", numRun)
	png(output)

	filename <- sprintf("refactCoopHare_run%d.dat", numRun)
	graph <- read.table(filename, sep=",", header=TRUE)
	
	bind <- rbind(graph$NbGoCoop, graph$NbNoCoop)
	barplot(bind, names.arg=c("Without predator", "With predator"), beside=TRUE, ylab="Number of preys", main="Proportion of preys chosen", col=c("firebrick1", "dodgerblue1"), ylim=c(0, nbTrials))

	legend("topleft", c("Hares","Other"), fill=c("firebrick1", "dodgerblue1"))
	dev.off()
}

if(setting == 2 || setting == 3 || setting == 5)
{
	output <- sprintf("CoopSStag_run%d.png", numRun)
	png(output)

	filename <- sprintf("refactCoopSStag_run%d.dat", numRun)
	graph <- read.table(filename, sep=",", header=TRUE)
	
	bind <- rbind(graph$NbGoCoop, graph$NbNoCoop)
	barplot(bind, names.arg=c("Without predator", "With predator"), beside=TRUE, ylab="Number of preys", main="Proportion of preys chosen", col=c("firebrick1", "dodgerblue1"), ylim=c(0, nbTrials))

	legend("topleft", c("Small Stags","Other"), fill=c("firebrick1", "dodgerblue1"))
	dev.off()
}

if(setting == 4 || setting == 5 || setting == 6)
{
	output <- sprintf("CoopBStag_run%d.png", numRun)
	png(output)

	filename <- sprintf("refactCoopBStag_run%d.dat", numRun)
	graph <- read.table(filename, sep=",", header=TRUE)
	
	bind <- rbind(graph$NbGoCoop, graph$NbNoCoop)
	barplot(bind, names.arg=c("Without predator", "With predator"), beside=TRUE, ylab="Number of preys", main="Proportion of preys chosen", col=c("firebrick1", "dodgerblue1"), ylim=c(0, nbTrials))

	legend("topleft", c("Big Stags","Other"), fill=c("firebrick1", "dodgerblue1"))
	dev.off()
}
