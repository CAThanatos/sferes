#!/usr/bin/perl

use strict;
use Getopt::Std;

my %conf = ();

my $dossier = undef;
my $precision = 1000;
my $fitnessMin = -1;
my $fitnessMax = -1;
my $preysMin = -1;
my $preysMax = -1;
my $maxIter = -1;
my $prefix = "Dir";

getopts( 'd:p:f:r:x:m:h', \%conf ) or die $!;

if($conf{h})
{
	&printHelp();
	exit 0;
}

if($conf{d})
{
	$dossier = $conf{d};
}

if($conf{p})
{
	$precision = $conf{p};
}

if($conf{f})
{
	($fitnessMin, $fitnessMax) = split ':', $conf{f}, 2;
}

if($conf{r})
{
	($preysMin, $preysMax) = split ':', $conf{r}, 2;
}

if($conf{"x"})
{
	$prefix = $conf{"x"};
}

if($conf{m})
{
	$maxIter = $conf{m};
}

if(defined($dossier))
{
	&generateDirectory($dossier);
}
else
{
	&printHelp();
	exit 1;
}

sub generateDirectory()
{
	my $dossierSub = $_[0];

	opendir DIR, $dossierSub or die $!;
	my @files = grep {/^[^.]/} readdir(DIR);
	closedir DIR;
	
	# On regarde si c'est le dossier d'une expérience
	my $expDir = 0;
	my $nbFiles = 0;
	foreach my $file (@files)
	{
		if(-d "$dossierSub/$file" && $file =~ /$prefix/)
		{
			$expDir = 1;
			$nbFiles++;
		}
	}
	
	if(1 == $expDir)
	{
		print "Script : ./scriptsArthur/generateGraphs.perl -d $dossierSub -f \"$prefix\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter\n";
		system "./scriptsArthur/generateGraphs.perl -d $dossierSub -f \"$prefix\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter";
	}
	else
	{
		foreach my $file (@files)
		{
			my $subFile = "$dossierSub/$file";
			if(-d "$subFile")
			{
				&generateDirectory($subFile);
			}
		}
	}
}

sub printHelp()
{
	print "Usage : ./generateGraphsDeep.perl -d FilesDirectory [-p Precision] [-m IterationMax] [-f FitnessMin:FitnessMax] [-r PreysMin:PreysMax] [-x DirectoryPrefix] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Number of iteration max computed and drawn. No maximum by default\n";
	print "\t-f : Bounds on the graphs for the fitness. No bounds by defaults\n";
	print "\t-r : Bounds on the graphs for the number of preys. No bounds by defaults\n";
	print "\t-x : Prefix in the name of the directories. \"Dir\" by default\n";
	print "\t-h : Prints this help\n";
	exit;
}
