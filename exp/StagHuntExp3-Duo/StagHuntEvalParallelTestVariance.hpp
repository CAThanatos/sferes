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




#ifndef STAG_HUNT_EVAL_PARALLEL_TEST_VARIANCE_HPP_
#define STAG_HUNT_EVAL_PARALLEL_TEST_VARIANCE_HPP_

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
    struct _parallel_ev_test
    {
      typedef std::vector<boost::shared_ptr<Phen> > pop_t;
      pop_t _pop;

      ~_parallel_ev_test() { }
      _parallel_ev_test(const pop_t& pop) : _pop(pop) {}
      _parallel_ev_test(const _parallel_ev_test& ev) : _pop(ev._pop) {}
      void operator() (const parallel::range_t& r) const
      {
				for (size_t i = r.begin(); i != r.end(); ++i)
				{
					assert(i < _pop.size());

					_pop[i]->fit().eval_compet(*_pop[i], *_pop[i]);
				}
      }
    };
    
    SFERES_CLASS(StagHuntEvalParallelTestVariance)
    {
    public:
	    enum status_t { free = 0, obstacle = 255 };

    	StagHuntEvalParallelTestVariance() : _nb_eval(0) { }
    
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
				// We create here the positions for all the prey in the arena
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
					pop[i]->fit().set_vec_pos(_vec_pos);
#endif

					pop[i]->fit().set_res_dir(_res_dir);
					pop[i]->fit().set_gen(_gen);
				}

				parallel::init();
				parallel::p_for(parallel::range_t(begin, end), _parallel_ev_test<Phen>(pop));
				_nb_eval += pop.size();

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
				// formatted (as can Gimp spit out). This ignores comments lines (#) and empty
				// lines 
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
					_vec_pos.push_back(Posture(width/2, height - 80, -M_PI/2));
					
					// We need to add the obstacles formed by the robots
					float x = _vec_pos[0].x();
					float y = _vec_pos[0].y();
					float radius = Params::simu::hunter_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);

					x = _vec_pos[1].x();
					y = _vec_pos[1].y();
					_bbx = x - radius - 4;
					_bby = y - radius - 4;
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
				for(int i = 0; i < max_tries && !found; ++i)
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
