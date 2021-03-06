#ifndef HUNTER_HPP_
#define HUNTER_HPP_

#include <modules/fastsim_multi/posture.hpp>
#include <modules/fastsim_multi/simu_fastsim_multi.hpp>
#include <modules/nn2/nn.hpp>
#include <modules/nn2/elman.hpp>

#include "defparams.hpp"
#include "StagHuntRobot.hpp"

using namespace nn;

namespace sferes
{
	class Hunter : public StagHuntRobot
	{
		public :
#ifdef ELMAN
			typedef Elman< Neuron<PfWSum<>, AfSigmoidNoBias<> >, Connection<> > nn_t;
#else
			typedef Mlp< Neuron<PfWSum<>, AfSigmoidNoBias<> >, Connection<> > nn_t;
#endif
			
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, bool deactivated = false, bool leader = false) : StagHuntRobot(radius, pos, color, color/100), _food_gathered(0), _nb_hares_hunted(0), _nb_hares_hunted_solo(0), _nb_small_stags_hunted(0), _nb_small_stags_hunted_solo(0), _nb_big_stags_hunted(0), _nb_big_stags_hunted_solo(0), _deactivated(deactivated) 
			{	
				_distance_hunter = 0.0f;
				_angle_hunter = 0.0f;
				_direction_hunter = 0.0f;

				_bool_leader = false;
				_bool_nn1 = false;

#if LEADERSHIP_INFO
				_nb_get_first = 0;
#endif

#ifdef SCREAM
				_scream_value = 0.0f;
#endif

#ifdef OBSTACLE_AVOIDANCE
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
	
			~Hunter() {	}
	
			std::vector<float> step_action()
			{
				using namespace fastsim;

				std::vector<float> inputs;
				std::vector<float> outf(Params::nn::nb_outputs);
				
				// std::cout << " --- " << _bool_leader << " --- " << std::endl;

				if(!_deactivated)
				{
					inputs.resize(Params::nn::nb_inputs);
	
					// We compute the inputs of the nn  
					// Update of the sensors
					size_t nb_lasers = this->get_lasers().size();

					// *** set inputs ***
					_sens_max = 0;
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
							inputs[j] = std::min(1.f, std::max(0.f, val));
						
							if(inputs[j] > _sens_max)
								_sens_max = inputs[j];
						}
					}
					
					int current_index = nb_lasers;
		
					current_index = current_index + Params::simu::nb_bumpers;
		
					// Inputs for the camera
					for(int i = 0; i < Params::simu::nb_camera_pixels; ++i)
					{
						assert(current_index < inputs.size());
						assert((current_index + Params::nn::nb_info_by_pixel) <= inputs.size());
						assert(i < this->get_camera().pixels().size());
				

						// We gather the color type, the fur color and the pred_on boolean
						int pixel = this->get_camera().pixels()[i];
						float dist = this->get_camera().dist()[i];

						int type = -1;
						int fur_color = -1;
						if(pixel != -1)
						{
							type = get_color_type(pixel);
							fur_color = get_fur_color(pixel);
						}

						int type1 = 0;
						int type2 = 0;
						float color = 0.0f;

						// HUNTER
						if(HUNTER_COLOR == type) 
						{
							type1 = 1;
							type2 = 1;
						}
						// HARE
						else if(HARE_COLOR == type)
						{
							type1 = 0;
							type2 = 1;
						}
						// STAG
						else if(BIG_STAG_COLOR == type)
						{
							if(fur_color > 0)
							{
								type1 = 1;
								type2 = 0;
								color = 0;
							}
							else
							{
								type1 = 0;
								type2 = 0;
								color = 1;
							}
						}

						float max_dist = sqrtf(2.0f*pow(Params::simu::real_w, 2));

						if(pixel != -1)
						{
							inputs[current_index] = type1;
							inputs[current_index + 1] = type2;
							inputs[current_index + 2] = color;
							inputs[current_index + 3] = (max_dist - dist)/max_dist;
						}
						else
						{
							inputs[current_index] = 0;
							inputs[current_index + 1] = 0;
							inputs[current_index + 2] = 0;
							inputs[current_index + 3] = 0;
						}

						// std::cout << inputs[current_index] << "/" << inputs[current_index+1] << "/" << inputs[current_index+2] << "/" << inputs[current_index+3] << "/";

						current_index += Params::nn::nb_info_by_pixel;
 					}

#if defined(SCREAM)
#ifndef COM_COMPAS
 					inputs[current_index] = _scream_value;

 					// std::cout << inputs[current_index] << "/";

 					current_index++;
#endif

 					decay_scream();
#endif

#ifdef ID_LEADER
 					inputs[current_index] = (_bool_leader)?1:0;

 					// std::cout << inputs[current_index] << "/";

 					current_index++;
#endif

#ifdef COM_COMPAS
#ifdef COM_NN
 					if(!_bool_nn1)
 					{
	 					inputs[current_index] = (3400.0f - _distance_hunter)/3400.0f;
	 					inputs[current_index + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);
 					}
 					else
 					{
	 					inputs[current_index]  = 0.0f;
	 					inputs[current_index + 1]  = 0.0f;
 					}
#else
 					if(_scream_value > 0.0f)
 					{
	 					inputs[current_index] = (3400.0f - _distance_hunter)/3400.0f;
	 					inputs[current_index + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);
 					}
 					else
 					{
	 					inputs[current_index]  = 0.0f;
	 					inputs[current_index + 1]  = 0.0f;
 					}
#endif

 					// std::cout << inputs[current_index] << "/" << inputs[current_index + 1] << "/";

 					current_index += 2;
#endif

#ifdef COMPAS_FOLLOWER
 					if(_bool_leader)
 					{
	 					inputs[current_index] = 0.0f;
	 					inputs[current_index + 1] = 0.0f;
 					}
 					else
 					{
	 					inputs[current_index] = (3400.0f - _distance_hunter)/3400.0f;
	 					inputs[current_index + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);
 					}

 					current_index += 2;
#endif

					// std::cout << std::endl;
	
					std::vector<float> hidden(Params::nn::nb_hidden);
					
					size_t cpt_weights = 0;
					float lambda = 5.0f;
					for(size_t i = 0; i < hidden.size(); ++i)
					{
						hidden[i] = 0.0f;
						for(size_t j = 0; j < inputs.size(); ++j)
						{
							hidden[i] += inputs[j]*_weights[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						hidden[i] += 1.0f*_weights[cpt_weights];
						cpt_weights++;

						hidden[i] = (1.0 / (exp(-hidden[i] * lambda) + 1));
					}
					
					for(size_t i = 0; i < outf.size(); ++i)
					{
						outf[i] = 0.0f;
						for(size_t j = 0; j < hidden.size(); ++j)
						{
							outf[i] += hidden[j]*_weights[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						outf[i] += 1.0f*_weights[cpt_weights];
						cpt_weights++;
						
						outf[i] = (1.0 / (exp(-outf[i] * lambda) + 1));
					}

					assert(outf.size() == Params::nn::nb_outputs);

					for(size_t j = 0; j < outf.size(); j++)
						if(isnan(outf[j]))
							outf[j] = 0.0;

					_last_inputs = inputs;
				}
				else
				{
#ifdef OBSTACLE_AVOIDANCE
					outf = _move();
#else
					outf[0] = -1.0f;
					outf[1] = -1.0f;
#endif

#if defined(SCREAM) && !defined(SCREAM_PREY)
					outf[2] = -1.0f;
#endif

#ifdef STAG_STUN
					decay_stun();
#endif
				}

				return outf;
  		}
			
			void set_weights(const std::vector<float>& weights)
			{
				_weights.clear();
				_weights.resize((Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_hidden * Params::nn::nb_outputs + Params::nn::nb_outputs);
				assert(weights.size() == _weights.size());
				
				for(size_t i = 0; i < weights.size(); ++i)
				{
					_weights[i] = weights[i];
				}
			}
			
			void set_weights(const std::vector<float>& weights, int beg, int end)
			{
				_weights.clear();
				_weights.resize((Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_hidden * Params::nn::nb_outputs + Params::nn::nb_outputs);
				assert((end - beg) == _weights.size());
				assert(beg >= 0);
				assert(end <= weights.size());
				
				for(size_t i = beg; i < end; ++i)
				{
					_weights[i - beg] = weights[i];
				}
			}

			void choose_nn(int nn_chosen, const std::vector<float>& data)
			{
				int nb_weights = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;

				_weights.clear();
				_weights.resize(nb_weights);

				int first_weight = 0;
				if(nn_chosen >= 1)
					first_weight = nb_weights;

				if(first_weight == 0)
					_bool_nn1 = true;

				for(size_t i = first_weight; i < first_weight + nb_weights; ++i)
					_weights[i - first_weight] = data[i];

				_data = data;
			}

			bool nn1_chosen() { return _bool_nn1; }
  	
      int get_color_type(int pixel)
      {
        int color_type = floor(pixel/100) * 100;
        return abs(color_type);
      }

      bool get_pred_on(int pixel)
      {
        if(pixel > 0)
          return false;
        else
        {
          return true;
        }
      }

      int get_fur_color(int pixel)
      {
        int color_type = get_color_type(pixel);
        int fur_color = abs(pixel) - color_type;
        return fur_color;
      }
			
			float get_food_gathered() { return _food_gathered; }
			void add_food(float food) { _food_gathered += food; }
			
			void eat_hare(bool solo) { _nb_hares_hunted++; if(solo) _nb_hares_hunted_solo++; }
			void eat_small_stag(bool solo) { _nb_small_stags_hunted++; if(solo) _nb_small_stags_hunted_solo++; }
			void eat_big_stag(bool solo) 
			{ 
				_nb_big_stags_hunted++; 
				if(solo) 
					_nb_big_stags_hunted_solo++; 
			}

#ifdef LEADERSHIP_INFO
			void add_get_first() { _nb_get_first++; }
			int nb_get_first() { return _nb_get_first; }
#endif

			int nb_hares_hunted() { return _nb_hares_hunted; }
	    int nb_hares_hunted_solo() { return _nb_hares_hunted_solo; }
			int nb_small_stags_hunted() { return _nb_small_stags_hunted; }
			int nb_small_stags_hunted_solo() { return _nb_small_stags_hunted_solo; }
			int nb_big_stags_hunted() { return _nb_big_stags_hunted; }
			int nb_big_stags_hunted_solo() { return _nb_big_stags_hunted_solo; }
			bool is_deactivated() { return _deactivated; }
			void set_deactivated(bool deactivated) { _deactivated = deactivated; }		

			void set_distance_hunter(float distance_hunter) { _distance_hunter = distance_hunter; }
			void set_angle_hunter(float angle_hunter) { _angle_hunter = angle_hunter; }
			void set_direction_hunter(float direction_hunter) { _direction_hunter = direction_hunter; }

			std::vector<float>& get_last_inputs() { return _last_inputs; }

			void set_bool_leader(bool bool_leader) 
			{ 
				_bool_leader = bool_leader;
				this->set_leader_status(bool_leader);
			}
			bool is_leader() { return _bool_leader; }

#ifdef SCREAM
			void hear_scream() { _scream_value = SCREAM_MAX; }
			void decay_scream() { if(_scream_value > 0) _scream_value = std::max(0.0f, _scream_value - SCREAM_DECAY); }
			void set_scream(float value) { _scream_value = value; }
#endif

#ifdef STAG_STUN
			void stun_hunter() { _stun_time = STUN_TIME; _deactivated = true; }
			void decay_stun() { _stun_time--; if(_stun_time <= 0) _deactivated = false; }
#endif

#ifdef STAG_KILL
			void kill_hunter() { _deactivated = true; }
#endif

		private :
			std::vector<float> _weights;

			float _food_gathered;
			int _nb_hares_hunted;
      int _nb_hares_hunted_solo;
			int _nb_small_stags_hunted;
			int _nb_small_stags_hunted_solo;
			int _nb_big_stags_hunted;
			int _nb_big_stags_hunted_solo;
			bool _deactivated;

#ifdef LEADERSHIP_INFO
			int _nb_get_first;
#endif

			float _distance_hunter;
			float _angle_hunter;	
			float _direction_hunter;

			bool _bool_leader;

			bool _bool_nn1;

			std::vector<float> _data;

			std::vector<float> _last_inputs;

#ifdef SCREAM
			float _scream_value;
#endif

#ifdef OBSTACLE_AVOIDANCE
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
