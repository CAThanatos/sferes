#ifndef HUNTER_HPP_
#define HUNTER_HPP_

#include <modules/fastsim_multi/posture.hpp>
#include <modules/fastsim_multi/simu_fastsim_multi.hpp>
#include <modules/nn2/nn.hpp>

#include "defparams.hpp"
#include "StagHuntRobot.hpp"

using namespace nn;

namespace sferes
{
	class Hunter : public StagHuntRobot
	{
		public :
			typedef Mlp< Neuron<PfWSum<>, AfSigmoidNoBias<> >, Connection<> > nn_t;
			
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, nn_t& nn, bool deactivated = false, bool leader = false) : StagHuntRobot(radius, pos, color, color/100), _nn(nn), _food_gathered(0), _nb_hares_hunted(0), _nb_hares_hunted_solo(0), _nb_small_stags_hunted(0), _nb_small_stags_hunted_solo(0), _nb_big_stags_hunted(0), _nb_big_stags_hunted_solo(0), _deactivated(deactivated) 
			{	
				_distance_hunter = 0.0f;
				_angle_hunter = 0.0f;
				_direction_hunter = 0.0f;

				_distance_nearest_prey = 3400.0f;
			}
	
			~Hunter() {	}
	
			std::vector<float> step_action()
			{
				using namespace fastsim;

#ifndef MLP_PERSO
				_nn.init();
#endif

				std::vector<float> inputs;
				std::vector<float> outf(Params::nn::nb_outputs);
				
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
							inputs[j] = 0;
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
						assert(current_index + i < inputs.size());
						assert(i < this->get_camera().pixels().size());
				

						// We gather the color type, the fur color and the pred_on boolean
						int pixel = this->get_camera().pixels()[i];
						float dist = this->get_camera().dist()[i];

						int type = -1;
						int fur_color = -1;
						int pred_on = -1;
						if(pixel != -1)
						{
							type = get_color_type(pixel);
							fur_color = get_fur_color(pixel);
							pred_on = (get_pred_on(pixel))?1:0;
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

						if(pixel != -1)
						{
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = type1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = type2;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = color;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (3400.0f - dist)/(3400.0f);
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = pred_on;
						}
						else
						{
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = 0;
						}

//						std::cout << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel)] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 1] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 2] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 3] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 4] << "/";
 					}
			
					current_index = current_index + Params::simu::nb_camera_pixels*Params::nn::nb_info_by_pixel;

//					std::cout << std::endl;
					
#ifdef MLP_PERSO
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
						
						outf[i] = (1.0 / (exp(-outf[i] * lambda) + 1));
					}
					
					assert(outf.size() == Params::nn::nb_outputs);
#else	
					// Step check of the inputs
					for(size_t i = 0; i < 3; ++i)
					{
						_nn.step(inputs);
					}
				
					const std::vector<float>& outf2 = _nn.get_outf();

					outf[0] = outf2[0];
					outf[1] = outf2[1];

					assert(outf.size() == Params::nn::nb_outputs);
#endif

					for(size_t j = 0; j < outf.size(); j++)
						if(isnan(outf[j]))
							outf[j] = 0.0;

					_last_inputs = inputs;
				}
				else
				{
					outf[0] = -1.0f;
					outf[1] = -1.0f;
				}


				return outf;
  		}
			
#ifdef MLP_PERSO
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
#endif

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

			float get_distance_nearest_prey() { return _distance_nearest_prey; }
			void set_distance_nearest_prey(float distance_nearest_prey) { _distance_nearest_prey = distance_nearest_prey; }
			
			nn_t& get_nn() { return _nn; }

			std::vector<float>& get_last_inputs() { return _last_inputs; }

		private :
#ifdef MLP_PERSO
			std::vector<float> _weights;
#endif

			std::vector<float> _last_inputs;

			nn_t& _nn;
			float _food_gathered;
			int _nb_hares_hunted;
      int _nb_hares_hunted_solo;
			int _nb_small_stags_hunted;
			int _nb_small_stags_hunted_solo;
			int _nb_big_stags_hunted;
			int _nb_big_stags_hunted_solo;
			bool _deactivated;

			float _distance_hunter;
			float _angle_hunter;	
			float _direction_hunter;

			float _distance_nearest_prey;
	};
}

#endif
