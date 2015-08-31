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
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, int id, bool deactivated = false) : StagHuntRobot(radius, pos, color + id, color/100), _deactivated(deactivated), _food_gathered(0), _id(id)
			{
				_vec_reputation.resize(Params::pop::size);
				for(size_t i = 0; i < _vec_reputation.size(); ++i)
					_vec_reputation[i] = -1.0f;

				_nb_cooperate = 0;
				_nb_defect = 0;
			}
	
			~Hunter() {	}
	
			std::vector<float> step_action()
			{
				using namespace fastsim;

				std::vector<float> inputs;
				std::vector<float> outf;
				
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
						int id = -1;
						if(pixel != -1)
						{
							type = get_color_type(pixel);
							id = get_id(pixel);
						}

						int type1 = 0;
						float reputation = 0;

						// HUNTER
						if(HUNTER_COLOR == type) 
						{
							type1 = 1;

#ifdef NO_REPUTATION
							reputation = 0;
#else
							if(id != -1)
							{
								if(_vec_reputation[id] < 0.0f)
								{
									// The reputation needs to be computed
									std::vector<float> inputs_reputation(Params::nn_reputation::nb_inputs, 0.0f);

									int max_interactions = Params::simu::nb_steps/STAMINA;
									int max_reward = REWARD_COOP*max_interactions;

#ifdef INTERACTION_MEMORY
									std::vector<float> interactions = find_interactions(id, Params::nn_reputation::interactions_memory);

									assert(interactions.size()*2 <= Params::nn_reputation::nb_inputs);
									for(size_t i = 0; i < interactions.size(); ++i)
									{
										inputs_reputation[i] = 1.0f;
										inputs_reputation[i + 1] = interactions[i]/max_reward;
									}
#else
									float mean_reward = 0.0f;
									int nb_interactions = compress_interactions(id, mean_reward);

									inputs_reputation[0] = mean_reward/(float)max_reward;
									inputs_reputation[1] = nb_interactions/(float)max_interactions;
#endif

									std::vector<float> out_rep = compute_nn(inputs_reputation, 1);

									assert(out_rep.size() == 1);
									_vec_reputation[id] = out_rep[0];
								}

								reputation = _vec_reputation[id];
							}
#endif
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
							inputs[current_index + 1] = reputation;
							inputs[current_index + 2] = (max_dist - dist)/max_dist;
						}
						else
						{
							inputs[current_index] = 0;
							inputs[current_index + 1] = 0;
							inputs[current_index + 2] = 0;
						}

						// std::cout << inputs[current_index] << "/" << inputs[current_index+1] << "/" << inputs[current_index+2] << "/";

						current_index += Params::nn_move::nb_info_by_pixel;
 					}

					// std::cout << std::endl;
	
					outf = compute_nn(inputs, 0);

					for(size_t j = 0; j < outf.size(); j++)
						if(isnan(outf[j]))
							outf[j] = 0.0;

					_last_inputs = inputs;
				}
				else
				{
					outf.push_back(-1.0f);
					outf.push_back(-1.0f);
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

			// nn: 0 for nn_move
			//		 1 for nn_reputation
			std::vector<float> compute_nn(const std::vector<float>& inputs, bool nn)
			{
				size_t cpt_weights = 0;
				float lambda = 5.0f;

				int nb_hidden = 0;
				int nb_outputs = 0;
				std::vector<float> weights;

				if(nn == 0)
				{
					nb_hidden = Params::nn_move::nb_hidden;
					nb_outputs = Params::nn_move::nb_outputs;
					weights = _weights_nn_move;
				}
				else
				{
					nb_hidden = Params::nn_reputation::nb_hidden;
					nb_outputs = Params::nn_reputation::nb_outputs;
					weights = _weights_nn_reputation;
				}

				std::vector<float> outputs(nb_outputs);
				std::vector<float> hidden(nb_hidden);

				if(nb_hidden > 0)
				{
					for(size_t i = 0; i < hidden.size(); ++i)
					{
						hidden[i] = 0.0f;
						for(size_t j = 0; j < inputs.size(); ++j)
						{
							hidden[i] += inputs[j]*weights[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						hidden[i] += 1.0f*weights[cpt_weights];
						cpt_weights++;

						hidden[i] = (1.0 / (exp(-hidden[i] * lambda) + 1));
					}
					
					for(size_t i = 0; i < outputs.size(); ++i)
					{
						outputs[i] = 0.0f;
						for(size_t j = 0; j < hidden.size(); ++j)
						{
							outputs[i] += hidden[j]*weights[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						outputs[i] += 1.0f*weights[cpt_weights];
						
						outputs[i] = (1.0 / (exp(-outputs[i] * lambda) + 1));
					}
				}
				else
				{
					for(size_t i = 0; i < outputs.size(); ++i)
					{
						outputs[i] = 0.0f;
						for(size_t j = 0; j < inputs.size(); ++j)
						{
							outputs[i] += inputs[j]*weights[cpt_weights];
							cpt_weights++;
						}

						// Bias neuron
						outputs[i] += 1.0f*weights[cpt_weights];
						
						outputs[i] = (1.0 / (exp(-outputs[i] * lambda) + 1));
					}
				}

				return outputs;		
			}

			int compress_interactions(int id, float& mean_reward)
			{
				mean_reward = 0.0f;
				int nb_interactions = 0;
				for(size_t i = 0; i < _vec_interactions.size(); ++i)
				{
					if(_vec_interactions[i].sharer == id)
					{
						mean_reward += _vec_interactions[i].reward;
						nb_interactions++;
					}
				}

				if(nb_interactions > 0)
					mean_reward /= (float)nb_interactions;

				return nb_interactions;
			}

			std::vector<float> find_interactions(int id, int memory_size)
			{
				std::vector<float> vec_rewards;
				int cpt = 0;
				for(size_t i = _vec_interactions.size() - 1; (i >= 0) && (cpt < memory_size); i--)
				{
					if(_vec_interactions[i].sharer == id)
					{
						vec_rewards.push_back(_vec_interactions[i].reward);
						cpt++;
					}
				}

				return vec_rewards;
			}


			bool decide_sharing()
			{
				float lambda = 5.0f;
				float out = (1.0 / (exp(-_weight_sharing_decision * lambda) + 1));

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

      int get_id(int pixel)
      {
        int color_type = get_color_type(pixel);
        int id = abs(pixel) - color_type;
        return id;
      }
			
      void add_interaction(float food, Hunter* sharer) 
      {
      	interaction_t interaction;
      	interaction.sharer = sharer->get_id();
      	interaction.reward = food;
      	_vec_interactions.push_back(interaction);

      	// The reputation of this sharer needs to be updated
      	_vec_reputation[sharer->get_id()] = -1.0f;

      	add_food(food);
      }

      void add_cooperation()
      {
      	_nb_cooperate++;
      }
      float nb_cooperate() { return _nb_cooperate; }

      void add_defection()
      {
      	_nb_defect++;
      }
      float nb_defect() { return _nb_defect; }

			float get_food_gathered() { return _food_gathered; }
			void add_food(float food) { _food_gathered += food; }

			bool is_deactivated() { return _deactivated; }
			void set_deactivated(bool deactivated) { _deactivated = deactivated; }

			int get_id() { return _id; }

			std::vector<float>& get_last_inputs() { return _last_inputs; }

		private :
			std::vector<float> _weights_nn_move;
			std::vector<float> _weights_nn_reputation;
			float _weight_sharing_decision;

			bool _deactivated;

			float _food_gathered;

			int _id;

			int _nb_cooperate, _nb_defect;

			std::vector<float> _last_inputs;

			struct Interaction
			{
				int sharer;
				int reward;
			};
			typedef struct Interaction interaction_t;
			std::vector<interaction_t> _vec_interactions;

			std::vector<float> _vec_reputation;
	};
}

#endif
