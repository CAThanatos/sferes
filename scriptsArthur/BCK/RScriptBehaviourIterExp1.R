args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
dossier <- args[2]
min <- as.numeric(args[3])
max <- as.numeric(args[4])

cpt <- 1;
while(cpt <= nbFiles) {
	filename <- sprintf("%srefactIterControl_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$GoHare, graph$GoStag)
	output <- sprintf("%scontrolIter_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(2))
	} else {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(3), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Stag"),fill=gray.colors(2))
	dev.off()
	
	

	filename <- sprintf("%srefactIterCoop_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$GoHare, graph$GoStag)
	output <- sprintf("%scoopIter_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(2))
	} else {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(3), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Stag"),fill=gray.colors(2))
	dev.off()
	
	

	filename <- sprintf("%srefactIterDist_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$GoHare, graph$GoStag)
	output <- sprintf("%sdistIter_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(2))
	} else {
		barplot(bind, names.arg = graph$Iteration, beside=FALSE,names=levels(graph$Iteration),xlab="Iterations",ylab="Choice",main="Choice by Iteration",col=gray.colors(3), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Stag"),fill=gray.colors(2))
	dev.off()
	
	cpt <- cpt + 1;
}
