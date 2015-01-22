#!/usr/bin/perl

use strict;
use POSIX qw/ceil/;
use POSIX qw/floor/;

use Getopt::Std;
use GD::Graph::bars;
use GD::Graph::mixed;
use GD::Graph::boxplot;
use GD::Graph::colour;
use GD::Text;

my %conf = ();

my $dossier = undef;
my $maxEval = undef;
my $drawTheoritical = 0;
my $drawGeneration = 0;
my $nbEvalByGen = 100;


getopts( 'd:m:t', \%conf ) or die $!;

if($conf{d})
{
	$dossier = $conf{d};
}
else
{
	die "Le dossier doit être renseigné";
}

if($conf{m})
{
	$maxEval = $conf{m};
}

if($maxEval == -1)
{
	$maxEval = undef;
}

if($conf{t})
{
	$drawTheoritical = 1;
}

opendir DIR, $dossier or die $!;
my @files = grep {/^[^.]/} readdir(DIR);
closedir DIR;

GD::Graph::colour::add_colour(HaresSolo => [94, 212, 94]);
GD::Graph::colour::add_colour(HaresDuo => [50, 132, 50]);
GD::Graph::colour::add_colour(SStagsSolo => [89, 208, 232]);
GD::Graph::colour::add_colour(SStagsDuo => [51, 102, 153]);
GD::Graph::colour::add_colour(BStagsSolo => [184, 89, 232]);
GD::Graph::colour::add_colour(BStagsDuo => [100, 47, 127]);

my $x_label = "Evaluations";
if($drawGeneration == 1)
{
	$x_label = "Generations";
}

my %dataRuns = ();
my $maxFitness = 0;
my $maxPreys = 0;
my $nbRuns = 0;

foreach my $file (@files)
{
	if($file =~ /^refactData.dat$/)
	{
		print "$file\n";
	
		open FILEIN, "<$dossier/$file" or die $!;
		
		my %hashData = ();
		my $cpt = 0;
		my $diffEvals = undef;
		my $lastEval = undef;
		while (my $ligne = <FILEIN>)
		{
			chomp $ligne;
			if($cpt > 0)
			{
				if($ligne =~ /^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$/)
				{
					my $evaluation = $1;
					my $run = $2;
					my $fitness = $3;
					
					if(exists($hashData{$evaluation}))
					{
						my $ref = $hashData{$evaluation};
						push @{$ref}, $fitness;
					}
					else
					{
						my @tab_ref = ();
						push @tab_ref, $fitness;
						$hashData{$evaluation} = \@tab_ref;
					}
				
					if(defined($diffEvals))
					{
						if($evaluation > $lastEval)
						{
							$diffEvals = $evaluation - $lastEval;
							$lastEval = $evaluation;
						}
					}
					else
					{
						$diffEvals = 0;
						$lastEval = $evaluation;
					}
				}
			}
			else
			{
				$cpt++;
			}
		}
		
		close FILEIN;
		
		my @keys = keys(%hashData);
		my $firstTab = $hashData{$keys[0]};
		my $nbRuns = scalar(@{$firstTab});
		if(defined($maxEval) && defined($lastEval))
		{
			while($lastEval < $maxEval)
			{
				$lastEval += $diffEvals;
				
				my @tab_ref = ();
				my $compteur = 0;
				while($compteur < $nbRuns)
				{
					push @tab_ref, undef;
					$compteur++;
				}
				
				$hashData{$lastEval} = \@tab_ref;
			}
		}
		
		my @dataEvalTmp = sort {$a <=> $b} keys(%hashData);
		my @dataEval = ();
		my @dataFitness = ();
		foreach my $eval (@dataEvalTmp)
		{
			if(!defined($maxEval) || $eval <= $maxEval)
			{
				push @dataEval, $eval;
				push @dataFitness, $hashData{$eval};
			}
		}

		if($drawGeneration == 1)
		{
			my $cpt = 0;
			while ($cpt < scalar(@dataEval))
			{
				my $eval = $dataEval[$cpt];
				$dataEval[$cpt] = floor($eval/$nbEvalByGen);
				$cpt++;
			}
		}
		
		# BoxPlot
		my @data = (\@dataEval, \@dataFitness);
		my $graph = GD::Graph::boxplot->new(800, 600);
	
		$graph->set(title => "Best Fitness",
								
									# Graph margins
									t_margin => 10,
									b_margin => 10,
									l_margin => 10,
									r_margin => 10,
								
									# Self explanatory
									x_label => $x_label,
									x_label_position => 0.5,
									y_label => "Fitness",
								
#										y_tick_number => 14,
#									x_tick_number => 10,
#										y_label_skip => 2,
#										line_width => 2,
#										long_ticks => 1,

									y_min_value => 0,
#									y_max_value => 8000,

									lower_percent => 25,
									upper_percent => 75,
									
									dclrs => [ qw(white) ],

									# Skip between each tick on the x axis
									x_label_skip => 5,
									
									box_spacing => 5,
								
									# No background transparency
									transparent => 0);

		GD::Text->font_path( "/usr/share/fonts/truetype/ubuntu-font-family" );
		$graph->set_title_font( "Ubuntu-R", 16 );
		$graph->set_legend_font( "Ubuntu-R", 10 );
		$graph->set_x_axis_font( "Ubuntu-R", 9 );
		$graph->set_x_label_font( "Ubuntu-R", 11 );
		$graph->set_y_axis_font( "Ubuntu-R", 9 );
		$graph->set_y_label_font( "Ubuntu-R", 11 );
	
		my $image = $graph->plot( \@data ) or die( "Cannot create image" );
		open(IMG, ">$dossier/fileBest.png") or die $!;
		binmode IMG;
		print IMG $image->png();
		close IMG;
	}
	else
	{
		if($file =~ /^refactData_run(\d+).dat$/)
		{
			print "$file\n";

			my $run = $1;
			my @dataRun = ();
			
			$nbRuns++;
		
			open FILEIN, "<$dossier/$file" or die $!;
		
			my $diffEvals = undef;
			my $lastEval = undef;
			my $cpt = 0;
			while (my $ligne=<FILEIN>)
			{
				chomp $ligne;
			
				if($cpt > 0)
				{
					if($ligne =~ /^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$/)
					{
						my $evaluation = $1;
						my $fitness = $2;
						my $nbHaresDuo = $3;
						my $nbHaresSolo = $4;
						my $nbHares = $5;
						my $nbSStagsDuo = $6;
						my $nbSStagsSolo = $7;
						my $nbSStags = $8;
						my $nbBStagsDuo = $9;
						my $nbBStagsSolo = $10;
						my $nbBStags = $11;
				
						my @ligne = ($evaluation, $fitness, $nbHaresSolo, $nbHaresDuo, $nbSStagsSolo, $nbSStagsDuo, $nbBStagsSolo, $nbBStagsDuo);
						push @dataRun, \@ligne;
				
						if(defined($diffEvals))
						{
							$diffEvals = $evaluation - $lastEval;
							$lastEval = $evaluation;
						}
						else
						{
							$diffEvals = 0;
							$lastEval = $evaluation;
						}
						
						my $totalPreys = $nbHares + $nbSStags + $nbBStags;
						if($totalPreys > $maxPreys)
						{
							$maxPreys = $totalPreys;
						}
						
						if($fitness > $maxFitness)
						{
							$maxFitness = $fitness;
						}
					}
				}
				else
				{
					$cpt++;
				}
			}
		
			close FILEIN;
		
			if(defined($maxEval) && defined($lastEval))
			{
				while($lastEval < $maxEval)
				{
					$lastEval += $diffEvals;
					my @ligne = ($lastEval, undef, undef, undef, undef, undef, undef, undef);
					push @dataRun, \@ligne;
				}
			}
		
			$dataRuns{$run} = \@dataRun;
		}
	}
}

$maxFitness = ceil(1.05*$maxFitness);
my $stepFitness = 0.1*$maxFitness;

$maxPreys = ceil(1.05*$maxPreys);
my $stepPreys = 0.1*$maxPreys;

my $numRun = 1;
while($numRun <= $nbRuns)
{		
	my $refRun = $dataRuns{$numRun};
	my @dataRun = @{$refRun};

	my @dataEval = ();
	my @dataFitness = ();
	my @dataHaresDuo = ();
	my @dataHaresSolo = ();
	my @dataSStagsDuo = ();
	my @dataSStagsSolo = ();
	my @dataBStagsDuo = ();
	my @dataBStagsSolo = ();

	foreach my $ligne (@dataRun)
	{
		my $eval = $ligne->[0];

		if(!defined($maxEval) || $eval <= $maxEval)
		{
			push @dataEval, $ligne->[0];
			push @dataFitness, $ligne->[1];
			push @dataHaresSolo, $ligne->[2];
			push @dataHaresDuo, $ligne->[3];
			push @dataSStagsSolo, $ligne->[4];
			push @dataSStagsDuo, $ligne->[5];
			push @dataBStagsSolo, $ligne->[6];
			push @dataBStagsDuo, $ligne->[7];
		}
	}

	my $maxEvalTmp = $maxEval;
	if($drawGeneration == 1)
	{
		my $cpt = 0;
		while ($cpt < scalar(@dataEval))
		{
			my $eval = $dataEval[$cpt];
			$dataEval[$cpt] = floor($eval/$nbEvalByGen);
			$cpt++;
		}

		$maxEvalTmp = $maxEval/$nbEvalByGen;
	}

	# Fitness
	my @data = (\@dataEval, \@dataFitness);
	my $graph = GD::Graph::lines->new(800, 600);

	$graph->set(title => "Best Fitness",
						
								# Graph margins
								t_margin => 10,
								b_margin => 10,
								l_margin => 10,
								r_margin => 20,
						
								# Self explanatory
								x_label => $x_label,
								x_label_position => 0.5,
								y_label => "Fitness",
						
								y_max_value => $maxFitness,
								x_max_value => $maxEvalTmp,
						
								y_tick_number => 10,
								x_tick_number => 10,
								
#										line_width => 2,
#										long_ticks => 1,

								# Skip between each tick on the x and y axis
								x_label_skip => 1,
								y_label_skip => 1,
						
								# No background transparency
								transparent => 0);

	GD::Text->font_path( "/usr/share/fonts/truetype/ubuntu-font-family" );
	$graph->set_title_font( "Ubuntu-R", 16 );
	$graph->set_legend_font( "Ubuntu-R", 10 );
	$graph->set_x_axis_font( "Ubuntu-R", 9 );
	$graph->set_x_label_font( "Ubuntu-R", 11 );
	$graph->set_y_axis_font( "Ubuntu-R", 9 );
	$graph->set_y_label_font( "Ubuntu-R", 11 );

	my $image = $graph->plot( \@data ) or die( "Cannot create image" );
	open(IMG, ">$dossier/best_run$numRun.png") or die $!;
	binmode IMG;
	print IMG $image->png();
	close IMG;
	
	# Preys repartition
	@data = (\@dataEval, \@dataHaresSolo, \@dataHaresDuo, \@dataSStagsSolo, \@dataSStagsDuo, \@dataBStagsSolo, \@dataBStagsDuo);
	$graph = GD::Graph::mixed->new(800, 600);

	$graph->set(title => "Repartition of Preys Hunted",
						
								# Graph margins
								t_margin => 10,
								b_margin => 10,
								l_margin => 10,
								r_margin => 20,
						
								# Self explanatory
								x_label => $x_label,
								x_label_position => 0.5,
								y_label => "Preys Hunted",

								y_max_value => $maxPreys,
								x_max_value => $maxEvalTmp,

								legend_placement => "RT",
						
								# Type of each graph
								types => [ qw(bars bars bars bars bars bars) ],
						
								# Color of each graph
								dclrs => [ qw(HaresSolo HaresDuo SStagsSolo SStagsDuo BStagsSolo BStagsDuo) ],
						
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
						
#	$graph->set_legend("Hares Solo",
#								"Hares Coop.",
#								"Small Stags Solo",
#								"Small Stags Coop.",
#								"Big Stags Solo",
#								"Big Stags Coop.");

	GD::Text->font_path( "/usr/share/fonts/truetype/ubuntu-font-family" );
	$graph->set_title_font( "Ubuntu-R", 16 );
	$graph->set_legend_font( "Ubuntu-R", 10 );
	$graph->set_x_axis_font( "Ubuntu-R", 9 );
	$graph->set_x_label_font( "Ubuntu-R", 11 );
	$graph->set_y_axis_font( "Ubuntu-R", 9 );
	$graph->set_y_label_font( "Ubuntu-R", 11 );

	$image = $graph->plot( \@data ) or die( "Cannot create image" );
	open(IMG, ">$dossier/preys_run$numRun.png") or die $!;
	binmode IMG;
	print IMG $image->png();
	close IMG;

	$numRun++;
}
