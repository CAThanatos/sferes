#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd "abs_path";

my $numArg = 0;
my $nbFiles = 5;
my $fitnessMin = -1;
my $fitnessMax = -1;
my $preysMin = -1;
my $preysMax = -1;
my $vite = 0;
my $dossier = -1;
my $countTime = 0;

while($numArg < scalar(@ARGV))
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
						if($ARGV[$numArg] =~ "-v")
						{
							$vite = 1;
						}
						else
						{
							if($ARGV[$numArg] =~ "-d")
							{
								$numArg++;
								$dossier = $ARGV[$numArg];
							}
							else
							{
								if($ARGV[$numArg] =~ "-c")
								{
									$countTime = 1;
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

if($fitnessMax == -1)
{
	$fitnessMin = -1;
}

if($preysMax == -1)
{
	$preysMin = -1;
}

my $abs_dir = dirname(abs_path($0));
chdir "$dossier";
if($vite == 0) 
{
	system "Rscript $abs_dir/RScript.R $nbFiles $fitnessMin $fitnessMax $preysMin $preysMax";
	
	if($countTime == 1)
	{
		system "Rscript $abs_dir/RScriptTime.R $nbFiles";
	}
}
else 
{
	system "Rscript $abs_dir/scriptVite.R $fitnessMin $fitnessMax $preysMin $preysMax";
}
