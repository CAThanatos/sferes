args <- commandArgs(trailingOnly=TRUE)

output <- sprintf("ratioVariance.png");
png(output);

filename = sprintf("refactVariances.dat");
graph <- read.table(filename, sep=",", header=TRUE);
graph$Generation <- factor(graph$Generation);

#plot(graph$Generation, graph$Ratio, type="l", main="Ratio of standard deviation on mean", xlab="Generation", ylab="Ratio");
plot(graph$Generation, graph$Fitness, main="Mean Fitness", xlab="Generation", ylab="Fitness", ylim=c(0,4000));
#lines(graph$Generation, graph$Ratio,col="firebrick1");
dev.off();
