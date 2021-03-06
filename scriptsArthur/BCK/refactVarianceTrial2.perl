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
		
		my %tabValues = ();	
		my %tabValues2 = ();	
		foreach my $fichier (@files)
		{
			if($fichier =~ /^fitnessDebug.txt$/)
			{
				open FILEIN, "$file/$fichier" or die $!;
				open FILEOUT, ">$file/refactVariances.dat" or die $!;
				print FILEOUT "Generation,Fitness\n";
				
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
						my @tabTmp = ();
						push @tabTmp, $moyenneFitness;
						push @tabTmp, $variance;
						push @tabTmp, $std;
						push @tabTmp, $ratio;
						$tabValues{$gen} = \@tabTmp;
						
						my @tabTmp2 = ();
						$index = 1;
						while($index < scalar(@matches))
						{
							push @tabTmp2, $matches[$index];
							$index++;
						}
						$tabValues2{$gen} = \@tabTmp2;
						
						#print FILEOUT "$gen,$moyenneFitness,$variance,$std,$ratio\n";
					}
				}
				
				my @sortValues = sort {$a <=> $b} keys(%tabValues);

				foreach my $value (@sortValues)
				{
					my $moyenneFitness = $tabValues{$value}->[0];
					my $variance = $tabValues{$value}->[1];
					my $std = $tabValues{$value}->[2];
					my $ratio = $tabValues{$value}->[3];
					
					#print FILEOUT "$value,$moyenneFitness,$variance,$std,$ratio\n";
				}
				
				@sortValues = sort {$a <=> $b} keys(%tabValues2);
				foreach my $value (@sortValues)
				{
					my $index = 0;
					my @tab = @{$tabValues2{$value}};
					while ($index < scalar(@tab))
					{
						my $fitness = $tab[$index];
						print FILEOUT "$value,$fitness\n";
						$index++;
					}
				}
				
				close FILEOUT;
				close FILEIN;
				
				my $abs_dir = dirname(abs_path($0));
				my $cwd = abs_path(getcwd);
				chdir "$file";
				system "Rscript $abs_dir/scriptVariance2.R";
				chdir "$cwd";
			}
		}
	}
}
