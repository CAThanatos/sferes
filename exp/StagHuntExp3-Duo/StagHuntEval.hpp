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




#ifndef STAG_HUNT_EVAL_HPP_
#define STAG_HUNT_EVAL_HPP_

#include <sferes/stc.hpp>
#include <ctime>

namespace sferes
{
  namespace eval
  {
    SFERES_CLASS(StagHuntEval)
    {
    public:
    	StagHuntEval() : _nb_eval(0) { }
    
			template<typename Phen>
				void eval(std::vector<boost::shared_ptr<Phen> >& pop, size_t begin, size_t end)
      {
				dbg::trace trace("eval", DBG_HERE);
				assert(pop.size());
				assert(begin < pop.size());
				assert(end <= pop.size());
				
				bool first_time = true;

#ifndef NDEBUG
				std::ofstream os("debug.txt", std::ios::out | std::ios::app);
				int duration = time(NULL);
#endif				
				for (size_t i = begin; i < end; ++i)
				{
					if(first_time)
					{
						pop[i]->develop();

						// We need to set all the objective values to 0
						pop[i]->fit().set_value(0);
						
						pop[i]->fit().resize_objs(1);
						for(int k = 0; k < pop[i]->fit().objs().size(); ++k)
							pop[i]->fit().set_obj(k, 0);
					}
						
					for (size_t j = i + 1; j < end; ++j)
					{
						if(first_time)
						{
							pop[j]->develop();

							// We need to set all the objective values to 0
							pop[j]->fit().set_value(0);
						
							pop[j]->fit().resize_objs(1);
							for(int k = 0; k < pop[j]->fit().objs().size(); ++k)
								pop[j]->fit().set_obj(k, 0);
						}
						pop[i]->fit().eval_compet(*pop[i], *pop[j]);
					}
					
					_nb_eval++;
					
					if(first_time)
						first_time = false;
				}
#ifndef NDEBUG
				os << "GEN : " << time(NULL) - duration << std::endl;
				os.close();
#endif
      }

			size_t nb_eval() const { return _nb_eval; }
    protected:
    	size_t _nb_eval;
    };
  }
}

#define SFERES_EVAL SFERES_CLASS

#endif
