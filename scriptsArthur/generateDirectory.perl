#!/usr/bin/perl

my $dossier = 0;
my $precision = 1000;
my $refactDir = 0;
my $fitnessMin = -1;
my $fitnessMax = -1;
my $preysMin = -1;
my $preysMax = -1;
my $countTime = 0;
my $maxIter = -1;

while($numArg < scalar(@ARGV))
{
	if($ARGV[$numArg] =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
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
							if($ARGV[$numArg] =~ "-h")
							{
								&printHelp();
							}
							else
							{								
								if($ARGV[$numArg] =~ "r")
								{
									$refactDir = 1;
								}
								else
								{
									if($ARGV[$numArg] =~ "c")
									{
										$countTime = 1;
									}
									else
									{
											if($ARGV[$numArg] =~ "m")
											{
												$numArg++;
												$maxIter = $ARGV[$numArg];
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

opendir DIR, "$dossier" or die $!;
my @files = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $file (@files)
{
	print "$dossier$file\n";

	my $fileTest = "$dossier$file";
	if(-d $fileTest)
	{
		opendir DIR, "$dossier$file" or die $!;
		my @filesDir = grep {/^[^.]/} readdir(DIR);
		closedir DIR;

		my $nbFiles = 0;
		foreach my $fileDir (@filesDir)
		{
			if($fileDir !~ /BestFit/ && $fileDir !~ /MeanFit/ && $fileDir !~ /BestEver/ && $fileDir !~ /Refactor/)
			{
				if($refactDir == 1 && $fileDir !~ /Dir/)
				{
					my $numFile = $nbFiles + 1;
					system "mv $dossier$file/$fileDir $dossier$file/Dir$numFile";
				}

				$nbFiles++;
			}
		}
		
		if($countTime == 1)
		{
			print "Script : ./scriptsArthur/generateGraphs.perl -d $dossier$file -f \"Dir\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter -c\n";
			system "./scriptsArthur/generateGraphs.perl -d $dossier$file -f \"Dir\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter -c";
		}
		else
		{
			print "Script : ./scriptsArthur/generateGraphs.perl -d $dossier$file -f \"Dir\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter\n";
			system "./scriptsArthur/generateGraphs.perl -d $dossier$file -f \"Dir\" -n $nbFiles -fmin $fitnessMin -fmax $fitnessMax -pmin $preysMin -pmax $preysMax -p $precision -m $maxIter";
		}
	}
}

sub printHelp()
{
	print "Usage : ./scriptVite2.perl -d FilesDirectory [-p Precision] [-m IterationMax] [-fmin FitnessMin] [-fmax FitnessMax] [-pmin PreysMin] [-pmax PreysMax] [-r] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Number of iteration max computed and drawn. No maximum by default\n";
	print "\t-fmin, -fmax : Bounds on the graphs for the fitness. No bounds by defaults\n";
	print "\t-pmin, -pmax : Bounds on the graphs for the number of preys. No bounds by defaults\n";
	print "\t-r : Directory names are changed so that they all begin with \"Dir\"\n";
	print "\t-h : Prints this help\n";
	exit;
}
