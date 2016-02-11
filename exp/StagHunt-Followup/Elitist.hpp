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




#ifndef ELITIST_HPP_
#define ELITIST_HPP_

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
    SFERES_EA(Elitist, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;
      
      static const unsigned mu = Params::pop::mu;
      static const unsigned lambda = Params::pop::lambda;

#ifdef ONE_PLUS_ONE_REPLACEMENT
			Elitist() : _step_size(mu, 1.0f)
#else
			Elitist() : _step_size(1)
#endif
			{ }

      void random_pop()
      {
      	if(Params::pop::pop_init > 0)
      		this->_pop.resize(Params::pop::pop_init);
      	else
      		this->_pop.resize(mu);

				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();
				}

				this->_eval.eval(this->_pop, 0, this->_pop.size());
				this->apply_modifier();
				std::partial_sort(this->_pop.begin(), this->_pop.begin() + mu,
							this->_pop.end(), fit::compare());
				this->_pop.resize(mu);
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// We create the children
				pop_t child_pop;

				std::vector<int> parents_list(lambda);
				int parent_rank = 0;

				// We set the genome_from value as if each of the individuals is going to clone itself 
				// to the next generation
				for(size_t i = 0; i < mu; ++i)
					this->_pop[i]->gen().set_genome_from(i);

#ifdef RESTART
				int nb_min_diversity = 0;
				for(size_t i = 0; i < mu; ++i)
					if(this->_pop[i]->fit().obj(1) < Params::pop::diversity_threshold)
						nb_min_diversity++;

				int total_restarts = Params::pop::prop_restart*nb_min_diversity;
				std::vector<size_t> ord_vect;
				misc::rand_ind(ord_vect, mu);
				int nb_restarts = 0;
				for(size_t i = 0; (i < mu) && (nb_restarts < total_restarts); ++i)
				{
					int index_ind = ord_vect[i];
					if(this->_pop[i]->fit().obj(1) < Params::pop::diversity_threshold)
					{
						this->_pop[i] = boost::shared_ptr<Phen>(new Phen());
						this->_pop[i]->gen().random();
						nb_restarts++;
					}
				}
#endif

#if defined(DOUBLE_NN) && defined(RECOMBINATION)
				assert(lambda%2 == 0);
				for(size_t i = 0; i < lambda - 1; i += 2)
				{
					// Recombination of parents
					indiv_t new_indiv1 = indiv_t(new Phen());
					indiv_t new_indiv2 = indiv_t(new Phen());
					this->_pop[parent_rank%mu]->cross(this->_pop[(parent_rank + 1)%mu], new_indiv1, new_indiv2);

					// Mutation
					new_indiv1->gen().mutate(_step_size);
					new_indiv2->gen().mutate(_step_size);

					child_pop.push_back(new_indiv1);
					child_pop.push_back(new_indiv2);

					int worse_parent = parent_rank + 1;
					if(this->_pop[parent_rank%mu]->fit().value() > this->_pop[(parent_rank + 1)%mu]->fit().value())
						worse_parent = parent_rank;
					
					parents_list[i] = worse_parent%mu;

					parent_rank = parent_rank + 2;
				}
#else
				for(size_t i = 0; i < lambda; ++i)
				{
					// Cloning of a parent
					child_pop.push_back(this->_pop[parent_rank%mu]->clone());

#ifdef RANDOM_MUTANT
					float proba_random_mutant = misc::rand<float>();

					if(proba_random_mutant < Params::evo_float::random_mutant_probability)
					{
						child_pop[i]->gen().set_genome_from(-1);
						child_pop[i]->gen().random();
					}
					else
						child_pop[i]->gen().set_genome_from(parent_rank%mu);
#else
					child_pop[i]->gen().set_genome_from(parent_rank%mu);
#endif

					parents_list[i] = parent_rank%mu;
					parent_rank++;
					
#if defined(DOUBLE_NN) && defined(DUPLICATION)
					// Neural network duplication
					if(misc::rand<float>() < Params::evo_float::duplication_rate)
						child_pop[i]->gen().duplicate_nn();

					// Neural network deletion
					if(misc::rand<float>() < Params::evo_float::deletion_rate)
						child_pop[i]->gen().delete_nn();
#endif

					// Mutation
#ifdef ONE_PLUS_ONE_REPLACEMENT
					child_pop[i]->gen().mutate(_step_size[parents_list[i]]);
#else
					child_pop[i]->gen().mutate(_step_size);
#endif
				}
#endif
				assert(child_pop.size() == lambda);

				pop_t selection_pop;
				for(size_t i = 0; i < mu; ++i)
				{
					selection_pop.push_back(this->_pop[i]);
				}
				for(size_t i = 0; i < lambda; ++i)
				{
					selection_pop.push_back(child_pop[i]);
				}
				assert(selection_pop.size() == (mu + lambda));
				
				// Evaluation of the children and the parents if need be
#ifdef EVAL_PARENTS
#ifdef SEPARATE_PARENTS
				this->_eval.eval(selection_pop, 0, mu);
				this->_eval.eval(selection_pop, mu, selection_pop.size());
#else
				this->_eval.eval(selection_pop, 0, selection_pop.size());
#endif
#else
				this->_eval.eval(selection_pop, mu, selection_pop.size());
#endif
								
				int successful_offsprings = 0;

#ifdef ONE_PLUS_ONE_REPLACEMENT
				// We count the number of offsprings who are better than their parents
				// and replace the parent population if need be
				std::vector<bool> replaced(mu, false);
				for(size_t i = 0; i < lambda; ++i)
				{
					successful_offsprings = 0;

					if(child_pop[i]->fit().value() > this->_pop[parents_list[i]]->fit().value())
					{
						successful_offsprings++;
						
						if(!replaced[parents_list[i]])
						{
							this->_pop[parents_list[i]] = child_pop[i];
							replaced[parents_list[i]] = true;
						}
							
						// We modify the step_size
#ifndef NO_STEP_SIZE
						float ps = successful_offsprings/(float)lambda;
						float factor = (1.0f/3.0f) * (ps - 0.2f) / (1.0f - 0.2f);
						_step_size[parents_list[i]] = _step_size[parents_list[i]] * exp(factor);
#endif
					}
				}
#elif defined(N_PLUS_N_REPLACEMENT)
				std::partial_sort(this->_pop.begin(), this->_pop.begin() + mu,
							this->_pop.end(), fit::compare());

				// We count the number of offsprings better than the worst parent
				for(size_t i = 0; i < lambda; ++i)
				{
					if(child_pop[i]->fit().value() > this->_pop[this->_pop.size() - 1]->fit().value())
					{
						successful_offsprings++;
					}
				}

				std::partial_sort(selection_pop.begin(), selection_pop.begin() + mu + lambda,
							selection_pop.end(), fit::compare());
							
				// We select the mu best individuals
				for(size_t i = 0; i < mu; ++i)
				{
					this->_pop[i] = selection_pop[i];
				}
							
				// We modify the step_size
#ifndef NO_STEP_SIZE
				int duration = time(NULL);
				float ps = successful_offsprings/(float)lambda;
				float factor = (1.0f/3.0f) * (ps - 0.2f) / (1.0f - 0.2f);
				_step_size = _step_size * exp(factor);
#endif
#endif

				assert(this->_pop.size() == mu);

				std::partial_sort(this->_pop.begin(), this->_pop.begin() + mu,
							this->_pop.end(), fit::compare());
							
				dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
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
            
    protected:
#ifdef ONE_PLUS_ONE_REPLACEMENT
    	std::vector<float> _step_size;
#else
    	float _step_size;
#endif
    };
  }
}
#endif
