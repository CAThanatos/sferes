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
		
			Stag() : Prey() { _stamina = STAMINA; }
			Stag(float radius, const fastsim::Posture& pos, int color, type_stag type, unsigned int fur_color) : Prey(radius, pos, (fur_color + color), color/100), _type(type), _fur_color(fur_color)
			{
#ifdef CONFUSION
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
					_stamina = STAMINA;
					_type_prey = Prey::BIG_STAG;
				  	_fur_color = fur_color;
					_huntable_alone = true;
					this->set_display_color(BIG_STAG_COLOR/100);
				}
#else
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

#ifdef TRIGO
#ifdef ONEVALUE
						float angle_color = 3.0f*M_PI/4.0f;
#elif defined(QUARTERVALUE)
						float angle_color = misc::rand(2.0f*M_PI/3.0f, 7.0f*M_PI/6.0f);
#else
						float angle_color = misc::rand(2.0f*M_PI/3.0f, 4.0f*M_PI/3.0f);

						while(!(angle_color*10 < ceil(4.0f*M_PI/3.0f)*10))
							angle_color = misc::rand(2.0f*M_PI/3.0f, 4.0f*M_PI/3.0f);
#endif

						this->set_angle_color(angle_color);
						this->set_color(color + angle_color*10);
#endif
					}
					else if(_fur_color >= 50)
					{
						_stamina = STAMINA;
						_type_prey = Prey::BIG_STAG;
				  	_fur_color = fur_color;
						_huntable_alone = true;
						this->set_display_color(BIG_STAG_COLOR/100);

#ifdef TRIGO
#ifdef ONEVALUE
						float angle_color = 7.0f*M_PI/4.0f;
#elif defined(QUARTERVALUE)
						float angle_color = misc::rand(4.0f*M_PI/3.0f, 11.0f*M_PI/6.0f);
#else
						float angle_color = misc::rand(4.0f*M_PI/3.0f, 2.0f*M_PI);

						while(!(angle_color*10 < ceil(2.0f*M_PI)*10))
							angle_color = misc::rand(4.0f*M_PI/3.0f, 2.0f*M_PI);
#endif

						this->set_angle_color(angle_color);
						this->set_color(color + angle_color*10);
#endif
					}

#ifdef CONFUSIONPREY
					float rand_confusion = misc::rand(0.0f, 1.0f);

					// Confusion on the prey : We see the other type
					// of stag
					if((rand_confusion < Params::simu::confusion_prey) && (fur_color >= 50))
					{
						_fur_color = (fur_color + 50)%100;
						this->set_color(color + _fur_color);
					}
#endif
				}
#endif
			}
			
			~Stag()	{}
			
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
					if(_nb_blocked == 1)
						return FOOD_SMALL_STAG_SOLO;
					else if(_nb_blocked > 1)
						return FOOD_SMALL_STAG_COOP;
					else
						return 0;
				}
				else if(_type_prey == Prey::BIG_STAG)
				{
					if(_nb_blocked == 1)
						return FOOD_BIG_STAG_SOLO;
					else if(_nb_blocked > 1)
						return FOOD_BIG_STAG_COOP;
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
