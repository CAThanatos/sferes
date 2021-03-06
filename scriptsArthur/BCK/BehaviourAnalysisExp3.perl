#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd;
use Cwd "abs_path";

my $numArg = 0;
my $dossier = "";
my $prefixeDossier = "Dir";
my $refactory = "BehaviouralAnalysis";
my $precision = 100;
my $genInd = -1;
my $exec = "StagHuntExp2_parallel_mlp_fitprop";
my $setting = 0;
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
          if($arg =~ "-x")
          {
            $numArg++;
            $exec = $ARGV[$numArg];
            $numArg++;
          }
          else
          {
          	if($arg =~ "-s")
          	{
          		$numArg++;
          		$setting = $ARGV[$numArg];
          		$numArg++;
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
}

my $logFile = "log.txt";
open FILELOG, ">>$logFile" or die $!;

opendir DIR, $dossier or die $!;
my @dossiers = grep {/^[^.]/} readdir(DIR);
closedir DIR;

my $dossierRef = "$dossier/Refactor";
if($numAnalysis == 2)
{
	$dossierRef = "$dossier/Refactor2";
}

if(-e "$dossierRef")
{
	system "rm -r $dossierRef";
}
system "mkdir $dossierRef";

if($setting == 1 || $setting == 2 || $setting == 4)
{
	open FILEREFCOOPHARE, ">$dossierRef/refactCoopHare.dat" or die $!;
	print FILEREFCOOPHARE "Run,NbGoCoop,NbNoCoop\n";
	
	open FILEREFCOOPHAREPRED, ">$dossierRef/refactCoopHarePred.dat" or die $!;
	print FILEREFCOOPHAREPRED "Run,NbGoCoop,NbNoCoop\n";
}

if($setting == 2 || $setting == 3 || $setting == 5)
{	
	open FILEREFCOOPSSTAG, ">$dossierRef/refactCoopSStag.dat" or die $!;
	print FILEREFCOOPSSTAG "Run,NbGoCoop,NbNoCoop\n";
	
	open FILEREFCOOPSSTAGPRED, ">$dossierRef/refactCoopSStagPred.dat" or die $!;
	print FILEREFCOOPSSTAGPRED "Run,NbGoCoop,NbNoCoop\n";
}

if($setting == 4 || $setting == 5 || $setting == 6)
{	
	open FILEREFCOOPBSTAG, ">$dossierRef/refactCoopBStag.dat" or die $!;
	print FILEREFCOOPBSTAG "Run,NbGoCoop,NbNoCoop\n";
	
	open FILEREFCOOPBSTAGPRED, ">$dossierRef/refactCoopBStagPred.dat" or die $!;
	print FILEREFCOOPBSTAGPRED "Run,NbGoCoop,NbNoCoop\n";
}

my $numIter = 1;
my $nbDossiers = scalar(@dossiers);
foreach my $subDossier (@dossiers)
{
	if($subDossier =~ /^$prefixeDossier/)
	{
		print "File : $subDossier ($numIter/$nbDossiers)\n";
	
		my $num = $numIter;
		
		if($subDossier =~ /^$prefixeDossier(\d+)$/)
		{
			$num = $1;
		}
		
		my $dossierRun = "$dossierRef/Run$num";
		system "mkdir $dossierRun";
		print "$dossierRun\n";
				
		opendir DIR, "$dossier/$subDossier" or die $!;
		my @fichiers = grep {/^gen_/} readdir(DIR);
		closedir DIR;
		
		# On cherche la dernière génération
		my $numLastGen = 0;

		foreach my $fichier (@fichiers)
		{
			if($fichier =~ /^gen_(\d+)$/)
			{
				my $gen = $1;
				if($gen > $numLastGen)
				{
					$numLastGen = $gen;
				}
			}
		}
		$genInd = $numLastGen;
			
		if($setting == 0)
		{
			print "Aucun setting n'a été spécifié !\n";
			exit 1;
		}
		else
		{
			if($setting == 1 || $setting == 2 || $setting == 4)
			{
				open FILERUNCOOPHARE, ">$dossierRef/refactCoopHare_run$num.dat" or die $!;
				print FILERUNCOOPHARE "NbGoCoop,NbNoCoop\n";
		
				open FILERUNITERCOOPHARE, ">$dossierRef/refactIterCoopHare_run$num.dat" or die $!;
				print FILERUNITERCOOPHARE "Iteration,GoCoop,NoCoop\n";
		
				open FILERUNITERCOOPHAREPRED, ">$dossierRef/refactIterCoopHarePred_run$num.dat" or die $!;
				print FILERUNITERCOOPHAREPRED "Iteration,GoCoop,NoCoop\n";

				# COOP HARE
				print "\t->### COOP HARE ###\n";
				
				my $command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_hare --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_replace_hare --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP HARE ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPHARE "$1,$2\n";
						print FILEREFCOOPHARE "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPHARE "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopHare_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopHare_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopHare_run$num.dat";
				
				# COOP HARE PRED PRESENT
				print "\t->### COOP HARE PRED PRESENT ###\n";
				
				$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_hare_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_coop_hare_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP HARE PRED PRESENT ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPHARE "$1,$2\n";
						print FILEREFCOOPHAREPRED "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPHAREPRED "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopHarePred_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopHarePred_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopHarePred_run$num.dat";
		
				close FILERUNCOOPHARE;
				close FILERUNITERCOOPHARE;
				close FILERUNITERCOOPHAREPRED;
			}
			
			if($setting == 2 || $setting == 3 || $setting == 5)
			{		
				open FILERUNCOOPSSTAG, ">$dossierRef/refactCoopSStag_run$num.dat" or die $!;
				print FILERUNCOOPSSTAG "NbGoCoop,NbNoCoop\n";
		
				open FILERUNITERCOOPSSTAG, ">$dossierRef/refactIterCoopSStag_run$num.dat" or die $!;
				print FILERUNITERCOOPSSTAG "Iteration,GoCoop,NoCoop\n";
		
				open FILERUNITERCOOPSSTAGPRED, ">$dossierRef/refactIterCoopSStagPred_run$num.dat" or die $!;
				print FILERUNITERCOOPSSTAGPRED "Iteration,GoCoop,NoCoop\n";
		
				# COOP SSTAG
				print "\t->### COOP SSTAG ###\n";
				
				my $command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_sstag --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_replace_sstag --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP SSTAG ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPSSTAG "$1,$2\n";
						print FILEREFCOOPSSTAG "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPSSTAG "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopSStag_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopSStag_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopSStag_run$num.dat";
				
				# COOP SSTAG PRED PRESENT
				print "\t->### COOP SSTAG PRED PRESENT ###\n";
				
				$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_sstag_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_coop_sstag_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP SSTAG PRED PRESENT ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPSSTAG "$1,$2\n";
						print FILEREFCOOPSSTAGPRED "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPSSTAGPRED "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopSStagPred_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopSStagPred_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopSStagPred_run$num.dat";

				close FILERUNCOOPSSTAG;
				close FILERUNITERCOOPSSTAG;
				close FILERUNITERCOOPSSTAGPRED;
			}
			
			if($setting == 4 || $setting == 5 || $setting == 6)
			{
				open FILERUNCOOPBSTAG, ">$dossierRef/refactCoopBStag_run$num.dat" or die $!;
				print FILERUNCOOPBSTAG "NbGoCoop,NbNoCoop\n";
		
				open FILERUNITERCOOPBSTAG, ">$dossierRef/refactIterCoopBStag_run$num.dat" or die $!;
				print FILERUNITERCOOPBSTAG "Iteration,GoCoop,NoCoop\n";
		
				open FILERUNITERCOOPBSTAGPRED, ">$dossierRef/refactIterCoopBStagPred_run$num.dat" or die $!;
				print FILERUNITERCOOPBSTAGPRED "Iteration,GoCoop,NoCoop\n";
			
				# COOP BSTAG
				print "\t->### COOP BSTAG ###\n";
				
				my $command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_bstag --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_replace_bstag --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP BSTAG ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPBSTAG "$1,$2\n";
						print FILEREFCOOPBSTAG "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPBSTAG "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopBStag_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopBStag_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopBStag_run$num.dat";
				
				# COOP BSTAG PRED PRESENT
				print "\t->### COOP BSTAG PRED PRESENT ###\n";
				
				$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis/" . $exec . "_setting" . $setting . "_coop_bstag_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				if($numAnalysis == 2)
				{
					$command = "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2-BehaviourAnalysis2/" . $exec . "_setting" . $setting . "_coop_bstag_pred_present --load $dossier/$subDossier/gen_$genInd -o output.txt";
				}
				
				if($log == 1)
				{
					print FILELOG "\t->### COOP BSTAG PRED PRESENT ###\n";
					print FILELOG "$command\n";
					my $output = `$command`;
					print FILELOG "$output\n";
				}
				else
				{				
					system $command;
				}
				
				open FILEIN, "<choices.txt" or die $!;
				
				while (my $ligne=<FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+)$/)
					{
						print FILERUNCOOPBSTAG "$1,$2\n";
						print FILEREFCOOPBSTAGPRED "$num,$1,$2\n";
					}
				}
				
				close FILEIN;
				
				open FILEIN, "<iterations.txt" or die $!;
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d+),(\d+),(\d+)$/)
					{
						my $numIteration = $1;
						my $goCoop = $2;
						my $noCoop = $3;
						
						if($numIteration % $precision == 0)
						{
							print FILERUNITERCOOPBSTAGPRED "$numIteration,$goCoop,$noCoop\n";
						}
					}
				}
				
				close FILEIN;

				system "mv -f choices.txt $dossierRun/choicesCoopBStagPred_run$num.dat";
				system "mv -f iterations.txt $dossierRun/iterationsCoopBStagPred_run$num.dat";
				system "mv -f output.txt $dossierRun/outputCoopBStagPred_run$num.dat";

				close FILERUNCOOPBSTAG;
				close FILERUNITERCOOPBSTAG;
				close FILERUNITERCOOPBSTAGPRED;
			}
			
				
			my $abs_dir = dirname(abs_path($0));
			my $workingDir = getcwd;
			chdir "$dossierRef";
			system "Rscript $abs_dir/RScriptBehaviourExp3.R $num 10000 $setting";
			chdir "$workingDir";
		}
		
		$numIter++;
	}
}

if($setting == 1 || $setting == 2 || $setting == 4)
{
	close FILEREFCOOPHARE;
	close FILEREFCOOPHAREPRED;
}

if($setting == 2 || $setting == 3 || $setting == 5)
{	
	close FILEREFCOOPSSTAG;
	close FILEREFCOOPSSTAGPRED;
}

if($setting == 4 || $setting == 5 || $setting == 6)
{	
	close FILEREFCOOPBSTAG;
	close FILEREFCOOPBSTAGPRED;
}

sub printHelp()
{
	print "Usage : ./BehaviourAnalysisExp3.perl -d FilesDirectory [-f DirectoryPrefix] [-x Executable] [-p Precision] [-g GenInd] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-f : Prefix of all the directories that have to be computed. \"Dir\" by default\n";
	print "\t-x : Program of Behavioural Analysis that will be executed. StagHuntExp2_parallel_mlp_fitprop by default\n";
	print "\t-p : Precision in number of generations. 100 by default\n";
	print "\t-g : From which generation the individual must be analysed. By default, we take the one from the last generation\n";
	print "\t-h : Prints this help\n";
	exit;
}
