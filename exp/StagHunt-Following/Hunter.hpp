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
			
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, nn_t& nn, bool deactivated = false, bool leader = false) : StagHuntRobot(radius, pos, color, color/100), _nn(nn), _deactivated(deactivated), _waypoints(Params::simu::nb_waypoints, false)
			{	
				_distance_hunter = 0.0f;
				_angle_hunter = 0.0f;
				_direction_hunter = 0.0f;

				_bool_leader = false;
				_nb_waypoints_done = 0;
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
						// GOAL
						else if(SMALL_STAG_COLOR == type)
						{
							// If the hunter has already crossed this waypoint, it isn't seen
							assert(fur_color < _waypoints.size());
							if((fur_color > -1) && (_waypoints[fur_color]))
								pixel = -1;
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

					// std::cout << std::endl;
	
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

					assert(outf.size() == Params::nn::nb_outputs);

					for(size_t j = 0; j < outf.size(); j++)
						if(isnan(outf[j]))
							outf[j] = 0.0;
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
			
			bool is_deactivated() { return _deactivated; }
			void set_deactivated(bool deactivated) { _deactivated = deactivated; }		

			void set_distance_hunter(float distance_hunter) { _distance_hunter = distance_hunter; }
			void set_angle_hunter(float angle_hunter) { _angle_hunter = angle_hunter; }
			void set_direction_hunter(float direction_hunter) { _direction_hunter = direction_hunter; }
			
			nn_t& get_nn() { return _nn; }

			std::vector<std::vector<float> > last_inputs;

			void set_bool_leader(bool bool_leader) 
			{ 
				_bool_leader = bool_leader;
				this->set_leader_status(bool_leader);
			}
			bool is_leader() { return _bool_leader; }

			void add_waypoint(int id) 
			{ 
				assert(id < _waypoints.size()); 
				assert(!_waypoints[id]);

				_waypoints[id] = true; 
				_nb_waypoints_done++;
				_waypoints_order.push_back(id);
			}
			
			std::vector<bool>& get_waypoints() { return _waypoints; }
			std::vector<int>& get_waypoints_order() { return _waypoints_order; }
			int get_nb_waypoints_done() const { return _nb_waypoints_done; }

			void reset_waypoints()
			{
				_waypoints_order.clear();
			}

		private :
#ifdef MLP_PERSO
			std::vector<float> _weights;
#endif

			nn_t& _nn;
			bool _deactivated;

			float _distance_hunter;
			float _angle_hunter;	
			float _direction_hunter;

			bool _bool_leader;
			std::vector<bool> _waypoints;
			std::vector<int> _waypoints_order;
			int _nb_waypoints_done;
	};
}

#endif
