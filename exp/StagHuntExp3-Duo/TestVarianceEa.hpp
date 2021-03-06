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




#ifndef TEST_VARIANCE_EA_HPP_
#define TEST_VARIANCE_EA_HPP_

#include <algorithm>
#include <boost/foreach.hpp>
#include <sferes/stc.hpp>
#include <sferes/ea/ea.hpp>
#include <sferes/fit/fitness.hpp>

namespace sferes
{
  namespace ea
  {
    SFERES_EA(TestVarianceEa, Ea)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;

      static const unsigned nb_keep = (unsigned)(Params::pop::keep_rate * Params::pop::size);

      void random_pop()
      {
				this->_pop.resize(Params::pop::size * Params::pop::initial_aleat);
				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();
				}

				this->_eval.set_res_dir(this->_res_dir);
				this->_eval.set_gen(this->_gen);
				this->_eval.eval(this->_pop, 0, this->_pop.size());
				this->apply_modifier();
				std::partial_sort(this->_pop.begin(), this->_pop.begin() + Params::pop::size,
							this->_pop.end(), fit::compare());
				this->_pop.resize(Params::pop::size);
      }
      
      void epoch()
      {
				assert(this->_pop.size());
				this->_eval.set_gen(this->_gen);
				
				this->_pop.clear();
				this->_pop.resize(Params::pop::size);
				BOOST_FOREACH(boost::shared_ptr<Phen>& indiv, this->_pop)
				{
					indiv = boost::shared_ptr<Phen>(new Phen());
					indiv->random();
				}

				this->_eval.eval(this->_pop, 0, Params::pop::size);

				this->apply_modifier();
				std::partial_sort(this->_pop.begin(), this->_pop.begin() + Params::pop::size,
							this->_pop.end(), fit::compare());
				dbg::out(dbg::info, "ea")<<"best fitness: " << this->_pop[0]->fit().value() << std::endl;
      }
      
    protected:
    };
  }
}
#endif
