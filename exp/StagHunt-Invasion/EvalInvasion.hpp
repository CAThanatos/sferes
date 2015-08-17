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




#ifndef EVAL_INVASION_HPP
#define EVAL_INVASION_HPP_

#include <sferes/stc.hpp>
#include <sferes/parallel.hpp>
#include <sferes/misc/rand.hpp>
#include <ctime>

#include <modules/fastsim_multi/simu_fastsim_multi.hpp>

namespace sferes
{
  namespace eval
  {
        
    template<typename Phen>
    struct _parallel_ev_select
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;
      size_t _pos_mutant;
      std::vector<int> _select;

      ~_parallel_ev_select() { }
      _parallel_ev_select(const pop_t& pop, size_t pos_mutant, const std::vector<int>& select) : _pop(pop), _pos_mutant(pos_mutant), _select(select)
      {
      }
      _parallel_ev_select(const _parallel_ev_select& ev) : _pop(ev._pop), _pos_mutant(ev._pos_mutant), _select(ev._select)
      {
      }
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());
					assert(_pos_mutant < _pop.size());

					int count = _select[i];
					while(count > 0)
					{
						_pop[i]->fit().eval_compet(*_pop[_pos_mutant], *_pop[i]);
						count--;
					}
				}
      }
    };

    template<typename Phen>
    struct _parallel_ev_mutant
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;
      size_t _pos_mutant;

      ~_parallel_ev_mutant() { }
      _parallel_ev_mutant(const pop_t& pop, size_t pos_mutant) : _pop(pop), _pos_mutant(pos_mutant) {}
      _parallel_ev_mutant(const _parallel_ev_mutant& ev) : _pop(ev._pop), _pos_mutant(ev._pos_mutant) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());
					assert(_pos_mutant < _pop.size());

					_pop[_pos_mutant]->fit().eval_compet(*_pop[_pos_mutant], *_pop[i]);
				}
      }
    };


    SFERES_CLASS(EvalInvasion)
    {
    public:
	    enum status_t { free = 0, obstacle = 255 };

    	EvalInvasion() : _nb_eval(0) { }
    
			template<typename Phen>
				void eval(std::vector<boost::shared_ptr<Phen> >& pop, size_t pos_mutant, size_t begin, size_t end)
      {
				dbg::trace trace("eval", DBG_HERE);
				assert(pop.size());
				assert(pos_mutant < pop.size());
			
#ifndef NDEBUG
				std::ofstream os("debug.txt", std::ios::out | std::ios::app);
				int duration = time(NULL);
#endif
		
				pop[pos_mutant]->develop();
				pop[pos_mutant]->fit().set_value(0);
				pop[pos_mutant]->fit().resize_objs(1);
				for(int k = 0; k < pop[pos_mutant]->fit().objs().size(); ++k)
					pop[pos_mutant]->fit().set_obj(k, 0);

#ifdef NOT_AGAINST_ALL
				std::vector<int> select(end - begin, 0);

				for(size_t k = 0; k < Params::pop::nb_opponents; ++k)
				{
					int opponent = -1;
					do
					{
						opponent = misc::rand(0, (int)(end - begin));
					} while((opponent < 0) || (opponent >= end - begin));
					
					assert(opponent != -1);
					select[opponent]++;
				}
#endif

				parallel::init();
#ifdef NOT_AGAINST_ALL
				parallel::p_for(parallel::range_t(begin, end), _parallel_ev_select<Phen>(pop, pos_mutant, select));
				_nb_eval += 1;
#else
				parallel::p_for(parallel::range_t(begin, end), _parallel_ev_mutant<Phen>(pop, pos_mutant));
				_nb_eval += end - begin;
#endif

				pop[pos_mutant]->set_nb_leader_first(pop[pos_mutant]->nb_leader_first_at());
				pop[pos_mutant]->set_nb_preys_killed_coop(pop[pos_mutant]->nb_preys_killed_coop_at());
				pop[pos_mutant]->set_proportion_leader(pop[pos_mutant]->proportion_leader_at());


#ifndef NDEBUG
				os << "GEN : " << time(NULL) - duration << std::endl;
				os.close();
#endif
      }

	    
			size_t nb_eval() const { return _nb_eval; }
#ifdef ELITIST
			void set_nb_eval(size_t gen) { _nb_eval = (gen * Params::pop::size) + Params::pop::mu; }
#else
			void set_nb_eval(size_t gen) { _nb_eval = ((gen + 1) * Params::pop::size); }
#endif
			
			void set_res_dir(std::string res_dir) { _res_dir = res_dir; }
			void set_gen(int gen) { _gen = gen; }
    protected:
    	size_t _nb_eval;
    	
     	int w, h;
     	float real_w, real_h, fx;
			std::vector<status_t> data;
   	
    	std::vector<fastsim::Posture> _vec_pos;
    	std::string _res_dir;
    	size_t _gen;
		};
  }
}

#define SFERES_EVAL SFERES_CLASS

#endif
