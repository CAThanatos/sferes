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

			Elitist() : _step_size(1)
			{ }

      void random_pop()
      {
#ifdef POP_INIT100
				this->_pop.resize(100);
#elif defined(POP_INIT50)
				this->_pop.resize(50);
#elif defined(POP_INIT20)
				this->_pop.resize(20);
#else
				this->_pop.resize(mu);
#endif
				int nb_indiv = 0;
				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();
					indiv->set_pop_pos(nb_indiv);

					this->_eval.eval(this->_pop, nb_indiv, 0, nb_indiv + 1);
					nb_indiv++;
				}

				for(size_t i = 0; i < this->_pop.size(); ++i)
				{
					float fitness = 0.0f;
					float nb_hares = 0, nb_hares_solo = 0;
					float nb_sstags = 0, nb_sstags_solo = 0;
					float nb_bstags = 0, nb_bstags_solo = 0;

					for(size_t j = 0; j < this->_pop.size(); ++j)
					{
						fitness += this->_pop[i]->get_payoff(j);

						nb_hares += this->_pop[i]->get_nb_hares(j);
						nb_hares_solo += this->_pop[i]->get_nb_hares_solo(j);

						nb_sstags += this->_pop[i]->get_nb_sstags(j);
						nb_sstags_solo += this->_pop[i]->get_nb_sstags_solo(j);

						nb_bstags += this->_pop[i]->get_nb_bstags(j);
						nb_bstags_solo += this->_pop[i]->get_nb_bstags_solo(j);
					}

					this->_pop[i]->fit().set_value(fitness/(float)this->_pop.size());
					this->_pop[i]->set_nb_hares(nb_hares/(float)this->_pop.size(), nb_hares_solo/(float)this->_pop.size());
					this->_pop[i]->set_nb_sstags(nb_sstags/(float)this->_pop.size(), nb_sstags_solo/(float)this->_pop.size());
					this->_pop[i]->set_nb_bstags(nb_bstags/(float)this->_pop.size(), nb_bstags_solo/(float)this->_pop.size());
				}

				this->apply_modifier();
				std::partial_sort(this->_pop.begin(), this->_pop.begin() + mu,
							this->_pop.end(), fit::compare());

#if defined(POP_INIT100) || defined(POP_INIT20) || defined(POP_INIT50)
				this->_pop.resize(mu);
#endif
      }
      
      void epoch()
      {
				assert(this->_pop.size()); 

				// We create the children
				pop_t child_pop;
				std::vector<int> parents_list(lambda);
				int parent_rank = 0;
				for(size_t i = 0; i < lambda; ++i)
				{
					// Cloning of a parent
					child_pop.push_back(this->_pop[parent_rank%mu]->clone());
					parents_list[i] = parent_rank%mu;
					parent_rank++;
					
					// Mutation
					child_pop[i]->gen().mutate(_step_size);
				}
				assert(child_pop.size() == lambda);

				pop_t selection_pop;
				for(size_t i = 0; i < mu; ++i)
				{
					selection_pop.push_back(this->_pop[i]);
				}
				for(size_t i = 0; i < lambda; ++i)
				{
					child_pop[i]->set_pop_pos(mu + i);
					selection_pop.push_back(child_pop[i]);
				}
				assert(selection_pop.size() == (mu + lambda));

				// Evaluation of the children and the parents if need be
#ifdef EVAL_PARENTS
				for(size_t i = 0; i < selection_pop.size(); ++i)
					this->_eval.eval(selection_pop, i, 0, selection_pop.size());
#else
				for(size_t i = mu; i < selection_pop.size(); ++i)
					this->_eval.eval(selection_pop, i, 0, selection_pop.size());
#endif

				for(size_t i = 0; i < selection_pop.size(); ++i)
				{
					float fitness = 0.0f;
					float nb_hares = 0, nb_hares_solo = 0;
					float nb_sstags = 0, nb_sstags_solo = 0;
					float nb_bstags = 0, nb_bstags_solo = 0;

					for(size_t j = 0; j < selection_pop.size(); ++j)
					{
						fitness += selection_pop[i]->get_payoff(j);

						nb_hares += selection_pop[i]->get_nb_hares(j);
						nb_hares_solo += selection_pop[i]->get_nb_hares_solo(j);

						nb_sstags += selection_pop[i]->get_nb_sstags(j);
						nb_sstags_solo += selection_pop[i]->get_nb_sstags_solo(j);

						nb_bstags += selection_pop[i]->get_nb_bstags(j);
						nb_bstags_solo += selection_pop[i]->get_nb_bstags_solo(j);
					}

					selection_pop[i]->fit().set_value(fitness/(float)selection_pop.size());
					selection_pop[i]->set_nb_hares(nb_hares/(float)selection_pop.size(), nb_hares_solo/(float)selection_pop.size());
					selection_pop[i]->set_nb_sstags(nb_sstags/(float)selection_pop.size(), nb_sstags_solo/(float)selection_pop.size());
					selection_pop[i]->set_nb_bstags(nb_bstags/(float)selection_pop.size(), nb_bstags_solo/(float)selection_pop.size());
				}
								
				int successful_offsprings = 0;

#ifdef ONE_PLUS_ONE_REPLACEMENT
				// We count the number of offsprings who are better than their parents
				// and replace the parent population if need be
				std::vector<bool> replaced(mu, false);
				for(size_t i = 0; i < lambda; ++i)
				{
					if(child_pop[i]->fit().value() > this->_pop[parents_list[i]]->fit().value())
					{
						successful_offsprings++;
						
						if(!replaced[parents_list[i]])
						{
							this->_pop[parents_list[i]] = child_pop[i];
							replaced[parents_list[i]] = true;
						}
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
#endif
							
				// We modify the step_size
				float ps = successful_offsprings/(float)lambda;
				float factor = (1.0f/3.0f) * (ps - 0.2f) / (1.0f - 0.2f);
				_step_size = _step_size * exp(factor);

				assert(this->_pop.size() == mu);

				std::partial_sort(this->_pop.begin(), this->_pop.begin() + mu,
							this->_pop.end(), fit::compare());
							
				dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }
      
    protected:
    	float _step_size;
    };
  }
}
#endif
