#!/usr/bin/perl

use strict;
use Switch;
use Cwd "abs_path";
use File::Basename;

my $dossier = 0;
my $numArg = 0;
my $meanFromEval = 10000;
my $setting = 0;

while($numArg < scalar(@ARGV))
{
	if($ARGV[$numArg] =~ "d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
	}
	else
	{
		if($ARGV[$numArg] =~ /^-s$/)
		{
			$numArg++,
			$setting = $ARGV[$numArg];
		}
		else
		{
			if($ARGV[$numArg] =~ "-h")
			{
				&printHelp();
			}
		}
	}

	$numArg++;
}

opendir DIR, "$dossier" or die $!;
my @fichiers = grep {/^[^.]/} readdir(DIR);
closedir DIR;

my %tabMeansHaresSolo = ();
my %tabMeansHaresDuo = ();
my %tabMeansSStagsSolo = ();
my %tabMeansSStagsDuo = ();
my %tabMeansBStagsSolo = ();
my %tabMeansBStagsDuo = ();
my $nbRuns = 0;

foreach my $fichier (@fichiers)
{
	if($fichier =~ /^refactData_run(\d*).dat$/)
	{
		my $numRun = $1;

		open FILEIN, "<$dossier/$fichier" or die $!;
		
		my $minStags = 10000;
		my $minHares = 10000;
		my $minBStags = 10000;
		while (my $ligne = <FILEIN>)
		{
			chomp $ligne;

			if($ligne =~ /^(\d*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)$/)
			{
				my $eval = $1;
				my $nbHaresDuo = $2;
				my $nbHaresSolo = $3;
				my $nbSStagsDuo = $5;
				my $nbSStagsSolo = $6;
				my $nbBStagsDuo = $8;
				my $nbBStagsSolo = $9;
				
				if(($nbSStagsSolo < $minStags) && ($nbSStagsSolo > 0))
				{
					$minStags = $nbSStagsSolo;
				}

				if(($nbHaresSolo < $minHares) && ($nbHaresSolo > 0))
				{
					$minHares = $nbHaresSolo;
				}

				if(($nbBStagsSolo < $minBStags) && ($nbBStagsSolo > 0))
				{
					$minBStags = $nbBStagsSolo;
				}
			}
		}

		if($minStags == 10000)
		{
			$minStags = 0.1;
		}
		if($minHares == 10000)
		{
			$minHares = 0.1;
		}
		if($minBStags == 10000)
		{
			$minBStags = 0.1;
		}
		
		close FILEIN;

		open FILEIN, "<$dossier/$fichier" or die $!;
		open FILEOUT, ">$dossier/refactDataRatio_run$numRun.dat";

		print FILEOUT "Evaluation,RatioHares,RatioHaresSolo,RatioHaresDuo,RatioSStags,RatioSStagsSolo,RatioSStagsDuo,RatioBStags,RatioBStagsSolo,RatioBStagsDuo\n";

		while (my $ligne = <FILEIN>)
		{
			chomp $ligne;

			if($ligne =~ /^(\d*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)$/)
			{
				my $eval = $1;
				my $nbHaresDuo = $2;
				my $nbHaresSolo = $3;
				my $nbHares = $4;
				my $nbSStagsDuo = $5;
				my $nbSStagsSolo = $6;
				my $nbSStags = $7;
				my $nbBStagsDuo = $8;
				my $nbBStagsSolo = $9;
				my $nbBStags = $10;
				
				my $ratioHares = 0;
				my $ratioHaresSolo = 0;
				my $ratioHaresDuo = 0;
				my $ratioSStags = 0;
				my $ratioSStagsSolo = 0;
				my $ratioSStagsDuo = 0;
				my $ratioBStags = 0;
				my $ratioBStagsSolo = 0;
				my $ratioBStagsDuo = 0;

				switch ($setting)
				{
					case [1..4]
					{
						# Hare - SStag
						my $totalPreys = $nbHares + $nbSStags;
						
						if($totalPreys != 0)
						{
							$ratioHares = $nbHares/$totalPreys;
							$ratioSStags = $nbSStags/$totalPreys;
						}
					}
					case [5..8]
					{
						# Hare - BStag
						my $totalPreys = $nbHares + $nbBStags;
						
						if($totalPreys != 0)
						{
							$ratioHares = $nbHares/$totalPreys;
							$ratioBStags = $nbBStags/$totalPreys;
						}
					}
					case [9..12]
					{
						# SStag - BStag
						my $totalPreys = $nbSStags + $nbBStags;
						
						if($totalPreys != 0)
						{
							$ratioSStags = $nbSStags/$totalPreys;
							$ratioBStags = $nbBStags/$totalPreys;
						}
					}
					case 13
					{
						# Hare Coop - Hare
						my $totalPreys = $nbHaresSolo + $nbHaresDuo;
						
						if($totalPreys != 0)
						{
							$ratioHaresSolo = $nbHaresSolo/$totalPreys;
							$ratioHaresDuo = $nbHaresDuo/$totalPreys;
						}
					}
					case 14
					{
						# SStag Coop - SStag
						my $totalPreys = $nbSStagsSolo + $nbSStagsDuo;
						
						if($totalPreys != 0)
						{
							$ratioSStagsSolo = $nbSStagsSolo/$totalPreys;
							$ratioSStagsDuo = $nbSStagsDuo/$totalPreys;
						}
					}
					case 15
					{
						# BStag Coop - BStag
						my $totalPreys = $nbBStagsSolo + $nbBStagsDuo;
						
						if($totalPreys != 0)
						{
							$ratioBStagsSolo = $nbBStagsSolo/$totalPreys;
							$ratioBStagsDuo = $nbBStagsDuo/$totalPreys;
						}
					}
					else
					{
						print "Wrong setting : $setting\n";
						exit 1;
					}
				}


				print FILEOUT "$eval,$ratioHares,$ratioHaresSolo,$ratioHaresDuo,$ratioSStags,$ratioSStagsSolo,$ratioSStagsDuo,$ratioBStags,$ratioBStagsSolo,$ratioBStagsDuo\n";
			
				if(!exists($tabMeansHaresSolo{$eval}))
				{
					$tabMeansHaresSolo{$eval} = $nbHaresSolo;
				}
				else
				{
					$tabMeansHaresSolo{$eval} = $tabMeansHaresSolo{$eval} + $nbHaresSolo;
				}
			
				if(!exists($tabMeansHaresDuo{$eval}))
				{
					$tabMeansHaresDuo{$eval} = $nbHaresDuo;
				}
				else
				{
					$tabMeansHaresDuo{$eval} = $tabMeansHaresDuo{$eval} + $nbHaresDuo;
				}
			
				if(!exists($tabMeansSStagsSolo{$eval}))
				{
					$tabMeansSStagsSolo{$eval} = $nbSStagsSolo;
				}
				else
				{
					$tabMeansSStagsSolo{$eval} = $tabMeansSStagsSolo{$eval} + $nbSStagsSolo;
				}

				if(!exists($tabMeansSStagsDuo{$eval}))
				{
					$tabMeansSStagsDuo{$eval} = $nbSStagsDuo;
				}
				else
				{
					$tabMeansSStagsDuo{$eval} = $tabMeansSStagsDuo{$eval} + $nbSStagsDuo;
				}
			
				if(!exists($tabMeansBStagsSolo{$eval}))
				{
					$tabMeansBStagsSolo{$eval} = $nbBStagsSolo;
				}
				else
				{
					$tabMeansBStagsSolo{$eval} = $tabMeansBStagsSolo{$eval} + $nbBStagsSolo;
				}
			
				if(!exists($tabMeansBStagsDuo{$eval}))
				{
					$tabMeansBStagsDuo{$eval} = $nbBStagsDuo;
				}
				else
				{
					$tabMeansBStagsDuo{$eval} = $tabMeansBStagsDuo{$eval} + $nbBStagsDuo;
				}
			}

		}

		close FILEOUT;
		close FILEIN;

		$nbRuns++;
	}
}

foreach my $eval (keys(%tabMeansHaresSolo))
{
	$tabMeansHaresSolo{$eval} = $tabMeansHaresSolo{$eval}/$nbRuns;
}

foreach my $eval (keys(%tabMeansHaresDuo))
{
	$tabMeansHaresDuo{$eval} = $tabMeansHaresDuo{$eval}/$nbRuns;
}

foreach my $eval (keys(%tabMeansSStagsSolo))
{
	$tabMeansSStagsSolo{$eval} = $tabMeansSStagsSolo{$eval}/$nbRuns;
}

foreach my $eval (keys(%tabMeansSStagsDuo))
{
	$tabMeansSStagsDuo{$eval} = $tabMeansSStagsDuo{$eval}/$nbRuns;
}

foreach my $eval (keys(%tabMeansBStagsSolo))
{
	$tabMeansBStagsSolo{$eval} = $tabMeansBStagsSolo{$eval}/$nbRuns;
}

foreach my $eval (keys(%tabMeansBStagsDuo))
{
	$tabMeansBStagsDuo{$eval} = $tabMeansBStagsDuo{$eval}/$nbRuns;
}

my @sortHaresSolo = sort {$b <=> $a} keys(%tabMeansHaresSolo);
my @sortHaresDuo = sort {$b <=> $a} keys(%tabMeansHaresDuo);
my @sortSStagsSolo = sort {$b <=> $a} keys(%tabMeansSStagsSolo);
my @sortSStagsDuo = sort {$b <=> $a} keys(%tabMeansSStagsDuo);
my @sortBStagsSolo = sort {$b <=> $a} keys(%tabMeansBStagsSolo);
my @sortBStagsDuo = sort {$b <=> $a} keys(%tabMeansBStagsDuo);

my $cpt = 0;
my $nbEvals = 0;
my $meanHaresSolo = 0;
my $ecartEvals = 1000;
if(scalar(@sortHaresSolo) > 0)
{
	$ecartEvals = @sortHaresSolo[0] - @sortHaresSolo[1];
}
while ($cpt < scalar(@sortHaresSolo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortHaresSolo[$cpt];

	$meanHaresSolo += $tabMeansHaresSolo{$eval};
	
	$nbEvals += $ecartEvals;
	$cpt++;
}

$meanHaresSolo = $meanHaresSolo/$cpt;

$cpt = 0;
$nbEvals = 0;
my $meanHaresDuo = 0;
if(scalar(@sortHaresDuo) > 0)
{
	$ecartEvals = @sortHaresDuo[0] - @sortHaresDuo[1];
}
while ($cpt < scalar(@sortHaresDuo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortHaresDuo[$cpt];

	$meanHaresDuo += $tabMeansHaresDuo{$eval};
	
	$nbEvals += $ecartEvals;
	$cpt++;
}
$meanHaresDuo = $meanHaresDuo/$cpt;

my $meanHares = $meanHaresDuo + $meanHaresSolo;

$cpt = 0;
$nbEvals = 0;
my $meanSStagsSolo = 0;
if(scalar(@sortSStagsSolo) > 0)
{
	$ecartEvals = @sortSStagsSolo[0] - @sortSStagsSolo[1];
}
while ($cpt < scalar(@sortSStagsSolo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortSStagsSolo[$cpt];

	$meanSStagsSolo += $tabMeansSStagsSolo{$eval};

	$nbEvals += $ecartEvals;
	$cpt++;
}
$meanSStagsSolo = $meanSStagsSolo/$cpt;

$cpt = 0;
$nbEvals = 0;
my $meanSStagsDuo = 0;
if(scalar(@sortSStagsDuo) > 0)
{
	$ecartEvals = @sortSStagsDuo[0] - @sortSStagsDuo[1];
}
while ($cpt < scalar(@sortSStagsDuo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortSStagsDuo[$cpt];

	$meanSStagsDuo += $tabMeansSStagsDuo{$eval};

	$nbEvals += $ecartEvals;
	$cpt++;
}
$meanSStagsDuo = $meanSStagsDuo/$cpt;

my $meanSStags = $meanSStagsDuo + $meanSStagsSolo;

$cpt = 0;
$nbEvals = 0;
my $meanBStagsSolo = 0;
if(scalar(@sortBStagsSolo) > 0)
{
	$ecartEvals = @sortBStagsSolo[0] - @sortBStagsSolo[1];
}
while ($cpt < scalar(@sortBStagsSolo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortBStagsSolo[$cpt];

	$meanBStagsSolo += $tabMeansBStagsSolo{$eval};

	$nbEvals += $ecartEvals;
	$cpt++;
}
$meanBStagsSolo = $meanBStagsSolo/$cpt;

$cpt = 0;
$nbEvals = 0;
my $meanBStagsDuo = 0;
if(scalar(@sortBStagsDuo) > 0)
{
	$ecartEvals = @sortBStagsDuo[0] - @sortBStagsDuo[1];
}
while ($cpt < scalar(@sortBStagsDuo) && $nbEvals <= $meanFromEval)
{
	my $eval = $sortBStagsDuo[$cpt];

	$meanBStagsDuo += $tabMeansBStagsDuo{$eval};

	$nbEvals += $ecartEvals;
	$cpt++;
}
$meanBStagsDuo = $meanBStagsDuo/$cpt;

my $meanBStags = $meanBStagsDuo + $meanBStagsSolo;

open FILEOUT, ">$dossier/refactMeans.dat" or die $!;

print FILEOUT "MeanHares,MeanHaresSolo,MeanHaresDuo,MeanSStags,MeanSStagsSolo,MeanSStagsDuo,MeanBStags,MeanBStagsSolo,MeanBStagsDuo\n";
print FILEOUT "$meanHares,$meanHaresSolo,$meanHaresDuo,$meanSStags,$meanSStagsSolo,$meanSStagsDuo,$meanBStags,$meanBStagsSolo,$meanBStagsDuo\n";

close FILEOUT;

sub printHelp()
{
	print "Usage : ./refactRatio.perl -d FilesDirectory [-s] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-s : Setting of the experiment\n";
	print "\t-h : Prints this help\n";
	exit;
}
