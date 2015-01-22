#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd;
use Cwd "abs_path";

my $dossier = 0;

my $numArg = 0;
while ($numArg < scalar(@ARGV))
{
	my $arg = $ARGV[$numArg];
	
	if($arg =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
	}
	
	$numArg++;
}

my $dossierRefact = "refactVarianceTrials";
if(-e $dossierRefact)
{
	system "rm -r $dossierRefact";
}


opendir DIR, $dossier or die $!;
my @files = grep {/^[^.]/} readdir(DIR);
closedir DIR;

my @trials = (2,5,10,20);
my $numTrial = 0;
while ($numTrial < scalar(@trials))
{
	my $trial = $trials[$numTrial];
	my $dossierOut = "$dossierRefact/refactVarianceTrials$trial";

	if(-e $dossierOut)
	{
		system "rm -r $dossierOut";
	}
	system "mkdir -p $dossierOut";
	
	if(-e "$dossierOut/fitnessDebug.txt")
	{
		system "rm $dossierOut/fitnessDebug.txt";
	}
	
#	open FILEOUT, ">>$dossierOut/fitnessDebug.txt" or die $!;
#	print FILEOUT "Generation,Fitness\n";
#	close FILEOUT;

	foreach my $file (@files)
	{
		if($file =~ /^gen_(\d+)/)
		{
			my $gen = $1;
		
			print "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2/StagHuntExp2_test_variance_mlp_trials$trial --load $dossier/$file -o output.txt\n";
			system "/home/abernard/sferes2-0.99/build/default/exp/StagHuntExp2/StagHuntExp2_test_variance_mlp_trials$trial --load $dossier/$file -o output.txt";
			
			open FILEIN, "<fitnessDebug.txt" or die $!;
			open FILEOUT, ">>$dossierOut/fitnessDebug.txt" or die $!;
			
			while (my $ligne = <FILEIN>)
			{
				chomp $ligne;
				my @matches = ($ligne =~ m/,?([^,]+)/g);
				
				print FILEOUT "$gen";
				my $index = 1;
				while ($index < scalar(@matches))
				{
					my $fitness = $matches[$index];
					print FILEOUT ",$fitness";
					$index++;
				}
				print FILEOUT "\n";
			}
			close FILEOUT;
			close FILEIN;
			
			system "rm fitnessDebug.txt";
		}
	}
	
	$numTrial++;
}
				
my $abs_dir = dirname(abs_path($0));
#print "$abs_dir/refactVarianceTrial2.perl -d ./$dossierRefact\n";
#system "$abs_dir/refactVarianceTrial2.perl -d ./$dossierRefact";
print "$abs_dir/refactVarianceTrial2.perl -d ./$dossierRefact\n";
system "$abs_dir/refactVarianceTrial2.perl -d ./$dossierRefact";
