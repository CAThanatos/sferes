#!/usr/bin/perl

use strict;

use Getopt::Std;
use GD::Graph::bars;
use GD::Graph::mixed;
use GD::Graph::boxplot;
use GD::Graph::colour;
use GD::Text;

GD::Graph::colour::add_colour(Defector => [94, 212, 94]);
GD::Graph::colour::add_colour(Cooperator => [184, 89, 232]);

my %conf = ();
my $dossier = undef;
my $precision = 100;
my $maxEval = undef;
my $outputDirName = "PopulationRepartition";
my $maxPreys = 15;

getopts( 'd:p:m:h', \%conf ) or die $!;

if($conf{h})
{
	&printHelp();
}

if($conf{d})
{
	$dossier = $conf{d};
}
else
{
	die "Le dossier doit être renseigné";
}

if($conf{p})
{
	$precision = $conf{p};
}

if($conf{m})
{
	$maxEval = $conf{m};
}

opendir DIR, $dossier or die $!;
my @dirs = grep {/^[^.]/} readdir(DIR);
closedir DIR;

foreach my $dir (@dirs)
{
	if(-d "$dossier/$dir")
	{
		opendir DIR, "$dossier/$dir" or die $!;
		my @subDirs = grep {/^[^.]/} readdir(DIR);
		closedir DIR;
		
		my $outputDir = "$dossier/$dir/$outputDirName";
		if(-e $outputDir)
		{
			system "rm -r $outputDir";
		}
		system "mkdir $outputDir";
		
		foreach my $subDir (@subDirs)
		{
			if(-d "$dossier/$dir/$subDir")
			{
				if($subDir =~ /^Dir(\d*)/)
				{
					my $numRun = $1;
					opendir DIR, "$dossier/$dir/$subDir" or die $!;
					my @files = grep {/^[^.]/} readdir(DIR);
					closedir DIR;
					
					foreach my $file (@files)
					{
						if($file =~ /^allgenomes.dat$/)
						{
							system "cp $dossier/$dir/$subDir/$file $outputDir/allgenomes$numRun.dat";
						}
					}
				}
			}			
		}
		
		opendir DIR, $outputDir or die $!;
		my @files = grep {/^[^.]/} readdir(DIR);
		closedir DIR;
		
		foreach my $file (@files)
		{
			if($file =~ /^allgenomes(\d*).dat$/)
			{
				my $numRun = $1;
				
				my @dataRun = ();
				
				open FILEIN, "<$outputDir/$file" or die $!;
				
				my $currentEval = undef;
				my $cumulEval = 0;
				my $nbCoop = 0;
				my $nbNonCoop = 0;
				my $firstEval = 1;
				while (my $ligne = <FILEIN>)
				{
					chomp $ligne;
					
					if($ligne =~ /^(\d*),(\d*)$/)
					{
						my $eval = $1;
						my $gene = $2;
						
						if(!defined($currentEval))
						{
							$currentEval = $eval;
						}
						
						if($eval > $currentEval)
						{
							$cumulEval += $eval - $currentEval;
							
							if(($cumulEval >= $precision) || ($firstEval == 1))
							{
								my @ligne = ($currentEval, $nbCoop, $nbNonCoop);
								push @dataRun, \@ligne;
								$cumulEval = 0;	
								
								if($firstEval == 1)
								{
									$firstEval = 0;
								}
							}
							
							$nbCoop = 0;
							$nbNonCoop = 0;
							
							if($gene == 0)
							{
								$nbNonCoop++;
							}
							else
							{
								$nbCoop++;
							}
							
							$currentEval = $eval;
						}
						else
						{
							if($gene == 0)
							{
								$nbNonCoop++;
							}
							else
							{
								$nbCoop++;
							}
						}
					}
				}
				
				close FILEIN;
				
				my @dataEval = ();
				my @dataNbCoop = ();
				my @dataNbNonCoop = ();
				
				my $lastEval = 0;
				my $curEval = undef;
				my $diffEval = undef;
				foreach my $refLigne (@dataRun)
				{
					my $eval = $refLigne->[0];
					my $nbCoop = $refLigne->[1];
					my $nbNonCoop = $refLigne->[2];
					
					$lastEval = $eval;
					if(!defined($maxEval) || $eval < $maxEval)
					{
						push @dataEval, $eval;
						push @dataNbCoop, $nbCoop;
						push @dataNbNonCoop, $nbNonCoop;
					}
					
					if(defined($curEval))
					{
						$diffEval = $eval - $curEval;
					}
					$curEval = $eval;
				}
				
				while(defined($maxEval) && $lastEval < $maxEval)
				{
					$lastEval += $diffEval;
											
					push @dataEval, $lastEval;
					push @dataNbCoop, undef;
					push @dataNbNonCoop, undef;
				}
				
				my @data = (\@dataEval, \@dataNbCoop, \@dataNbNonCoop);
				my $graph = GD::Graph::mixed->new(800, 600);

				$graph->set(title => "Repartition of Cooperators and Defectors",
					
											# Graph margins
											t_margin => 10,
											b_margin => 10,
											l_margin => 10,
											r_margin => 10,
					
											# Self explanatory
											x_label => "Evaluations",
											x_label_position => 0.5,
											y_label => "Number of Individuals",

											y_max_value => $maxPreys,
											x_max_value => $maxEval,

											legend_placement => "RT",
					
											# Type of each graph
											types => [ qw(bars bars) ],
					
											# Color of each graph
											dclrs => [ qw(Cooperator Defector) ],
					
											y_tick_number => 10,
											x_tick_number => 10,

				#										line_width => 2,
				#										long_ticks => 1,

											# Skip between each tick on the x and y axis
											x_label_skip => 1,
											y_label_skip => 1,
					
											# Stacking of the bar graphs
											cumulate => 1,
					
											# Width and spacing of the bars
											bar_width => 20,
											bar_spacing => 3,
					
				#										markers => [ 5, 5 ],
					
											# No background transparency
											transparent => 0);
					
				$graph->set_legend("Cooperators",
											"Defectors");

				GD::Text->font_path( "/usr/share/fonts/truetype/ubuntu-font-family" );
				$graph->set_title_font( "Ubuntu-R", 16 );
				$graph->set_legend_font( "Ubuntu-R", 10 );
				$graph->set_x_axis_font( "Ubuntu-R", 9 );
				$graph->set_x_label_font( "Ubuntu-R", 11 );
				$graph->set_y_axis_font( "Ubuntu-R", 9 );
				$graph->set_y_label_font( "Ubuntu-R", 11 );

				my $image = $graph->plot( \@data ) or die( "Cannot create image" );
				open(IMG, ">$outputDir/repartition_run$numRun.png") or die $!;
				binmode IMG;
				print IMG $image->png();
				close IMG;
			}
		}
	}
}

sub printHelp()
{
	print "Usage : ./generateTheoritical.perl -d FilesDirectory [-p Precision] [-m IterationMax] [-h]\n";
	print "\t-d : Directory with all the files to compute\n";
	print "\t-p : Precision in number of evaluations. 100 by default\n";
	print "\t-m : Number of iteration max computed and drawn. No maximum by default\n";
	print "\t-h : Prints this help\n";
	exit;
}
