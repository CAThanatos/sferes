#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd "abs_path";

my $numArg = 0;
my $dossier = "";
my $prefixeDossier = "Dir";
my $precision = 100;
my $genInd = -1;
my $refactDir = 0;
my $log = 0;
my $numAnalysis = 1;

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
			if($arg =~ "-p")
			{
				$numArg++;
				$precision = $ARGV[$numArg];
				$numArg++;
			}
			else
			{
			  if($arg =~ "-g")
			  {
				  $numArg++;
				  $genInd = $ARGV[$numArg];
				  $numArg++;
			  }
        else
        {
        	if($arg =~ "-r")
        	{
        		$numArg++;
        		$refactDir = 1;
        	}
        	else
        	{
		      	if($arg =~ "-h")
		      	{
		      		$numArg++;
		      		&printHelp();
		      	}
						else
						{
							if($arg =~ "-l")
							{
								$numArg++;
								$log = 1;
							}
							else
							{
								if($arg =~ "-n")
								{
									$numArg++;
									$numAnalysis = $ARGV[$numArg];
									$numArg++;
								}
							}
						}
        	}
        }
			}
		}
	}
}

opendir DIR, "$dossier" or die $!;
my @files = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $file (@files)
{
	print "$dossier/$file\n";
	
	my $fileTest = "$dossier/$file";
	if(-d $fileTest)
	{
		my $setting = 0;
		if($file =~ /^SETTING(\d)/)
		{
			$setting = $1;
		}
		else
		{
			if($file =~ /^CONTROL1/)
			{
				$setting = 4;
			}
			else
			{
				if($file =~ /^CONTROL2/)
				{
					$setting = 3;
				}
				else
				{
					if($file =~ /^CONTROL3/)
					{
						$setting = 5;
					}
				}
			}
		}
	
		opendir DIR, "$dossier/$file" or die $!;
		my @filesDir = grep {/^[^.]/} readdir(DIR);
		closedir DIR;

		if($refactDir == 1)
		{
			my $nbFiles = 0;
			foreach my $fileDir (@filesDir)
			{
				if($fileDir !~ /BestFit/ && $fileDir !~ /MeanFit/ && $fileDir !~ /BestEver/)
				{
					my $numFile = $nbFiles + 1;
					system "mv $dossier/$file/$fileDir $dossier$file/Dir$numFile";

					$nbFiles++;
				}
			}
		}
		
		my $dir = dirname($0);

		if($log == 1)
		{
			print "Script : $dir/BehaviourAnalysisExp3.perl -d $dossier/$file -f \"Dir\" -g $genInd -p $precision -s $setting -n $numAnalysis -l\n";
			system "$dir/BehaviourAnalysisExp3.perl -d $dossier/$file -f \"Dir\" -g $genInd -p $precision -s $setting -n $numAnalysis -l";
		}
		else
		{
			print "Script : $dir/BehaviourAnalysisExp3.perl -d $dossier/$file -f \"Dir\" -g $genInd -p $precision -s $setting -n $numAnalysis\n";
			system "$dir/BehaviourAnalysisExp3.perl -d $dossier/$file -f \"Dir\" -g $genInd -p $precision -s $setting -n $numAnalysis";
		}
	}
}


sub printHelp()
{
	print "Usage : ./BehaviourAnalysisExp2.perl -d FilesDirectory [-f DirectoryPrefix] [-p Precision] [-g GenInd] [-r] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"Dir\" by default\n";
	print "\t-p : Precision in number of generations. 100 by default\n";
	print "\t-g : From which generation the individual must be analysed. By default, we take the one from the last generation\n";
	print "\t-r : Directory names are changed to all begin with \"Dir\"\n";
	print "\t-h : Prints this help\n";
	exit;
}
