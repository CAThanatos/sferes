#!/usr/bin/perl

use strict;

my $dossier = $ARGV[0];
opendir DIR, "$dossier" or die $!;
my @dirs = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $dir (@dirs)
{
	if(-d "$dossier/$dir")
	{
		opendir DIR, "$dossier/$dir" or die $!;
		my @subDirs = grep {/^[^.]/} readdir(DIR);
		closedir DIR;

		foreach my $subDir (@subDirs)
		{
			if(-d "$dossier/$dir/$subDir")
			{
				if($subDir !~ /^BestFit$/)
				{
					system "rm -r $dossier/$dir/$subDir";
				}
			}
		}
	}
}
