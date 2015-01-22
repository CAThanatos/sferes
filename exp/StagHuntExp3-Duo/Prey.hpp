#ifndef PREY_HPP_
#define PREY_HPP_

#include <boost/assign/list_of.hpp>
#include <modules/fastsim_multi/posture.hpp>
#include <modules/fastsim_multi/simu_fastsim_multi.hpp>

#include "defparams.hpp"
#include "StagHuntRobot.hpp"

namespace sferes
{
	class Prey : public StagHuntRobot
	{
		public :
			Prey() : StagHuntRobot(), _blocked(false) {}
			Prey(float radius, const fastsim::Posture& pos, int color, unsigned int color_alt = 0) : StagHuntRobot(radius, pos, color, color_alt), _blocked(false), _nb_blocked(0), _stamina_lost_coop(1), _pred_on_it(false) 
			{ 
#ifdef MOVING_PREYS
				// Front laser
//				SENSORS_INF.push_back(std::make_pair(MAX_SENSOR_INFLUENCE/2.0f, MIN_SENSOR_INFLUENCE));
				SENSORS_INF.push_back(std::make_pair(NEUTRAL_SENSOR_INFLUENCE, NEUTRAL_SENSOR_INFLUENCE));
				
				// Front right laser
				SENSORS_INF.push_back(std::make_pair(MAX_SENSOR_INFLUENCE, MIN_SENSOR_INFLUENCE));
				
				// Front left laser
				SENSORS_INF.push_back(std::make_pair(MIN_SENSOR_INFLUENCE, MAX_SENSOR_INFLUENCE));
				
				// Back right laser
				SENSORS_INF.push_back(std::make_pair(MAX_SENSOR_INFLUENCE, MIN_SENSOR_INFLUENCE));
				
				// Back left laser
				SENSORS_INF.push_back(std::make_pair(MIN_SENSOR_INFLUENCE, MAX_SENSOR_INFLUENCE));
				
				// Back laser
//				SENSORS_INF.push_back(std::make_pair(MAX_SENSOR_INFLUENCE/2.0f, MAX_SENSOR_INFLUENCE/2.0f));
				SENSORS_INF.push_back(std::make_pair(NEUTRAL_SENSOR_INFLUENCE, NEUTRAL_SENSOR_INFLUENCE));
#endif
			}

			virtual ~Prey()	{	}

			std::vector<float> step_action()
			{
				std::vector<float> ret(2);
				ret[0] = -1.0f;
				ret[1] = -1.0f;
				
#ifdef MOVING_PREYS
				ret = _move();
#endif

				if(_blocked)
					lose_stamina();
					
				return ret;
			}
			
			bool is_blocked() { return _blocked; }
			bool is_dead() { return (_stamina <= 0); }
			
			virtual void blocked_by_hunters(int nb_hunters) = 0;
			virtual float feast() = 0;
			virtual void lose_stamina() = 0;
		
      void set_pred_on_it(bool pred_on_it)
      {
#ifndef NO_BOOLEAN
        if(pred_on_it != _pred_on_it)
        {
          _pred_on_it = pred_on_it;

          int color = this->color();
          // This is used as a verification
          if((color < 0 && !pred_on_it) || (color > 0 && pred_on_it))
            this->set_color(-color);
        }
#else
				_pred_on_it = false;
#endif
      }
			bool is_pred_on_it() { return _pred_on_it; }

			enum type_prey
			{
				HARE,
				SMALL_STAG,
				BIG_STAG
			};
			
			type_prey get_type() { return _type_prey; }

			int get_nb_blocked() { return _nb_blocked; }

#ifdef TRIGO
			float get_angle_color() { return _angle_color; }
			void set_angle_color(float angle_color) { _angle_color = angle_color; }
#endif
			
		protected :
			bool _blocked;
			int _nb_blocked;
			float _stamina;
			float _stamina_lost_coop;
			type_prey _type_prey;
			
			bool _pred_on_it;

#ifdef TRIGO
			float _angle_color;
#endif
			
#ifdef MOVING_PREYS
			static const float V_DEFAULT = 1.4f;
			static const float SPEED_RATIO = 1.0f;
			static const float SENSOR_STRENGTH = 64.0f;
			static const float MAX_SENSOR_INFLUENCE = 2.0f;
			static const float NEUTRAL_SENSOR_INFLUENCE = 1.0f;
			static const float MIN_SENSOR_INFLUENCE = 0.0f;
			
			std::vector<std::pair<float, float> > SENSORS_INF;
			
			virtual std::vector<float> _move()
			{
				size_t nb_lasers = this->get_lasers().size();

				std::vector<float> inputs(nb_lasers);
				
				// We get the laser inputs
				for (size_t j = 0; j < nb_lasers; ++j)
				{
					float d = this->get_lasers()[j].get_dist();
					float range = this->get_lasers()[j].get_range();
				
					if(d == -1)
					{
						inputs[j] = 0;
					}
					else
					{
						// Getting the input between 0 and 1
						d = d - _radius;
						float val = 1 - d/(range - _radius);
						inputs[j] = SENSOR_STRENGTH * std::min(1.f, std::max(0.f, val));
						inputs[j] = pow(inputs[j], 1.0f/SENSOR_STRENGTH);
					}
				}
				
				std::vector<float> output(2);
				
				for(size_t i = 0; i < nb_lasers; ++i)
				{
					output[0] += (V_DEFAULT + inputs[i]*(SENSORS_INF[i].first - V_DEFAULT))/MAX_SENSOR_INFLUENCE;
					output[1] += (V_DEFAULT + inputs[i]*(SENSORS_INF[i].second - V_DEFAULT))/MAX_SENSOR_INFLUENCE;
				}
				
				// Between 0 and 1
				output[0] /= (float)nb_lasers;
				output[1] /= (float)nb_lasers;
				
				// Computation of the actual speed of the prey
				// Speed amplitude is set to SPEED_RATIO and kept centered on 0.5
				for(size_t i = 0; i < 2; ++i)
					output[i] = (SPEED_RATIO*(2.0f*output[i] - 1.0f) + 1.0f)/2.0f;
					
				return output;
			}
#endif
	};
}

#endif
