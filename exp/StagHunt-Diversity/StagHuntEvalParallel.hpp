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




#ifndef STAG_HUNT_EVAL_PARALLEL_HPP_
#define STAG_HUNT_EVAL_PARALLEL_HPP_

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

					_pop[_opponent]->fit().eval_compet(*_pop[_opponent], *_pop[i]);
				}
      }
    };

    template<typename Phen>
    struct _parallel_ev_altruism
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;

      ~_parallel_ev_altruism() { }
      _parallel_ev_altruism(const pop_t& pop) : _pop(pop) {}
      _parallel_ev_altruism(const _parallel_ev_altruism& ev) : _pop(ev._pop) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());

					_pop[i]->fit().eval_compet(*_pop[i], *_pop[i]);
				}
      }
    };
    
    template<typename Phen>
    struct _parallel_ev_opponent
    {
    	typedef std::vector<boost::shared_ptr<Phen> > pop_t;
    	pop_t _pop;
    	std::vector<size_t> _opponents;
    	size_t _ind_ev; 	

      ~_parallel_ev_opponent() { }
      _parallel_ev_opponent(const pop_t& pop, const std::vector<size_t>& opponents, size_t ind_ev) : _pop(pop), _opponents(opponents), _ind_ev(ind_ev) {}
      _parallel_ev_opponent(const _parallel_ev_opponent& ev) : _pop(ev._pop), _opponents(ev._opponents), _ind_ev(ev._ind_ev) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _opponents.size());
					
					size_t opponent = _opponents[i];
					
					assert(opponent < _pop.size());
					assert(_ind_ev < _pop.size());

					_pop[_ind_ev]->fit().eval_compet(*_pop[_ind_ev], *_pop[opponent]);
				}
      }
    };
        
    template<typename Phen>
    struct _parallel_ev_select
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;
      int nb_opponents;
      int nb_eval;
      int _size;

      ~_parallel_ev_select() { }
      _parallel_ev_select(const pop_t& pop, int size) : _pop(pop), _size(size)
      {
		    nb_opponents = Params::pop::nb_opponents;
		    nb_eval = Params::pop::nb_eval;
      }
      _parallel_ev_select(const _parallel_ev_select& ev) : _pop(ev._pop), _size(ev._size)
      {
		    nb_opponents = Params::pop::nb_opponents;
		    nb_eval = Params::pop::nb_eval;
      }
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());
					
					for(size_t j = 0; j < nb_eval; ++j)
					{
#ifdef NESTED
						std::vector<size_t> opponents;

						for(size_t k = 0; k < nb_opponents; ++k)
						{
							int opponent = -1;
							do
							{
								opponent = misc::rand(0, _size);
							} while((opponent == i) || (opponent < 0) || (opponent >= _size));
							
							assert(opponent != -1);
							opponents.push_back(opponent);
						}
						assert(opponents.size() == nb_opponents);

						parallel::p_for(parallel::range_t(0, nb_opponents), _parallel_ev_opponent<Phen>(_pop, opponents, i));
#else
						for(size_t k = 0; k < nb_opponents; ++k)
						{
							int opponent = -1;
							do
							{
								opponent = misc::rand(0, _size);
							} while((opponent == i) || (opponent < 0) || (opponent >= _size));
							
							assert(opponent != -1);
							
							_pop[i]->fit().eval_compet(*_pop[i], *_pop[opponent]);
						}
#endif
					}
				}
      }
    };

		float dist(std::vector<float> v1, std::vector<float> v2)
		{
			assert(v1.size() == v2.size());

			float dist = 0.0f;
			for(size_t i = 0; i < v1.size(); ++i)
			{
				assert(v1[i] >= 0.0f);
				assert(v2[i] >= 0.0f);
				assert(v1[i] <= 1.0f);
				assert(v2[i] <= 1.0f);

				float x = v1[i] - v2[i];
				dist += x * x;
			}

			return sqrtf(dist)/sqrt(v1.size());
		}


    SFERES_CLASS(StagHuntEvalParallel)
    {
    public:
	    enum status_t { free = 0, obstacle = 255 };

    	StagHuntEvalParallel() : _nb_eval(0) 
    	{
#ifdef NOVELTY
    		_nov_min = Params::novelty::nov_min;
    		_k = Params::novelty::k;
#endif 
    	}
    
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
					
#if defined(MONO_OBJ) || defined(MONO_DIV)
					pop[i]->fit().resize_objs(1);
#else
#if defined(DIVERSITY) && defined(MULTI_ACTIVITY)
					pop[i]->fit().resize_objs(3);
#else
					pop[i]->fit().resize_objs(2);
#endif
#endif
					for(int k = 0; k < pop[i]->fit().objs().size(); ++k)
						pop[i]->fit().set_obj(k, 0);
				}

#ifdef ALTRUISM
				parallel::init();
				parallel::p_for(parallel::range_t(begin, end), _parallel_ev_altruism<Phen>(pop));
				_nb_eval += (end - begin);
#elif defined(NOT_AGAINST_ALL)
				parallel::init();
				parallel::p_for(parallel::range_t(begin, end), _parallel_ev_select<Phen>(pop, (end - begin)));
				_nb_eval += (end - begin);
#else
				for(size_t i = begin; i != end; ++i)
				{
					parallel::init();
					parallel::p_for(parallel::range_t(i + 1, end), 
					_parallel_ev<Phen>(i, pop));
					_nb_eval++;
				}
#endif

				// We need to compute the total fitness 
				// and number of preys for each individual
				for (size_t i = begin; i != end; ++i)
				{
					assert(i < pop.size());
					
					pop[i]->fit().set_obj(0, pop[i]->fit().fitness_at);

					pop[i]->set_nb_hares(pop[i]->nb_hares_at(), pop[i]->nb_hares_solo_at());
					pop[i]->set_nb_sstag(pop[i]->nb_sstag_at(), pop[i]->nb_sstag_solo_at());
					pop[i]->set_nb_bstag(pop[i]->nb_bstag_at(), pop[i]->nb_bstag_solo_at());

#ifdef SIMILARITY
					pop[i]->set_similarity();
#endif

#ifdef FITSIM
					float fitness = 1.0f - pop[i]->similarity_value();
					pop[i]->fit().set_obj(0, fitness);
#endif

#ifdef DIVSM
					pop[i]->set_vec_sm();
#endif

#ifdef PROXIMITY
					pop[i]->set_proximity(pop[i]->proximity_at());
#endif

					pop[i]->create_vector_diversity();
				}

#ifdef NOVELTY
				_compute_novelty(pop, begin, end);
#endif

				// And we now compute the diversity
#ifdef NEW_DISTANCE
				std::vector<float> vec_mean(pop[0]->vector_diversity().size(), 0.0f);
				std::vector<float> vec_var(pop[0]->vector_diversity().size(), 0.0f);

				for(size_t i = 0; i != vec_mean.size(); ++i)
				{
					for(size_t j = begin; j != end; ++j)
						vec_mean[i] += pop[j]->vector_diversity()[i];
					vec_mean[i] /= end - begin;

					for(size_t j = begin; j != end; ++j)
						vec_var[i] += (pop[j]->vector_diversity()[i] - vec_mean[i]) * (pop[j]->vector_diversity()[i] - vec_mean[i]);
					vec_var[i] /= begin - end;

					for(size_t j = begin; j != end; ++j)
					{
						float deviation = (pop[j]->vector_diversity()[i] - vec_mean[i]) * (pop[j]->vector_diversity()[i] - vec_mean[i]);
						if(deviation < vec_var[i])
							pop[j]->set_vector_diversity(i, 0.0f);
#ifdef MAXVARIANCE
						else
							pop[j]->set_vector_diversity(i, 1.0f);
#endif
					}
				}
#endif

				for (size_t i = begin; i != end; ++i)
				{
#if !defined(NOVELTY) && !defined(MONO_OBJ)
					float diversity = 0.0f;
					for (size_t j = begin; j != end; ++j)
					{
						if(i != j)
#ifdef DIST_HAMMING
							diversity += pop[i]->dist_hamming_diversity(*pop[j]);
#else
							diversity += pop[i]->dist_diversity(*pop[j]);
#endif
					}
					diversity /= end - begin - 1;
#ifdef MONO_DIV
					pop[i]->fit().set_obj(0, diversity);
#else
#ifdef MULTI_COOP
					float max_hunts = Params::simu::nb_steps/STAMINA;
					float fitness = pop[i]->nb_bstag() - pop[i]->nb_bstag_solo();
		     	fitness = std::min(fitness, max_hunts)/max_hunts;

					pop[i]->fit().set_obj(1, fitness);
#elif defined(MULTI_SIM)
					float fitness = 1.0f - pop[i]->similarity_value();
#ifdef DIVERSITY
					pop[i]->fit().set_obj(1, diversity);
					pop[i]->fit().set_obj(2, fitness);
#else
					pop[i]->fit().set_obj(1, fitness);
#endif
#elif defined(MULTI_ACTIVITY)
					float fitness = 1.0f - pop[i]->similarity_value();
#ifdef DIVERSITY
					pop[i]->fit().set_obj(1, diversity);
					pop[i]->fit().set_obj(2, fitness);
#else
					pop[i]->fit().set_obj(1, fitness);
#endif
#else
					pop[i]->fit().set_obj(1, diversity);
#endif
#endif
#endif

					pop[i]->set_developed_at(false);
				}

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

#ifdef NOVELTY
    	std::vector<std::vector<float> > _archive_novelty;
    	int _nb_eval_last_add;
    	float _nov_min;
    	int _k;

			struct compare_dist_f
			{
			  compare_dist_f(const std::vector<float>& v) : _v(v) {}
			  const std::vector<float> _v;

			  bool operator()(const std::vector<float>& v1, const std::vector<float>& v2) const
			  {
			    assert(v1.size() == _v.size());
			    assert(v2.size() == _v.size());

			    return dist(v1, _v) < dist(v2, _v);
			  }
			};

				template<typename Phen>
    	void _compute_novelty(std::vector<boost::shared_ptr<Phen> >& pop, size_t begin, size_t end)
    	{
		    float max_n = 0;
		    int added = 0;

		    std::vector<std::vector<float> > archive = _archive_novelty;

#ifndef NOVELTY_NO_DIV 
		    for (size_t i = 0; i < pop.size(); ++i)
		      archive.push_back(pop[i]->vector_diversity());
#endif

		    for (size_t i = 0; i < pop.size(); ++i)
		    {
					const std::vector<float>& behavior = pop[i]->vector_diversity();
					assert(behavior.size() == 2);

					tbb::parallel_sort(archive.begin(), archive.end(),
							   compare_dist_f(behavior));

					float n = 0;
					if (archive.size() > _k)
					  for (size_t j = 1; j <= _k; ++j)
					    n += dist(archive[j], behavior);
					else
					  n += 1;

					n /= _k;
					max_n = std::max(n, max_n);

#ifdef MONO_DIV
					pop[i]->fit().set_obj(0, n);
#else
					pop[i]->fit().set_obj(1, n);
#endif

					if (_archive_novelty.size() < _k || n > _nov_min || misc::rand<float>() < 0.01 / 100.0f)
				  {
				    assert(behavior.size() == 2);

				    _archive_novelty.push_back(behavior);
				    _nb_eval_last_add = 0;

				    ++added;
				  }
					else
					  ++_nb_eval_last_add;
				}

		    if (_nb_eval_last_add > 2500)
		      _nov_min *= 0.95;

		    if (_archive_novelty.size() > _k  && added > 4)
		      _nov_min *= 1.05f;
    	}
#endif
		};
  }
}

#define SFERES_EVAL SFERES_CLASS

#endif
