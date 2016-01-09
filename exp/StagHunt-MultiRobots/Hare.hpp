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
			std::map<int, int> map_reward_hares;

			Hare() : Prey() { _stamina = STAMINA; set_rewards(); }
			Hare(float radius, const fastsim::Posture& pos, int color) : Prey(radius, pos, color, color/100) 
			{ 
				_stamina = STAMINA; 
				_type_prey = Prey::HARE; 
				set_rewards();
			}
			
			void set_rewards()
			{
				map_reward_hares[1] = FOOD_HARE_SOLO;

				int level_reward = 0;
				if(Params::simu::nb_hunters_coop_hares_max > 2)
					level_reward = int((FOOD_HARE_COOP_HIGH - FOOD_HARE_COOP_LOW)/(Params::simu::nb_hunters_coop_hares_max - 2));

				for(size_t i = 2; i <= Params::simu::nb_hunters_coop_hares_max; ++i)
					map_reward_hares[i] = FOOD_HARE_COOP_LOW + (i - 2) * level_reward;
			}

			~Hare()	{	}
			
			void blocked_by_hunters(int nb_hunters)
			{
				if(nb_hunters > 0)
				{
					_blocked = true;
					set_pred_on_it(true);
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
				if(_nb_blocked >= 1)
					return map_reward_hares[_nb_blocked];
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
