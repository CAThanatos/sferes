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




#ifndef INVASION_EA_FINITE_HPP_
#define INVASION_EA_FINITE_HPP_

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
    SFERES_EA(InvasionEaFinite, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;

			InvasionEaFinite() : _step_size(1.0f)
			{ }

      void random_pop()
      {
      	this->_pop.clear();
      	this->_vec_fitness.clear();

      	_nb_genotypes = 0;
      	assert(Params::pop::pop_init <= Params::pop::size);
      	assert(Params::pop::size%Params::pop::pop_init == 0);
      	int nb_indiv = Params::pop::size/Params::pop::pop_init;
      	for(size_t i = 0; i < Params::pop::pop_init; ++i)
      	{
	      	this->_pop.push_back(boost::shared_ptr<Phen>(new Phen()));
	      	this->_pop[i]->random();
					this->_pop[i]->set_pop_pos(i);
					this->_pop[i]->develop();

					this->_eval.eval(this->_pop, _nb_genotypes, 0, _nb_genotypes + 1);

					this->_pop[i]->set_freq((float)nb_indiv/(float)Params::pop::size);
					this->_pop[i]->set_evaluated(true);

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

				// Generation of offsprings
				pop_t pop_offsprings(Params::pop::size + _nb_genotypes);
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					pop_offsprings[i] = this->_pop[i]->clonePhen();
					pop_offsprings[i]->set_freq(0.0f);
				}

				int old_nb_genotypes = _nb_genotypes;

#ifdef FITPROP
				float fitness_tot = 0.0f;
				for(size_t i = 0; i < _nb_genotypes; ++i)
					fitness_tot += this->_pop[i]->fit().value()*this->_pop[i]->get_freq();

				if(fitness_tot > 0.0f)
				{
					for(size_t j = 0; j < Params::pop::size; j += Params::pop::nb_offsprings)
					{
						float random_child = misc::rand<float>();
						float fit_sum = 0.0f;

						for(size_t i = 0; i < old_nb_genotypes; ++i)
						{
							fit_sum += (this->_pop[i]->fit().value()*this->_pop[i]->get_freq())/fitness_tot;

							if((random_child <= fit_sum) || (i == old_nb_genotypes - 1))
							{
								generate_new_offspring(pop_offsprings, i);
								break;
							}
						}
					}
				}
				else
				{
					for(size_t i = 0; i < Params::pop::size; i += Params::pop::nb_offsprings)
					{
						int random_child = misc::rand((int)0, (int)old_nb_genotypes);
						assert(random_child >= 0 && random_child < old_nb_genotypes);

						generate_new_offspring(pop_offsprings, i);
					}
				}
#else
				for(size_t i = 0; i < Params::pop::size; ++i)
				{
					int random_child = misc::rand((int)0, (int)old_nb_genotypes);
					assert(random_child >= 0 && random_child < old_nb_genotypes);

					generate_new_offspring(pop_offsprings, i);
				}
#endif
				std::vector<int> vec_remove_genotypes;

				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					if(pop_offsprings[i]->get_freq() <= 0.0f)
						vec_remove_genotypes.push_back(i);
				}

				remove_genotypes(vec_remove_genotypes, pop_offsprings);

				assert(_nb_genotypes > 0);
				assert(_nb_genotypes <= Params::pop::size);

#ifdef EVAL_PARENTS
				if((this->gen() % Params::pop::eval_parents_period) == 0)
					for(size_t i = 0; i < _nb_genotypes; ++i)
						if(pop_offsprings[i]->is_evaluated())
							pop_offsprings[i]->set_evaluated(false);
#endif

				// We evaluate all new mutants
				for(size_t i = 0; i < _nb_genotypes; ++i)
					if(!pop_offsprings[i]->is_evaluated())
						pop_offsprings[i]->develop();

				for(size_t i = 0; i < _nb_genotypes; ++i)
					if(!pop_offsprings[i]->is_evaluated())
					{
						this->_eval.eval(pop_offsprings, i, 0, _nb_genotypes);
						pop_offsprings[i]->set_evaluated(true);
					}

				this->_pop.clear();
				this->_pop.resize(_nb_genotypes);

				for(size_t i = 0; i < _nb_genotypes; ++i)
					this->_pop[i] = pop_offsprings[i];

				assert(_nb_genotypes > 0);
				assert(_nb_genotypes <= Params::pop::size);

				// We update the fitness and preys hunted information
				float total_freq = 0.0f;
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					total_freq += this->_pop[i]->get_freq();

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

#ifdef STEP_SIZE
				_step_size = 2 * _step_size;
#endif
				// assert(total_freq == 1.0f);

				// std::partial_sort(this->_pop.begin(), this->_pop.begin() + _nb_genotypes,
				// 			this->_pop.end(), fit::compare());
							
				// dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }

      int nb_genotypes() const { return _nb_genotypes; }

      void load_genotypes() { _nb_genotypes = this->_pop.size(); }

      void load_genome(const std::string fname) 
      {
        // Add a particular individual to the population
        std::string path = fname.substr(0, fname.find_last_of("/") + 1);
        std::ifstream ifs2((path + "genome.dat").c_str());

        if (!ifs2.fail())
        {
          std::cout << "Adding individual(s) with genotype in genome.dat..." << std::endl;
          
          std::vector<std::vector<float> > new_inds;
          while(ifs2.good())
          {
            std::string line;
            std::getline(ifs2, line);

            std::stringstream ss(line);
            std::string gene;

            std::vector<float> vec_genotype;
            while(std::getline(ss, gene, ','))
            	vec_genotype.push_back(std::atof(gene.c_str()));

            new_inds.push_back(vec_genotype);
          }

          int old_nb_genotypes = _nb_genotypes;


          std::cout << "Adding " << new_inds.size() << " individuals" << std::endl;
          for(size_t i = 0; i < new_inds.size(); ++i)
          {
          	// We add the individual to the list of genotypes
						boost::shared_ptr<Phen> new_indiv = boost::shared_ptr<Phen>(new Phen());

						for(unsigned j = 0; j < new_indiv->gen().size(); ++j)
							new_indiv->gen().data(j, new_inds[i][j]);

						new_indiv->set_pop_pos(_nb_genotypes); 
						new_indiv->set_freq(1.0f/(float)Params::pop::size);
						this->_pop.push_back(new_indiv);

						// We remove one of the individuals
						int rand_ind = misc::rand<int>(0, old_nb_genotypes);
						this->_pop[rand_ind]->set_freq(this->_pop[rand_ind]->get_freq() - 1.0f/(float)Params::pop::size);

						if(this->_pop[rand_ind]->get_freq() <= 0.0f)
						{
							std::vector<int> vec_remove_genotypes;
							vec_remove_genotypes.push_back(rand_ind);

							remove_genotypes(vec_remove_genotypes, this->_pop);
						}

						_nb_genotypes++;
          }

        }

				// We evaluate all new mutants (and parents if need be)
				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					this->_pop[i]->develop();
					this->_pop[i]->set_pop_pos(i);
				}

				for(size_t i = 0; i < _nb_genotypes; ++i)
				{
					this->_eval.eval(this->_pop, i, 0, _nb_genotypes);
					this->_pop[i]->set_evaluated(true);
				}

        // We evaluate all the population
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

      void fill_pop()
      {}

      void play_run(const std::string& fname)
      {
        std::ifstream ifs(fname.c_str());

        boost::shared_ptr<Phen> ind1 = boost::shared_ptr<Phen>(new Phen());;
        boost::shared_ptr<Phen> ind2 = boost::shared_ptr<Phen>(new Phen());;

        if (!ifs.fail())
        {
          int numIndiv = 0;
          while(ifs.good())
          {
            std::string line;
            std::getline(ifs, line);

            std::stringstream ss(line);
            std::string gene;
            int cpt = 0;
            while(std::getline(ss, gene, ','))
            {
              if(numIndiv == 0)
                ind1->gen().data(cpt, std::atof(gene.c_str()));
              else
                ind2->gen().data(cpt, std::atof(gene.c_str()));

              cpt++;
            }

            numIndiv++;
          }

          ind1->develop();
          ind2->develop();
          ind1->fit().set_mode(fit::mode::view);
          // std::string file_behaviour = ea.res_dir() + "/behaviourGen_" + boost::lexical_cast<std::string>(ea.gen()) + ".bmp";
          // ind1->fit().set_file_behaviour("./videoDir");
          ind1->fit().eval_compet(*ind1, *ind2);
        }
        else
        {
          std::cerr << "Cannot open :" << fname
                    << "(does this file exist ?)" << std::endl;
          exit(1);
        }
      }

    protected:
    	size_t _nb_genotypes;

    	std::vector<float> _vec_fitness;
    	int _step_size;

    	void generate_new_offspring(pop_t& pop_offsprings, int pos_parent)
    	{
				indiv_t offspring = this->_pop[pos_parent]->clone();

				bool mutation = false;

#ifdef RANDOM_MUTANT
				// Probability that the mutation produces a totally random new individual
				float proba_random_mutant = misc::rand<float>();

				if(proba_random_mutant < Params::evo_float::random_mutant_probability)
				{
					offspring->gen().random();
					mutation = true;
				}
				else
					mutation = offspring->gen().mutate(_step_size);
#else
				mutation = offspring->gen().mutate(_step_size);
#endif

				float freq_offsprings = (float)Params::pop::nb_offsprings/(float)Params::pop::size;

				if(mutation)
				{
					pop_offsprings[_nb_genotypes] = offspring;
					pop_offsprings[_nb_genotypes]->set_pop_pos(_nb_genotypes);
					pop_offsprings[_nb_genotypes]->set_freq(freq_offsprings);

					_nb_genotypes++;
				}
				else
				{
					pop_offsprings[pos_parent]->set_freq(pop_offsprings[pos_parent]->get_freq() + freq_offsprings);
				}
    	}

    	void remove_genotypes(std::vector<int>& vec_remove_genotypes, std::vector<indiv_t>& vec_pop)
    	{
    		for(size_t i = 0; i < vec_remove_genotypes.size(); ++i)
    		{
    			int genotype = vec_remove_genotypes[i];

					if(vec_remove_genotypes[i] < (_nb_genotypes - 1))
					{
						// We move the last genotype at this index
						vec_pop[genotype] = vec_pop[_nb_genotypes - 1];
						vec_pop[genotype]->set_pop_pos(genotype);

						// We update all the payoffs
						for(size_t j = 0; j < _nb_genotypes - 1; ++j)
						{
							vec_pop[j]->set_payoff(genotype, vec_pop[j]->get_payoff(_nb_genotypes - 1));

							vec_pop[j]->set_nb_hares(genotype, vec_pop[j]->get_nb_hares(_nb_genotypes - 1), vec_pop[j]->get_nb_hares_solo(_nb_genotypes - 1));
							vec_pop[j]->set_nb_sstags(genotype, vec_pop[j]->get_nb_sstags(_nb_genotypes - 1), vec_pop[j]->get_nb_sstags_solo(_nb_genotypes - 1));
							vec_pop[j]->set_nb_bstags(genotype, vec_pop[j]->get_nb_bstags(_nb_genotypes - 1), vec_pop[j]->get_nb_bstags_solo(_nb_genotypes - 1));
						}

						// We must update vec_remove_genotypes
						for(size_t j = i + 1; j < vec_remove_genotypes.size(); ++j)
							if(vec_remove_genotypes[j] == _nb_genotypes - 1)
								vec_remove_genotypes[j] = genotype;
					}

					_nb_genotypes--;
    		}
			}
    };
  }
}
#endif
