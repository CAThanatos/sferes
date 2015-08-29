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
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, int id, bool deactivated = false) : StagHuntRobot(radius, pos, color, color/100), _deactivated(deactivated), _food_gathered(0), _id(id)
			{	
			}
	
			~Hunter() {	}
	
			std::vector<float> step_action()
			{
				using namespace fastsim;

				std::vector<float> inputs;
				std::vector<float> outf(Params::nn_move::nb_outputs);
				
				// std::cout << " --- " << _bool_leader << " --- " << std::endl;

				if(!_deactivated)
				{
					inputs.resize(Params::nn_move::nb_inputs);
	
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
						assert((current_index + Params::nn_move::nb_info_by_pixel) <= inputs.size());
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
						}
						// HARE
						else if(FOOD_COLOR == type)
						{
							type1 = 0;
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

						current_index += Params::nn_move::nb_info_by_pixel;
 					}

					// std::cout << std::endl;
	
					std::vector<float> hidden(Params::nn_move::nb_hidden);
					
					size_t cpt_weights = 0;
					float lambda = 5.0f;
					for(size_t i = 0; i < hidden.size(); ++i)
					{
						hidden[i] = 0.0f;
						for(size_t j = 0; j < inputs.size(); ++j)
						{
							hidden[i] += inputs[j]*_weights_nn_move[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						hidden[i] += 1.0f*_weights_nn_move[cpt_weights];
						cpt_weights++;

						hidden[i] = (1.0 / (exp(-hidden[i] * lambda) + 1));
					}
					
					for(size_t i = 0; i < outf.size(); ++i)
					{
						outf[i] = 0.0f;
						for(size_t j = 0; j < hidden.size(); ++j)
						{
							outf[i] += hidden[j]*_weights_nn_move[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						outf[i] += 1.0f*_weights_nn_move[cpt_weights];
						
						outf[i] = (1.0 / (exp(-outf[i] * lambda) + 1));
					}
					
					assert(outf.size() == Params::nn_move::nb_outputs);

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
			
			void set_weights(const std::vector<float>& weights)
			{
				_weights_nn_move.clear();
				_weights_nn_move.resize(Params::nn_move::nn_size);
				assert(weights.size() > _weights_nn_move.size());
				
				for(size_t i = 0; i < Params::nn_move::nn_size; ++i)
					_weights_nn_move[i] = weights[i];

				_weights_nn_reputation.clear();
				_weights_nn_reputation.resize(Params::nn_reputation::nn_size);
				assert(weights.size() > _weights_nn_reputation.size());
				
				for(size_t i = 0; i < Params::nn_reputation::nn_size; ++i)
					_weights_nn_reputation[i] = weights[i + Params::nn_move::nn_size];

				_weight_sharing_decision = weights[Params::nn_move::nn_size + Params::nn_reputation::nn_size];
			}

			bool decide_sharing()
			{
				float lambda = 5.0f;
				out = (1.0 / (exp(-_weight_sharing_decision * lambda) + 1));

				if(out < 0.5f)
					// No sharing
					return false;
				else
					// Sharing
					return true;
			}
  	
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
			
      void add_interaction(float food, Hunter* sharer) 
      {
      	interaction_t interaction;
      	interaction.sharer = sharer->get_id();
      	interaction.reward = food;
      	_vec_interactions.push_back(interaction);

      	add_food(food);
      }

			float get_food_gathered() { return _food_gathered; }
			void add_food(float food) { _food_gathered += food; }

			bool is_deactivated() { return _deactivated; }
			void set_deactivated(bool deactivated) { _deactivated = deactivated; }

			int get_id() { return _id; }

			std::vector<float>& get_last_inputs() { return _last_inputs; }

		private :
			std::vector<float> _weights_nn_move;
			std::vector<flat> _weights_nn_reputation;
			float _weight_sharing_decision;

			float _food_gathered;

			bool _deactivated;

			int _id;

			std::vector<float> _last_inputs;

			struct Interaction
			{
				int sharer;
				int reward;
			};
			typedef struct Interaction interaction_t;
			std::vector<interaction_t> _vec_interactions;
	};
}

#endif
