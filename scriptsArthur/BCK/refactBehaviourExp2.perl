#!/usr/bin/perl

use strict;

my $dossier = -1;
my $dossierRefact = -1;
my $precision = 100;
my $numArg = 0;
my $lastGen = 4400;

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
		if($arg =~ "-r")
		{
			$numArg++;
			$dossierRefact = $ARGV[$numArg];
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
					$lastGen = $ARGV[$numArg];
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

opendir DIR, "$dossier" or die $!;
my @dossiers = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $subDossier (@dossiers)
{
	if($subDossier =~ /^Run([0-9]*)/)
	{
		print "$subDossier\n";
	
		my $numRun = $1;
		
		opendir DIR, "$dossier/$subDossier" or die $!;
		my @subDossiers = grep {/^[^.]/} readdir(DIR);
		closedir DIR;
		
		foreach my $subSubDossier (@subDossiers)
		{
			print "\t->$subSubDossier\n";
			my $fileOut = "";
			my $control = 0;
			
			if($subSubDossier =~ /Control/)
			{
				$fileOut = "$dossierRefact/refactIterControl_run$numRun.dat";
				$control = 1;
			}
			else
			{
				if($subSubDossier =~ /Coop/)
				{
					$fileOut = "$dossierRefact/refactIterCoop_run$numRun.dat";
				}
				else
				{
					if($subSubDossier =~ /Dist/)
					{
						$fileOut = "$dossierRefact/refactIterDist_run$numRun.dat";
					}
				}
			}
			
			opendir DIR, "$dossier/$subDossier/$subSubDossier" or die $!;
			my @fichiers = grep {/^iterations_gen/} readdir(DIR);
			closedir DIR;
			
			my $chemin = "$dossier/$subDossier/$subSubDossier";
			foreach my $fichier (@fichiers)
			{
				if($fichier =~ /^iterations_gen_([0-9]*)\.dat$/)
				{
					my $gen = $1;
					
					if($gen == $lastGen)
					{
						print "\t\t->$fichier\n";
						open FILEIN, "<$chemin/$fichier" or die $!;
						open FILEOUT, ">$fileOut" or die $!;
						
						print FILEOUT "Iteration,GoHare,GoSmallStag,GoBigStag\n";
						while (my $ligne = <FILEIN>)
						{
							chomp $ligne;
							
							if($control == 1)
							{
								if($ligne =~ /^([0-9]*),[0-9]*,([0-9]*),([0-9]*)$/)
								{
									my $numIteration = $1;
									my $GoHare = $2;
									my $GoStag = $3;
								
									if($numIteration % $precision == 0)
									{
										print FILEOUT "$numIteration,$GoHare,$GoStag\n";
									}
								}
							}
							else
							{
								if($ligne =~ /^([0-9]*),[0-9]*,[0-9]*,([0-9]*),([0-9]*)$/)
								{
									my $numIteration = $1;
									my $GoHare = $2;
									my $GoStag = $3;
								
									if($numIteration % $precision == 0)
									{
										print FILEOUT "$numIteration,$GoHare,$GoStag\n";
									}
								}
							}
						}
						
						close FILEOUT;
						close FILEIN;
					}
				}
			}
		}
	}
}


sub printHelp()
{
	print "Usage : ./refactBehaviourExp2.perl -d FilesDirectory -r RefactoryDirectory [-p Precision] [-g LastGen] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-r : Output refactory directory\n";
	print "\t-p : Precision in number of generations. 100 by default\n";
	print "\t-g : Last generation computed. 4400 by default\n";
	print "\t-h : Prints this help\n";
}
