#ifndef STAG_HPP_
#define STAG_HPP_

#include <modules/fastsim_multi/posture.hpp>
#include <modules/fastsim_multi/simu_fastsim_multi.hpp>
#include <sferes/misc/rand.hpp>
#include <cmath>

#include "defparams.hpp"
#include "Prey.hpp"

namespace sferes
{
	class Stag : public Prey
	{
		public :
			enum type_stag 
			{
				small,
				big
			}; 

			std::map<int, int> map_reward_sstags;
			std::map<int, int> map_reward_bstags;
		
			Stag() : Prey() { _stamina = STAMINA; set_rewards(); }
			Stag(float radius, const fastsim::Posture& pos, int color, type_stag type, unsigned int fur_color) : Prey(radius, pos, (fur_color + color), color/100), _type(type), _fur_color(fur_color)
			{
				if(type == Stag::small)
				{
					_stamina = STAMINA;
 					_type_prey = Prey::SMALL_STAG;
 					_fur_color = fur_color;
 					_huntable_alone = true; 					
					this->set_display_color(SMALL_STAG_COLOR/100);
 				}
				else
				{
					if(_fur_color < 50)
					{
				  	_stamina = STAMINA;
				  	_type_prey = Prey::SMALL_STAG;
				  	_fur_color = fur_color;
				  	_huntable_alone = true;		
						this->set_display_color(SMALL_STAG_COLOR/100);
					}
					else if(_fur_color >= 50)
					{
						_stamina = STAMINA;
						_type_prey = Prey::BIG_STAG;
				  	_fur_color = fur_color;
						_huntable_alone = true;
						this->set_display_color(BIG_STAG_COLOR/100);
					}
				}

				set_rewards();
			}
			
			void set_rewards()
			{
				map_reward_sstags[1] = FOOD_SMALL_STAG_SOLO;

				int level_reward = 0;
				if(Params::simu::nb_hunters_coop_sstags_max > 2)
					level_reward = int((FOOD_SMALL_STAG_COOP_HIGH - FOOD_SMALL_STAG_COOP_LOW)/(Params::simu::nb_hunters_coop_sstags_max - 2));

				for(size_t i = 2; i <= Params::simu::nb_hunters_coop_sstags_max; ++i)
					map_reward_sstags[i] = FOOD_SMALL_STAG_COOP_LOW + (i - 2) * level_reward;

				map_reward_bstags[1] = FOOD_BIG_STAG_SOLO;

				for(size_t i = 2; i < Params::simu::nb_hunters_coop_bstags_max; ++i)
					map_reward_bstags[i] = 0;

				map_reward_bstags[(int)Params::simu::nb_hunters_coop_bstags_max] = FOOD_BIG_STAG_COOP_HIGH;
			}

			~Stag()	{}
			
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
					
#ifdef RECUP_STAMINA
					if(_stamina < STAMINA)
						_stamina = STAMINA;
#endif
				}

				if(_blocked)
					_nb_blocked = nb_hunters;
				else
					_nb_blocked = 0;
			}
			
			float feast()
			{
				if(_type_prey == Prey::SMALL_STAG)
				{
					if(_nb_blocked >= 1)
						return map_reward_sstags[_nb_blocked];
					else
						return 0;
				}
				else if(_type_prey == Prey::BIG_STAG)
				{
					if(_nb_blocked >= 1)
						return map_reward_bstags[_nb_blocked];
					else
						return 0;
				}
				else
				{
					return 0;
				}
			}
			
			void lose_stamina()
			{
				if(_nb_blocked > 0)
				{
					float stamina_lost = 1;
					_stamina = _stamina - stamina_lost;
				}
			}
			
			type_stag get_type() const { return _type; }
			float fur_color() const { return _fur_color; }
			bool huntable_alone() const { return _huntable_alone; }

		private :
			type_stag _type;
			float _fur_color;
			bool _huntable_alone;
	};
}

#endif
