#include "includes.hpp"
#include "defparams.hpp"

namespace sferes
{
  using namespace nn;
  
  // ********** Main Class ***********
  SFERES_FITNESS(FitStagHunt, sferes::fit::Fitness)
  {
  public:
		typedef Neuron<PfWSum<>, AfSigmoidNoBias<> > neuron_t;
		typedef Connection<float> connection_t;
		typedef Mlp< neuron_t, connection_t > nn_t;

    template<typename Indiv>
      void eval(Indiv& ind) 
		{
			std::cout << "Nop !" << std::endl;
		}

    template<typename Indiv>
      void eval_compet(Indiv& ind1, Indiv& ind2) 
    {
      nn_t nn1(Params::nn::nb_inputs, Params::nn::nb_hidden, Params::nn::nb_outputs);
      nn_t nn2(Params::nn::nb_inputs, Params::nn::nb_hidden, Params::nn::nb_outputs);

      nn1.set_all_weights(ind1.data());
      nn2.set_all_weights(ind2.data());

      typedef simu::FastsimMulti<Params> simu_t;
      typedef fastsim::Map map_t;

      using namespace fastsim;	
      
      //this->set_mode(fit::mode::eval);

      // *** Main Loop *** 
      float moy_hares1 = 0, moy_sstags1 = 0, moy_bstags1 = 0;
      float moy_hares1_solo = 0, moy_sstags1_solo = 0, moy_bstags1_solo = 0;
     	int food1 = 0;

      float moy_hares2 = 0, moy_sstags2 = 0, moy_bstags2 = 0;
      float moy_hares2_solo = 0, moy_sstags2_solo = 0, moy_bstags2_solo = 0;
     	int food2 = 0;

#ifdef SIMILARITY
     	std::vector<float> similarity(Params::simu::size_sim_vector, 0.0f);
#endif

#ifdef DIVSM
     	std::vector<float> vec_sm(Params::nn::nb_inputs + Params::nn::nb_outputs, 0.0f);
#endif

#ifdef PROXIMITY
     	float proximity = 0.0f;
#endif

      for (size_t j = 0; j < Params::simu::nb_trials; ++j)
      {
      	// init
				map_t map(Params::simu::map_name(), Params::simu::real_w);
				simu_t simu(map, (this->mode() == fit::mode::view));
				init_simu(simu, nn1, nn2);

#ifdef BEHAVIOUR_LOG
				_file_behaviour = "behaviourTrace";
				cpt_files = 0;
#endif
	
#ifdef MLP_PERSO
				StagHuntRobot* robotTmp = (StagHuntRobot*)(simu.robots()[0]);
				Hunter* hunterTmp = (Hunter*)robotTmp;
				hunterTmp->set_weights(ind1.data());
				robotTmp = (StagHuntRobot*)(simu.robots()[1]);
				hunterTmp = (Hunter*)robotTmp;
				hunterTmp->set_weights(ind2.data());
#endif

				float food_trial = 0;

#ifdef SIMILARITY
				std::vector<float> similarity_trials(Params::simu::size_sim_vector, 0.0f);
#endif

#ifdef DIVSM
				std::vector<float> vec_sm_trials(Params::nn::nb_inputs + Params::nn::nb_outputs, 0.0f);
#endif

#ifdef PROXIMITY
				float proximity_trials = 0.0f;
#endif

#ifdef SIMILARITY_ACTIVITY
				std::vector<Posture> vec_prev_pos(2);
				std::vector<float> vec_activity(2);

				for(size_t l = 0; l < 2; ++l)
				{
					StagHuntRobot* rob = (StagHuntRobot*)(simu.robots()[l]);
					vec_prev_pos[l].set_x(rob->get_pos().x());
					vec_prev_pos[l].set_y(rob->get_pos().y());
				}

				vec_activity.push_back(0.0f);
				vec_activity.push_back(0.0f);
				int nb_steps_activity = Params::simu::nb_steps * (float)Params::simu::ratio_steps_activity;

#ifdef ACT_DER
				std::vector<float> vec_prev_dist(2);
				vec_prev_dist.push_back(0.0f);
				vec_prev_dist.push_back(0.0f);
#endif
#endif

#ifdef SIM_WINDOW
#ifdef SLIDING_WINDOW
				std::vector<std::queue<float> > vec_sm_rob1(Params::simu::size_sim_vector);
				std::vector<std::queue<float> > vec_sm_rob2(Params::simu::size_sim_vector);

				for(size_t l = 0; l < Params::simu::size_sim_vector; ++l)
				{
					vec_sm_rob1.push_back(std::queue<float>());
					vec_sm_rob2.push_back(std::queue<float>());
				}

				std::vector<float> vec_sm_total_rob1(Params::simu::size_sim_vector, 0.0f);
				std::vector<float> vec_sm_total_rob2(Params::simu::size_sim_vector, 0.0f);
#else
				std::vector<float> vec_sm_rob1(Params::simu::size_sim_vector, 0.0f);
				std::vector<float> vec_sm_rob2(Params::simu::size_sim_vector, 0.0f);
#endif

				int nb_steps_similarity = Params::simu::nb_steps * (float)Params::simu::ratio_steps_similarity;
				bool first_step = true;
#endif


#ifdef LIMITED_SENSORS
				std::vector<bool> vec_sensors(Params::nn::nb_inputs, false);
				int nb_sensors = 0;

				for (size_t i = 0; i < vec_sensors.size(); ++i)
				{
					if(i < Params::simu::nb_lasers)
					{
						vec_sensors[i] = true;
						nb_sensors++;
					}
					else 
					{
						int rank = (i - Params::simu::nb_lasers)%Params::nn::nb_info_by_pixel;

						if(rank == 0 || rank == 1 || rank == 2)
						{
							vec_sensors[i] = true;
							nb_sensors++;
						}
					}
				}
#endif

     		for (size_t i = 0; i < Params::simu::nb_steps && !stop_eval; ++i)
				{
					// Number of steps the robots are evaluated
					_nb_eval = i + 1;

					// We compute the robots' actions in an ever-changing order
					std::vector<size_t> ord_vect;
					misc::rand_ind(ord_vect, simu.robots().size());

#ifdef SIM_MEAN
					float mean_rob1 = 0.0f;
					float mean_rob2 = 0.0f;
#endif

#ifdef SIMILARITY_ACTIVITY
					if((i >= nb_steps_activity) && ((i % nb_steps_activity) == 0))
					{
						vec_activity[0] /= (float)nb_steps_activity;
						vec_activity[1] /= (float)nb_steps_activity;

						float distance_activity = sqrtf((vec_activity[0] - vec_activity[1]) * (vec_activity[0] - vec_activity[1]));
						similarity_trials[0] += distance_activity;

						vec_activity[0] = 0.0f;
						vec_activity[1] = 0.0f;
					}
#endif

#ifdef SIM_WINDOW
					if((i >= nb_steps_similarity) && ((i % nb_steps_similarity) == 0))
					{
#ifdef SLIDING_WINDOW
						int size_window_cur = vec_sm_rob1[0].size();
#endif

						for(size_t l = 0; l < Params::simu::size_sim_vector; ++l)
						{
#ifdef SLIDING_WINDOW
							assert(size_window_cur == vec_sm_rob1[l].size());
							assert(size_window_cur == vec_sm_rob2[l].size());
							assert(size_window_cur <= Params::simu::sim_window_size);

							float value_rob1 = vec_sm_total_rob1[l] / (float)size_window_cur;
							float value_rob2 = vec_sm_total_rob2[l] / (float)size_window_cur;

							float distance_similarity = sqrtf((value_rob1 - value_rob2) * (value_rob1 - value_rob2));
							similarity_trials[l] += distance_similarity;
#else		
							vec_sm_rob1[l] /= nb_steps_similarity;
							vec_sm_rob2[l] /= nb_steps_similarity;

							float distance_similarity = sqrtf((vec_sm_rob1[l] - vec_sm_rob2[l]) * (vec_sm_rob1[l] - vec_sm_rob2[l]));
							similarity_trials[l] += distance_similarity;

							vec_sm_rob1[l] = 0.0f;
							vec_sm_rob2[l] = 0.0f;
#endif
						}
					}
#endif


#ifdef SIMILARITY_SM
					std::vector<float> action_prev(2);
					action_prev[0] = -1.0f;
					action_prev[1] = -1.0f;
#endif

					for(int k = 0; k < ord_vect.size(); ++k)
					{
						int num = (int)(ord_vect[k]);
						assert(num < simu.robots().size());
	
						StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[num]);

						std::vector<float> action = robot->step_action();
	
						// We compute the movement of the robot
						if(action[0] >= 0 || action[1] >= 0)
						{
							float v1 = 4.0*(action[0] * 2.0-1.0);
							float v2 = 4.0*(action[1] * 2.0-1.0);
							
							// v1 and v2 are between -4 and 4
							simu.move_robot(v1, v2, num);

#ifdef SIMILARITY
							if(0 == num || 1 == num)
							{
#ifdef SIMILARITY_SM
							// We compute the similarity
#ifdef SIM_WINDOW
								for(size_t l = 0; l < action.size(); ++l)
								{
#ifdef LIMITED_SENSORS
									break;
#endif


#ifdef SLIDING_WINDOW
									if(0 == num)
									{
										if(i >= Params::simu::sim_window_size)
										{
											float value = vec_sm_rob1[Params::nn::nb_inputs + l].front();
											vec_sm_rob1[Params::nn::nb_inputs + l].pop();
											vec_sm_total_rob1[Params::nn::nb_inputs + l] -= value;
										}

										vec_sm_rob1[Params::nn::nb_inputs + l].push(action[l]);
										vec_sm_total_rob1[Params::nn::nb_inputs + l] += action[l];
									}
									else
									{
										if(i >= Params::simu::sim_window_size)
										{
											float value = vec_sm_rob2[Params::nn::nb_inputs + l].front();
											vec_sm_rob2[Params::nn::nb_inputs + l].pop();
											vec_sm_total_rob2[Params::nn::nb_inputs + l] -= value;
										}

										vec_sm_rob2[Params::nn::nb_inputs + l].push(action[l]);
										vec_sm_total_rob2[Params::nn::nb_inputs + l] += action[l];
									}
#elif defined(SIM_MEAN)
									if(0 == num)
										mean_rob1 += action[l];
									else
										mean_rob2 += action[l];
#else
									if(0 == num)
										vec_sm_rob1[Params::nn::nb_inputs + l] += action[l];
									else
										vec_sm_rob2[Params::nn::nb_inputs + l] += action[l];
#endif
								}
#else
								if(action_prev[0] > -1.0f)
									for(size_t l = 0; l < action_prev.size(); ++l)
									{
										float dist = (action_prev[l] - action[l]) * (action_prev[l] - action[l]);
										dist = sqrtf(dist);
										similarity_trials[Params::nn::nb_inputs + l] += dist;
									}
								else
								{
									action_prev[0] = action[0];
									action_prev[1] = action[1];
								}
#endif
#elif defined(ACT_WHEELS)
								float activity = (action[0] + action[1])/2.0f;
								vec_activity[num] += activity;
#endif
							}
#endif

#ifdef DIVSM
							if(0 == num || 1 == num)
								for(size_t l = 0; l < action.size(); ++l)
									vec_sm_trials[Params::nn::nb_inputs + l] = action[l];
#endif
						}
					} // End for(robots)

#ifdef SIMSENSORS
					// Computing the similarity on the sensors inputs
					std::vector<float>& vec_inputs_rob1 = ((Hunter*)(simu.robots()[0]))->get_last_inputs();
					std::vector<float>& vec_inputs_rob2 = ((Hunter*)(simu.robots()[1]))->get_last_inputs();

					assert(vec_inputs_rob1.size() == vec_inputs_rob2.size());

					for(size_t l = 0; l < vec_inputs_rob1.size(); ++l)
					{
#ifdef LIMITED_SENSORS
						if(!vec_sensors[l])
							continue;
#endif

#ifdef SIM_WINDOW
#ifdef SLIDING_WINDOW
						if(i >= Params::simu::sim_window_size)
						{
							float value = vec_sm_rob1[l].front();
							vec_sm_rob1[l].pop();
							vec_sm_total_rob1[l] -= value;

							value = vec_sm_rob2[l].front();
							vec_sm_rob2[l].pop();
							vec_sm_total_rob2[l] -= value;
						}

						vec_sm_rob1[l].push(vec_inputs_rob1[l]);
						vec_sm_total_rob1[l] += vec_inputs_rob1[l];

						vec_sm_rob2[l].push(vec_inputs_rob2[l]);
						vec_sm_total_rob2[l] += vec_inputs_rob2[l];
#elif defined(SIM_MEAN)
						mean_rob1 += vec_inputs_rob1[l];
						mean_rob2 += vec_inputs_rob2[l];
#else
						vec_sm_rob1[l] += vec_inputs_rob1[l];
						vec_sm_rob2[l] += vec_inputs_rob2[l];
#endif
#else
						float dist = (vec_inputs_rob1[l] - vec_inputs_rob2[l]) * (vec_inputs_rob1[l] - vec_inputs_rob2[l]);
						dist = sqrtf(dist);
						similarity_trials[l] += dist;
#endif
					}
#endif

#ifdef SIM_MEAN
#ifdef LIMITED_SENSORS
					vec_sm_rob1[0] += mean_rob1/(float)nb_sensors;
					vec_sm_rob2[0] += mean_rob2/(float)nb_sensors;
#else
					vec_sm_rob1[0] += mean_rob1/(float)(vec_inputs_rob1.size() + 2);
					vec_sm_rob2[0] += mean_rob2/(float)(vec_inputs_rob2.size() + 2);
#endif
#endif

#ifdef DIVSM
					std::vector<float>& vec_inputs_rob = ((Hunter*)(simu.robots()[0]))->get_last_inputs();

					for(size_t l = 0; l < vec_inputs_rob.size(); ++l)
						vec_sm_trials[l] = vec_inputs_rob[l];
#endif


#if defined(SIMILARITY_ACTIVITY) && !defined(ACT_WHEELS)
					// We compute the distance for each hunter from their previous positions
					for(size_t l = 0; l < 2; ++l)
					{
						StagHuntRobot* rob = (StagHuntRobot*)(simu.robots()[l]);

						float distance = rob->get_pos().dist_to(vec_prev_pos[l].x(), vec_prev_pos[l].y());

#ifdef ACT_EXP5
						distance = 1.0f - expf(-5.0f * distance);
#elif defined(ACT_EXP10)
						distance = 1.0f - expf(-10.0f * distance);
#elif defined(ACT_EXP3)
						distance = 1.0f - expf(-3.0f * distance);
#elif defined(ACT_EXP1)
						distance = 1.0f - expf(-1.0f * distance);
#else
						distance /= (float)MAX_DIST_STEP;
#endif

#ifdef ACT_DER
						vec_activity[l] += fabs(distance - vec_prev_dist[l]);
						vec_prev_dist[l] = distance;
#else
						vec_activity[l] += distance;
#endif

						vec_prev_pos[l].set_x(rob->get_pos().x());
						vec_prev_pos[l].set_y(rob->get_pos().y());
					}
#endif


#ifdef PROXIMITY
					// We compute the distance between the two individuals
					StagHuntRobot* rob1 = (StagHuntRobot*)(simu.robots()[0]);
					StagHuntRobot* rob2 = (StagHuntRobot*)(simu.robots()[1]);

					float distance = rob1->get_pos().dist_to(rob2->get_pos().x(), rob2->get_pos().y());
					proximity_trials += (3400.0f - distance)/3400.0f;
#endif

					update_simu(simu);

					// And then we update their status : food gathered, prey dead
					// For each prey, we check if there are hunters close
					std::vector<int> dead_preys;

					for(int k = 2; k < simu.robots().size(); ++k)
						check_status(simu, (Prey*)(simu.robots()[k]), dead_preys, k);

#ifdef SIMILARITY_HUNT
					StagHuntRobot* rob1 = (StagHuntRobot*)(simu.robots()[0]);
					StagHuntRobot* rob2 = (StagHuntRobot*)(simu.robots()[1]);

					float dist_nearest_prey_rob1 = (3400.0f - rob1->get_distance_nearest_prey())/3400.0f;
					float dist_nearest_prey_rob2 = (3400.0f - rob2->get_distance_nearest_prey())/3400.0f;

					similarity_trials[0] += sqrtf((dist_nearest_prey_rob1 - dist_nearest_prey_rob2) * (dist_nearest_prey_rob1 - dist_nearest_prey_rob2));
#endif

					// We remove the dead preys
					while(!dead_preys.empty())
					{
						int index = dead_preys.back();
	
						Prey::type_prey type = ((Prey*)simu.robots()[index])->get_type();
						Posture pos;

						int nb_blocked = ((Prey*)simu.robots()[index])->get_nb_blocked();
						bool alone = (nb_blocked > 1) ? false : true;

#ifdef BEHAVIOUR_LOG
						if(this->mode() == fit::mode::view)
						{
							std::string fileDump = _file_behaviour + boost::lexical_cast<std::string>(cpt_files + 1) + ".bmp";
       				simu.add_dead_prey(index, fileDump, alone);
       				cpt_files++;
						}
#endif

						bool pred_on_it = ((Prey*)simu.robots()[index])->is_pred_on_it();

						dead_preys.pop_back();
						simu.remove_robot(index);

						if(type == Prey::HARE)
						{
							Posture pos;
		
							if(simu.get_random_initial_position(Params::simu::hare_radius, pos))
							{
								Hare* r = new Hare(Params::simu::hare_radius, pos, HARE_COLOR);
								
								if(pred_on_it)
									r->set_pred_on_it(true);
								
								simu.add_robot(r);
							}
						}
						else if(type == Prey::SMALL_STAG)
						{
							if(simu.get_random_initial_position(Params::simu::big_stag_radius, pos))
							{
								int fur_color = 0;

								Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);

								if(pred_on_it)
									r->set_pred_on_it(true);
									
								simu.add_robot(r);
							}
				 		}
						else if(type == Prey::BIG_STAG)
						{
							Posture pos;

							if(simu.get_random_initial_position(Params::simu::big_stag_radius, pos))
							{
								int fur_color = 50;

								Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);
								
								if(pred_on_it)
									r->set_pred_on_it(true);
									
								simu.add_robot(r);
							}
						}
					} // End while(dead_preys)
				} // End for(steps)


#ifdef SIMILARITY_ACTIVITY
				// We compute the last iterations if necessary
				if(((int)Params::simu::nb_steps % nb_steps_activity) == 0)
				{
					vec_activity[0] /= (float)nb_steps_activity;
					vec_activity[1] /= (float)nb_steps_activity;

					float distance_activity = sqrtf((vec_activity[0] - vec_activity[1]) * (vec_activity[0] - vec_activity[1]));
					similarity_trials[0] += distance_activity;

					vec_activity[0] = 0.0f;
					vec_activity[1] = 0.0f;
				}
#endif

#ifdef SIM_WINDOW
				// We compute the last iterations if necessary
				if(((int)Params::simu::nb_steps % nb_steps_similarity) == 0)
				{
#ifdef SLIDING_WINDOW
					int size_window_cur = vec_sm_rob1[0].size();
#endif

					for(size_t l = 0; l < Params::simu::size_sim_vector; ++l)
					{
#ifdef SLIDING_WINDOW
						assert(size_window_cur == vec_sm_rob1[l].size());
						assert(size_window_cur == vec_sm_rob2[l].size());
						assert(size_window_cur <= Params::simu::sim_window_size);

						float value_rob1 = vec_sm_total_rob1[l] / (float)size_window_cur;
						float value_rob2 = vec_sm_total_rob2[l] / (float)size_window_cur;

						float distance_similarity = sqrtf((value_rob1 - value_rob2) * (value_rob1 - value_rob2));
						similarity_trials[l] += distance_similarity;
#else		
						vec_sm_rob1[l] /= nb_steps_similarity;
						vec_sm_rob2[l] /= nb_steps_similarity;

						float distance_similarity = sqrtf((vec_sm_rob1[l] - vec_sm_rob2[l]) * (vec_sm_rob1[l] - vec_sm_rob2[l]));
						similarity_trials[l] += distance_similarity;

						vec_sm_rob1[l] = 0.0f;
						vec_sm_rob2[l] = 0.0f;
#endif
					}
				}
#endif

       	Hunter* h1 = (Hunter*)(simu.robots()[0]);
       	food1 += h1->get_food_gathered();
		   	food_trial += h1->get_food_gathered();
       	
       	moy_hares1 += h1->nb_hares_hunted();
       	moy_sstags1 += h1->nb_small_stags_hunted();
       	moy_bstags1 += h1->nb_big_stags_hunted();
				moy_hares1_solo += h1->nb_hares_hunted_solo();
       	moy_sstags1_solo += h1->nb_small_stags_hunted_solo();
       	moy_bstags1_solo += h1->nb_big_stags_hunted_solo();
       	
       	Hunter* h2 = (Hunter*)(simu.robots()[1]);
       	food2 += h2->get_food_gathered();
       	
       	moy_hares2 += h2->nb_hares_hunted();
       	moy_sstags2 += h2->nb_small_stags_hunted();
       	moy_bstags2 += h2->nb_big_stags_hunted();
				moy_hares2_solo += h2->nb_hares_hunted_solo();
       	moy_sstags2_solo += h2->nb_small_stags_hunted_solo();
       	moy_bstags2_solo += h2->nb_big_stags_hunted_solo();

#ifdef SIMILARITY
#ifdef SIMILARITY_ACTIVITY
       	int nb_activity_dump = 1.0f/Params::simu::ratio_steps_activity;

     		similarity[0] += similarity_trials[0]/(float)nb_activity_dump;
#elif defined(SIM_WINDOW)
       	int nb_similarity_dump = 1.0f/Params::simu::ratio_steps_similarity;

       	for(size_t l = 0; l < similarity_trials.size(); ++l)
	     		similarity[l] += similarity_trials[l]/(float)nb_similarity_dump;
#else
       	for(size_t l = 0; l < similarity_trials.size(); ++l)
       		similarity[l] += similarity_trials[l]/(float)Params::simu::nb_steps;
#endif
#endif

#ifdef PROXIMITY
       	proximity += proximity_trials/(float)Params::simu::nb_steps;
#endif

#ifdef DIVSM
       	for(size_t l = 0; l < vec_sm_trials.size(); ++l)
       		vec_sm[l] += vec_sm_trials[l]/(float)Params::simu::nb_steps;
#endif

       	
#ifdef BEHAVIOUR_VIDEO
				if(this->mode() == fit::mode::view)
					return;
#endif
			} // End for(trials)
			
			// Mean on all the trials
     	moy_hares1 /= Params::simu::nb_trials;
     	moy_sstags1 /= Params::simu::nb_trials;
     	moy_bstags1 /= Params::simu::nb_trials;
      moy_hares1_solo /= Params::simu::nb_trials;
     	moy_sstags1_solo /= Params::simu::nb_trials;
     	moy_bstags1_solo /= Params::simu::nb_trials;

			food1 /= Params::simu::nb_trials;


     	moy_hares2 /= Params::simu::nb_trials;
     	moy_sstags2 /= Params::simu::nb_trials;
     	moy_bstags2 /= Params::simu::nb_trials;
      moy_hares2_solo /= Params::simu::nb_trials;
     	moy_sstags2_solo /= Params::simu::nb_trials;
     	moy_bstags2_solo /= Params::simu::nb_trials;

			food2 /= Params::simu::nb_trials;
		
#ifdef NOT_AGAINST_ALL	
			int nb_encounters = Params::pop::nb_opponents*Params::pop::nb_eval;
#elif defined(ALTRUISM)
			int nb_encounters = 1;
#else
			int nb_encounters = Params::pop::size - 1;
#endif

     	moy_hares1 /= nb_encounters;
     	moy_sstags1 /= nb_encounters;
     	moy_bstags1 /= nb_encounters;
      moy_hares1_solo /= nb_encounters;
     	moy_sstags1_solo /= nb_encounters;
     	moy_bstags1_solo /= nb_encounters;
     	
			ind1.add_nb_hares(moy_hares1, moy_hares1_solo);
			ind1.add_nb_sstag(moy_sstags1, moy_sstags1_solo);
			ind1.add_nb_bstag(moy_bstags1, moy_bstags1_solo);

     	moy_hares2 /= nb_encounters;
     	moy_sstags2 /= nb_encounters;
     	moy_bstags2 /= nb_encounters;
      moy_hares2_solo /= nb_encounters;
     	moy_sstags2_solo /= nb_encounters;
     	moy_bstags2_solo /= nb_encounters;
     	
#if !defined(NOT_AGAINST_ALL) && !defined(ALTRUISM)
			ind2.add_nb_hares(moy_hares2, moy_hares1_solo);
			ind2.add_nb_sstag(moy_sstags2, moy_sstags1_solo);
			ind2.add_nb_bstag(moy_bstags2, moy_bstags1_solo);
#endif
     	
     	food2 /= nb_encounters;
     	food1 /= nb_encounters;

#ifdef FITCOOP
			float max_hunts = Params::simu::nb_steps/STAMINA;
     	float fitness = moy_bstags1 - moy_bstags1_solo;
     	fitness = std::min(fitness, max_hunts)/max_hunts;

     	ind1.fit().add_fitness(fitness);
#else
			ind1.fit().add_fitness(food1);
#endif
			
#if !defined(NOT_AGAINST_ALL) && !defined(ALTRUISM)
			ind2.fit().add_fitness(food2);
#endif

#ifdef SIMILARITY
			for(size_t l = 0; l < similarity.size(); ++l)
			{
				similarity[l] /= Params::simu::nb_trials;
				similarity[l] /= nb_encounters;
				ind1.add_similarity(similarity[l], l);
			}
#endif

#ifdef PROXIMITY
			proximity /= Params::simu::nb_trials;
			proximity /= nb_encounters;
			ind1.add_proximity(proximity);
#endif

#ifdef DIVSM
			for(size_t l = 0; l < vec_sm.size(); ++l)
			{
				vec_sm[l] /= Params::simu::nb_trials;
				vec_sm[l] /= nb_encounters;
				ind1.add_vec_sm(vec_sm[l], l);
			}
#endif
    } // *** end of eval ***

    
    template<typename Simu>
      void init_simu(Simu& simu, nn_t &nn1, nn_t &nn2)
    {
  		// Preparing the environment
      prepare_env(simu, nn1, nn2);
      
      // Visualisation mode
			if(this->mode() == fit::mode::view)
			{
			  simu.init_view(true);
				
#ifdef BEHAVIOUR_VIDEO
				simu.set_file_video(_file_video);
#endif
			}
      
      stop_eval = false;
      reinit = false;
    }

    // Prepare environment
    template<typename Simu>
      void prepare_env(Simu& simu, nn_t &nn1, nn_t &nn2)
    {
      using namespace fastsim;

      simu.init();
      simu.map()->clear_illuminated_switches();
			
		  // Sizes
	    width=simu.map()->get_real_w();
	    height=simu.map()->get_real_h();

			// Robots :
			// First the robots for the two hunters
			std::vector<Posture> pos_init;
			
#ifdef POS_CLOSE
			pos_init.push_back(Posture(width/2 - 40, 80, M_PI/2));
			pos_init.push_back(Posture(width/2 + 40, 80, M_PI/2));
#else
			pos_init.push_back(Posture(width/2, 80, M_PI/2));
			pos_init.push_back(Posture(width/2, height - 80, -M_PI/2));
#endif

			invers_pos = false;
			
			for(int i = 0; i < 2; ++i)
			{
				Hunter* r;				
				Posture pos = (invers_pos) ? pos_init[(i + 1)%2] : pos_init[i];
		
				if(0 == i)
					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR, nn1);
				else
					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR, nn2);

				if(!r->is_deactivated())
				{	
					// 12 lasers range sensors 
					r->add_laser(Laser(0, 50));
					r->add_laser(Laser(M_PI / 6, 50));
					r->add_laser(Laser(M_PI / 3, 50));
					r->add_laser(Laser(M_PI / 2, 50));
					r->add_laser(Laser(2*M_PI / 3, 50));
					r->add_laser(Laser(5*M_PI / 6, 50));
					r->add_laser(Laser(M_PI, 50));
					r->add_laser(Laser(-5*M_PI / 6, 50));
					r->add_laser(Laser(-2*M_PI / 3, 50));
					r->add_laser(Laser(-M_PI / 2, 50));
					r->add_laser(Laser(-M_PI / 3, 50));
					r->add_laser(Laser(-M_PI / 6, 50));
		
					// 1 linear camera
					r->use_camera(LinearCamera(M_PI/2, Params::simu::nb_camera_pixels));
				}
		
				simu.add_robot(r);
			}
								
			// Then the hares std::vector<Posture> vec_pos;
			int nb_big_stags = Params::simu::ratio_big_stags*Params::simu::nb_big_stags;
			int nb_small_stags = Params::simu::nb_big_stags - nb_big_stags;

			for(int i = 0; i < Params::simu::nb_hares; ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::big_stag_radius + 5, pos))
				{
					Hare* r = new Hare(Params::simu::hare_radius, pos, HARE_COLOR);
			
#ifdef COOP_HARE
					if(0 == i)
						r->set_pred_on_it(true);
#endif
		
					simu.add_robot(r);
				}
			}
	
			// And finally the big stags
			for(int i = 0; i < Params::simu::nb_big_stags; ++i)
			{
				int fur_color = 0;
				if(i >= nb_small_stags)
					fur_color = 50;
			
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::big_stag_radius + 5, pos))
				{
					Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);
			
#ifdef COOP_SSTAG
					if(0 == i)
						r->set_pred_on_it(true);
#endif
#ifdef COOP_BSTAG
					if(nb_small_stags == i)
						r->set_pred_on_it(true);
#endif
					simu.add_robot(r);
				}
			}
		}
    
    // *** Refresh infos about the robots
    template<typename Simu>
      void update_simu(Simu &simu) 
    {
      // refresh
      using namespace fastsim;
//      simu.refresh();
			
			if (this->mode() == fit::mode::view)
			  simu.refresh_view();
    }
    
    template<typename Simu>
    	void check_status(Simu &simu, Prey* prey, std::vector<int>& dead_preys, int position)
   	{
   		using namespace fastsim;
   		
   		// We compute the distance between this prey and each of its hunters
   		std::vector<Hunter*> hunters;
   		float px = prey->get_pos().x();
   		float py = prey->get_pos().y();
   		
   		for(int i = 0; i < 2; ++i)
   		{
   			Hunter* hunter = (Hunter*)(simu.robots()[i]);
   			float hx = hunter->get_pos().x();
   			float hy = hunter->get_pos().y();
   			float dist = sqrt(pow(px - hx, 2) + pow(py - hy, 2));

   			// The radius must not be taken into account
   			if((dist - prey->get_radius() - hunter->get_radius()) <= CATCHING_DISTANCE)
   				hunters.push_back(hunter);

   			if(dist < hunter->get_distance_nearest_prey())
   				hunter->set_distance_nearest_prey(dist);
   		}
   		
   		// We check if the prey is blocked
   		prey->blocked_by_hunters(hunters.size());
   	
   		// And then we check if the prey is dead and let the hunters
   		// have a glorious feast on its corpse. Yay !
   		if(prey->is_dead())
   		{
   			float food = 0;
   			
	   		food = prey->feast();
	   		
   			Prey::type_prey type = prey->get_type();
   			dead_preys.push_back(position);

				bool alone;
				if(prey->get_nb_blocked() <= 1)
					alone = true;
				else
					alone = false;

   			for(int i = 0; i < hunters.size(); ++i)
   			{
   				hunters[i]->add_food(food);

   				if(type == Prey::HARE)
   					hunters[i]->eat_hare(alone);
   				else if(type == Prey::SMALL_STAG)
   					hunters[i]->eat_small_stag(alone);
   				else
   					hunters[i]->eat_big_stag(alone);
   			}
   		}
   	}
   	    
		
		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool invers_pos;
		bool reinit;
		int nb_invers_pos, nb_spawn;

		std::string res_dir;
		size_t gen;
		
		void set_res_dir(std::string res_dir)
		{
			this->res_dir = res_dir;
		}
		
		void set_gen(size_t gen)
		{
			this->gen = gen;
		}

#ifdef BEHAVIOUR_VIDEO
		std::string _file_video;
		
		void set_file_video(const std::string& file_video)
		{
			_file_video = file_video;
		}
#endif

#ifdef BEHAVIOUR_LOG
		std::string _file_behaviour;
		int cpt_files;
#endif

		std::vector<float> vec_fitness;
		tbb::atomic<float> fitness_at;
		
		void add_fitness(float fitness)
		{
			fitness_at.fetch_and_store(fitness_at + fitness);
		}
  };
}


// ****************** Main *************************
int main(int argc, char **argv)
{
  srand(time(0));
  
  // FITNESS
  typedef FitStagHunt<Params> fit_t;

	// GENOTYPE
#ifdef CMAES
  typedef gen::Cmaes<(Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs, Params> gen_t;
//  typedef gen::Cmaes<90, Params> gen_t;
#else
#ifdef ELITIST
  typedef gen::ElitistGen<(Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs, Params> gen_t;
#else
  typedef gen::EvoFloat<(Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs, Params> gen_t;
#endif
#endif
  
  // PHENOTYPE
  typedef phen::PhenChasseur<gen_t, fit_t, Params> phen_t;

	// EVALUATION
	typedef eval::StagHuntEvalParallel<Params> eval_t;

  // STATS 
  typedef boost::fusion::vector<
#if defined(DIVERSITY) && defined(MULTI_ACTIVITY)
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
		  sferes::stat::BestDiversityEval<phen_t, Params>,
		  sferes::stat::AllDiversityEvalStat<phen_t, Params>,
		  sferes::stat::BestSimilarityEval<phen_t, Params>,
		  sferes::stat::AllSimilarityEvalStat<phen_t, Params>,
#else
#ifndef MONO_DIV
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
#endif
#ifndef MONO_OBJ
		  sferes::stat::BestDiversityEval<phen_t, Params>,
		  sferes::stat::MeanDiversityEval<phen_t, Params>,
		  sferes::stat::BestEverDiversityEval<phen_t, Params>,
		  sferes::stat::AllDiversityEvalStat<phen_t, Params>,
#endif
#endif
#if defined(BEHAVIOUR_VIDEO) && !defined(MONO_DIV)
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
#endif
		  sferes::stat::StopEval<Params>
    >  stat_t;
  
  //MODIFIER
  typedef modif::Dummy<Params> modifier_t;

	// EVOLUTION ALGORITHM
	typedef ea::Nsga2<phen_t, eval_t, stat_t, modifier_t, Params> ea_t; 

  ea_t ea;

  // RUN EA
  time_t exec = time(NULL);
  run_ea(argc, argv, ea);
	std::cout << "Temps d'exécution : " << time(NULL) - exec;

  return 0;
}
