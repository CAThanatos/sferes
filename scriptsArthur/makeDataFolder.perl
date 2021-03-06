#!/usr/bin/perl

use strict;
use File::Basename;

my @fichiers = ();
my $dossier = "0";
my $numArg = 0;
my $prefixeDossier = "ISIR-stage";
my $clean = 0;

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
		if($arg =~ "-p")
		{
			$numArg++;
			$prefixeDossier = $ARGV[$numArg];
			$numArg++;
		}
		else
		{
			if($arg =~ "-c")
			{
				$clean = 1;
				$numArg++;
			}
		}
	}
}

opendir DIR, $dossier or die $!;
my @dossiers = grep {/^[^.]/} readdir(DIR);
closedir DIR;

my $dossierBest = "BestFit";
my $dossierBestEver = "BestEverFit";
my $dossierMean = "MeanFit";

if(-e "$dossier/$dossierBest")
{
	if($clean == 1)
	{
		system "rm -r $dossier/$dossierBest";
		system "mkdir $dossier/$dossierBest";
	}
}
else
{
	system "mkdir $dossier/$dossierBest";
}

if(-e "$dossier/$dossierBestEver")
{
	if($clean == 1)
	{
		system "rm -r $dossier/$dossierBestEver";
		system "mkdir $dossier/$dossierBestEver";
	}
}
else
{
	system "mkdir $dossier/$dossierBestEver";
}

if(-e "$dossier/$dossierMean")
{
	if($clean == 1)
	{
		system "rm -r $dossier/$dossierMean";
		system "mkdir $dossier/$dossierMean";
	}
}
else
{
	system "mkdir $dossier/$dossierMean";
}

my $numIter = 1;
foreach my $subDossier (@dossiers)
{
	if($subDossier =~ /^$prefixeDossier/)
	{
		opendir DIR, "$dossier/$subDossier" or die $!;
		my @fichiers = grep {/^[^.]/} readdir(DIR);
		closedir DIR;
		
		my $num = $numIter;
		
		if($subDossier =~ /^$prefixeDossier(\d+)$/)
		{
			$num = $1;
		}
		
		foreach my $fichier (@fichiers)
		{
			if($fichier =~ /^bestfit.dat$/)
			{
				my $newFile = "bestfit" . $num . ".dat";
				system "cp $dossier/$subDossier/$fichier $dossier/$dossierBest/$newFile";
			}
			else 
			{
				if($fichier =~ /^besteverfit.dat$/)
				{
					my $newFile = "besteverfit" . $num . ".dat";
					system "cp $dossier/$subDossier/$fichier $dossier/$dossierBestEver/$newFile";
				}
				else
				{
					if($fichier =~ /^meanfit.dat$/)
					{
						my $newFile = "meanfit" . $num . ".dat";
						system "cp $dossier/$subDossier/$fichier $dossier/$dossierMean/$newFile";
					}
					else
					{
						if($fichier =~ /^bestfittime.dat$/)
						{
							my $newFile = "bestfittime" . $num . ".dat";
							system "cp $dossier/$subDossier/$fichier $dossier/$dossierBest/$newFile";
						}
					}
				}
			}
		}
		
		$numIter++;
	}
}
