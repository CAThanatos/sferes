#!/usr/bin/perl

use strict;
use File::Basename;

my $numArg = 0;
my $dossier = 0;
my $iterMax = -1;
my $precision = 1000;
my $nbFiles = 5;
my $fitnessMin = -1;
my $fitnessMax = -1;
my $preysMin = -1;
my $preysMax = -1;
my $prefixeDossier = "ISIR";
my $typeData = "BestFit";
my $countTime = 0;
my $useR = 0;

while($numArg < scalar(@ARGV))
{
	if($ARGV[$numArg] =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
	}
	else
	{
		if($ARGV[$numArg] =~ "-m")
		{
			$numArg++;
			$iterMax = $ARGV[$numArg];
		}
		else
		{
			if($ARGV[$numArg] =~ /^-p$/)
			{
				$numArg++;
				$precision = $ARGV[$numArg];
			}
			else
			{
				if($ARGV[$numArg] =~ "-n")
				{
					$numArg++;
					$nbFiles = $ARGV[$numArg];
				}
				else
				{
					if($ARGV[$numArg] =~ "-fmin")
					{
						$numArg++;
						$fitnessMin = $ARGV[$numArg];
					}
					else
					{
						if($ARGV[$numArg] =~ "-fmax")
						{
							$numArg++;
							$fitnessMax = $ARGV[$numArg];
						}
						else
						{
							if($ARGV[$numArg] =~ "-pmin")
							{
								$numArg++;
								$preysMin = $ARGV[$numArg];
							}
							else
							{
								if($ARGV[$numArg] =~ "-pmax")
								{
									$numArg++;
									$preysMax = $ARGV[$numArg];
								}
								else
								{
									if($ARGV[$numArg] =~ "-f")
									{
										$numArg++;
										$prefixeDossier = $ARGV[$numArg];
									}
									else
									{
										if($ARGV[$numArg] =~ "-h")
										{
											&printHelp();
										}
										else
										{
											if($ARGV[$numArg] =~ "-t")
											{
												$numArg++;
												$typeData = $ARGV[$numArg];
											}
											else
											{
												if($ARGV[$numArg] =~ "-c")
												{
													$countTime = 1;
												}
												else
												{
													if($ARGV[$numArg] =~ "-r")
													{
														$useR = 1;
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}

	$numArg++;
}

my $dir = dirname($0);

system "$dir/refactData.perl -d $dossier -f $prefixeDossier -m $iterMax -p $precision";

if($countTime == 1)
{
	system "$dir/execRScript.perl -d $dossier/$typeData -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -c";
}
else
{
	if($useR == 1)
	{
		system "$dir/execRScript.perl -d $dossier/$typeData -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax";
	}
	else
	{
		system "$dir/drawGraphs.perl -d $dossier/$typeData -m $iterMax";
		#system "$dir/drawGraphs.perl -d $dossier/BestEverFit -m $iterMax";
	}
}

sub printHelp()
{
	print "Usage : ./generateGraphs.perl -d FilesDirectory [-f DirectoryPrefix] [-n NumberOfRuns] [-p Precision] [-m LastGen] [-t DataType] [-fmin FitnessMin] [-fmax FitnessMax] [-pmin PreysMin] [-pmax PreysMax] [-r] [-c] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"ISIR\" by default\n";
	print "\t-n : Number of runs to draw. 5 by default\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Last evaluation that will be drawn. No maximum by default\n";
	print "\t-t : Type of data (BestFit, BestEver, MeanFit) to draw\n";
	print "\t-fmin, -fmax : Bounds on the graphs for the fitness. No bounds by defaults\n";
	print "\t-pmin, -pmax : Bounds on the graphs for the number of preys. No bounds by defaults\n";
	print "\t-c : Computes the time analysis\n";
	print "\t-r : Uses R instead of Perl's GD::Graph\n";
	print "\t-h : Prints this help\n";
	exit;
}
