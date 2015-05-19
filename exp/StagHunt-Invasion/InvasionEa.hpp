//| This file is a part of the sferes2 framework.
//| Copyright 2009, ISIR / Universite Pierre et Marie Curie (UPMC)
//| Main contributor(s): Jean-Baptiste Mouret, mouret@isir.fr
//|
//| This software is a computer program whose purpose is to facilitate
//| experiments in evolutionary computation and evolutionary robotics.
//|
//| This software is governed by the CeCILL license under French law
//| and abiding by the rules of distribution of free software.  You
//| can use, modify and/ or redistribute the software under the terms
//| of the CeCILL license as circulated by CEA, CNRS and INRIA at the
//| following URL "http://www.cecill.info".
//|
//| As a counterpart to the access to the source code and rights to
//| copy, modify and redistribute granted by the license, users are
//| provided only with a limited warranty and the software's author,
//| the holder of the economic rights, and the successive licensors
//| have only limited liability.
//|
//| In this respect, the user's attention is drawn to the risks
//| associated with loading, using, modifying and/or developing or
//| reproducing the software by the user in light of its specific
//| status of free software, that may mean that it is complicated to
//| manipulate, and that also therefore means that it is reserved for
//| developers and experienced professionals having in-depth computer
//| knowledge. Users are therefore encouraged to load and test the
//| software's suitability as regards their requirements in conditions
//| enabling the security of their systems and/or data to be ensured
//| and, more generally, to use and operate it in the same conditions
//| as regards security.
//|
//| The fact that you are presently reading this means that you have
//| had knowledge of the CeCILL license and that you accept its terms.




#ifndef INVASION_EA_HPP_
#define INVASION_EA_HPP_

#include <algorithm>
#include <boost/foreach.hpp>
#include <sferes/stc.hpp>
#include <sferes/ea/ea.hpp>
#include <sferes/fit/fitness.hpp>
#include <sferes/misc/rand.hpp>

#include <cmath>

namespace sferes
{
  namespace ea
  {
    SFERES_EA(InvasionEa, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;

			InvasionEa()
			{ }

      void random_pop()
      {
      	this->_pop.clear();
      	this->_vec_fitness.clear();

      	_nb_genotypes = 0;
      	for(size_t i = 0; i < Params::pop::pop_init; ++i)
      	{
	      	this->_pop.push_back(boost::shared_ptr<Phen>(new Phen()));
	      	this->_pop[i]->random();
					this->_pop[i]->set_pop_pos(i);

					this->_eval.eval(this->_pop, _nb_genotypes, 0, _nb_genotypes + 1);

					this->_pop[i]->set_freq(1.0f/(float)Params::pop::pop_init);

					_nb_genotypes++;
	      }

	      for(size_t i = 0; i < _nb_genotypes; ++i)
	      {
					float fitness = 0;
					float nb_hares = 0, nb_hares_solo = 0;
					float nb_sstags = 0, nb_sstags_solo = 0;
					float nb_bstags = 0, nb_bstags_solo = 0;

					for(size_t j = 0; j < _nb_genotypes; ++j)
					{
						fitness += this->_pop[i]->get_payoff(j) * this->_pop[j]->get_freq();

						nb_hares += this->_pop[i]->get_nb_hares(j) * this->_pop[j]->get_freq();
						nb_hares_solo += this->_pop[i]->get_nb_hares_solo(j) * this->_pop[j]->get_freq();

						nb_sstags += this->_pop[i]->get_nb_sstags(j) * this->_pop[j]->get_freq();
						nb_sstags_solo += this->_pop[i]->get_nb_sstags_solo(j) * this->_pop[j]->get_freq();

						nb_bstags += this->_pop[i]->get_nb_bstags(j) * this->_pop[j]->get_freq();
						nb_bstags_solo += this->_pop[i]->get_nb_bstags_solo(j) * this->_pop[j]->get_freq();
					}

					this->_pop[i]->fit().set_value(fitness);
					this->_pop[i]->set_nb_hares(nb_hares, nb_hares_solo);
					this->_pop[i]->set_nb_sstags(nb_sstags, nb_sstags_solo);
					this->_pop[i]->set_nb_bstags(nb_bstags, nb_bstags_solo);
	      }
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// A mutant invades
				// We choose which of the genotype is the parent
#ifdef FITPROP
				float fitness_tot = 0.0f;
				for(size_t i = 0; i < _nb_genotypes; ++i)
					fitness_tot += this->_pop[i]->fit().value();

				if(fitness_tot > 0.0f)
				{
					float random_child = misc::rand(1.0f);
					float fit_sum = 0.0f;

					for(size_t i = 0; i < _nb_genotypes; ++i)
					{
						fit_sum += this->_pop[i]->fit().value()/fitness_tot;

						if((random_child <= fit_sum) || (i == _nb_genotypes - 1))
						{
							this->_pop.push_back(this->_pop[i]->clone());
							break;
						}
					}
				}
				else
				{
					int random_child = misc::rand((int)0, (int)_nb_genotypes);
					assert(random_child >= 0 && random_child < _nb_genotypes);

					this->_pop.push_back(this->_pop[random_child]->clone());
				}
#else
				int random_child = misc::rand((int)0, (int)_nb_genotypes);
				assert(random_child >= 0 && random_child < _nb_genotypes);

				this->_pop.push_back(this->_pop[random_child]->clone());
#endif

#ifdef RANDOM_MUTANT
				// Probability that the mutation produces a totally random new individual
				float proba_random_mutant = misc::rand<float>();

				if(proba_random_mutant < Params::evo_float::random_mutant_probability)
					this->_pop[_nb_genotypes]->gen().random();
				else
					this->_pop[_nb_genotypes]->gen().mutate();
#else
				this->_pop[_nb_genotypes]->gen().mutate();
#endif

				this->_pop[_nb_genotypes]->set_pop_pos(_nb_genotypes);

				// We evaluate this mutant's payoff against every other residents
				this->_eval.eval(this->_pop, _nb_genotypes, 0, _nb_genotypes + 1);

				// We set its frequency and update that of other individuals
				this->_pop[_nb_genotypes]->set_freq(Params::pop::invasion_frequency);
				this->_pop[_nb_genotypes]->set_pop_pos(_nb_genotypes);

				int pos_mutant = _nb_genotypes;
				std::vector<int> vec_remove_genotypes;
				_nb_genotypes++;

				this->_pop[random_child]->set_freq(this->_pop[random_child]->get_freq() - Params::pop::invasion_frequency);
				if(this->_pop[random_child]->get_freq() < 0.0f)
					vec_remove_genotypes.push_back(random_child);

				remove_genotypes(vec_remove_genotypes, pos_mutant);

				// float to_divide = Params::pop::invasion_frequency;
				// while(to_divide > 0.0f)
				// {
				// 	float next_divide = 0.0f;
				// 	vec_remove_genotypes.clear();
				// 	for(size_t i = 0; i < _nb_genotypes; ++i)
				// 	{
				// 		if(i != pos_mutant)
				// 		{
				// 			this->_pop[i]->set_freq(this->_pop[i]->get_freq() - to_divide/(float)(_nb_genotypes - 1));

				// 			if(this->_pop[i]->get_freq() < 0.0f)
				// 			{
				// 				next_divide += 0.0f - this->_pop[i]->get_freq();
				// 				vec_remove_genotypes.push_back(i);
				// 			}
				// 		}
				// 	}

				// 	remove_genotypes(vec_remove_genotypes, pos_mutant);
				// 	to_divide = next_divide;
				// }

				// We compute the equilibrium
				int max_generations = 10000;
				int generation = 0;
				float proba;
				float modif;
				do
				{
					// std::cout << "nieh ?" << std::endl;
					modif = 0.0f;

					_vec_fitness.clear();
					_vec_fitness.resize(_nb_genotypes);

					float fitnessMean = 0.0f;
					for(size_t i = 0; i < _nb_genotypes; ++i)
					{
						_vec_fitness[i] = 0.0f;
						for(size_t j = 0; j < _nb_genotypes; ++j)
							_vec_fitness[i] += this->_pop[i]->get_payoff(j) * this->_pop[j]->get_freq();

						fitnessMean += this->_pop[i]->get_freq()*_vec_fitness[i];
					}

					if(fitnessMean <= 0.0f)
						break;

					for(size_t i = 0; i < _nb_genotypes; ++i)
					{
						float old_freq = this->_pop[i]->get_freq();
						this->_pop[i]->set_freq(std::min(std::max(this->_pop[i]->get_freq()*_vec_fitness[i]/fitnessMean, 0.0f), 1.0f));
						float new_freq = this->_pop[i]->get_freq();

						// // We consider that when a genotype is below min_threshold (0.001 by default)
						// // this genotype doesn't exist in the population anymore
						// if(new_freq < Params::pop::min_threshold)
						// 	this->_pop[i]->set_freq(0.0f);

						modif += fabs(new_freq - old_freq)/old_freq;
					}
					modif /= _nb_genotypes;

					generation++;
					proba = misc::rand(1.0f);

					// We continue while we still have computation time AND there has been more than 1% modification AND no new mutant appeared
				}	while((generation < max_generations) && (proba > Params::evo_float::mutant_apparition_rate) && (modif > 0.01f));

				// We update the population: we remove the genotypes with freq = 0
				vec_remove_genotypes.clear();
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					assert(this->_pop[i]->get_freq() >= 0.0f && this->_pop[i]->get_freq() <= 1.0f);

					if(this->_pop[i]->get_freq() < Params::pop::min_threshold)
						vec_remove_genotypes.push_back(i);
				}

				remove_genotypes(vec_remove_genotypes, pos_mutant);

				assert(_nb_genotypes > 0);

				// We update the fitness and preys hunted information
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					float fitness = 0;
					float nb_hares = 0, nb_hares_solo = 0;
					float nb_sstags = 0, nb_sstags_solo = 0;
					float nb_bstags = 0, nb_bstags_solo = 0;

					for(size_t j = 0; j < _nb_genotypes; ++j)
					{
						fitness += this->_pop[i]->get_payoff(j) * this->_pop[j]->get_freq();

						nb_hares += this->_pop[i]->get_nb_hares(j) * this->_pop[j]->get_freq();
						nb_hares_solo += this->_pop[i]->get_nb_hares_solo(j) * this->_pop[j]->get_freq();

						nb_sstags += this->_pop[i]->get_nb_sstags(j) * this->_pop[j]->get_freq();
						nb_sstags_solo += this->_pop[i]->get_nb_sstags_solo(j) * this->_pop[j]->get_freq();

						nb_bstags += this->_pop[i]->get_nb_bstags(j) * this->_pop[j]->get_freq();
						nb_bstags_solo += this->_pop[i]->get_nb_bstags_solo(j) * this->_pop[j]->get_freq();
					}

					this->_pop[i]->fit().set_value(fitness);
					this->_pop[i]->set_nb_hares(nb_hares, nb_hares_solo);
					this->_pop[i]->set_nb_sstags(nb_sstags, nb_sstags_solo);
					this->_pop[i]->set_nb_bstags(nb_bstags, nb_bstags_solo);
				}

				// std::partial_sort(this->_pop.begin(), this->_pop.begin() + _nb_genotypes,
				// 			this->_pop.end(), fit::compare());
							
				// dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }
      
    protected:
    	size_t _nb_genotypes;

    	std::vector<float> _vec_fitness;

    	void remove_genotypes(std::vector<int>& vec_remove_genotypes, int& pos_mutant)
    	{
    		for(size_t i = 0; i < vec_remove_genotypes.size(); ++i)
    		{
    			int genotype = vec_remove_genotypes[i];

					if(vec_remove_genotypes[i] < (_nb_genotypes - 1))
					{
						// We move the last genotype at this index
						this->_pop[genotype] = this->_pop[_nb_genotypes - 1];
						this->_pop[genotype]->set_pop_pos(genotype);

						if(pos_mutant == _nb_genotypes - 1)
							pos_mutant = genotype;

						// We update all the payoffs
						for(size_t j = 0; j < _nb_genotypes; ++j)
						{
							this->_pop[j]->set_payoff(genotype, this->_pop[j]->get_payoff(_nb_genotypes - 1));

							this->_pop[j]->set_nb_hares(genotype, this->_pop[j]->get_nb_hares(_nb_genotypes - 1), this->_pop[j]->get_nb_hares_solo(_nb_genotypes - 1));
							this->_pop[j]->set_nb_sstags(genotype, this->_pop[j]->get_nb_sstags(_nb_genotypes - 1), this->_pop[j]->get_nb_sstags_solo(_nb_genotypes - 1));
							this->_pop[j]->set_nb_bstags(genotype, this->_pop[j]->get_nb_bstags(_nb_genotypes - 1), this->_pop[j]->get_nb_bstags_solo(_nb_genotypes - 1));
						}

						// We must update vec_remove_genotypes
						for(size_t j = i + 1; j < vec_remove_genotypes.size(); ++j)
							if(vec_remove_genotypes[j] == _nb_genotypes - 1)
								vec_remove_genotypes[j] = genotype;
					}

					_nb_genotypes--;
    		}

				this->_pop.resize(_nb_genotypes);
			}
    };
  }
}
#endif
