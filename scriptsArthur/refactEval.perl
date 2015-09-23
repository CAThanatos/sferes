#!/usr/bin/perl

use strict;
use Getopt::Std;

my $dossier = undef;

my %conf = ();

getopts( 'd:s:h', \%conf) or die $!;

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


opendir DIR, $dossier or die $!;
my @dirs = grep { /^[^.]/ } readdir(DIR);
closedir DIR;

foreach my $dir (@dirs)
{
	if (-d "$dossier/$dir")
	{
		opendir DIR, "$dossier/$dir" or die $!;
		my @subDirs = grep { /^[^.]/ } readdir(DIR);
		closedir DIR;

		my $waypoints = 0;
		if($dir =~ /WAYPOINTS7/)
		{
			$waypoints = 7;
		}
		else
		{
			$waypoints = 18
		}

		foreach my $subDir (@subDirs)
		{
			if(-d "$dossier/$dir/$subDir")
			{
				opendir DIR, "$dossier/$dir/$subDir" or die $!;
				my @ssubDirs = grep { /^[^.]/ } readdir(DIR);
				closedir DIR;

				foreach my $ssubDir (@ssubDirs)
				{
					if(-d "$dossier/$dir/$subDir/$ssubDir")
					{
						opendir DIR, "$dossier/$dir/$subDir/$ssubDir" or die $!;
						my @files = grep { /^[^.]/ } readdir(DIR);
						closedir DIR;

						foreach my $file (@files)
						{
							if ((-f "$dossier/$dir/$subDir/$ssubDir/$file"))
							{
								if($file =~ /\.dat$/)
								{
									open FILEIN, "<$dossier/$dir/$subDir/$ssubDir/$file" or die $!;

									my $contenu = "";
									while (my $ligne = <FILEIN>)
									{
										if($ligne =~ /^(\d+),(.*)$/)
										{
											my $eval = $1;
											my $reste = $2;

											# my $newEval = $eval*2 + 60;
											my $newEval = undef;
											if($waypoints == 7)
											{
												$newEval = $eval + 30390;
											}
											else
											{
												$newEval = $eval + 14990;
											}

											$contenu = $contenu . "$newEval,$reste\n";
										}
									}

									close FILEIN;

									open FILEOUT, ">$dossier/$dir/$subDir/$ssubDir/$file" or die $!;
									print FILEOUT $contenu;
									close FILEOUT;
								}
								else
								{
									if($file =~ /2$/)
									{
										system "rm $dossier/$dir/$subDir/$ssubDir/$file";
									}
								}
							}
						}
					}
				}
			}
		}
	}
}




sub printHelp()
{
	print "Usage : ./mergeRuns.perl -d DestinationDirectory [-h]\n";
	print "\t-d : Directory where the merging will happen\n";
	print "\t-h : Prints this help\n";
	exit;
}
