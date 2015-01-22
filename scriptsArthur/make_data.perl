#!/usr/bin/perl

use strict;
use File::Basename;

my @fichiers = ();
my $dossier = "0";
my $boolDossier = 0;
my $numArg = 0;
my $fileOutput = "refactData";
my $precision = 1000;
my $iterMax = -1;
my $countTime = 0;

while ($numArg < scalar(@ARGV))
{
	my $arg = $ARGV[$numArg];
	if($arg =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
		$boolDossier = 1;
		$numArg++;
	}
	else
	{
		if($arg =~ "-f")
		{
			$numArg++;
			$arg = $ARGV[$numArg];
			while($arg !~ /^-/ && $numArg < scalar(@ARGV))
			{
				push @fichiers, $arg;
				$numArg++;
				if($numArg < scalar(@ARGV))
				{
					$arg = $ARGV[$numArg];
				}
			}
		}
		else
		{
			if($arg =~ "-o")
			{
				$numArg++;
				$fileOutput = $ARGV[$numArg];
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
					if($arg =~ "-m")
					{
						$numArg++;
						$iterMax = $ARGV[$numArg];
						$numArg++;
					}
					else
					{
						if($arg =~ "-c")
						{
							$numArg++;
							$countTime = 1;
						}
					}
				}
			}
		}
	}
}

if($boolDossier != 0)
{
	opendir DIR, $dossier or die $!;
	@fichiers = grep {/^[^.]/} readdir(DIR);
	closedir DIR;
}

my %dataFitness = ();
my %dataHaresDuo = ();
my %dataHaresSolo = ();
my %dataSStagsDuo = ();
my %dataSStagsSolo = ();
my %dataBStagsDuo = ();
my %dataBStagsSolo = ();

my $stringLineGlob = "Evaluation,Run,Fitness,NbHaresDuo,NbHaresSolo,NbHares,NbSStagsDuo,NbSStagsSolo,NbSStags,NbBStagsDuo,NbBStagsSolo,NbBStags\n";
my $numFichier = 0;

# On cherche la dernière itération si besoin
if($iterMax == -1)
{
	foreach my $fichier (@fichiers)
	{
		if($fichier =~ /fit(\d*)\.dat$/)
		{
			my $fichierAlt = $fichier;
			if($boolDossier != 0)
			{
				$fichierAlt = $dossier . "/" . $fichier;
			}

			open FILEIN, "<$fichierAlt" or die $!;

			my $lastIter = 0;
			while(my $ligne = <FILEIN>)
			{
				chomp $ligne;

				if($ligne =~ /^(\d*),([^,]*),([^,]*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)$/)
				{
					$lastIter = $1;
				}
			}

			if(($iterMax == -1) || ($lastIter < $iterMax))
			{
				$iterMax = $lastIter;
			}
		}
	}
}


foreach my $fichier (@fichiers)
{
	if($fichier =~ /fit(\d*)\.dat$/)
	{
		$numFichier = $1;
		my $stringRun = "Evaluation,Fitness,NbHaresDuo,NbHaresSolo,NbHares,NbSStagsDuo,NbSStagsSolo,NbSStags,NbBStagsDuo,NbBStagsSolo,NbBStags\n";
		if($boolDossier != 0)
		{
			$fichier = $dossier . "/" . $fichier;
		}

		open FILEIN, "<$fichier" or die $!;

		my $first = 1;
		my $stop = 0;
		my $cumulIteration = 0;
		my $lastIteration = 0;
		while ((my $ligne = <FILEIN>) && ($stop == 0))
		{
			chomp $ligne;
	
			if($ligne =~ /^(\d*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)$/)
			{
				my $iteration = $1;

				my $fitness = $2;
				my $nbHares = $3;
				my $nbHaresSolo = $4;
				my $nbSStags = $5;
				my $nbSStagsSolo = $6;
				my $nbBStags = $7;
				my $nbBStagsSolo = $8;
		
				if(!exists($dataFitness{$iteration}))
				{
					my @tab_fitness = ();
					push @tab_fitness, $fitness;
					$dataFitness{$iteration} = \@tab_fitness;

					my @tab_hares_duo = ();
					push @tab_hares_duo, ($nbHares - $nbHaresSolo);
					$dataHaresDuo{$iteration} = \@tab_hares_duo;

					my @tab_hares_solo = ();
					push @tab_hares_solo, $nbHaresSolo;
					$dataHaresSolo{$iteration} = \@tab_hares_solo;

					my @tab_sstags_duo = ();
					push @tab_sstags_duo, ($nbSStags - $nbSStagsSolo);
					$dataSStagsDuo{$iteration} = \@tab_sstags_duo;

					my @tab_sstags_solo = ();
					push @tab_sstags_solo, $nbSStagsSolo;
					$dataSStagsSolo{$iteration} = \@tab_sstags_solo;

					my @tab_bstags_duo = ();
					push @tab_bstags_duo, ($nbBStags - $nbBStagsSolo);
					$dataBStagsDuo{$iteration} = \@tab_bstags_duo;

					my @tab_bstags_solo = ();
					push @tab_bstags_solo, $nbBStagsSolo;
					$dataBStagsSolo{$iteration} = \@tab_bstags_solo;
				}
				else
				{
					my $ref_tab = $dataFitness{$iteration};
					push @{$ref_tab}, $fitness;

					$ref_tab = $dataHaresDuo{$iteration};
					push @{$ref_tab}, ($nbHares - $nbHaresSolo);

					$ref_tab = $dataHaresSolo{$iteration};
					push @{$ref_tab}, $nbHaresSolo;

					$ref_tab = $dataSStagsDuo{$iteration};
					push @{$ref_tab}, ($nbSStags - $nbSStagsSolo);

					$ref_tab = $dataSStagsSolo{$iteration};
					push @{$ref_tab}, $nbSStagsSolo;

					$ref_tab = $dataBStagsDuo{$iteration};
					push @{$ref_tab}, ($nbBStags - $nbBStagsSolo);

					$ref_tab = $dataBStagsSolo{$iteration};
					push @{$ref_tab}, $nbBStagsSolo;
				}

				$cumulIteration += ($iteration - $lastIteration);
				$lastIteration = $iteration;
				if(($cumulIteration > $precision) || ($first == 1))
				{
					my $nbHaresDuo = $nbHares - $nbHaresSolo;
					my $nbSStagsDuo = $nbSStags - $nbSStagsSolo;
					my $nbBStagsDuo = $nbBStags - $nbBStagsSolo;

					$stringLineGlob = $stringLineGlob . "$iteration,$numFichier,$fitness,$nbHaresDuo,$nbHaresSolo,$nbHares,$nbSStagsDuo,$nbSStagsSolo,$nbSStags,$nbBStagsDuo,$nbBStagsSolo,$nbBStags\n";
					$stringRun = $stringRun . "$iteration,$fitness,$nbHaresDuo,$nbHaresSolo,$nbHares,$nbSStagsDuo,$nbSStagsSolo,$nbSStags,$nbBStagsDuo,$nbBStagsSolo,$nbBStags\n";
				
					if($first == 1)
					{
						$first = 0;
					}
					else
					{
						$cumulIteration = 0;
					}
				}
			
				if(($iterMax != -1) and ($iteration >= $iterMax))
				{
					$stop = 1;
				}
			}
		}

		open FILEOUT, (">" . $dossier . "/" . $fileOutput . "_run" . $numFichier . ".dat") or die $!; 
	
		print FILEOUT $stringRun;
	
		close FILEOUT;

		close FILEIN;
	}
	else
	{
		if($countTime == 1 && $fichier =~ /fittime(\d+)\.dat$/)
		{
			$numFichier = $1;
			my $stringRun = "Evaluation,Fitness,TimeOnHares,TimeOnSStags,TimeOnBStags,TimeTotal\n";
			if($boolDossier != 0)
			{
				$fichier = $dossier . "/" . $fichier;
			}

			open FILEIN, "<$fichier" or die $!;

			my $first = 1;
			my $stop = 0;
			my $cumulIteration = 0;
			my $lastIteration = 0;
			while ((my $ligne = <FILEIN>) && ($stop == 0))
			{
				chomp $ligne;
	
				if($ligne =~ /^(\d*),([^,]*),([^,]*),([^,]*),([^,]*)$/)
				{
					my $iteration = $1;

					my $fitness = $2;
					my $timeOnHares = $3;
					my $timeOnSStags = $4;
					my $timeOnBStags = $5;
		
					$cumulIteration += ($iteration - $lastIteration);
					$lastIteration = $iteration;
					if(($cumulIteration > $precision) || ($first == 1))
					{
						my $totalTime = $timeOnHares + $timeOnSStags + $timeOnBStags;
				
						$stringRun = $stringRun . "$iteration,$fitness,$timeOnHares,$timeOnSStags,$timeOnBStags,$totalTime\n";
				
						if($first == 1)
						{
							$first = 0;
						}
						else
						{
							$cumulIteration = 0;
						}
					}
			
					if(($iterMax != -1) and ($iteration >= $iterMax))
					{
						$stop = 1;
					}
				}
			}

			open FILEOUT, (">" . $dossier . "/" . $fileOutput . "Time_run" . $numFichier . ".dat") or die $!; 
	
			print FILEOUT $stringRun;
	
			close FILEOUT;

			close FILEIN;
		}
	}
}


open FILEOUT, (">" . $dossier . "/" . $fileOutput . ".dat") or die $!;

print FILEOUT $stringLineGlob;

close FILEOUT;

