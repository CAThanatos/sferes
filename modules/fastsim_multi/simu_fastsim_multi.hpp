#ifndef SIMU_FASTSIM_MULTI_HPP_
#define SIMU_FASTSIM_MULTI_HPP_

#include <sferes/simu/simu.hpp>
#include <sferes/misc/rand.hpp>
#include "fastsim_multi.hpp"

namespace sferes
{
  namespace simu
  {
    SFERES_SIMU(FastsimMulti, Simu)
    {
      public:
        FastsimMulti(bool view_activated = false) : _view_activated(view_activated)
        {
          //_map = boost::shared_ptr<fastsim::Map>(new fastsim::Map(Params::simu::map_name(), 600.0f));
          _map = boost::shared_ptr<fastsim::Map>(new fastsim::Map(Params::simu::map_name(), 600.0f));
          _view_initiated = false;
        }
        FastsimMulti(const fastsim::Map & m, bool view_activated = false) : _view_activated(view_activated)
        {
          _map = boost::shared_ptr<fastsim::Map>(new fastsim::Map(m));
          _view_initiated = false;
        }
        ~FastsimMulti()
        {
        	for(int i = 0; i < _robots.size(); ++i)
        	{
        		delete _robots[i];
        	}
        	_robots.clear();
        }
        void init()
        {
	       	for(int i = 0; i < _robots.size(); ++i)
        	{
        		delete _robots[i];
        	}
        	_robots.clear();
          _view_initiated = false;
        }
        void reinit()
        {
        	for(int i = 0; i < _robots.size(); ++i)
        	{
        		delete _robots[i];
        	}
        	_robots.clear();
          _view_initiated = false;
        }
        void reinit_with_map()
        {
        	for(int i = 0; i < _robots.size(); ++i)
        	{
        		delete _robots[i];
        	}
        	_robots.clear();
          _view_initiated = false;

					_map = boost::shared_ptr<fastsim::Map>(new fastsim::Map(Params::simu::map_name(), Params::simu::real_w));
        }
        void reinit_with_map(const fastsim::Map & m)
        {
        	for(int i = 0; i < _robots.size(); ++i)
        	{
        		delete _robots[i];
        	}
        	_robots.clear();
          _view_initiated = false;

					_map = boost::shared_ptr<fastsim::Map>(new fastsim::Map(m));
        }
        void refresh() 
        {
        	// We don't want to always refresh the robots in the same order each time
        	std::vector<size_t> ord_vect;
        	sferes::misc::rand_ind(ord_vect, _robots.size());
        	
        	for(int i = 0; i < ord_vect.size(); ++i)
        	{
        		int num = (int)ord_vect[i];
        		assert(num < _robots.size());
         		_map->update(_robots[num]->get_pos()); 
          }
        }
        void init_view(bool dump = false)
        {
          _display =
            boost::shared_ptr<fastsim::Display>(new fastsim::Display(_map, _robots));
            
          // We only create the robot obstacles now so that they are not displayed
          // (only esthetic)
					for(int i = 0; i < _robots.size(); ++i)
						_robots[i]->add_robot_obstacle(_map);
					  
					_view_initiated = true;
        }
        void set_map(const boost::shared_ptr<fastsim::Map>& map) { _map = map; }
        void refresh_view()
        {
          _display->update();
        }
        void refresh_map_view()
        {
          _display->update_map();
        }
        void dump_display(const char * file)
        {
        	_display->dump_display(file);
        }
        void dump_behaviour_log(const char * file)
        {
        	_display->dump_behaviour_log(file);
        }
        void add_dead_prey(int index, std::string& file, bool alone = true)
        {
        	_display->add_dead_prey(_robots[index]->get_pos().x(), _robots[index]->get_pos().y(), _robots[index]->get_radius(), _robots[index]->display_color(), file, alone);
        }
        void switch_map()
        {
          _map->terrain_switch(Params::simu::alt_map_name());
        }
        void reset_map()
        {
          _map->terrain_switch(Params::simu::map_name());
        }
        void move_robot(float v1, float v2, int index) 
        { 
        	if(index < _robots.size())
	        	_robots[index]->move(v1, v2, _map); 
        }
        void teleport_robot(fastsim::Posture& pos, int index)
        {
        	if(index < _robots.size())
        		_robots[index]->teleport(pos, _map);
        }
        
        // Used to get a random initial position in the map for a robot. Not a very smart function so it's encouraged
        // to use your own list of initial positions in a map with a lot of obstacles and/or robots as is
        // could take a pretty long time for this function to get a valid position
        bool get_random_initial_position(float radius, fastsim::Posture &pos, int max_tries = 1000)
        {
					// We don't want robots to appear outside the map
					float x_min = radius + 1;
					float x_max = _map->get_real_w() - radius - 1;
					float y_min = x_min;
					float y_max = _map->get_real_h() - radius - 1;
			
					bool found = false;
					float rand_x = 0;
					float rand_y = 0;
					for(int k = 0; k < max_tries && !found; ++k)
					{
						rand_x = misc::rand(x_min, x_max);
						rand_y = misc::rand(y_min, y_max);
				
						// We don't want this robot to collide with anything
						// We use the same code as for Robot :: _check_collision
						// pixel wise
						int rp = _map->real_to_pixel(radius);
						int r = rp * rp;
						int x = _map->real_to_pixel(rand_x);
						int y = _map->real_to_pixel(rand_y);
						
						// Bounding Box
						float _bbx = rand_x - radius - 4;
						float _bby = rand_y - radius - 4;
						float _bbw = radius * 2 + 8;
						float _bbh = radius * 2 + 8;
						int bbx = _map->real_to_pixel(_bbx);
						int bby = _map->real_to_pixel(_bby);
						int bbw = _map->real_to_pixel(_bbx + _bbw);
						int bbh = _map->real_to_pixel(_bby + _bbh);
				
						found = true;
						for (int i = bbx; i < bbw; ++i)
						{
							for (int j = bby; j < bbh; ++j)
							{
								if (_map->get_pixel(i, j) == fastsim::Map::obstacle)
								{
									float d1 = (i - x);
									float d2 = (j - y);
									if (d1 * d1 + d2 * d2 <= r)
									{
										found = false;
										break;
									}
								}
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

        				
				void add_robot(fastsim::Robot *robot)
				{
					_robots.push_back(robot);
					
					// We add an Illuminated Switch that is the robot to the map
					assert(_robots.size() > 0);
					fastsim::Map::ill_sw_t ill_sw = _robots[_robots.size() - 1]->get_ill_sw();
				  _map->add_illuminated_switch(ill_sw);
				  
//				  if(_view_initiated)
//					if(!display || _view_initiated)
					if(!_view_activated || _view_initiated)
						robot->add_robot_obstacle(_map);
				}
				
				void remove_robot(int index)
				{
					assert(index < _robots.size());
					_map->remove_illuminated_switch(_robots[index]->get_ill_sw());
					_robots[index]->clean_robot_obstacle(_map);
					
					fastsim::Robot* robot = _robots[index];
					_robots.erase(_robots.begin() + index);
					
					delete robot;
				}
				
				void change_selected_robot(int selected)
				{
					if(selected < _robots.size())
						_display->set_selected(selected);
				}

        boost::shared_ptr<fastsim::Map> map() { return _map; }
        const boost::shared_ptr<fastsim::Map> map() const { return _map; }

        std::vector<fastsim::Robot*>& robots() { return _robots; }
        const std::vector<fastsim::Robot*>& robots() const { return _robots; }

        fastsim::Display& display() {return *_display; }
        
        void set_file_video(std::string file_video)
        {
        	if(_display)
        		_display->set_file_video(file_video);
        }
      protected:
        std::vector<fastsim::Robot*> _robots;
        boost::shared_ptr<fastsim::Map> _map;
        boost::shared_ptr<fastsim::Display> _display;
        bool _view_initiated;
        bool _view_activated;
    };
  }
}

#endif
