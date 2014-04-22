#!/usr/bin/perl

use strict;

my $numArg = 0;
my $nbFiles = 5;
my $min = 0;
my $max = 1;
my $dossier = -1;

while($numArg < scalar(@ARGV))
{
	if($ARGV[$numArg] =~ "-n")
	{
		$numArg++;
		$nbFiles = $ARGV[$numArg];
	}
	else
	{
		if($ARGV[$numArg] =~ "-min")
		{
			$numArg++;
			$min = $ARGV[$numArg];
		}
		else
		{
			if($ARGV[$numArg] =~ "-max")
			{
				$numArg++;
				$max = $ARGV[$numArg];
			}
			else
			{
				if($ARGV[$numArg] =~ "-d")
				{
					$numArg++;
					$dossier = $ARGV[$numArg];
				}
			}
		}
	}

	$numArg++;
}

if($max == -1)
{
	$min = -1;
}

system "Rscript RScriptBehaviourIter.R $nbFiles $dossier $min $max";
