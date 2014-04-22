// THIS IS A GENERATED FILE - DO NOT EDIT
#define PARALLEL
#define MLP
#define ELITIST
#define SETTING1
#define PREYS18
#define MAP800
#define HIGH_STAMINA
#define STEPS15000
#define TRIALS5
#line 1 "/home/abernard/sferes2-0.99/exp/StagHuntExp3-Duo/StagHuntExp3.cpp"
#include "includes.hpp"
#include "defparams.hpp"

namespace sferes
{
  using namespace nn;
  
  // ********** Main Class ***********
  SFERES_FITNESS(FitStagHunt, sferes::fit::Fitness)
  {
  public:
#ifdef MLP
		typedef Neuron<PfWSum<>, AfSigmoidNoBias<> > neuron_t;
		typedef Connection<float> connection_t;
		typedef Mlp< neuron_t, connection_t > nn_t;
#else
		typedef NN<Neuron<PfWSum<>, AfSigmoidNoBias<float> >, Connection<> > nn_t;
#endif
    template<typename Indiv>
      void eval(Indiv& ind) 
		{
			std::cout << "Nop !" << std::endl;
		}

    template<typename Indiv>
      void eval_compet(Indiv& ind1, Indiv& ind2) 
    {
#ifdef MLP
      nn_t nn1(Params::nn::nb_inputs, Params::nn::nb_hidden, Params::nn::nb_outputs);
      nn_t nn2(Params::nn::nb_inputs, Params::nn::nb_hidden, Params::nn::nb_outputs);
#else
			nn_t nn1, nn2;

			nn1.set_nb_inputs(Params::nn::nb_inputs + 1);
			nn1.set_nb_outputs(Params::nn::nb_outputs);
			nn1.full_connect(nn1.get_inputs(), nn1.get_outputs(), 1.0f);

			nn2.set_nb_inputs(Params::nn::nb_inputs + 1);
			nn2.set_nb_outputs(Params::nn::nb_outputs);
			nn2.full_connect(nn2.get_inputs(), nn2.get_outputs(), 1.0f);
#endif

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

#ifdef COUNT_TIME
			float moy_time_on_hares1 = 0, moy_time_on_sstags1 = 0, moy_time_on_bstags1 = 0;
#endif

#ifdef TEST_VARIANCE_TRIALS
			std::string fileName = res_dir + "/fitnessTrialDebug.txt";
//			std::string fileName = "fitnessDebug.txt";
			std::ofstream fit(fileName.c_str(), std::ios::out | std::ios::app);
			fit << gen;
//			fit << 0;
#endif

//			map_t map(Params::simu::map_name(), Params::simu::real_w);

#ifdef VARIANCE_TRIALS
			std::string fileNameVariance = res_dir + "/fitnessVarianceTrials.txt";
			std::ofstream fitVariance(fileNameVariance.c_str(), std::ios::out | std::ios::app);
			fitVariance << gen;
			
			for (size_t l = 0; l < 10; ++l)
			{
#endif

//			std::remove("visionDebug.txt");

      for (size_t j = 0; j < Params::simu::nb_trials; ++j)
      {
      	// init
/*				simu_t simu(map);
				init_simu(simu, nn1);*/

				map_t map(Params::simu::map_name(), Params::simu::real_w);
				simu_t simu(map, (this->mode() == fit::mode::view));
				init_simu(simu, nn1, nn2);

#ifdef MLP_PERSO
				StagHuntRobot* robotTmp = (StagHuntRobot*)(simu.robots()[0]);
				Hunter* hunterTmp = (Hunter*)robotTmp;
				hunterTmp->set_weights(ind.data());
#endif
	
				float food_trial = 0;

				for (size_t i = 0; i < Params::simu::nb_steps && !stop_eval; ++i)
				{
					// Number of steps the robots are evaluated
					_nb_eval = i + 1;

					// We compute the robots' actions in an ever-changing order
					std::vector<size_t> ord_vect;
					misc::rand_ind(ord_vect, simu.robots().size());
					
#ifdef COMPAS_PRED
					// We update the compas information of each hunter
					StagHuntRobot* robot1 = (StagHuntRobot*)(simu.robots()[0]);
					Hunter* hunter1 = (Hunter*)robot1;
					StagHuntRobot* robot2 = (StagHuntRobot*)(simu.robots()[1]);
					Hunter* hunter2 = (Hunter*)robot2;
	
					float distance_toPred = robot1->get_pos().dist_to(robot2->get_pos().x(), robot2->get_pos().y());
					hunter1->set_distance_hunter(distance_toPred);
					hunter2->set_distance_hunter(distance_toPred);
					
					float angle_toPred2 = normalize_angle(atan2(robot2->get_pos().y() - robot1->get_pos().y(), robot2->get_pos().x() - robot1->get_pos().x()));
					angle_toPred2 = normalize_angle(angle_toPred2 - robot1->get_pos().theta());
					hunter1->set_angle_hunter(angle_toPred2);
					
					float angle_toPred1 = normalize_angle(atan2(robot1->get_pos().y() - robot2->get_pos().y(), robot1->get_pos().x() - robot2->get_pos().x()));
					angle_toPred1 = normalize_angle(angle_toPred1 - robot2->get_pos().theta());
					hunter2->set_angle_hunter(angle_toPred1);
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
#ifdef LOW_SPEED
							float v1 = 2.0*(action[0] * 2.0-1.0);
							float v2 = 2.0*(action[1] * 2.0-1.0);
#else
							float v1 = 4.0*(action[0] * 2.0-1.0);
							float v2 = 4.0*(action[1] * 2.0-1.0);
#endif
							
							// v1 and v2 are between -4 and 4
							simu.move_robot(v1, v2, num);
						}
						
#ifdef SCREAM
						if(action[2] >= Params::simu::scream_threshold)
						{
							// The other hunter hears the scream
							if(num == 0)
								((Hunter*)(simu.robots()[1]))->set_scream_heard(true);
							else if(num == 1)
								((Hunter*)(simu.robots()[0]))->set_scream_heard(true);
						}
#endif
					}
					update_simu(simu);

					// And then we update their status : food gathered, prey dead
					// For each prey, we check if there are hunters close
					std::vector<int> dead_preys;

#ifdef COMPAS_PREY
					bool found_prey = false;
#endif

#ifdef SOLO
					for(int k = 1; k < simu.robots().size(); ++k)
#else
					for(int k = 2; k < simu.robots().size(); ++k)
#endif
					{
						check_status(simu, (Prey*)(simu.robots()[k]), dead_preys, k);

#ifdef COMPAS_PREY			
						StagHuntRobot* botPrey = (StagHuntRobot*)(simu.robots()[k]);
						Prey* prey = (Prey*)botPrey;
					
						if(!found_prey && prey->is_pred_on_it())
						{
							StagHuntRobot* robot1 = (StagHuntRobot*)(simu.robots()[0]);
							Hunter* hunter1 = (Hunter*)robot1;
							StagHuntRobot* robot2 = (StagHuntRobot*)(simu.robots()[1]);
							Hunter* hunter2 = (Hunter*)robot2;

							float distance_toPrey1 = robot1->get_pos().dist_to(botPrey->get_pos().x(), botPrey->get_pos().y());
							hunter1->set_distance_prey(distance_toPrey1);
							float distance_toPrey2 = robot2->get_pos().dist_to(botPrey->get_pos().x(), botPrey->get_pos().y());
							hunter2->set_distance_prey(distance_toPrey2);
				
							float angle_toPrey1 = normalize_angle(atan2(botPrey->get_pos().y() - robot1->get_pos().y(), botPrey->get_pos().x() - robot1->get_pos().x()));
							angle_toPrey1 = normalize_angle(angle_toPrey1 - robot1->get_pos().theta());
							hunter1->set_angle_prey(angle_toPrey1);
				
							float angle_toPrey2 = normalize_angle(atan2(botPrey->get_pos().y() - robot2->get_pos().y(), botPrey->get_pos().x() - robot2->get_pos().x()));
							angle_toPrey2 = normalize_angle(angle_toPrey2 - robot2->get_pos().theta());
							hunter2->set_angle_prey(angle_toPrey2);
						
							found_prey = true;
						}
#endif
					}

#ifdef COMPAS_PREY
					if(!found_prey)
					{
							StagHuntRobot* robot1 = (StagHuntRobot*)(simu.robots()[0]);
							Hunter* hunter1 = (Hunter*)robot1;
							hunter1->set_distance_prey(-1.0f);
							hunter1->set_angle_prey(0.0f);
							
							StagHuntRobot* robot2 = (StagHuntRobot*)(simu.robots()[1]);
							Hunter* hunter2 = (Hunter*)robot2;
							hunter2->set_distance_prey(-1.0f);
							hunter2->set_angle_prey(0.0f);
					}
#endif
					
					// We remove the dead preys
					while(!dead_preys.empty())
					{
						int index = dead_preys.back();
	
						Prey::type_prey type = ((Prey*)simu.robots()[index])->get_type();
						Posture pos;

						if(this->mode() == fit::mode::view)
							simu.add_dead_prey(index);

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
					}
				}
       	
       	Hunter* h1 = (Hunter*)(simu.robots()[0]);
       	food1 += h1->get_food_gathered();
		   	food_trial += h1->get_food_gathered();
       	
       	moy_hares1 += h1->nb_hares_hunted();
       	moy_sstags1 += h1->nb_small_stags_hunted();
       	moy_bstags1 += h1->nb_big_stags_hunted();
				moy_hares1_solo += h1->nb_hares_hunted_solo();
       	moy_sstags1_solo += h1->nb_small_stags_hunted_solo();
       	moy_bstags1_solo += h1->nb_big_stags_hunted_solo();
       	
#ifndef SOLO
       	Hunter* h2 = (Hunter*)(simu.robots()[1]);
       	food2 += h2->get_food_gathered();
       	
       	moy_hares2 += h2->nb_hares_hunted();
       	moy_sstags2 += h2->nb_small_stags_hunted();
       	moy_bstags2 += h2->nb_big_stags_hunted();
				moy_hares2_solo += h2->nb_hares_hunted_solo();
       	moy_sstags2_solo += h2->nb_small_stags_hunted_solo();
       	moy_bstags2_solo += h2->nb_big_stags_hunted_solo();
#endif
       	       	
#ifdef COUNT_TIME
				moy_time_on_hares1 += h1->time_on_hares();
				moy_time_on_sstags1 += h1->time_on_sstags();
				moy_time_on_bstags1 += h1->time_on_bstags();
#endif
       	
#ifdef TEST_VARIANCE_TRIALS
				fit << "," << food_trial;
#endif
       	
#ifdef BEHAVIOUR_LOG
       	if(this->mode() == fit::mode::view)
       	{
       		simu.dump_behaviour_log(_file_behaviour.c_str());
       		return;
       	}
#endif
#ifdef BEHAVIOUR_VIDEO
				if(this->mode() == fit::mode::view)
					return;
#endif
			}
#ifdef TEST_VARIANCE_TRIALS
			fit << std::endl;
			fit.close();
#endif
			
			// Mean on all the trials
     	moy_hares1 /= Params::simu::nb_trials;
     	moy_sstags1 /= Params::simu::nb_trials;
     	moy_bstags1 /= Params::simu::nb_trials;
      moy_hares1_solo /= Params::simu::nb_trials;
     	moy_sstags1_solo /= Params::simu::nb_trials;
     	moy_bstags1_solo /= Params::simu::nb_trials;

			food1 /= Params::simu::nb_trials;

#ifndef SOLO
     	moy_hares2 /= Params::simu::nb_trials;
     	moy_sstags2 /= Params::simu::nb_trials;
     	moy_bstags2 /= Params::simu::nb_trials;
      moy_hares2_solo /= Params::simu::nb_trials;
     	moy_sstags2_solo /= Params::simu::nb_trials;
     	moy_bstags2_solo /= Params::simu::nb_trials;

			food2 /= Params::simu::nb_trials;
#endif
			
#ifdef NOT_AGAINST_ALL
			int nb_encounters = Params::pop::nb_opponents*Params::pop::nb_eval;
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

#ifndef SOLO
     	moy_hares2 /= nb_encounters;
     	moy_sstags2 /= nb_encounters;
     	moy_bstags2 /= nb_encounters;
      moy_hares2_solo /= nb_encounters;
     	moy_sstags2_solo /= nb_encounters;
     	moy_bstags2_solo /= nb_encounters;
     	
#ifndef NOT_AGAINST_ALL     	
			ind2.add_nb_hares(moy_hares2, moy_hares1_solo);
			ind2.add_nb_sstag(moy_sstags2, moy_sstags1_solo);
			ind2.add_nb_bstag(moy_bstags2, moy_bstags1_solo);
#endif
     	
     	food2 /= nb_encounters;
#endif
     	
     	food1 /= nb_encounters;
			
#ifdef COUNT_TIME
			moy_time_on_hares1 /= Params::simu::nb_trials;
			moy_time_on_sstags1 /= Params::simu::nb_trials;
			moy_time_on_bstags1 /= Params::simu::nb_trials;
			
			ind1.add_time_on_hares(moy_time_on_hares1);
			ind1.add_time_on_sstags(moy_time_on_sstags1);
			ind1.add_time_on_bstags(moy_time_on_bstags1);
#endif

#ifdef PUNITION_SOFT
			if(food1 < 0)
				food1 = 0.0f;
#endif

#ifdef VARIANCE_TRIALS
			fitVariance << "," << food1;
#endif

			ind1.fit().add_fitness(food1);
			
#ifndef NOT_AGAINST_ALL
			ind2.fit().add_fitness(food2);
#endif

#ifdef VARIANCE_TRIALS
			}
			fitVariance << std::endl;
			fitVariance.close();
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

			// Second map, used for initiating the robots positions
			fastsim::Map map2(Params::simu::map_name(), Params::simu::real_w);
			
		  // Sizes
	    width=simu.map()->get_real_w();
	    height=simu.map()->get_real_h();

			// Robots :
			// First the robots for the two hunters
			std::vector<Posture> pos_init;
			
#ifdef POS_ALEA
			for(int i = 0; i < 2; ++i)
			{
				Posture pos;

				if(map2.get_random_initial_position(Params::simu::hunter_radius + 5, pos))
				{
					pos_init.push_back(pos);

					float x = pos.x();
					float y = pos.y();
					float radius = Params::simu::hunter_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
				}
			}
#elif defined(POS_ALEA_CENTER)
			float circle_radius = width/4.0f;
			for(int i = 0; i < 2; ++i)
			{
				Posture pos;

				if(map2.get_random_initial_position_circle(Params::simu::hunter_radius + 5, pos, circle_radius))
				{
					pos_init.push_back(pos);

					float x = pos.x();
					float y = pos.y();
					float radius = Params::simu::hunter_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
				}
			}
#elif defined(POS_CENTER)
			pos_init.push_back(Posture(width/2, height/3.0f, M_PI/2));
			pos_init.push_back(Posture(width/2, 2.0f * height/3.0f, -M_PI/2));
#else
			pos_init.push_back(Posture(width/2, 80, M_PI/2));
			pos_init.push_back(Posture(width/2, height - 80, -M_PI/2));
#endif			

			invers_pos = false;
#ifdef SOLO
			for(int i = 0; i < 1; ++i)
#else
			for(int i = 0; i < 2; ++i)
#endif
			{
				Hunter* r;				
				Posture pos = (invers_pos) ? pos_init[(i + 1)%2] : pos_init[i];
		
				if(0 == i)
					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR, nn1);
				else
					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR, nn2);

#ifdef PRED_IMMOBILE
				if(i > 0)	
					r->set_deactivated(true);
#endif
#ifdef MOVING_PREYS
				r->set_deactivated(true);
#endif

				if(!r->is_deactivated())
				{	
			// 6 lasers range sensors 
#ifdef DOUBLE_RANGE
					r->add_laser(Laser(M_PI / 3, 100));
					r->add_laser(Laser(0, 100));
					r->add_laser(Laser(-M_PI / 3, 100));
					r->add_laser(Laser(2 * M_PI / 3, 100));
					r->add_laser(Laser(M_PI, 100));
					r->add_laser(Laser(-2 * M_PI / 3, 100));
#elif defined(MORE_SENSORS)
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
#else
					r->add_laser(Laser(M_PI / 3, 50));
					r->add_laser(Laser(0, 50));
					r->add_laser(Laser(-M_PI / 3, 50));
					r->add_laser(Laser(2 * M_PI / 3, 50));
					r->add_laser(Laser(M_PI, 50));
					r->add_laser(Laser(-2 * M_PI / 3, 50));
#endif
		
					// 1 linear camera
					r->use_camera(LinearCamera(M_PI/2, Params::simu::nb_camera_pixels));
				}
		
				simu.add_robot(r);
			}
					
#if !defined(POS_ALEA) && !defined(POS_ALEA_CENTER)
			// We need to add the obstacles formed by the robots
			float x = pos_init[0].x();
			float y = pos_init[0].y();
			float radius = Params::simu::hunter_radius;
			float _bbx = x - radius - 4;
			float _bby = y - radius - 4;
			float _bbw = radius * 2 + 8;
			float _bbh = radius * 2 + 8;				
			map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
					
			// We need to add the obstacles formed by the robots
			x = pos_init[1].x();
			y = pos_init[1].y();
			radius = Params::simu::hunter_radius;
			_bbx = x - radius - 4;
			_bby = y - radius - 4;
			_bbw = radius * 2 + 8;
			_bbh = radius * 2 + 8;				
			map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
#endif			
								
			// Then the hares std::vector<Posture> vec_pos;
			int nb_big_stags = Params::simu::ratio_big_stags*Params::simu::nb_big_stags;
			int nb_small_stags = Params::simu::nb_big_stags - nb_big_stags;

			for(int i = 0; i < Params::simu::nb_hares; ++i)
			{
				Posture pos;

				if(map2.get_random_initial_position(Params::simu::big_stag_radius + 5, pos))
				{
					Hare* r = new Hare(Params::simu::hare_radius, pos, HARE_COLOR);

#ifdef MOVING_PREYS
					r->add_laser(Laser(0, 50));
					r->add_laser(Laser(M_PI / 3, 50));
					r->add_laser(Laser(-M_PI / 3, 50));
					r->add_laser(Laser(2 * M_PI / 3, 50));
					r->add_laser(Laser(-2 * M_PI / 3, 50));
					r->add_laser(Laser(M_PI, 50));
#endif
			
#ifdef COOP_HARE
					if(0 == i)
						r->set_pred_on_it(true);
#endif
		
					simu.add_robot(r);

					float x = pos.x();
					float y = pos.y();
					float radius = Params::simu::hare_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
				}
			}
	
			// And finally the big stags
			for(int i = 0; i < Params::simu::nb_big_stags; ++i)
			{
				int fur_color = 0;
				if(i >= nb_small_stags)
					fur_color = 50;
			
				Posture pos;

				if(map2.get_random_initial_position(Params::simu::big_stag_radius + 5, pos))
				{
					Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);

#ifdef MOVING_PREYS
					r->add_laser(Laser(0, 50));
					r->add_laser(Laser(M_PI / 3, 50));
					r->add_laser(Laser(-M_PI / 3, 50));
					r->add_laser(Laser(2 * M_PI / 3, 50));
					r->add_laser(Laser(-2 * M_PI / 3, 50));
					r->add_laser(Laser(M_PI, 50));
#endif
			
#ifdef COOP_SSTAG
					if(0 == i)
						r->set_pred_on_it(true);
#endif
#ifdef COOP_BSTAG
					if(nb_small_stags == i)
						r->set_pred_on_it(true);
#endif
					simu.add_robot(r);

					float x = pos.x();
					float y = pos.y();
					float radius = Params::simu::big_stag_radius;
					float _bbx = x - radius - 4;
					float _bby = y - radius - 4;
					float _bbw = radius * 2 + 8;
					float _bbh = radius * 2 + 8;				
					map2.add_robot_obstacle(x, y, radius, _bbx, _bby, _bbw, _bbh);
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
   		
#ifdef SOLO
   		for(int i = 0; i < 1; ++i)
#else
   		for(int i = 0; i < 2; ++i)
#endif
   		{
   			Hunter* hunter = (Hunter*)(simu.robots()[i]);
   			float hx = hunter->get_pos().x();
   			float hy = hunter->get_pos().y();
   			float dist = sqrt(pow(px - hx, 2) + pow(py - hy, 2));
   			
   			// The radius must not be taken into account
   			if((dist - prey->get_radius() - hunter->get_radius()) <= CATCHING_DISTANCE)
   			{
#ifdef PRED_INACTIVE
					if(0 == i)
#endif
   				hunters.push_back(hunter);
   			}
   		}
   		
   		// We check if the prey is blocked
   		prey->blocked_by_hunters(hunters.size());
   		
#ifdef COUNT_TIME
			for(int i = 0; i < hunters.size(); ++i)
			{
   			Prey::type_prey type = prey->get_type();
				
				if(type == Prey::HARE)
					hunters[i]->add_time_on_hares(1);
				else if(type == Prey::SMALL_STAG)
					hunters[i]->add_time_on_sstags(1);
				else				
					hunters[i]->add_time_on_bstags(1);
			}
#endif
   	
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
   				{
   					hunters[i]->eat_hare(alone);
   				}
   				else if(type == Prey::SMALL_STAG)
   					hunters[i]->eat_small_stag(alone);
   				else
   				{
   					hunters[i]->eat_big_stag(alone);

#ifdef PUNITION_HARD
						stop_eval = true;
#endif
   				}
   			}
   		}
   	}
   	    
		
		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool invers_pos;
		bool reinit;
		int nb_invers_pos, nb_spawn;
		
//    std::vector<nn_t> vec_nn;

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
#ifdef DEFINED_POSITIONS
		std::vector<fastsim::Posture> _vec_pos;		

		void set_vec_pos(std::vector<fastsim::Posture>& vec_pos)
		{
			_vec_pos = vec_pos;
		}
#endif

#ifdef BEHAVIOUR_LOG
		std::string _file_behaviour;
		
		void set_file_behaviour(const std::string& file_behaviour)
		{
			_file_behaviour = file_behaviour;
		}
#endif

#ifdef BEHAVIOUR_VIDEO
		std::string _file_video;
		
		void set_file_video(const std::string& file_video)
		{
			_file_video = file_video;
		}
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
#ifdef MLP  
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
#else
#ifdef CMAES
  typedef gen::Cmaes<(Params::nn::nb_inputs + 1) * Params::nn::nb_outputs, Params> gen_t;
#else
#ifdef ELITIST
  typedef gen::ElitistGen<(Params::nn::nb_inputs + 1) * Params::nn::nb_outputs, Params> gen_t;
#else
  typedef gen::EvoFloat<(Params::nn::nb_inputs + 1) * Params::nn::nb_outputs, Params> gen_t;
#endif
#endif
#endif
  
  // PHENOTYPE
  typedef phen::PhenChasseur<gen_t, fit_t, Params> phen_t;

	// EVALUATION
#ifdef PARALLEL
//  typedef eval::Parallel<Params> eval_t;
	typedef eval::StagHuntEvalParallel<Params> eval_t;
#else
  typedef eval::StagHuntEval<Params> eval_t;
#endif

  // STATS 
  typedef boost::fusion::vector<
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
#ifdef BEHAVIOUR_LOG
		  sferes::stat::BestFitBehaviour<phen_t, Params>,
#endif
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
#endif
#ifdef COUNT_TIME
			sferes::stat::BestFitTime<phen_t, Params>,
#endif
		  sferes::stat::StopEval<Params>
    >  stat_t;
  
  //MODIFIER
  typedef modif::Dummy<Params> modifier_t;

	// EVOLUTION ALGORITHM
#ifdef FITPROP
  typedef ea::FitnessProp<phen_t, eval_t, stat_t, modifier_t, Params> ea_t; 
#elif defined(MULTI)
  typedef ea::Nsga2<phen_t, eval_t, stat_t, modifier_t, Params> ea_t; 
#elif defined(CMAES)
  typedef ea::Cmaes<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#elif defined(ELITIST)
  typedef ea::Elitist<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#else
  typedef ea::RankSimple<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#endif

  ea_t ea;

  // RUN EA
  time_t exec = time(NULL);
  run_ea(argc, argv, ea);
	std::cout << "Temps d'exécution : " << time(NULL) - exec;

  return 0;
}
