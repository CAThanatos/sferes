#ifndef HARE_HPP_
#define HARE_HPP_

#include <modules/fastsim_multi/posture.hpp>
#include <modules/fastsim_multi/simu_fastsim_multi.hpp>

#include "defparams.hpp"
#include "Prey.hpp"

namespace sferes
{
	class Hare : public Prey
	{
		public :
			Hare() : Prey() { _stamina = STAMINA; }
			Hare(float radius, const fastsim::Posture& pos, int color) : Prey(radius, pos, color, color/100) 
			{ 
				_stamina = STAMINA; 
				_type_prey = Prey::HARE; 

#ifdef TRIGO
#ifdef ONEVALUE
				float angle_color = M_PI/4.0f;
#elif defined(QUARTERVALUE)
				float angle_color = misc::rand(0.0, M_PI/2);
#else
				float angle_color = misc::rand(0.0, 2.0f*M_PI/3.0f);

				while(!(angle_color*10 < ceil(2.0f*M_PI/3.0f)*10))
					angle_color = misc::rand(0.0, 2.0f*M_PI/3.0f);
#endif

				this->set_angle_color(angle_color);
				this->set_color(color + angle_color*10);
#endif
			}
			
			~Hare()	{	}
			
			void blocked_by_hunters(int nb_hunters)
			{
				if(nb_hunters > 0)
				{
					_blocked = true;
					
#if !defined(NO_COOP) && !defined(NO_BOOLEAN)
					set_pred_on_it(true);
#endif
				}
				else
				{
					_blocked = false;
					set_pred_on_it(false);
				}
				
				if(_blocked)
					_nb_blocked = nb_hunters;
				else
					_nb_blocked = 0;
			}
			
			float feast()
			{
				if(1 == _nb_blocked)
					return FOOD_HARE_SOLO;
				else if(_nb_blocked > 1)
					return FOOD_HARE_COOP;
				else
					return 0;
			}
			
			void lose_stamina()
			{
				if(_nb_blocked > 0)
				{
					float stamina_lost = 1;
					_stamina = _stamina - stamina_lost;
				}
			}
	};
}

#endif
