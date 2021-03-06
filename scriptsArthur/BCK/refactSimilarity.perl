#!/usr/bin/perl

use strict;
use File::Basename;
use Cwd "abs_path";

my $file = $ARGV[0];

my $abs_dir = dirname(abs_path($file));

open FILEIN, "<$file" or die $!;
open FILEOUT, ">$abs_dir/refactSimilarity.dat" or die $!;

my $currentGen = -1;
my @bestIndividual = ();
my @bestLastGen = ();
my $genomeSize = -1;
while (my $ligne = <FILEIN>)
{
	chomp $ligne;
							
	my @matches = ($ligne =~ m/,?([^,]+)/g);
	my $gen = $matches[0];		
	my $index = 1;

	if($currentGen != -1)
	{
		my @individual = ();
	
		while($index < scalar(@matches))
		{
			push @individual, $matches[$index];
			$index++;
		}
		
		my $bool = 0;
		
		#if($currentGen == 13460 && $gen == 13480)
		#{
		#	$bool = 1;
		#}
		
		if($gen > $currentGen)
		{
			@bestLastGen = @bestIndividual;
		}			
		
		my ($similarityGen, $similarityMut) = &computeSimilarity(\@individual, \@bestIndividual, $bool);
		my ($similarityLastGen, $similarityMutLastGen) = &computeSimilarity(\@individual, \@bestLastGen, $bool); 
	
		if($gen > $currentGen)
		{
			$currentGen = $gen;
		
			@bestIndividual = ();
			$index = 1;
			while($index < scalar(@matches))
			{
				push @bestIndividual, $matches[$index];
				$index++;
			}
		
			print FILEOUT "-------- $gen ---------\n";
		}
	
		print FILEOUT "$similarityGen -- $similarityMut // $similarityLastGen -- $similarityMutLastGen\n";
	}
	else
	{
		$currentGen = $gen;
	
		while($index < scalar(@matches))
		{
			push @bestIndividual, $matches[$index];
			push @bestLastGen, $matches[$index];
			$index++;
		}
		
		$genomeSize = scalar(@bestIndividual);
		
		print FILEOUT "1\n";
	}
}

close FILEOUT;
close FILEIN;

sub computeSimilarity
{
	my $refIndividual = @_[0];
	my $refBest = @_[1];
	
	my $bool = @_[2];
	
	my $index = 0;
	my $similarity = 0;
	my $similarityMut = 0;
	my $taille1 = scalar(@{$refIndividual});
	my $taille2 = scalar(@{$refBest});
#	print "$taille1/$taille2\n";
	while ($index < $genomeSize)
	{
		my $val1 = $refIndividual->[$index];
		my $val2 = $refBest->[$index];
		if($bool == 1)
		{
			print "$val1/$val2";
		}
	
		my $diff = abs($refIndividual->[$index] - $refBest->[$index]);
		$similarity += $diff;
		
		if($refIndividual->[$index] != $refBest->[$index])
		{
			if($bool == 1)
			{
				print"==>BOOM";
			}

			$similarityMut += 1;
		}
		
		if($bool == 1)
		{
			print "\n";
		}
		
		$index++;
	}
	
	$similarity = $similarity/$genomeSize;
	$similarity = 1 - $similarity;
	
#	$similarityMut = $similarityMut/$genomeSize;
#	$similarityMut = 1 - $similarityMut;
	
	return ($similarity, $similarityMut);
}
