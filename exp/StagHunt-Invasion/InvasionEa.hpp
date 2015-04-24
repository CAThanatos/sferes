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

			ResidentMutant() : _step_size(1)
			{ }

      void random_pop()
      {
      	this->_pop.resize(Params::simu::pop_size);
      	this->_vec_payoffs.resize(Params::simu::pop_size);
      	this->_vec_freqs.resize(Params::simu::pop_size);

      	this->_pop[0] = boost::shared_ptr<Phen>(new Phen());
      	this->_pop[0]->random();

      	_nb_genotypes = 1;

				this->_eval.eval(this->_pop, _nb_genotypes, 0, _nb_genotypes);
				this->_pop[0]->set_freq(1.0f);
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// A mutant invades
				this->_pop[_nb_genotypes] = this->_pop[0]->clone();
				this->_pop[_nb_genotypes]->gen().mutate(_step_size);

				// We evaluate this mutant's payoff against everyother residents
				this->_eval.eval(this->_pop, _nb_genotypes, 0, _nb_genotypes);

				// We set its frequency and update that of other individuals
				this->_pop[_nb_genotypes].set_freq(Params::pop::invasion_frequency);
				for(size_t i = 0; i < _nb_genotypes; ++i)
					this->_pop[i].set_freq(this->_pop[i].get_freq() - Params::pop::invasion_frequency/(float)(_nb_genotypes + 1));

				_nb_genotypes++;

				// We compute the equilibrium
				int max_generations = 10000;
				int generation = 0;
				do
				{
					float modif = 0.0f;
					float proba = misc::rand();

					_vec_fitness.clear();
					_vec_fitness.resize(_nb_genotypes);
					float fitnessMean = 0.0f;
					for(size_t i = 0; i < _nb_genotypes; ++i)
					{
						_vec_fitness[i] = 0.0f;
						for(size_t j = 0; j < _nb_genotypes; ++j)
							_vec_fitness[i] += this->_pop[i].get_payoff(j) * this->_pop[j].get_freq();

						fitnessMean += _vec_fitness[i];
					}
					fitnessMean /= (float)_nb_genotypes

					for(size_t i = 0; i < _nb_genotypes; ++i)
					{
						float old_freq = this->_pop[i].get_freq();
						this->_pop[i].set_freq(this->_pop[i].get_freq()*_vec_fitness[i]/fitnessMean);
						float new_freq = this->_pop[i].get_freq();

						modif += fabs(new_freq - old_freq);
					}
					modif /= _nb_genotypes;

					generation++;

					// We continue while we still have computation time AND there has been more than 1% modification AND no new mutant appeared
				}	while((generation < max_generations) && (modif > 0.01f) && (proba > Params::evo_float::mutation_rate));

				// We update the population: we remove the genotypes with freq = 0
				float min_threshold = 0.001f;
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					if(this->_pop[i].get_freq < min_threshold; ++i)
					{
						// We move the last genotype at this index
						this->_pop[i] = this->_pop[_nb_genotypes - 1];

						// We update all the payoffs
						for(size_t j = 0; j < _nb_genotypes; ++j)
							this->_pop[j].set_payoff(i, this->_pop[j].get_payoff(_nb_genotypes - 1));

						_nb_genotypes--;
					}
				}

				std::partial_sort(this->_pop.begin(), this->_pop.begin() + _nb_genotypes,
							this->_pop.end(), fit::compare());
							
				dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }
      
    protected:
    	float _step_size;
    	size_t _nb_genotypes;

    	std::vector<float> _vec_fitness;
    };
  }
}
#endif
