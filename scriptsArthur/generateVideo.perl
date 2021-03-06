#!/usr/bin/perl

use strict;
use Getopt::Std;
use File::Basename;
use Cwd "abs_path";

my %conf = ();

my $width = 800;
my $height = 600;
my $morph = 1;
my $delay = 5;
my $output = "videoBest.mp4";
my $rate = 25;
my $quality = 2;
my $dossier = undef;

getopts( 'd:o:m:e:s:r:q:f:', \%conf ) or die $!;

if($conf{d})
{
	$dossier = $conf{d};
}
else
{
	die "Le dossier doit être renseigné";
}

if($conf{s})
{
	($width, $height) = split ':', $conf{s}, 2;
}

if($conf{m})
{
	$morph = $conf{m};
}

if($conf{o})
{
	$output = $conf{o};
}

if($conf{e})
{
	$delay = $conf{e};
}

if($conf{q})
{
	$quality = $conf{q};
}

if($conf{r})
{
	$rate = $conf{r};
}

opendir DIR, $dossier or die $!;
my @filesDir = grep {/^[^.]/} readdir(DIR);
closedir DIR;

my $dirArchive = undef;
foreach my $fileDir (@filesDir)
{
	if($fileDir =~ /^behaviourVideoGen/)
	{
		my $fileArchive = "$dossier/$fileDir";
		
		if(-e "$dossier/BehaviourVideo")
		{
			print "rm -r $dossier/BehaviourVideo\n";
			system "rm -r $dossier/BehaviourVideo";
		}
		print "mkdir $dossier/BehaviourVideo\n";
		system "mkdir $dossier/BehaviourVideo";
		
		print "tar -xf $fileArchive -C $dossier/BehaviourVideo\n";
		system "tar -xf $fileArchive -C $dossier/BehaviourVideo";
		
		# We look for the folder containing all the .bmp
		$dirArchive = "$dossier/BehaviourVideo";
		while($dirArchive !~ /behaviourVideoGen_/)
		{
			opendir DIR, $dirArchive or die $!;
			my @filesSubDir = grep {/^[^.]/} readdir(DIR);
			closedir DIR;
			
			my $subDir = @filesSubDir[0];
			$dirArchive = "$dirArchive/$subDir";
		}
	}
}

if(defined($dirArchive))
{
	my $abs_dir = dirname(abs_path($0));
	print "$abs_dir/video.perl -d $dirArchive -m $morph -e $delay -r $rate -q $quality -o $output\n";
	system "$abs_dir/video.perl -d $dirArchive -m $morph -e $delay -r $rate -q $quality -o $output";

	print "cp $dirArchive/$output $dossier\n";
	system "cp $dirArchive/$output $dossier";

	print "rm -rf $dossier/BehaviourVideo\n";
	system "rm -rf $dossier/BehaviourVideo";
}
