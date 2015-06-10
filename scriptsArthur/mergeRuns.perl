#!/usr/bin/perl

use strict;
use Getopt::Std;

my $dossierOrig = undef;
my $dossierCont = undef;

my %conf = ();

getopts( 'd:s:h', \%conf) or die $!;

if($conf{h})
{
	&printHelp();
	exit 0;
}

if($conf{d})
{
	$dossierOrig = $conf{d};
}
else
{
	&printHelp();
	exit 1;
}

if($conf{s})
{
	$dossierCont = $conf{s};
}
else
{
	&printHelp();
	exit 1;
}

opendir DIR, $dossierOrig or die $!;
my @dirsOrig = grep { /^[^.]/ } readdir(DIR);
closedir DIR;

opendir DIR, $dossierCont or die $!;
my @dirsCont = grep { /^[^.]/ } readdir(DIR);
closedir DIR;

foreach my $dirOrig (@dirsOrig)
{
	if( (-d "$dossierOrig/$dirOrig") && (-d "$dossierCont/$dirOrig") )
	{
		opendir DIR, "$dossierOrig/$dirOrig" or die $!;
		my @subDirs = grep { /^[^.]/ } readdir(DIR);
		closedir DIR;

		foreach my $subDir (@subDirs)
		{
			if( (-d "$dossierOrig/$dirOrig/$subDir") && (-d "$dossierCont/$dirOrig/$subDir") )
			{
				if($subDir =~ /^Dir(\d*)$/)
				{
					my $run = $1;

					opendir DIR, "$dossierCont/$dirOrig/$subDir" or die $!;
					my @nodes = grep { /^[^.]/ } readdir(DIR);
					close DIR;

					if(scalar(@nodes) > 1)
					{
						die "Erreur : too many nodes in : $dossierCont/$dirOrig/$subDir !\n";
					}

					opendir DIR, "$dossierCont/$dirOrig/$subDir/$nodes[0]" or die $!;
					my @filesCont = grep { /^[^.]/ } readdir(DIR);
					closedir DIR;

					foreach my $file (@filesCont)
					{
						if($file =~ /\.dat$/)
						{
							open FILEIN, "<$dossierCont/$dirOrig/$subDir/$nodes[0]/$file" or die $!;

							my $firstEval = undef;
							my $contenu = "";
							while (my $ligne = <FILEIN>)
							{
								if($ligne =~ /^(\d*),(.*)$/)
								{
									my $eval = $1;
									my $reste = $2;

#									$eval = (($firstGen * 20) + 10) + ($eval - 20);

									if(!defined($firstEval))
									{
										$firstEval = $eval;
									}

#									$contenu = $contenu . "$eval,$reste\n";
									$contenu = $contenu . $ligne;
								}
							}

							close FILEIN;

							if(-f "$dossierOrig/$dirOrig/$subDir/$file")
							{
								open FILEIN, "<$dossierOrig/$dirOrig/$subDir/$file" or die $!;
								open FILEOUT, ">$dossierOrig/$dirOrig/$subDir/${file}2" or die $!;

								my $stop = 0;
								while ((my $ligne = <FILEIN>) && ($stop == 0))
								{
									if($ligne =~ /^(\d*),/)
									{
										my $eval = $1;

										if($eval < $firstEval)
										{
											print FILEOUT "$ligne";
										}
										else
										{
											$stop = 1;
										}
									}
								}

								print FILEOUT "$contenu";

								close FILEOUT;
								close FILEIN;

								system "mv $dossierOrig/$dirOrig/$subDir/${file}2 $dossierOrig/$dirOrig/$subDir/$file";
							}
							else
							{
								open FILEOUT, ">$dossierOrig/$dirOrig/$subDir/$file" or die $!;
								print FILEOUT "$contenu";
								close FILEOUT;
							}
						}
						else
						{
							if($file =~ /^behaviourVideoGen/)
							{
								system "rm -r $dossierOrig/$dirOrig/$subDir/behaviourVideoGen*";
							}

							system "cp -r $dossierCont/$dirOrig/$subDir/$nodes[0]/$file $dossierOrig/$dirOrig/$subDir/";
						}
					}
				}
			}
		}
	}
}


sub printHelp()
{
	print "Usage : ./mergeRuns.perl -s SourceDirectory -d DestinationDirectory [-h]\n";
	print "\t-s : Directory from which the files to merge are taken\n";
	print "\t-d : Directory where the merging will happen\n";
	print "\t-h : Prints this help\n";
	exit;
}
