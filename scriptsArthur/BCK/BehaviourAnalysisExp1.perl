#!/usr/bin/perl

use strict;
#use File::basename;

my $numArg = 0;
my $dossier = "";
my $prefixeDossier = "node";
my $dossierOut = "BehaviouralAnalysis";
my $refactory = 0;
my $precision = 100;
my $nbEvaluationByGen = 20;
my $lastGen = 4400;
my $exec = "StagHuntExp1_parallel_fitprop";

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
			if($arg =~ "-o")
			{
				$numArg++;
				$dossierOut = $ARGV[$numArg];
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
					if($arg =~ "-n")
					{
						$numArg++;
						$nbEvaluationByGen = $ARGV[$numArg];
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
              if($arg =~ "-x")
              {
                $numArg++;
                $exec = $ARGV[$numArg];
                $numArg++;
              }
            }
          }
				}
			}
		}
	}
}

opendir DIR, $dossier or die $!;
my @dossiers = grep {/^[^.]/} readdir(DIR);
closedir DIR;

if(! -e "$dossier/$dossierOut")
{
	system "mkdir $dossier/$dossierOut";
}

my $dossierRef = "$dossier/$dossierOut/Refactor";

if(! -e "$dossierRef")
{
	system "mkdir $dossierRef";
}

open FILEREFCONTROL, ">$dossierRef/refactControl.dat" or die $!;
print FILEREFCONTROL "Evaluation,Run,NbGoHare,NbGoStag\n";

open FILEREFCOOP, ">$dossierRef/refactCoop.dat" or die $!;
print FILEREFCOOP "Evaluation,Run,NbGoHare,NbGoStag\n";

open FILEREFDIST, ">$dossierRef/refactDist.dat" or die $!;
print FILEREFDIST "Evaluation,Run,NbGoHare,NbGoStag\n";
	
my $numIter = 1;
my $nbDossiers = scalar(@dossiers);
foreach my $subDossier (@dossiers)
{
	if($subDossier =~ /^$prefixeDossier/)
	{
		print "File : $subDossier ($numIter/$nbDossiers)\n";
	
		my $dossierRun = "$dossier/$dossierOut/Run$numIter";
		if(! -e "$dossierRun")
		{
			system "mkdir $dossierRun";
		}
	
		my $dossierControl = "$dossierRun/Control";
		my $dossierCoop = "$dossierRun/Coop";
		my $dossierDist = "$dossierRun/Dist";
		
		if(! -e "$dossierControl")
		{
			system "mkdir $dossierControl";
		}
		
		if(! -e "$dossierCoop")
		{
			system "mkdir $dossierCoop";
		}
		
		if(! -e "$dossierDist")
		{
			system "mkdir $dossierDist";
		}
	
		opendir DIR, "$dossier/$subDossier" or die $!;
		my @fichiers = grep {/^gen_/} readdir(DIR);
		closedir DIR;
		
		open FILERUNCONTROL, ">$dossierRef/refactControl_run$numIter.dat" or die $!;
		print FILERUNCONTROL "Evaluation,NbGoHare,NbGoStag\n";
		
		open FILERUNITERCONTROL, ">$dossierRef/refactIterControl_run$numIter.dat" or die $!;
		print FILERUNITERCONTROL "Iteration,GoHare,GoStag\n";

		open FILERUNCOOP, ">$dossierRef/refactCoop_run$numIter.dat" or die $!;
		print FILERUNCOOP "Evaluation,NbGoHare,NbGoStag\n";
		
		open FILERUNITERCOOP, ">$dossierRef/refactIterCoop_run$numIter.dat" or die $!;
		print FILERUNITERCOOP "Iteration,GoHare,GoStag\n";

		open FILERUNDIST, ">$dossierRef/refactDist_run$numIter.dat" or die $!;
		print FILERUNDIST "Evaluation,NbGoHare,NbGoStag\n";
		
		open FILERUNITERDIST, ">$dossierRef/refactIterDist_run$numIter.dat" or die $!;
		print FILERUNITERDIST "Iteration,GoHare,GoStag\n";
		
		my $nbFichiers = scalar(@fichiers);
		my $numFichier = 1;
		foreach my $fichier (@fichiers)
		{
			if($fichier =~ /^gen_([0-9]*)/)
			{
				print "\tFile : $fichier ($numFichier/$nbFichiers)\n";
			
				my $numGen = $1;
				my $numEvaluation = $numGen*$nbEvaluationByGen;
				
				# CONTROL
				print "\t->### CONTROL ###\n";

				system "./build/default/exp/StagHuntExp1Test/" . $exec . " --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*)$/)
					{
						print FILERUNCONTROL "$numEvaluation,$1,$2\n";
						print FILEREFCONTROL "$numEvaluation,$numIter,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoStag = $3;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERCONTROL "$numIteration,$GoHare,$GoStag\n";
							}						
						}
					}
					
					close FILEIN;
				}

				system "mv -f choices.txt $dossierControl/choices_gen_$numGen.dat";
				system "mv -f iterations.txt $dossierControl/iterations_gen_$numGen.dat";
				
				# COOP
				print "\t->### COOP ###\n";

				system "./build/default/exp/StagHuntExp1Test/" . $exec . "_coop --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*)$/)
					{
						print FILERUNCOOP "$numEvaluation,$1,$2\n";
						print FILEREFCOOP "$numEvaluation,$numIter,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,[0-9]*,([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoStag = $3;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERCOOP "$numIteration,$GoHare,$GoStag\n";
							}						
						}
					}
					
					close FILEIN;
				}
				
				system "mv -f choices.txt $dossierCoop/choices_gen_$numGen.dat";
				system "mv -f iterations.txt $dossierCoop/iterations_gen_$numGen.dat";
				
				# DIST
				print "\t->### DIST ###\n";

				system "./build/default/exp/StagHuntExp1Test/" . $exec . "_dist_changed --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*)$/)
					{
						print FILERUNDIST "$numEvaluation,$1,$2\n";
						print FILEREFDIST "$numEvaluation,$numIter,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,[0-9]*,([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoStag = $3;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERDIST "$numIteration,$GoHare,$GoStag\n";
							}						
						}
					}
					
					close FILEIN;
				}
				
				system "mv -f choices.txt $dossierDist/choices_gen_$numGen.dat";
				system "mv -f iterations.txt $dossierDist/iterations_gen_$numGen.dat";
			}
				
			$numFichier++;
		}
		
		close FILERUNCONTROL;
		close FILERUNCOOP;
		close FILERUNDIST;
		
		$numIter++;
	}
}

close FILEREFCONTROL;
close FILEREFCOOP;
close FILEREFDIST;
