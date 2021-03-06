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




#ifndef STEADY_STATE_HPP_
#define STEADY_STATE_HPP_

#include <sferes/stc.hpp>
#include <sferes/parallel.hpp>
#include <ctime>

namespace sferes
{
  namespace eval
  {
    template<typename Phen>
    struct _parallel_ev
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;
      size_t _opponent;

      ~_parallel_ev() { }
      _parallel_ev(size_t opponent, const pop_t& pop) : _pop(pop), _opponent(opponent) {}
      _parallel_ev(const _parallel_ev& ev) : _pop(ev._pop), _opponent(ev._opponent) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());
					assert(_opponent < _pop.size());

						//std::cout << i << " : " << _pop[i]->developed_at() << std::endl;
//					std::cout << _opponent << std::endl;
					
//					std::cout << _pop[_opponent]->pop_pos() << " VS " << _pop[i]->pop_pos() << std::endl;									
					_pop[_opponent]->fit().eval_compet(*_pop[_opponent], *_pop[i]);
				}
      }
    };
    
    template<typename Phen>
    struct _parallel_ev_ind
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;
      size_t _end;

      ~_parallel_ev_ind() { }
      _parallel_ev_ind(pop_t& pop, size_t end) : _pop(pop), _end(end) {}
      _parallel_ev_ind(const _parallel_ev_ind& ev) : _pop(ev._pop), _end(ev._end) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());

					if(!_pop[i]->developed())
					{
						_pop[i]->develop();
						_pop[i]->set_pop_pos(i);

						// We need to set all the objective values to 0
						_pop[i]->fit().set_value(0);
						
						_pop[i]->fit().resize_objs(1);
						for(int k = 0; k < _pop[i]->fit().objs().size(); ++k)
							_pop[i]->fit().set_obj(k, 0);
					}


					//parallel::init();
					parallel::p_for(parallel::range_t(i + 1, _end), 
					_parallel_ev<Phen>(i, _pop));
				}
      }
    };

    template<typename Phen>
    struct _parallel_computation
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;

      ~_parallel_computation() { }
      _parallel_computation(pop_t& pop) : _pop(pop) {}
      _parallel_computation(const _parallel_computation& ev) : _pop(ev._pop) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());
					
					float total_fit = 0.f;
					float total_hares = 0.f, total_sstags = 0.f, total_bstags = 0.f;
					float total_sstags_solo = 0.f, total_bstags_solo = 0.f;
					for(size_t j = 0; j < _pop[i]->fit().vec_fitness.size(); ++j)
					{
						total_fit += _pop[i]->fit().vec_fitness[j];
					
						assert(j < _pop[i]->vec_hares().size());
						total_hares += _pop[i]->vec_hares()[j];
						
						assert(j < _pop[i]->vec_sstags().size());
						total_sstags += _pop[i]->vec_sstags()[j];
						
						assert(j < _pop[i]->vec_sstags_solo().size());
						total_sstags_solo += _pop[i]->vec_sstags_solo()[j];

						assert(j < _pop[i]->vec_bstags().size());
						total_bstags += _pop[i]->vec_bstags()[j];

						assert(j < _pop[i]->vec_bstags_solo().size());
						total_bstags_solo += _pop[i]->vec_bstags_solo()[j];
					}
					
					_pop[i]->fit().set_value(total_fit);
					_pop[i]->fit().set_obj(0, total_fit);
					_pop[i]->set_nb_hares(total_hares);
					_pop[i]->set_nb_sstag(total_sstags, total_sstags_solo);
					_pop[i]->set_nb_bstag(total_bstags, total_bstags_solo);
					
					_pop[i]->set_developed(false);
				}
      }
    };
    
    SFERES_CLASS(SteadyState)
    {
    public:
    	SteadyState() : _nb_eval(0) { }
    
			template<typename Phen>
				void eval(std::vector<boost::shared_ptr<Phen> >& pop, size_t begin, size_t end)
      {
				dbg::trace trace("eval", DBG_HERE);
				assert(pop.size());
				assert(begin < pop.size());
				assert(end <= pop.size());
			
#ifndef NDEBUG
				std::ofstream os("debug.txt", std::ios::out | std::ios::app);
				int duration = time(NULL);
#endif				
			
				for(int i = begin; i < end; ++i)
				{
					pop[i]->develop();
					pop[i]->set_pop_pos(i);

					// We need to set all the objective values to 0
					pop[i]->fit().set_value(0);
						
					pop[i]->fit().resize_objs(1);
					for(int k = 0; k < pop[i]->fit().objs().size(); ++k)
						pop[i]->fit().set_obj(k, 0);
				}

				for(int i = begin; i < end; ++i)
				{

						//std::cout << pop[i]->developed_at() << std::endl;
					parallel::init();
					parallel::p_for(parallel::range_t(i + 1, end), 
					_parallel_ev<Phen>(i, pop));
					_nb_eval++;
				}
				//parallel::init();
				//parallel::p_for(parallel::range_t(begin, end), 
				//_parallel_ev_ind<Phen>(pop, end));
				//_nb_eval += pop.size();

				// We need to compute the total fitness 
				// and number of preys for each individual
				for (size_t i = begin; i != end; ++i)
				{
					assert(i < pop.size());
					
					float total_fit = 0.f;
					float total_hares = 0.f, total_sstags = 0.f, total_bstags = 0.f;
					float total_sstags_solo = 0.f, total_bstags_solo = 0.f;
					//for(size_t j = 0; j < pop[i]->fit().vec_fitness.size(); ++j)
					//{
						//total_fit += pop[i]->fit().vec_fitness[j];
						
						//std::ofstream os("verbose.txt", std::ios::out | std::ios::app);
						//os << "------" << std::endl;
						//os << "i : " << i << std::endl;
						//os << "j : " << j << " / " << "size : " << pop[i]->vec_hares().size() << std::endl;
						//os.close();
						//assert(j < pop[i]->vec_hares().size());
						//total_hares += pop[i]->vec_hares()[j];
						
						//assert(j < pop[i]->vec_sstags().size());
						//total_sstags += pop[i]->vec_sstags()[j];
						
						//assert(j < pop[i]->vec_sstags_solo().size());
						//total_sstags_solo += pop[i]->vec_sstags_solo()[j];

						//assert(j < pop[i]->vec_bstags().size());
						//total_bstags += pop[i]->vec_bstags()[j];

						//assert(j < pop[i]->vec_bstags_solo().size());
						//total_bstags_solo += pop[i]->vec_bstags_solo()[j];
					//}
					
					//pop[i]->fit().set_value(total_fit);
					//pop[i]->fit().set_obj(0, total_fit);
					//pop[i]->set_nb_hares(total_hares);
					//pop[i]->set_nb_sstag(total_sstags, total_sstags_solo);
					//pop[i]->set_nb_bstag(total_bstags, total_bstags_solo);
					
					//pop[i]->set_developed(false);
					
					pop[i]->fit().set_value(pop[i]->fit().fitness_at);
					//pop[i]->fit().set_obj(0, pop[i]->fit().fitness_at);
					pop[i]->set_nb_hares(pop[i]->nb_hares_at());
					pop[i]->set_nb_sstag(pop[i]->nb_sstag_at(), pop[i]->nb_sstag_solo_at());
					pop[i]->set_nb_bstag(pop[i]->nb_bstag_at(), pop[i]->nb_bstag_solo_at());

					pop[i]->set_developed_at(false);
				}
				//parallel::init();
				//parallel::p_for(parallel::range_t(begin, end), 
				//_parallel_computation<Phen>(pop));
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
