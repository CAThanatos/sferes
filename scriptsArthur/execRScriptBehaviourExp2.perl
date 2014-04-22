#!/usr/bin/perl

use strict;

my $numArg = 0;
my $nbFiles = 5;
my $min = 0;
my $max = 15000;
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
				else
				{
					if($ARGV[$numArg] =~ "-h")
					{
						&printHelp();
					}
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

system "Rscript RScriptBehaviourExp2.R $nbFiles $dossier $min $max";


sub printHelp()
{
	print "Usage : ./execRScriptBehaviourExp2.perl -d Directory [-n NumberOfFiles] [-min IterMin] [-max IterMax] [-h]\n";
	print "\t-d : Directory with all the files to draw\n";
	print "\t-n : Number of files to draw. 5 by default\n";
	print "\t-min : Minimum iteration. 0 by default\n";
	print "\t-max : Maximum iteration. 15000 by default\n";
	print "\t-h : Prints this help\n";
	exit;
}
