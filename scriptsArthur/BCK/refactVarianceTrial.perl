#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd;
use Cwd "abs_path";

my $dossier = 0;
my $precision = 100;

my $numArg = 0;
while($numArg < scalar(@ARGV))
{
	my $arg = $ARGV[$numArg];
	
	if($arg =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
	}
	else
	{
		if($arg =~ "-p")
		{
			$numArg++;
			$precision = $ARGV[$numArg];
		}
	}
	
	$numArg++;
}

opendir DIR, $dossier or die $!;
my @subDirs = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $subDir (@subDirs)
{
	my $file = "$dossier/$subDir";
	if(-d $file)
	{
		opendir DIR, $file or die $!;
		my @files = grep {/^[^.]/} readdir(DIR);
		closedir DIR;
		
		foreach my $fichier (@files)
		{
			if($fichier =~ /^fitnessDebug.txt$/)
			{
				open FILEIN, "$file/$fichier" or die $!;
				open FILEOUT, ">$file/refactVariances.dat" or die $!;
				print FILEOUT "Generation,FitnessMoyenne,Variance,EcartType,Ratio\n";
				
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					my @matches = ($ligne =~ m/,?([^,]+)/g);
					
					my $gen = $matches[0];
					my $moyenneFitness = 0;
					my $index = 1;
					while ($index < scalar(@matches))
					{
						my $curFitness = $matches[$index];
						$moyenneFitness += $curFitness;
						
						$index++;					
					}
					$moyenneFitness /= (scalar(@matches) - 1);
					
					my $variance = 0;
					$index = 1;
					while ($index < scalar(@matches))
					{
						my $curFitness = $matches[$index];
						$variance += ($moyenneFitness - $curFitness)*($moyenneFitness - $curFitness);
						$index++;
					}
					$variance /= (scalar(@matches) - 1);
					
					my $std = sqrt($variance);
					
					my $ratio = 0;
					if($moyenneFitness != 0)
					{
						$ratio = $std/$moyenneFitness;
					}
					
					if(($gen % $precision) == 0)
					{
						print FILEOUT "$gen,$moyenneFitness,$variance,$std,$ratio\n";
					}
				}
				
				close FILEOUT;
				close FILEIN;
				
				my $abs_dir = dirname(abs_path($0));
				my $cwd = abs_path(getcwd);
				chdir "$file";
				system "Rscript $abs_dir/scriptVariance.R";
				chdir "$cwd";
			}
		}
	}
}
