#!/usr/bin/perl

use strict;

my $PROD_DIR = "./build/prod/exp";

my $expe = "StagHuntExp3-Duo";
my $prod = 0;
my $clean = 0;

my $numArg = 0;
while($numArg < scalar(@ARGV))
{
	if($ARGV[$numArg] =~ "-e")
	{
		$numArg++;
		$expe = $ARGV[$numArg];
	}
	else
	{
		if($ARGV[$numArg] =~ "-p")
		{
			$prod = 1;
		}
		else
		{
			if($ARGV[$numArg] =~ "-c")
			{
				$clean = 1;
			}
			else
			{
				if($ARGV[$numArg] =~ "-h")
				{
					&printHelp();
					exit 0;
				}
			}
		}
	}

	$numArg++;
}

if($clean == 1)
{
	`./waf clean`;
}

my $output = `./waf --exp $expe 2>&1`;
my @lignes = split /\n/, $output;
my $error = 0;

foreach my $ligne (@lignes)
{
	chomp $ligne;
	
	if($ligne =~ /error:/)
	{
		print "$ligne\n";
		$error = 1;
	}
}

open FILEOUT, ">waf_debug.txt" or die $!;
print FILEOUT $output;
close FILEOUT;

if($prod == 1 && $error == 0)
{
	my $prodDir = "$PROD_DIR/$expe";
	
	if(-e $prodDir)
	{
		system "rm -r $prodDir";
	}
	
	system "mkdir -p $prodDir";
	
	my $buildDir = "./build/default/exp/$expe";
	opendir DIR, $buildDir or die $!;
	my @files = grep {/^[^.]/} readdir(DIR);
	closedir DIR;
	
	foreach my $file (@files)
	{
		if($file !~ /\.o$/)
		{
			system "cp $buildDir/$file $prodDir";
		}
	}
}

sub printHelp()
{
	print "Usage : ./wafCompil2.perl -e Experiment [-p] [-c] [-h]\n";
	print "\t-e : The experiment to compile\n";
	print "\t-p : Push this version in production\n";
	print "\t-c : Cleans all the executables\n";
	print "\t-h : Prints this help\n";
	exit;
}
