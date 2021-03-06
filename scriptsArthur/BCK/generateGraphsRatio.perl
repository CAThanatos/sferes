#!/usr/bin/perl

use strict;
use Switch;
use Cwd "abs_path";
use File::Basename;

my $numArg = 0;
my $dossier = 0;
my $iterMax = -1;
my $precision = 1000;
my $nbFiles = 11;
my $fitnessMin = -1;
my $fitnessMax = -1;
my $preysMin = -1;
my $preysMax = -1;
my $prefixeDossier = "ISIR";
my $typeData = "BestFit";
my $setting = 0;

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
										if($ARGV[$numArg] =~ /^-h$/)
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
												if($ARGV[$numArg] =~ /^-s$/)
												{
													$numArg++;
													$setting = $ARGV[$numArg];
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

system "$dir/refactRatio.perl -d $dossier/$typeData -s $setting";

my $abs_path = dirname(abs_path($0));
chdir "$dossier/$typeData";

switch ($setting)
{
	case [1..4]
	{
		system "Rscript $abs_path/scriptRatioHaresSStags.R $nbFiles $preysMin $preysMax";
	}
	case [5..8]
	{
		system "Rscript $abs_path/scriptRatioHaresBStags.R $nbFiles $preysMin $preysMax";
	}
	case [9..12]
	{
		system "Rscript $abs_path/scriptRatioSStagsBStags.R $nbFiles $preysMin $preysMax";
	}
	case 13
	{
		system "Rscript $abs_path/scriptRatioHares.R $nbFiles $preysMin $preysMax";
	}
	case 14
	{
		system "Rscript $abs_path/scriptRatioSStags.R $nbFiles $preysMin $preysMax";
	}
	case 15
	{
		system "Rscript $abs_path/scriptRatioBStags.R $nbFiles $preysMin $preysMax";
	}
	else
	{
		print "Wrong setting : $setting\n";
	}
}


sub printHelp()
{
	print "Usage : ./generateGraphs.perl -d FilesDirectory [-f DirectoryPrefix] [-n NumberOfRuns] [-p Precision] [-m LastGen] [-t DataType] [-fmin FitnessMin] [-fmax FitnessMax] [-pmin PreysMin] [-pmax PreysMax] [-s] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"ISIR\" by default\n";
	print "\t-n : Number of runs to draw. 5 by default\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Last evaluation that will be drawn. No maximum by default\n";
	print "\t-t : Type of data (BestFit, BestEver, MeanFit) to draw\n";
	print "\t-pmin, -pmax : Bounds on the graphs for the number of preys. No bounds by defaults\n";
	print "\t-s : The setting of the experiment\n";
	print "\t-h : Prints this help\n";
	exit;
}
