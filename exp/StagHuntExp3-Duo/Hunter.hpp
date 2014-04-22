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
#ifdef MLP
			typedef Mlp< Neuron<PfWSum<>, AfSigmoidNoBias<> >, Connection<> > nn_t;
#else
			typedef	NN<Neuron<PfWSum<>, AfSigmoidNoBias<float> >, Connection<> > nn_t;
#endif
			
//			Hunter() : StagHuntRobot(), _food_gathered(0) {}
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, nn_t& nn, bool deactivated = false) : StagHuntRobot(radius, pos, color, color/100), _nn(nn), _food_gathered(0), _nb_hares_hunted(0), _nb_hares_hunted_solo(0), _nb_small_stags_hunted(0), _nb_small_stags_hunted_solo(0), _nb_big_stags_hunted(0), _nb_big_stags_hunted_solo(0), _deactivated(deactivated) 
			{
#ifdef SCREAM
				_scream_heard = false;
				_scream_decay = 0;
#endif
#ifdef COMPAS_PRED
				_distance_hunter = 0.0f;
				_angle_hunter = 0.0f;
#elif defined(COMPAS_PREY)
				_distance_prey = -1.0f;
				_angle_prey = 0.0f;
#endif
#ifdef COUNT_TIME
				_time_on_hares = 0;
				_time_on_sstags = 0;
				_time_on_bstags = 0;
#endif
			}
	
			~Hunter() {	}
	
			std::vector<float> step_action()
			{
				using namespace fastsim;

				_nn.init();

				std::vector<float> inputs;
				std::vector<float> outf(Params::nn::nb_outputs);
				
//				std::ofstream os("visionDebug.txt", std::ios::out | std::ios::app);
				
				if(!_deactivated)
				{
#ifdef MLP
					inputs.resize(Params::nn::nb_inputs);
#else
					inputs.resize(Params::nn::nb_inputs + 1);
#endif
	
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

#ifndef NO_BUMPERS
					inputs[nb_lasers+0] = this->get_left_bumper() ? 1 : 0;
					inputs[nb_lasers+1] = this->get_right_bumper() ? 1 : 0;
#endif
		
					// Inputs for the camera
					for(int i = 0; i < Params::simu::nb_camera_pixels; ++i)
					{
						assert(nb_lasers + Params::simu::nb_bumpers + i < inputs.size());
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
							type1 = 1;
							type2 = 0;
							color = (float)fur_color;
							
#ifdef COLOR_BOOL
							if(color > 0)
								color = 100;
#endif
						}

						if(pixel != -1)
						{
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5)] = type1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 1] = type2;
#ifdef NORMALIZE_INPUTS
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 2] = color/100.0f;
#ifdef MAP400
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 3] = (2000.0f - dist)/(2000.0f);
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 3] = (800.0f - dist)/(800.0f); //TODO 800.0f = beurk
#endif
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 2] = color;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 3] = dist;
#endif

							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 4] = pred_on;
						}
						else
						{
#ifdef ZERO_INPUT
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5)] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 1] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 2] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 3] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 4] = 0;
						}
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5)] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 1] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 2] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 3] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*5) + 4] = 0;
						}
#endif


//						std::cout << inputs[nb_lasers + (i*5)] << "/" << inputs[nb_lasers + (i*5) + 1] << "/" << inputs[nb_lasers + (i*5) + 2] << "/" << inputs[nb_lasers + (i*5) + 3] << "/" << inputs[nb_lasers + (i*5) + 4] << "/";
   					}
			
//					std::cout << std::endl;


#ifdef COMPAS_PRED
#ifdef MAP400
					inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5] = (2000.0f - _distance_hunter)/(2000.0f);
#else
					inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5] = (800.0f - _distance_hunter)/(800.0f);
#endif
					inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5 + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);
#elif defined(COMPAS_PREY)
					if(_distance_prey >= 0.0f)
#ifdef MAP400
						inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5] = (2000.0f - _distance_prey)/(2000.0f);
#else
						inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5] = (800.0f - _distance_prey)/(800.0f);
#endif
					else
						inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5] = 0.0f;
						
					inputs[nb_lasers + Params::simu::nb_bumpers + Params::simu::nb_camera_pixels*5 + 1] = (_angle_prey + M_PI)/(2.0f*M_PI);
#endif


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
					
/*					for(size_t i = 0; i < inputs.size(); ++i)
					{
						std::cout << inputs[i] << "/";
					}
					std::cout << " => " << outf2[0] << "/" << outf2[1] << std::endl;*/
					
					outf[0] = outf2[0];
					outf[1] = outf2[1];
			
#ifdef SCREAM
					outf[2] = outf2[2];
#endif

					assert(outf.size() == Params::nn::nb_outputs);

					for(size_t j = 0; j < outf.size(); j++)
						if(isnan(outf[j]))
							outf[j] = 0.0;
#endif
				}
				else
				{
					outf[0] = -1.0f;
					outf[1] = -1.0f;
#ifdef SCREAM
					outf[2] = -1.0f;
#endif
				}
				
#ifdef SCREAM
				// The scream fades away as time goes by
				decay_scream();
				
#endif

				return outf;
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
			
#ifdef COUNT_TIME
			void add_time_on_hares(float time_on_hares) { _time_on_hares += time_on_hares; }
			void add_time_on_sstags(float time_on_sstags) { _time_on_sstags += time_on_sstags; }
			void add_time_on_bstags(float time_on_bstags) { _time_on_bstags += time_on_bstags; }
			
			float time_on_hares() const { return _time_on_hares; }
			float time_on_sstags() const { return _time_on_sstags; }
			float time_on_bstags() const { return _time_on_bstags; }
#endif

#ifdef COMPAS_PRED
			void set_distance_hunter(float distance_hunter) { _distance_hunter = distance_hunter; }
			void set_angle_hunter(float angle_hunter) { _angle_hunter = angle_hunter; }
#endif

#ifdef COMPAS_PREY
			void set_distance_prey(float distance_prey) { _distance_prey = distance_prey; }
			void set_angle_prey(float angle_prey) { _angle_prey = angle_prey; }
#endif
			
#ifdef SCREAM
			void set_scream_heard(bool scream_heard) 
			{ 
				_scream_heard = scream_heard; 
				_scream_decay = Params::simu::scream_decay;
			}
			
			void decay_scream() 
			{
				if(_scream_heard)
				{
					_scream_decay--;
					if(_scream_decay <= 0)
						_scream_heard = false;
				}
			}
#endif
			
			nn_t& get_nn() { return _nn; }

			std::vector<std::vector<float> > last_inputs;
			
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
		private :
#ifdef MLP_PERSO
			std::vector<float> _weights;
#endif
		
			nn_t& _nn;
			float _food_gathered;
			int _nb_hares_hunted;
      int _nb_hares_hunted_solo;
			int _nb_small_stags_hunted;
			int _nb_small_stags_hunted_solo;
			int _nb_big_stags_hunted;
			int _nb_big_stags_hunted_solo;
			bool _deactivated;

#ifdef COMPAS_PRED
			float _distance_hunter;
			float _angle_hunter;	
#endif

#ifdef COMPAS_PREY
			float _distance_prey;
			float _angle_prey;	
#endif
			
#ifdef SCREAM
			bool _scream_heard;
			int _scream_decay;
#endif

#ifdef COUNT_TIME
			float _time_on_hares;
			float _time_on_sstags;
			float _time_on_bstags;
#endif
	};
}

#endif
