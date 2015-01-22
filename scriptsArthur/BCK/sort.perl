#!/usr/bin/perl

my $dossier = -1;
my $numArg = 0;

while ($numArg < scalar(@ARGV))
{
	my $arg = $ARGV[$numArg];
	
	if($arg =~ "-d")
	{
		$numArg++;
		$dossier = $ARGV[$numArg];
		$numArg++;
	}
}

opendir DIR, $dossier or die $!;
my @fichiers = grep {/dat$/} readdir(DIR);
closedir DIR;

foreach my $fichier (@fichiers)
{
  if($fichier =~ /^refact[^I].*$/)
  {
    print "$fichier\n";
  	my @values = ();
  
  	open FILEIN, "<$dossier/$fichier" or die $!;
  	
  	while (my $ligne = <FILEIN>)
  	{
  		chomp $ligne;
  		
  		if($ligne =~ /^([0-9]*),([0-9]*),([0-9]*)$/)
  		{
  			my $numEval = $1;
  			my $nbGoHare = $2;
  			my $nbGoStag = $3;
			
	  		my %object = ();
	  		$object{"numEval"} = $numEval;
	  		$object{"nbGoHare"} = $nbGoHare;
	  		$object{"nbGoStag"} = $nbGoStag;
			
  			push @values, \%object;			
  		}
  	}
	
  	close FILEIN;
	
	  system "rm -f $fichier";
	
	  open FILEOUT, ">$dossier/$fichier" or die $!;
	
	  my @sortValues = sort {$a->{"numEval"} <=> $b->{"numEval"}} @values;

  	print FILEOUT "Evaluation,NbGoHare,NbGoStag\n";
  	foreach my $value (@sortValues)
  	{
  		my $numEval = $value->{"numEval"};
  		my $nbGoHare = $value->{"nbGoHare"};
	  	my $nbGoStag = $value->{"nbGoStag"};

  		print FILEOUT "$numEval,$nbGoHare,$nbGoStag\n";
	  }
	  
  	close FILEOUT;
  }
}
