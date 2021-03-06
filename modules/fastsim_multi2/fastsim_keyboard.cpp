#include <boost/foreach.hpp>
#include "simu_fastsim_multi.hpp"

using namespace sferes;
struct Params
{
  struct simu
  {
    // SFERES_STRING(map_name, "modules/fastsim_multi2/map800x800.pbm");
    SFERES_STRING(map_name, "modules/fastsim_multi2/map400x400.pbm");
  };
};



int main(int argc, char *argv[])
{
  using namespace fastsim;
  typedef simu::FastsimMulti<Params> simu_t;
  simu_t s(true);

	Robot* r1 = new Robot(20.0f, Posture(250, 250, -M_PI/2), 2);  
  r1->use_camera();
  r1->add_laser(Laser(0, 50));
  r1->add_laser(Laser(M_PI / 6, 50));
  r1->add_laser(Laser(M_PI / 3, 50));
  r1->add_laser(Laser(M_PI, 50));
  r1->add_laser(Laser(-M_PI / 3, 50));
  r1->add_laser(Laser(-M_PI / 6, 50));
	s.add_robot(r1);

/*	Robot* r2 = new Robot(20.0f, Posture(100, 100, -M_PI/2), 4, 2);  
  r2->use_camera();
  r2->add_laser(Laser(M_PI / 3, 50));
	r2->add_laser(Laser(0, 50));
	r2->add_laser(Laser(-M_PI / 3, 50));
	s.add_robot(r2);*/

  Map::ill_sw_t s1 = Map::ill_sw_t(new IlluminatedSwitch(200, 10, 300, 251, true));
/*  Map::ill_sw_t s2 = Map::ill_sw_t(new IlluminatedSwitch(2, 10, 530, 150, true));
  Map::ill_sw_t s3 = Map::ill_sw_t(new IlluminatedSwitch(3, 10, 200, 150, true));
  Map::ill_sw_t s4 = Map::ill_sw_t(new IlluminatedSwitch(4, 10, 400, 350, true));*/

  s.map()->add_illuminated_switch(s1);
/*  s.map()->add_illuminated_switch(s2);
  s.map()->add_illuminated_switch(s3);
  s.map()->add_illuminated_switch(s4);*/

  s.init_view();

  int numkey;
  int num_robot = 0;

  while(true)
  {
    SDL_PumpEvents();
    Uint8* keys = SDL_GetKeyState(&numkey);
    if (keys[SDLK_TAB]) 
    {
    	num_robot = (num_robot+1)%(s.robots().size());
    	s.change_selected_robot(num_robot);
    }
    if (keys[SDLK_UP])
			s.move_robot(1.0, 1.0, num_robot);
    if (keys[SDLK_DOWN])
			s.move_robot(-1.0, -1.0, num_robot);
    if (keys[SDLK_LEFT])
     	s.move_robot(1.0, -1.0, num_robot);
    if (keys[SDLK_RIGHT])
     	s.move_robot(-1.0, 1.0, num_robot);
    s.refresh();
    s.refresh_view();

    // float distance = r1->get_pos().dist_to(s1->get_x(), s1->get_y());
    // distance = distance - r1->get_radius() - s1->get_radius();
    // float angle12 = normalize_angle(atan2(s1->get_y() - r1->get_pos().y(), s1->get_x() - r1->get_pos().x()));
    // angle12 = normalize_angle(angle12 - r1->get_pos().theta());

    // std::cout << distance << "/" << angle12 << std::endl;
    
		for (size_t j = 0; j < 6; ++j)
		{
			float d = r1->get_lasers()[j].get_dist();
			float range = r1->get_lasers()[j].get_range();
		
			// Getting the input between 0 and 1
			d = d - 20.0f;
			float val = 1 - d/(range - 20.0f);
			std::cout << std::min(1.f, std::max(0.f, val)) << "/";
		}
		std::cout << std::endl;
  }

  return 0;
}
