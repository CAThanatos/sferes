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




#ifndef ELITIST_TUPLE_HPP_
#define ELITIST_TUPLE_HPP_

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

    SFERES_EA(ElitistTuple, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;
      
      static const unsigned mu = Params::pop::mu;
      static const unsigned lambda = Params::pop::lambda;
      // bool compare_pair(const pair_t& i1, const pair_t& i2) { return (i1.fitness > i2.fitness); }

			ElitistTuple() : _step_size(1), _vec_pairs(mu/2)
			{ }

      void random_pop()
      {
				this->_pop.resize(mu);
				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();
				}

				// Random pairing
				std::vector<int> available_ind(mu);
				int nb_available = mu;

				for(size_t i = 0; i < mu; ++i)
					available_ind[i] = i;

				std::vector<int> vec_pairing(mu);
				int cpt_pair = 0;
				for(size_t i = 0; i < mu/2; ++i)
				{
					int partner = -1;
					do
					{
						partner = misc::rand(1, nb_available);
					} while((partner < 0) || (partner >= nb_available));

					_vec_pairs[cpt_pair].ind1 = available_ind[0];
					_vec_pairs[cpt_pair].ind2 = available_ind[partner];
					_vec_pairs[cpt_pair].fitness = 0.0f;

					vec_pairing[available_ind[0]] = available_ind[partner];
					vec_pairing[available_ind[partner]] = available_ind[0];

					available_ind[partner] = available_ind[nb_available - 1];
					available_ind[0] = available_ind[nb_available - 2];
					nb_available -= 2;

					cpt_pair++;
				}

				this->_eval.eval(this->_pop, 0, this->_pop.size(), vec_pairing);

				// The fitness of a pair is equal to the mean of both individuals
				for(size_t i = 0; i < _vec_pairs.size(); ++i)
					_vec_pairs[i].fitness = (this->_pop[_vec_pairs[i].ind1]->fit().value() + this->_pop[_vec_pairs[i].ind2]->fit().value())/2.0f;

				this->apply_modifier();
				std::sort(_vec_pairs.begin(), _vec_pairs.end(), ea::compare_pair());
				this->_pop.resize(mu);
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// We create the children
				pop_t child_pop;
				std::vector<ea::pair_t> vec_child_pairs(lambda/2);
				std::vector<int> vec_child_pairing(lambda);

				std::vector<int> parents_list(lambda/2);
				int pair_rank = 0;

				// We set the genome_from value as if each of the individuals is going to clone itself 
				// to the next generation
				for(size_t i = 0; i < mu; ++i)
					this->_pop[i]->gen().set_genome_from(i);

				int cpt_pair = 0;
				for(size_t i = 0; i < lambda; i += 2)
				{
					// Cloning of a pair
					child_pop.push_back(this->_pop[_vec_pairs[pair_rank%(mu/2)].ind1]->clone());

#ifdef RANDOM_MUTANT
					float proba_random_mutant = misc::rand<float>();

					if(proba_random_mutant < Params::evo_float::random_mutant_probability)
						child_pop[i]->gen().random();
					else
						child_pop[i]->gen().set_genome_from(_vec_pairs[pair_rank%(mu/2)].ind1);
#else
					child_pop[i]->gen().set_genome_from(_vec_pairs[pair_rank%(mu/2)].ind1);
#endif

					// Mutation
					child_pop[i]->gen().mutate(_step_size);

					child_pop.push_back(this->_pop[_vec_pairs[pair_rank%(mu/2)].ind2]->clone());

#ifdef RANDOM_MUTANT
					float proba_random_mutant = misc::rand<float>();

					if(proba_random_mutant < Params::evo_float::random_mutant_probability)
						child_pop[i + 1]->gen().random();
					else
						child_pop[i + 1]->gen().set_genome_from(_vec_pairs[pair_rank%(mu/2)].ind2);
#else
					child_pop[i + 1]->gen().set_genome_from(_vec_pairs[pair_rank%(mu/2)].ind2);
#endif

					// Mutation
					child_pop[i + 1]->gen().mutate(_step_size);

					parents_list[cpt_pair] = pair_rank%(mu/2);

					vec_child_pairs[cpt_pair].ind1 = i;
					vec_child_pairs[cpt_pair].ind2 = i + 1;
					vec_child_pairs[cpt_pair].fitness = 0.0f;
					vec_child_pairs[cpt_pair].child = true;

					vec_child_pairing[i] = i + 1;
					vec_child_pairing[i + 1] = i;

					pair_rank++;
					cpt_pair++;
				}

				assert(child_pop.size() == lambda);

#ifdef TUPLE_SWAP
				// There is a certain probability that we swap individuals between pairs
				for(size_t i = 0; i < vec_child_pairs.size(); ++i)
				{
					float proba_swap = misc::rand<float>();

					if(proba_swap < Params::evo_float::tuple_swap_probability)
					{
						int pair = -1;

						// We randomly select the pair with which we swap
						do
						{
							pair = misc::rand<int>(0, (int)(vec_child_pairs.size()));
						} while ((pair == i) || (pair < 0) || (pair >= vec_child_pairs.size()));

						vec_child_pairing[vec_child_pairs[i].ind1] = vec_child_pairs[pair].ind2;
						vec_child_pairing[vec_child_pairs[pair].ind2] = vec_child_pairs[i].ind1;

						vec_child_pairing[vec_child_pairs[pair].ind1] = vec_child_pairs[i].ind2;
						vec_child_pairing[vec_child_pairs[i].ind2] = vec_child_pairs[pair].ind1;

						// And the randomly select wich individuals are swapped
						bool ind1_pair1 = misc::flip_coin();
						bool ind1_pair2 = misc::flip_coin();

						if(ind1_pair1)
						{
							int tmp_ind = vec_child_pairs[i].ind1;

							if(ind1_pair2)
							{
								vec_child_pairs[i].ind1 = vec_child_pairs[pair].ind1;
								vec_child_pairs[pair].ind1 = tmp_ind;
							}
							else
							{
								vec_child_pairs[i].ind1 = vec_child_pairs[pair].ind2;
								vec_child_pairs[pair].ind2 = tmp_ind;
							}
						}
						else
						{
							int tmp_ind = vec_child_pairs[i].ind2;

							if(ind1_pair2)
							{
								vec_child_pairs[i].ind2 = vec_child_pairs[pair].ind1;
								vec_child_pairs[pair].ind1 = tmp_ind;
							}
							else
							{
								vec_child_pairs[i].ind2 = vec_child_pairs[pair].ind2;
								vec_child_pairs[pair].ind2 = tmp_ind;
							}
						}
					}
				}
#endif

				// Evaluation of the children and the parents if need be
				this->_eval.eval(child_pop, 0, child_pop.size(), vec_child_pairing);

#ifdef EVAL_PARENTS
				std::vector<int> vec_pairing(mu);
				for(size_t i = 0; i < _vec_pairs.size(); ++i)
				{
					vec_pairing[_vec_pairs[i].ind1] = _vec_pairs[i].ind2;
					vec_pairing[_vec_pairs[i].ind2] = _vec_pairs[i].ind1;
				}
				// std::cout << "parents" << std::endl;
				this->_eval.eval(this->_pop, 0, this->_pop.size(), vec_pairing);
#endif

				// The fitness of a pair is equal to the mean of both individuals
				for(size_t i = 0; i < vec_child_pairs.size(); ++i)
					vec_child_pairs[i].fitness = (child_pop[vec_child_pairs[i].ind1]->fit().value() + child_pop[vec_child_pairs[i].ind2]->fit().value())/2.0f;

				int successful_offsprings = 0;

#ifdef ONE_PLUS_ONE_REPLACEMENT
				// We count the number of offsprings who are better than their parents
				// and replace the parent population if need be
				std::vector<bool> replaced(mu/2, false);
				for(size_t i = 0; i < lambda/2; ++i)
				{
					if(vec_child_pairs[i].fitness > this->_vec_pairs[parents_list[i]].fitness)
					{
						successful_offsprings++;
						
						if(!replaced[parents_list[i]])
						{
							this->_pop[_vec_pairs[parents_list[i]].ind1] = child_pop[vec_child_pairs[i].ind1];
							this->_pop[_vec_pairs[parents_list[i]].ind2] = child_pop[vec_child_pairs[i].ind2];

							_vec_pairs[parents_list[i]].fitness = vec_child_pairs[i].fitness;
							replaced[parents_list[i]] = true;
						}
					}
				}
#elif defined(N_PLUS_N_REPLACEMENT)
				// We count the number of offsprings better than the worst parent
				for(size_t i = 0; i < lambda/2; ++i)
				{
					if(vec_child_pairs[i].fitness > _vec_pairs[_vec_pairs.size() - 1].fitness)
						successful_offsprings++;
				}

				_vec_pairs.insert(_vec_pairs.end(), vec_child_pairs.begin(), vec_child_pairs.end());
				std::sort(_vec_pairs.begin(), _vec_pairs.end(), ea::compare_pair());
							
				pop_t new_pop;

				// We select the mu/2 best pairs (and mu best individuals)
				for(size_t i = 0; i < mu/2; ++i)
				{
					if(_vec_pairs[i].child)
					{
						new_pop.push_back(child_pop[_vec_pairs[i].ind1]);
						new_pop.push_back(child_pop[_vec_pairs[i].ind2]);
					}
					else
					{
						new_pop.push_back(this->_pop[_vec_pairs[i].ind1]);
						new_pop.push_back(this->_pop[_vec_pairs[i].ind2]);
					}

					_vec_pairs[i].ind1 = (i*2);
					_vec_pairs[i].ind2 = (i*2) + 1;
					_vec_pairs[i].child = false;
				}

				_vec_pairs.resize(mu/2);
				this->_pop = new_pop;
#endif
							
				// We modify the step_size
				float ps = successful_offsprings/(float)(lambda/2);
				float factor = (1.0f/3.0f) * (ps - 0.2f) / (1.0f - 0.2f);
				_step_size = _step_size * exp(factor);

				assert(this->_pop.size() == mu);

				std::sort(_vec_pairs.begin(), _vec_pairs.end(), ea::compare_pair());
							
				// dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
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
          ind1->fit().eval_compet(*ind1, *ind2);
        }
        else
        {
          std::cerr << "Cannot open :" << fname
                    << "(does this file exist ?)" << std::endl;
          exit(1);
        }
      }
            
      const std::vector<ea::pair_t>& vec_pairs() const { return _vec_pairs; }

    protected:
    	float _step_size;
    	std::vector<ea::pair_t> _vec_pairs;
    };
  }
}
#endif
