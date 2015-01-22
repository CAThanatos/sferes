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
			Hunter(float radius, const fastsim::Posture& pos, unsigned int color, nn_t& nn, bool deactivated = false, bool leader = false) : StagHuntRobot(radius, pos, color, color/100), _nn(nn), _food_gathered(0), _nb_hares_hunted(0), _nb_hares_hunted_solo(0), _nb_small_stags_hunted(0), _nb_small_stags_hunted_solo(0), _nb_big_stags_hunted(0), _nb_big_stags_hunted_solo(0), _deactivated(deactivated) 
			{
#ifdef SCREAM
				_scream_heard = false;
				_scream_decay = 0;
#endif
				_distance_hunter = 0.0f;
				_angle_hunter = 0.0f;
				_direction_hunter = 0.0f;

#if defined(COMPAS_PREY)
				_distance_prey = -1.0f;
				_angle_prey = 0.0f;
#elif defined(COMPAS_LANDMARK)
				_distance_landmark = 0.0f;
				_angle_landmark = 0.0f;
#endif
#ifdef COUNT_TIME
				_time_on_hares = 0;
				_time_on_sstags = 0;
				_time_on_bstags = 0;
#endif
#ifdef LEADERSHIP
				_leader = leader;
#endif
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
					
					int current_index = nb_lasers;

#ifndef NO_BUMPERS
					inputs[current_index + 0] = this->get_left_bumper() ? 1 : 0;
					inputs[current_index + 1] = this->get_right_bumper() ? 1 : 0;
#endif
		
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

#ifdef TRIGO
						float angle_color = 0.0f;
						float cosinus = 0.0f;
						float sinus = 0.0f;
						int typePred = 0;
						if(pixel != -1)
						{
							angle_color = (float)fur_color/10.0f;
							cosinus = (cosf(angle_color) + 1.0f)/(2.0f);
							sinus = (sinf(angle_color) + 1.0f)/(2.0f);

							if(HUNTER_COLOR == type)
							{
								typePred = 1;
								cosinus = 0;
								sinus = 0;
							}
						}
#endif

#ifdef TYPEB
						int type3 = 0;
#endif

#ifdef DIR_CLOSE
						float direction = 0.0f;
#endif

						// HUNTER
						if(HUNTER_COLOR == type) 
						{
#ifdef TYPEB
							type1 = 0;
							type2 = 0;
							type3 = 1;
#else
							type1 = 1;
							type2 = 1;
#endif

#ifdef DIR_CLOSE
							direction = (_direction_hunter + M_PI)/(2.0f*M_PI);
#endif
						}
						// HARE
						else if(HARE_COLOR == type)
						{
#ifdef TYPE1
							type1 = 0;
							type2 = 1;
							color = 0.0f;
#elif defined(TYPE2) || defined(TYPE3) || defined(TYPE4)
							type1 = 1;
							type2 = 1;
							color = 0.0f;
#else
							type1 = 0;
							type2 = 1;
#endif
						}
						// STAG
						else if(BIG_STAG_COLOR == type)
						{
#ifdef NEW_TYPES
							if(fur_color > 0)
							{
#ifdef TYPE1
								type1 = 1;
								type2 = 0;
								color = 0;
#elif defined(TYPE2)
								type1 = 1;
								type2 = 0;
								color = 1;
#elif defined(TYPE3)
								type1 = 1;
								type2 = 0;
								color = 0;
#elif defined(TYPE4)
								type1 = 0;
								type2 = 0;
								color = 1;
#else
								type1 = 1;
								type2 = 0;
								color = 0;
#endif
							}
							else
							{
#ifdef TYPE1
								type1 = 0;
								type2 = 0;
								color = 1;
#elif defined(TYPE2) || defined(TYPE4)
								type1 = 0;
								type2 = 1;
								color = 1;
#elif defined(TYPE3)
								type1 = 0;
								type2 = 1;
								color = 0;
#else
								type1 = 0;
								type2 = 0;
								color = 1;
#endif
							}

#else
							type1 = 1;
							type2 = 0;
							color = (float)fur_color;
#endif
						}

						if(pixel != -1)
						{
#ifdef TRIGO
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = cosinus;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = sinus;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = typePred;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (3400.0f - dist)/(3400.0f);
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = pred_on;
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = type1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = type2;

#ifdef NORMALIZE_INPUTS
#ifdef NEW_TYPES
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = color;
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = color/100.0f;
#endif

#ifdef RANGE_COR
#if defined(MAP800)
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (3400.0f - dist)/(3400.0f);
#elif defined(MAP400)
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (2000.0f - dist)/(2000.0f);
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (800.0f - dist)/(800.0f); //TODO 800.0f = beurk
#endif
#else
#ifdef MAP400
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (2000.0f - dist)/(2000.0f);
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = (800.0f - dist)/(800.0f); //TODO 800.0f = beurk
#endif
#endif
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = color;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = dist;
#endif

							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = pred_on;

#ifdef TYPEB
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 5] = type3;
#endif
#ifdef DIR_CLOSE
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 5] = direction;
#endif
#endif
						}
						else
						{
#ifdef ZERO_INPUT
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = 0;
#if defined(DIR_CLOSE) || defined(TYPEB)
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 5] = 0;
#endif
						}
#else
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel)] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 1] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 2] = -1;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 3] = 0;
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 4] = 0;
#if defined(DIR_CLOSE) || defined(TYPEB)
							inputs[nb_lasers + Params::simu::nb_bumpers + (i*Params::nn::nb_info_by_pixel) + 5] = 0;
#endif
						}
#endif

//						std::cout << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel)] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 1] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 2] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 3] << "/" << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 4] << "/";

#if defined(DIR_CLOSE) || defined(TYPEB)
//						std::cout << inputs[nb_lasers + (i*Params::nn::nb_info_by_pixel) + 5] << "/";
#endif
   					}
			
					current_index = current_index + Params::simu::nb_camera_pixels*Params::nn::nb_info_by_pixel;
			
#ifdef LEADERSHIP
					inputs[current_index] = _leader;
					
//					std::cout << inputs[current_index] << "/";

					current_index = current_index + 1;

#ifdef COMPAS_LF
					if(!_leader)
					{
						inputs[current_index] = (_direction_hunter + M_PI)/(2.0f*M_PI);
					}
					else
					{
						inputs[current_index] = 0;
					}

//					std::cout << inputs[current_index] << "/";

					current_index = current_index + 1;
#endif
#endif

#ifdef SCREAM
					if(_scream_heard)
						inputs[current_index] = (float)_scream_decay/(float)Params::simu::scream_decay;
					else
						inputs[current_index] = 0;

//					std::cout << inputs[current_index] << "/";
						
					current_index = current_index + 1;
					
#ifdef COMPAS_SCR
					if(_scream_heard)
					{
						inputs[current_index] = (3400.0f - _distance_hunter)/(3400.0f);
						inputs[current_index + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);
					}
					else
					{
						inputs[current_index] = 0;
						inputs[current_index + 1] = 0;
					}

//					std::cout << inputs[current_index] << "/" << inputs[current_index + 1] << "/";
					
					current_index = current_index + 2;
#endif
#endif

#ifdef COMPAS_PRED
					inputs[current_index] = (3400.0f - _distance_hunter)/(3400.0f);
					inputs[current_index + 1] = (_angle_hunter + M_PI)/(2.0f*M_PI);

//					std::cout << inputs[current_index] << "/" << inputs[current_index + 1] << "/";
					
					current_index = current_index + 2;
#endif

#ifdef COMPAS_DIR
					inputs[current_index] = (_direction_hunter + M_PI)/(2.0f*M_PI);

//					std::cout << inputs[current_index] << "/";
					
					current_index = current_index + 1;
#endif

#ifdef COMPAS_LANDMARK
#ifdef LANDMARK_CENTER
					inputs[current_index] = (3400.0f - _distance_landmark)/(3400.0f);
#else
					inputs[current_index] = (1700.0f - _distance_landmark)/(1700.0f);
#endif
					inputs[current_index + 1] = (_angle_landmark + M_PI)/(2.0*M_PI);

//					std::cout << inputs[current_index] << "/" << inputs[current_index + 1] << "/";
					
					current_index = current_index + 2;
#endif

//					std::cout << std::endl;


/*#ifdef COMPAS_PRED
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
#endif*/


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
					
#ifdef MOVING_PREYS
					outf[0] = -1;
					outf[1] = -1;
#else
					outf[0] = outf2[0];
					outf[1] = outf2[1];
#endif
			
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

			void set_distance_hunter(float distance_hunter) { _distance_hunter = distance_hunter; }
			void set_angle_hunter(float angle_hunter) { _angle_hunter = angle_hunter; }
			void set_direction_hunter(float direction_hunter) { _direction_hunter = direction_hunter; }

#ifdef COMPAS_PREY
			void set_distance_prey(float distance_prey) { _distance_prey = distance_prey; }
			void set_angle_prey(float angle_prey) { _angle_prey = angle_prey; }
#endif

#ifdef COMPAS_LANDMARK
			void set_distance_landmark(float distance_landmark) { _distance_landmark = distance_landmark; }
			void set_angle_landmark(float angle_landmark) { _angle_landmark = angle_landmark; }
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

			float _distance_hunter;
			float _angle_hunter;	
			float _direction_hunter;

#ifdef COMPAS_PREY
			float _distance_prey;
			float _angle_prey;	
#endif

#ifdef COMPAS_LANDMARK
			float _distance_landmark;
			float _angle_landmark;
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

#ifdef LEADERSHIP
			bool _leader;
#endif
	};
}

#endif
