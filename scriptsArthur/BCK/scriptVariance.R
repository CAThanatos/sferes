args <- commandArgs(trailingOnly=TRUE)

output <- sprintf("ratioVariance.png");
png(output);

filename = sprintf("refactVariances.dat");
graph <- read.table(filename, sep=",", header=TRUE);
graph$Generation <- factor(graph$Generation);

plot(graph$Generation, graph$Ratio, main="Ratio of standard deviation on mean", xlab="Generation", ylab="Ratio");
dev.off();
