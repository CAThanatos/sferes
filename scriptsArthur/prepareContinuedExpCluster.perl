#!/usr/bin/perl

use strict;
use List::MoreUtils 'true';
use Getopt::Std;

my $dossier = undef;
my $date = "2014_04_24";

my %conf = ();

getopts( 'd:t:h', \%conf) or die $!;

if($conf{h})
{
	&printHelp();
	exit 0;
}

if($conf{d})
{
	$dossier = $conf{d};
}
else
{
	&printHelp();
	exit 1;
}

if($conf{t})
{
	$date = $conf{t};
}

my $fileExpToContinue = "expToContinu.txt";
my $outDir = "lastGenPop";
my $fileOut = "submit_job";

open FILEIN, "<$fileExpToContinue" or die $!;

my %listExp = ();
while (my $ligne = <FILEIN>)
{
	chomp $ligne;

	if($ligne =~ /^(.*)\t(.*)$/)
	{
		my $exp = $1;
		my $exec = $2;
		$listExp{$exp} = $exec;
	}
}

close FILEIN;


opendir DIR, "$dossier" or die $!;
my @dirs = grep { /^[^.]/ } readdir(DIR);
closedir DIR;

if(-e "$outDir")
{
	system "rm -r $outDir";
}
system "mkdir $outDir";

my $nbTotalRuns = 0;
foreach my $dir (@dirs)
{
	if(-d "$dossier/$dir")
	{
		my $count = true { /^$dir$/ } keys(%listExp);
		if($count > 0)
		{
			opendir DIR, "$dossier/$dir" or die $!;
			my @subDirs = grep { /^[^.]/ } readdir(DIR);
			closedir DIR;

			system "mkdir $outDir/$dir";

			foreach my $subDir (@subDirs)
			{
				if(-d "$dossier/$dir/$subDir")
				{
					if($subDir =~ /^Dir(\d*)$/)
					{
						my $run = $1;

						my $dirCp = "$outDir/$dir/$subDir";
						system "mkdir $dirCp";

						opendir DIR, "$dossier/$dir/$subDir" or die $!;
						my @files = grep { /^[^.]/ } readdir(DIR);
						closedir DIR;

						my $lastGen = 0;
						foreach my $file (@files)
						{
							if($file =~ /^popGen_(\d*)$/)
							{
								my $gen = $1;
								if($gen > $lastGen)
								{
									$lastGen = $gen;
								}
							}
						}

						$fileOut = $fileOut
						open FILEOUT, ">$fileOut" or die $!;

#						print "cp $dossier/$dir/$subDir/popGen_$lastGen $dirCp/\n";
						system "cp $dossier/$dir/$subDir/popGen_$lastGen $dirCp/";

						my $nameExp = $dir;

						my $job = "#! /bin/sh\n";
						$job = $job . "#PBS -N $nameExp\n"
						$job = $job . "#PBS -o test_job.out\n"
						$job = $job . "#PBS -o test_job.err\n"
						$job = $job . "#PBS -M arthur.bernard1204@gmail.com\n"
						$job = $job . "#PBS -l walltime=11:59:00\n"
						$job = $job . "#PBS -d /home/abernard/sferes2-0.99/res/StagHunt-Leadership/$dir/$subDir\n"
						$job = $job . "$listExp{$dir} -c $dirCp/popGen_$lastGen\n"

						print FILEOUT "$exp";
						$nbTotalRuns++;

						close FILEOUT;
					}
				}
			}
		}
		else
		{
			print "L'expérience $dir ne sera pas continuée.\n";
		}
	}
}

print "\t->Nombre total de runs à lancer : $nbTotalRuns\n";


sub printHelp()
{
	print "Usage : ./prepareContinuedExp.perl -d Directory [-t Date] [-h]\n";
	print "\t-d : Directory where are the experiences to continue\n";
	print "\t-t : Date\n";
	print "\t-h : Prints this help\n";
	exit;
}
