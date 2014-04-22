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
my $prefix = "Dir";

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

if($conf{f})
{
	$prefix = $conf{f};
}

opendir DIR, $dossier or die $!;
my @files = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $file (@files)
{
	my $subDir = "$dossier/$file";
	if(-d $subDir)
	{
		print "-> $subDir\n";

		my $abs_dir = dirname(abs_path($0));
		print "$abs_dir/generateVideoExp.perl -d $subDir -f $prefix -m $morph -e $delay -r $rate -q $quality -o $output\n";
		system "$abs_dir/generateVideoExp.perl -d $subDir -f $prefix -m $morph -e $delay -r $rate -q $quality -o $output";
	}
}
