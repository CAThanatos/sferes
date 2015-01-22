#!/usr/bin/perl

use strict;
use Getopt::Std;

my %conf = ();

my $width = 800;
my $height = 600;
my $morph = 1;
my $delay = 5;
my $output = "videoBest.mp4";
my $rate = 25;
my $quality = 2;
my $dossier = undef;

getopts( 'd:o:m:e:s:r:q:', \%conf ) or die $!;

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

#print "mogrify -resize ${width}x${height} *.bmp\n";
#system "mogrify -resize ${width}x${height} *.bmp";

chdir "$dossier";

print "convert *.bmp -delay $delay -morph $morph %05d.morph.jpg\n";
system "convert *.bmp -delay $delay -morph $morph %05d.morph.jpg";

print "avconv -r $rate -qscale $quality -i %05d.morph.jpg $output\n";
system "avconv -r $rate -qscale $quality -i %05d.morph.jpg $output";

print "rm *.morph.jpg\n";
system "rm *.morph.jpg";
