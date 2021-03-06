#!/usr/bin/perl

use strict;
use File::Basename;

my $dossier = "0";
my $fileOutput = "refactData";
my $precision = 1000;
my $iterMax = -1;
my $prefixeDossier = "ISIR-stage";
my $typeData = "BestFit";

my $numArg = 0;
while ($numArg < scalar(@ARGV))
{
	my $arg = $ARGV[$numArg];
	if($arg =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
		$numArg++;
	}
	else
	{
		if($arg =~ "-f")
		{
			$numArg++;
			$prefixeDossier = $ARGV[$numArg];
			$numArg++;
		}
		else
		{
			if($arg =~ "-o")
			{
				$numArg++;
				$fileOutput = $ARGV[$numArg];
				$numArg++;
			}
			else
			{
				if($arg =~ "-p")
				{
					$numArg++;
					$precision = $ARGV[$numArg];
					$numArg++;
				}
				else
				{
					if($arg =~ "-m")
					{
						$numArg++;
						$iterMax = $ARGV[$numArg];
						$numArg++;
					}
					else
					{
						if($arg =~ "-t")
						{
							$numArg++;
							$typeData = $ARGV[$numArg];
							$numArg++;
						}
						else
						{
							if($arg =~ "-h")
							{
								$numArg++;
								&printHelp();
							}
						}
					}
				}
			}
		}
	}
}

my $dir = dirname($0);

system "$dir/makeDataFolder.perl -d $dossier -p $prefixeDossier -c";
system "$dir/make_data.perl -d $dossier/$typeData -p $precision -m $iterMax -o $fileOutput -c";
system "$dir/make_data.perl -d $dossier/BestEverFit -p $precision -m $iterMax -o $fileOutput -c";

sub printHelp()
{
	print "Usage : ./refactData.perl -d FilesDirectory [-f DirectoryPrefix] [-o FileOutput] [-p Precision] [-m LastGen] [-t DataType] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"ISIR\" by default\n";
	print "\t-o : Name of the ouput files after refactoring. \"refactData\" by default\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Last evaluation that will be drawn. No maximum by default\n";
	print "\t-t : Type of data (BestFit, BestEver, MeanFit) to draw\n";
	print "\t-h : Prints this help\n";
	exit;
}
