args <- commandArgs(trailingOnly=TRUE)
nbFiles <- as.integer(args[1])
dossier <- args[2]
min <- as.numeric(args[3])
max <- as.numeric(args[4])

cpt <- 1;
while(cpt <= nbFiles) {
	filename <- sprintf("%srefactControl_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$NbGoHare, graph$NbGoSmallStag, graph&NbGoBigStag)
	output <- sprintf("%scontrol_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"))
	} else {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Small Stag","Big Stag"),fill=c("forestgreen", "firebrick1", "dodgerblue1"))
	dev.off()
	
	

	filename <- sprintf("%srefactCoop_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$NbGoHare, graph$NbGoSmallStag, graph&NbGoBigStag)
	output <- sprintf("%scoop_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"))
	} else {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Small Stag","Big Stag"),fill=c("forestgreen", "firebrick1", "dodgerblue1"))
	dev.off()
	
	

	filename <- sprintf("%srefactDist_run%d.dat", dossier, cpt);
	print(filename);
	
	graph <- read.table(filename, sep=",", header=TRUE)
	bind <- rbind(graph$NbGoHare, graph$NbGoSmallStag, graph&NbGoBigStag)
	output <- sprintf("%sdist_run%d.png", dossier, cpt);
	png(output)
	
	if(min == -1) {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"))
	} else {
		barplot(bind, names.arg = graph$Evaluation, beside=FALSE,names=levels(graph$Evaluation),xlab="Evaluations",ylab="Times hunted",main="Proportion of choices",col=c("forestgreen", "firebrick1", "dodgerblue1"), ylim=c(min, max))
	}
	legend("topleft", c("Hare","Small Stag","Big Stag"),fill=c("forestgreen", "firebrick1", "dodgerblue1"))
	dev.off()
	
	cpt <- cpt + 1;
}
