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




#ifndef ELITIST_PAIRING_HPP_
#define ELITIST_PAIRING_HPP_

#include <algorithm>
#include <boost/foreach.hpp>
#include <sferes/stc.hpp>
#include <sferes/ea/ea.hpp>
#include <sferes/fit/fitness.hpp>

#include <cmath>

namespace sferes
{
  namespace ea
  {
    typedef struct pair {
    	int ind1;
    	int ind2;
    	float fitness;
    	bool child;

    	pair() : ind1(-1), ind2(-1), fitness(0.0f), child(false) {}
    } pair_t;

		struct compare_pair
		{
		    inline bool operator() (const pair_t& ind1, const pair_t& ind2)
		    {
		        return (ind1.fitness > ind2.fitness);
		    }
		};

    SFERES_EA(ElitistPairing, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;
      
      static const unsigned mu = Params::pop::mu;
      static const unsigned lambda = Params::pop::lambda;

      static const unsigned nb_niches = Params::pop::nb_niches;

			ElitistPairing() : _step_size(nb_niches, 1.0f), _vec_niches(nb_niches), _vec_pairing(nb_niches)
			{ }

      void random_pop()
      {
      	if((Params::pop::pop_init > 0) && (Params::pop::pop_init >= mu*nb_niches))
      		this->_pop.resize(Params::pop::pop_init);
      	else
					this->_pop.resize(mu*nb_niches);

				int cpt_niche = 0;
				int cpt_indiv = 0;
				int nb_indiv_by_niche = this->_pop.size()/nb_niches;
				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();

					_vec_niches[cpt_niche].push_back(indiv);
					cpt_indiv++;

					if(cpt_indiv >= nb_indiv_by_niche)
					{
						cpt_indiv = 0;
						cpt_niche++;
					}
				}

				// Random one to one pairing
#ifdef AGAINST_ALL_NICHES
				for(size_t i = 0; i < nb_niches; ++i)
				{
					for(size_t j = 0; j < nb_niches; ++j)
					{
						if(i != j)
							_vec_pairing[i].push_back(true);
						else
							_vec_pairing[i].push_back(false);
					}
				}
#elif defined(ALL_PAIRINGS)
				for(size_t i = 0; i < nb_niches; ++i)
					for(size_t j = 0; j < nb_niches; ++j)
							_vec_pairing[i].push_back(true);
#else
				for(size_t i = 0; i < nb_niches/2; i++)
				{
					for(size_t j = 0; j < nb_niches; ++j)
					{
						_vec_pairing[i*2].push_back(false);
						_vec_pairing[i*2 + 1].push_back(false);
					}

					_vec_pairing[i*2][i*2 + 1] = true;
					_vec_pairing[i*2 + 1][i*2] = true;
				}
#endif

				this->_eval.eval(this->_pop, 0, this->_pop.size(), _vec_pairing);

				this->apply_modifier();
				for(size_t i = 0; i < nb_niches; i++)
				{
					std::sort(_vec_niches[i].begin(), _vec_niches[i].end(), fit::compare());
					_vec_niches[i].resize(mu);

					for(size_t j = 0; j < _vec_niches[i].size(); ++j)
						this->_pop[i*mu + j] = _vec_niches[i][j];
				}
				this->_pop.resize(mu*nb_niches);
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// We create the children
				std::vector<pop_t> vec_child_niches(nb_niches);
				pop_t child_pop;

				std::vector<int> parents_list(lambda);
				int parent_rank = 0;

				// We set the genome_from value as if each of the individuals is going to clone itself 
				// to the next generation
				for(size_t i = 0; i < mu; ++i)
					this->_pop[i]->gen().set_genome_from(i);

// #ifdef RESTART
// 				int nb_min_diversity = 0;
// 				for(size_t i = 0; i < mu; ++i)
// 					if(this->_pop[i]->fit().obj(1) < Params::pop::diversity_threshold)
// 						nb_min_diversity++;

// 				int total_restarts = Params::pop::prop_restart*nb_min_diversity;
// 				std::vector<size_t> ord_vect;
// 				misc::rand_ind(ord_vect, mu);
// 				int nb_restarts = 0;
// 				for(size_t i = 0; (i < mu) && (nb_restarts < total_restarts); ++i)
// 				{
// 					int index_ind = ord_vect[i];
// 					if(this->_pop[i]->fit().obj(1) < Params::pop::diversity_threshold)
// 					{
// 						this->_pop[i] = boost::shared_ptr<Phen>(new Phen());
// 						this->_pop[i]->gen().random();
// 						nb_restarts++;
// 					}
// 				}
// #endif

				int cpt_niche = 0;
				for(size_t i = 0; i < lambda*nb_niches; ++i)
				{
					child_pop.push_back(_vec_niches[cpt_niche][i%mu]->clone());
					vec_child_niches[cpt_niche].push_back(child_pop[i]);

					child_pop[i]->gen().set_genome_from(i%mu);

					// Mutation
					child_pop[i]->gen().mutate(_step_size[cpt_niche]);

					if((i + 1)%lambda == 0)
						cpt_niche++; 
				}
				assert(child_pop.size() == lambda*nb_niches);

				pop_t selection_pop;
#ifdef EVAL_PARENTS
#ifdef SEPARATE_PARENTS
				for(size_t i = 0; i < child_pop.size(); ++i)
					selection_pop.push_back(child_pop[i]);

				assert(selection_pop.size() == lambda*nb_niches);

				this->_eval.eval(selection_pop, 0, selection_pop.size(), _vec_pairing);

				selection_pop.clear();
				for(size_t i = 0; i < this->_pop.size(); ++i)
					selection_pop.push_back(this->_pop[i]);

				assert(selection_pop.size() == mu*nb_niches);

				this->_eval.eval(selection_pop, 0, selection_pop.size(), _vec_pairing);
#else
				for(size_t i = 0; i < nb_niches; ++i)
				{
					for(size_t j = 0; j < _vec_niches[i].size(); ++j)
						selection_pop.push_back(_vec_niches[i][j]);

					for(size_t j = 0; j < vec_child_niches[i].size(); ++j)
						selection_pop.push_back(vec_child_niches[i][j]);
				}

				assert(selection_pop.size() == (mu + lambda)*nb_niches);

				this->_eval.eval(selection_pop, 0, selection_pop.size(), _vec_pairing);
#endif
#else
				for(size_t i = 0; i < child_pop.size(); ++i)
					selection_pop.push_back(child_pop[i]);

				assert(selection_pop.size() == lambda*nb_niches);

				this->_eval.eval(selection_pop, 0, selection_pop.size(), _vec_pairing);
#endif

				// We update each niche independantly
				for(size_t i = 0; i < nb_niches; ++i)
				{
					int successful_offsprings = 0;
	
					std::sort(_vec_niches[i].begin(), _vec_niches[i].end(), fit::compare());

					// We count the number of offsprings better than the worst parent
					for(size_t j = 0; j < lambda; ++j)
					{
						if(vec_child_niches[i][j]->fit().value() > _vec_niches[i][mu - 1]->fit().value())
							successful_offsprings++;
					}
							
					// We modify the step_size
					float ps = successful_offsprings/(float)lambda;
					float factor = (1.0f/3.0f) * (ps - 0.2f) / (1.0f - 0.2f);
					_step_size[i] = _step_size[i] * exp(factor);

					_vec_niches[i].insert(_vec_niches[i].end(), vec_child_niches[i].begin(), vec_child_niches[i].end());
					std::sort(_vec_niches[i].begin(), _vec_niches[i].end(), fit::compare());
					_vec_niches[i].resize(mu);

					for(size_t j = 0; j < mu; ++j)
						this->_pop[i*mu + j] = _vec_niches[i][j];
				}

#ifdef EVOL_PAIRING
				if((this->gen() % Params::pop::evolve_pairing_period) == 0)
					evolve_pairing();
#endif

#ifdef PRUNING
				if((this->nb_eval() % Params::pop::pruning_eval_period) == 0)
				{
#ifdef REPLACE_WORST
					// We look for the best and worst niches
					float best_fitness = 0.0f, worst_fitness = 10000.0f;
					int best_niche = -1, worst_niche = -1;
					for(size_t i = 0; i < _vec_niches.size(); ++i)
					{
						float fitness = _vec_niches[i][0]->fit().value();
						if(fitness > best_fitness)
						{
							best_fitness = fitness;
							best_niche = i;
						}
						if(fitness < worst_fitness)
						{
							worst_fitness = fitness;
							worst_niche = i;
						}
					}

					if(best_niche != worst_niche)
					{
						for(size_t i = 0; i < mu; ++i)
						{
							this->_pop[worst_niche*mu + i] = this->_pop[best_niche*mu + i]->clone();
							this->_pop[worst_niche*mu + i]->gen().set_genome_from(best_niche*mu + i);
							this->_pop[worst_niche*mu + i]->fit().set_value(this->_pop[best_niche*mu + i]->fit().value());
							this->_vec_niches[worst_niche][i] = this->_pop[worst_niche*mu + i];
							_step_size[worst_niche] = 1.0f;
						}
					}
#endif
				}
#endif
				// dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }

      void evolve_pairing()
      {
      	for(size_t i = 0; i < _vec_niches.size(); ++i)
      	{
      		float best_fitness = _vec_niches[i][0]->fit().value();
      		std::vector<std::vector<bool> > best_vec_pairing = _vec_pairing;

      		for(size_t k = 0; k < Params::pop::nb_offsprings_evol_pairing; ++k)
      		{
	      		std::vector<std::vector<bool> > vec_pairing;

	      		// Mutations on the pairing vector
      			int cpt_false;
      			bool mut;
	      		do
	      		{
	      			cpt_false = 0;
	      			mut = false;
	      			vec_pairing = _vec_pairing;
		      		for(size_t j = 0; j < vec_pairing[i].size(); ++j)
		      		{
		      			if(misc::rand<float>() < Params::pop::proba_mut_pairing)
		      			{
		      				vec_pairing[i][j] = !vec_pairing[i][j];
		      				mut = true;
		      			}

		      			if(!vec_pairing[i][j])
		      				cpt_false++;
		      		}
	      		}
	      		while((cpt_false >= vec_pairing[i].size()) || (!mut));

	      		// Evaluation of the population
	      		int nb_indiv_by_niche = this->_pop.size()/nb_niches;
	      		int min_ind = i*nb_indiv_by_niche;
	      		int max_ind = min_ind + nb_indiv_by_niche;
						this->_eval.eval(this->_pop, min_ind, max_ind, vec_pairing);

						if(_vec_niches[i][0]->fit().value() > best_fitness)
						{
							best_fitness = _vec_niches[i][0]->fit().value();
							best_vec_pairing = vec_pairing;
						}
					}

					_vec_pairing = best_vec_pairing;
      	}
      }

      // Assumes all niches are sorted
      int find_best_niche() const
      {
      	int best_niche = 0;
      	float bestfit = _vec_niches[0][0]->fit().value();

      	for(size_t i = 1; i < _vec_niches.size(); ++i)
      	{
      		if(_vec_niches[i][0]->fit().value() > bestfit)
      		{
      			bestfit = _vec_niches[i][0]->fit().value();
      			best_niche = i;
      		}
      	}

      	return best_niche;
      }

      void load_niches()
      {
      	_vec_niches.resize(mu*nb_niches);
      	int cpt_niche = -1;
      	for(size_t i = 0; i < this->_pop.size(); ++i)
      	{
      		if(i%mu == 0)
      			cpt_niche++;

      		_vec_niches[cpt_niche].push_back(this->_pop[i]);
      	}

      	_vec_pairing.resize(nb_niches);
				for(size_t i = 0; i < nb_niches/2; i++)
				{
					for(size_t j = 0; j < nb_niches; ++j)
					{
						_vec_pairing[i*2].push_back(false);
						_vec_pairing[i*2 + 1].push_back(false);
					}

					_vec_pairing[i*2][i*2 + 1] = true;
					_vec_pairing[i*2 + 1][i*2] = true;
				}
			}

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
          // ind1->fit().eval_compet(*ind1, *ind2);
        }
        else
        {
          std::cerr << "Cannot open :" << fname
                    << "(does this file exist ?)" << std::endl;
          exit(1);
        }
      }

      const std::vector<pop_t>& vec_niches() const { return _vec_niches; }
      const std::vector<std::vector<bool> >& vec_pairing() const { return _vec_pairing; }

    protected:
    	std::vector<float> _step_size;

    	std::vector<pop_t> _vec_niches;

    	std::vector<std::vector<bool> > _vec_pairing;
    	float _fitness_pairing;
    };
  }
}
#endif
