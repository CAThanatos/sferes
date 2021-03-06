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
my $exec = "StagHuntExp2_parallel_fitprop_mlp";

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
print FILEREFCONTROL "Evaluation,Run,NbGoHare,NbGoSmallStag,NbGoBigStag\n";

open FILEREFCOOP, ">$dossierRef/refactCoop.dat" or die $!;
print FILEREFCOOP "Evaluation,Run,NbGoHare,NbGoSmallStag,NbGoBigStag\n";

open FILEREFDIST, ">$dossierRef/refactDist.dat" or die $!;
print FILEREFDIST "Evaluation,Run,NbGoHare,NbGoSmallStag,NbGoBigStag\n";
	
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
		print FILERUNCONTROL "Evaluation,NbGoHare,NbGoSmallStag,NbGoBigStag\n";
		
		open FILERUNITERCONTROL, ">$dossierRef/refactIterControl_run$numIter.dat" or die $!;
		print FILERUNITERCONTROL "Iteration,GoHare,GoSmallStag,GoBigStag\n";

		open FILERUNCOOP, ">$dossierRef/refactCoop_run$numIter.dat" or die $!;
		print FILERUNCOOP "Evaluation,NbGoHare,NbGoSmallStag,NbGoBigStag\n";
		
		open FILERUNITERCOOP, ">$dossierRef/refactIterCoop_run$numIter.dat" or die $!;
		print FILERUNITERCOOP "Iteration,GoHare,GoSmallStag,GoBigStag\n";

		open FILERUNDIST, ">$dossierRef/refactDist_run$numIter.dat" or die $!;
		print FILERUNDIST "Evaluation,NbGoHare,NbGoSmallStag,NbGoBigStag\n";
		
		open FILERUNITERDIST, ">$dossierRef/refactIterDist_run$numIter.dat" or die $!;
		print FILERUNITERDIST "Iteration,GoHare,GoSmallStag,GoBigStag\n";
		
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

				system "./build/default/exp/StagHuntExp2BehaviourAnalysis/" . $exec . " --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*),([0-9]*)$/)
					{
						print FILERUNCONTROL "$numEvaluation,$1,$2,$3\n";
						print FILEREFCONTROL "$numEvaluation,$numIter,$1,$2,$3\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,([0-9]*),([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoSStag = $3;
							my $GoBStag = $4;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERCONTROL "$numIteration,$GoHare,$GoSStag,$GoBStag\n";
							}						
						}
					}
					
					close FILEIN;
				}

				system "mv -f choices.txt $dossierControl/choices_gen_$numGen.dat";
				system "mv -f iterations.txt $dossierControl/iterations_gen_$numGen.dat";
				
				# COOP
				print "\t->### COOP ###\n";

				system "./build/default/exp/StagHuntExp2BehaviourAnalysis/" . $exec . "_coop --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*),([0-9]*)$/)
					{
						print FILERUNCOOP "$numEvaluation,$1,$2,$3\n";
						print FILEREFCOOP "$numEvaluation,$numIter,$1,$2,$3\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,[0-9]*,[0-9]*,[0-9]*,([0-9]*),([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoSStag = $3;
							my $GoBStag = $4;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERCOOP "$numIteration,$GoHare,$GoSStag,$GoBStag\n";
							}						
						}
					}
					
					close FILEIN;
				}
				
				system "mv -f choices.txt $dossierCoop/choices_gen_$numGen.dat";
				system "mv -f iterations.txt $dossierCoop/iterations_gen_$numGen.dat";
				
				# DIST
				print "\t->### DIST ###\n";

				system "./build/default/exp/StagHuntExp2BehaviourAnalysis/" . $exec . "_dist_changed --load $dossier/$subDossier/$fichier -o output.txt";
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^([0-9]*),([0-9]*),([0-9]*)$/)
					{
						print FILERUNDIST "$numEvaluation,$1,$2,$3\n";
						print FILEREFDIST "$numEvaluation,$numIter,$1,$2,$3\n";
					}
				}
				
				close FILEIN;
				
				if($numGen == $lastGen)
				{
					open FILEIN, "<iterations.txt" or die $!;
					
					while (my $ligne=<FILEIN>)
					{
						chomp $ligne;
						
						if($ligne =~ /^([0-9]*),[0-9]*,[0-9]*,[0-9]*,[0-9]*,([0-9]*),([0-9]*),([0-9]*)$/)
						{
							my $numIteration = $1;
							my $GoHare = $2;
							my $GoSStag = $3;
							my $GoBStag = $4;
						
							if($numIteration % $precision == 0)
							{
								print FILERUNITERDIST "$numIteration,$GoHare,$GoSStag,$GoBStag\n";
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


sub printHelp()
{
	print "Usage : ./BehaviourAnalysisExp2.perl -d FilesDirectory [-o OutputDirectory] [-f DirectoryPrefix] [-n NumberOfEvalByGen] [-x Executable] [-p Precision] [-g LastGen] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-o : Output directory. BehaviouralAnalysis by default. Will be created if it does not exist\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"node\" by default (results from the isir cluster)\n";
	print "\t-n : Number of evaluations by generation. 20 by default\n";
	print "\t-x : Program of Behavioural Analysis that will be executed. StagHuntExp2_parallel_fitprop_mlp by default\n";
	print "\t-p : Precision in number of generations. 100 by default\n";
	print "\t-g : Last generation computed. 4400 by default\n";
	print "\t-h : Prints this help\n";
	exit;
}
