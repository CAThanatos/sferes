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


    SFERES_CLASS(StagHuntEvalParallel)
    {
    public:
	    enum status_t { free = 0, obstacle = 255 };

    	StagHuntEvalParallel() : _nb_eval(0) { }
    
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

#ifdef DEFINED_POSITIONS
				create_positions();
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

#ifdef DEFINED_POSITIONS
					pop[i]->set_vec_pos(_vec_pos);
#endif

#ifdef TEST_VARIANCE_TRIALS
					pop[i]->fit().set_res_dir(_res_dir);
					pop[i]->fit().set_gen(_gen);
#endif
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
					
					float total_fit = 0.f;
					float total_hares = 0.f, total_sstags = 0.f, total_bstags = 0.f;
					float total_hares_solo = 0.f, total_sstags_solo = 0.f, total_bstags_solo = 0.f;
					
					pop[i]->fit().set_value(pop[i]->fit().fitness_at);

					pop[i]->set_nb_hares(pop[i]->nb_hares_at(), pop[i]->nb_hares_solo_at());
					pop[i]->set_nb_sstag(pop[i]->nb_sstag_at(), pop[i]->nb_sstag_solo_at());
					pop[i]->set_nb_bstag(pop[i]->nb_bstag_at(), pop[i]->nb_bstag_solo_at());
					
#ifdef COUNT_TIME
					pop[i]->set_time_on_hares(pop[i]->time_on_hares_at());
					pop[i]->set_time_on_sstags(pop[i]->time_on_sstags_at());
					pop[i]->set_time_on_bstags(pop[i]->time_on_bstags_at());
#endif

					pop[i]->set_developed_at(false);
				}

#ifndef NDEBUG
				os << "GEN : " << time(NULL) - duration << std::endl;
				os.close();
#endif
      }
      
      void create_positions() 
      {
				_vec_pos.clear();

      	// We first need to read the map
      	std::string fname = Params::simu::map_name();
				std::string str;
				std::ifstream ifs(fname.c_str());
				if (!ifs.good())
					std::cerr << std::string("cannot open map :") + fname << std::endl;
//				  throw Exception(std::string("cannot open map :") + fname);

				ifs >> str;
				if (str != "P4")
					std::cerr << "wrong file type for map" << std::endl;
//				  throw Exception("wrong file type for map");

				// These next few lines are useful when your map file is not correctly
				// formatted (as can Gimp spit out sometimes). This ignores comments lines 
				// (#) and empty lines 
				std::string comments;
				ifs >> comments;
				while(comments=="#"||comments==""||comments==" ")
				{
					std::getline(ifs, comments);
					ifs >> comments;
				}
				
				w = atof(comments.c_str());    
				ifs >> h;

				data.resize(w * h);
				if (w % 8 != 0)
					std::cerr << "wrong map size" << std::endl;
//				  throw Exception("wrong map size");
				int k = w * h / 8;
				char buffer[k];

				ifs.read((char*)buffer, k);

#ifdef TRIAL_POSITIONS
				for(int j = 0; j < Params::simu::nb_trials; ++j)
#endif
				{
					data.clear();
					data.resize(w * h);
					for (int i = 0; i < k - 1; ++i)
						for (int j = 0; j < 8; ++j)
						{
							data[i * 8 + j] = get_bit(buffer[i + 1], j) ? obstacle : free;
						}
							
					real_w = Params::simu::real_w;
					real_h = real_w;

					fx = w / real_w;
					
					// Then we create the positions for all the preys and hunters
					float width = real_w;
					float height = real_h;

					// The two hunters first, there shouldn't be any problem with their position
					using namespace fastsim;

					_vec_pos.push_back(Posture(width/2, 80, M_PI/2));
					
					// We need to add the obstacles formed by the robots
					float x = _vec_pos[0].x();
					float y = _vec_pos[0].y();
					float radius = Params::simu::hunter_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
		
					// Then the hares std::vector<Posture> vec_pos;
					int nb_big_stags = Params::simu::ratio_big_stags*Params::simu::nb_big_stags;
					int nb_small_stags = Params::simu::nb_big_stags - nb_big_stags;

					for(int i = 0; i < Params::simu::nb_hares; ++i)
					{
						Posture pos;

						if(get_random_initial_position(Params::simu::hare_radius, pos))
						{
							_vec_pos.push_back(pos);

							x = pos.x();
							y = pos.y();
							radius = Params::simu::hare_radius;
							_bbx = x - radius - 4;
							_bby = y - radius - 4;
							_bbw = radius * 2 + 8;
							_bbh = radius * 2 + 8;				
							add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
						}
					}
			
					// And finally the big stags
					for(int i = 0; i < Params::simu::nb_big_stags; ++i)
					{
						Posture pos;

						if(get_random_initial_position(Params::simu::big_stag_radius, pos))
						{
							_vec_pos.push_back(pos);

							x = pos.x();
							y = pos.y();
							radius = Params::simu::big_stag_radius;
							_bbx = x - radius - 4;
							_bby = y - radius - 4;
							_bbw = radius * 2 + 8;
							_bbh = radius * 2 + 8;				
							add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
						}
					}
				}
			}
    
		  bool get_bit(char c, int i) const 
		  { 
		  	return (c & (1 << (7 - i))); 
		  }

		  status_t get_pixel(unsigned x, unsigned y) const 
		  {
		    return (y * h + x >= 0 && y * h + x < data.size()) ? 
					data[y * h + x]	: data[data.size()-1]; 
		  }

		  void set_pixel(unsigned x, unsigned y, status_t v) 
		  {
		    if (y * h + x >= 0 && y * h + x < data.size()) 
					data[y * h + x] = v;	
		  }
		  
      bool get_random_initial_position(float radius, fastsim::Posture &pos, int max_tries = 1000)
      {
				// We don't want robots to appear outside of the map
				float x_min = radius + 1;
				float x_max = real_w - radius - 1;
				float y_min = x_min;
				float y_max = real_h - radius - 1;
		
				bool found = false;
				float rand_x = 0;
				float rand_y = 0;
				for(int k = 0; k < max_tries && !found; ++k)
				{
					rand_x = misc::rand(x_min, x_max);
					rand_y = misc::rand(y_min, y_max);
			
					// We don't want this robot to collide with anything
					// pixel wise
					int rp = real_to_pixel(radius);
					int r = rp * rp;
					int x = real_to_pixel(rand_x);
					int y = real_to_pixel(rand_y);
					
					// Bounding Box
					float _bbx = rand_x - radius - 4;
					float _bby = rand_y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;
					int bbx = real_to_pixel(_bbx);
					int bby = real_to_pixel(_bby);
					int bbw = real_to_pixel(_bbx + _bbw);
					int bbh = real_to_pixel(_bby + _bbh);
			
					typedef std::pair<int, int> p_t;
					found = true;

					int compteur = 0;
					for (int i = bbx; i < bbw; ++i)
					{
						for (int j = bby; j < bbh; ++j)
						{
							if (get_pixel(i, j) == obstacle)
							{
								float d1 = (i - x);
								float d2 = (j - y);
								if (d1 * d1 + d2 * d2 <= r)
								{
									found = false;
									break;
								}
							}
							compteur++;
						}
						
						if(!found)
							break;
					}
				}
		
				if(found)
				{
					float rand_theta = misc::rand(-M_PI, M_PI);
			
					pos.set_x(rand_x);
					pos.set_y(rand_y);
					pos.set_theta(rand_theta);
				}
		
				return found;
      }
      
	    int real_to_pixel(float x) const { return (unsigned) roundf(x * fx); }
	    
	    void add_robot_obstacle(float x, float y, float radius, float bbx, float bby, float bbw, float bbh)
	    {
				int _rp = real_to_pixel(radius);
				int _r = _rp * _rp;
				int _x = real_to_pixel(x);
				int _y = real_to_pixel(y);
				int _bbx = real_to_pixel(bbx);
				int _bby = real_to_pixel(bby);
				int _bbw = real_to_pixel(bbx + bbw);
				int _bbh = real_to_pixel(bby + bbh);
				
				for (int i = _bbx; i < _bbw; ++i)
				  for (int j = _bby; j < _bbh; ++j)
						if (get_pixel(i, j) == free)
						{
							float d1 = (i - _x);
							float d2 = (j - _y);
							if (d1 * d1 + d2 * d2 <= _r)
								set_pixel(i, j, obstacle);
						}
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
