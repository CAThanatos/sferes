#include "includes.hpp"
#include "defparams.hpp"

namespace sferes
{
  // ********** Main Class ***********
  SFERES_FITNESS(FitStagHunt, sferes::fit::Fitness)
  {
  public:
    // typedef std::vector<boost::shared_ptr<Indiv> > pop_t;

    template<typename Indiv>
      void eval(Indiv& ind) 
		{
			std::cout << "Nop !" << std::endl;
		}

    template<typename Phen>
      void eval_compet(const std::vector<boost::shared_ptr<Phen> >& vec_ind, const std::vector<bool> is_evaluated) 
      // void eval_compet(pop_t& pop) 
    {
      typedef simu::FastsimMulti<Params> simu_t;
      typedef fastsim::Map map_t;

      using namespace fastsim;	
      
      //this->set_mode(fit::mode::eval);
      // this->set_mode(fit::mode::view);

      // *** Main Loop *** 

			// clock_t deb = clock();

      std::vector<std::vector<float> > vec_mean_nb_hares(vec_ind.size());
      std::vector<std::vector<float> > vec_mean_nb_sstags(vec_ind.size());
      std::vector<std::vector<float> > vec_mean_nb_bstags(vec_ind.size());

      for(size_t i = 0; i < vec_ind.size(); ++i)
      {
      	for(size_t j = 0; j < Params::simu::nb_hunters; ++j)
      	{
      		vec_mean_nb_hares[i].push_back(0.0f);
      		vec_mean_nb_sstags[i].push_back(0.0f);
      		vec_mean_nb_bstags[i].push_back(0.0f);
      	}
      }

      std::vector<float> vec_mean_food(vec_ind.size(), 0.0f);

      _nb_leader_first = 0.0f;
      _nb_preys_killed = 0.0f;
      _nb_preys_killed_coop = 0.0f;
      float proportion_leader = 0.0f;

      for (size_t j = 0; j < Params::simu::nb_trials; ++j)
      {
	    	// init
				map_t map(Params::simu::map_name(), Params::simu::real_w);
				simu_t simu(map, (this->mode() == fit::mode::view));
				init_simu(simu, vec_ind);


#ifdef BEHAVIOUR_LOG
				_file_behaviour = "behaviourTrace";
				cpt_files = 0;
#endif

				float max_rand = 0.0f;
				int max_ind = -1;
				for (size_t k = 0; k < vec_ind.size(); ++k)
				{
					float rand_ind = misc::rand(1.0f);

					if(rand_ind >= max_rand)
					{
						max_rand = rand_ind;
						max_ind = k;
					}
				}

				assert(max_ind > -1);
				_num_leader = max_ind;

#ifdef DOUBLE_NN
#ifdef COM_NN
				for(size_t k = 0; k < vec_ind.size(); ++k)
				{
					StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[k]);
					Hunter* hunter = (Hunter*)robot;
					hunter->choose_nn(0, vec_ind[k]->data());

					if(k == max_ind)
						hunter->set_bool_leader(true);
					else
						hunter->set_bool_leader(false);

					_num_compas = -1;
				}
#elif defined(NO_CHOICE_DUP)
				int nb_weights = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;

				// First the leader choose its neural network
				StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[max_ind]);
				Hunter* hunter = (Hunter*)robot;
				hunter->set_bool_leader(true);

				int choice_leader = 0;
				if((vec_ind[max_ind]->data().size() == nb_weights) || (misc::rand<float>() < 0.5f))
					hunter->choose_nn(0, vec_ind[max_ind]->data());
				else
				{
					hunter->choose_nn(1, vec_ind[max_ind]->data());
					choice_leader = 1;
				}

				for(size_t k = 0; k < vec_ind.size(); ++k)
				{
					StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[k]);
					Hunter* hunter = (Hunter*)robot;

					if(max_ind != k)
					{
						hunter->set_bool_leader(false);

						if(vec_ind[k]->data().size() == nb_weights)
							hunter->choose_nn(0, vec_ind[k]->data());
						else
						{
							if(vec_ind[max_ind]->data().size() == nb_weights)
							{
								if(misc::rand<float>() < 0.5f)
									hunter->choose_nn(0, vec_ind[k]->data());
								else
									hunter->choose_nn(1, vec_ind[k]->data());
							}
							else
								hunter->choose_nn(1 - choice_leader, vec_ind[k]->data());
						}
					}
				}
#else
				int nb_weights = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;

				for(size_t k = 0; k < vec_ind.size(); ++k)
				{
					StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[k]);
					Hunter* hunter = (Hunter*)robot;

					if(max_ind == k)
					{
						hunter->set_bool_leader(true);
						hunter->choose_nn(0, vec_ind[k]->data());
					}
					else
					{
						hunter->set_bool_leader(false);

						if(vec_ind[max_ind]->data().size() == nb_weights)
						{
							if((vec_ind[k]->data().size() == nb_weights) || (misc::rand<float>() < 0.5f))
								hunter->choose_nn(0, vec_ind[k]->data());
							else
								hunter->choose_nn(1, vec_ind[k]->data());
						}
						else
						{
							if((vec_ind[k]->data().size() == nb_weights) && (misc::rand<float>() < 0.5f))
								hunter->choose_nn(0, vec_ind[k]->data());
							else
								hunter->choose_nn(1, vec_ind[k]->data());
						}
					}
				}
#endif
#else
				for(size_t k = 0; k < vec_ind.size(); ++k)
				{
					StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[k]);
					Hunter* hunter = (Hunter*)robot;
					hunter->set_weights(vec_ind[k]->data());

					if(k == max_ind)
						hunter->set_bool_leader(true);
					else
						hunter->set_bool_leader(false);
				}
#endif

				_nb_leader_first_trial = 0;
				_nb_preys_killed_coop_leader_trial = 0;

				for (size_t i = 0; i < Params::simu::nb_steps && !stop_eval; ++i)
				{
#if defined(COM_COMPAS)
#ifdef COM_NN
					if(_num_compas > -1)
					{
						assert(_num_compas < vec_ind.size());

						StagHuntRobot *robLeader = (StagHuntRobot*)(simu.robots()[_num_compas]);
						Hunter* hunterLeader = (Hunter*)robLeader;

						for(size_t k = 0; k < vec_ind.size(); ++k)
						{
							if(_num_compas == k)
							{
								hunterLeader->set_distance_hunter(0.0f);
								hunterLeader->set_angle_hunter(0.0f);
							}
							else
							{
								StagHuntRobot *robFollower = (StagHuntRobot*)(simu.robots()[k]);
								Hunter* hunterFollower = (Hunter*)robFollower;

								float distance = robLeader->get_pos().dist_to(robFollower->get_pos().x(), robFollower->get_pos().y());
								distance = distance - robLeader->get_radius() - robFollower->get_radius();
								hunterFollower->set_distance_hunter(distance);

								float angle = normalize_angle(atan2(robLeader->get_pos().y() - robFollower->get_pos().y(), robLeader->get_pos().x() - robFollower->get_pos().x()));
								angle = normalize_angle(angle - robFollower->get_pos().theta());
								hunterFollower->set_angle_hunter(angle);
							}
						}
					}
					else
					{
						for(size_t k = 0; k < vec_ind.size(); ++k)
						{
							StagHuntRobot *robot = (StagHuntRobot*)(simu.robots()[k]);
							Hunter* hunter = (Hunter*)robot;

							hunter->set_distance_hunter(0.0f);
							hunter->set_angle_hunter(0.0f);
						}
					}
#else
					StagHuntRobot *robLeader = (StagHuntRobot*)(simu.robots()[_num_leader]);
					Hunter* hunterLeader = (Hunter*)robLeader;

					for(size_t k = 0; k < vec_ind.size(); ++k)
					{
						if(_num_leader == k)
						{
							hunterLeader->set_distance_hunter(0.0f);
							hunterLeader->set_angle_hunter(0.0f);
						}
						else
						{
							StagHuntRobot *robFollower = (StagHuntRobot*)(simu.robots()[k]);
							Hunter* hunterFollower = (Hunter*)robFollower;

							float distance = robLeader->get_pos().dist_to(robFollower->get_pos().x(), robFollower->get_pos().y());
							distance = distance - robLeader->get_radius() - robFollower->get_radius();
							hunterFollower->set_distance_hunter(distance);

							float angle = normalize_angle(atan2(robLeader->get_pos().y() - robFollower->get_pos().y(), robLeader->get_pos().x() - robFollower->get_pos().x()));
							angle = normalize_angle(angle - robFollower->get_pos().theta());
							hunterFollower->set_angle_hunter(angle);
						}
					}
#endif
#endif

					// Number of steps the robots are evaluated
					_nb_eval = i + 1;

					// We compute the robots' actions in an ever-changing order
					std::vector<size_t> ord_vect;
					misc::rand_ind(ord_vect, simu.robots().size());

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
						}
					}


					update_simu(simu);

					std::vector<int> dead_preys;

					for(int k = vec_ind.size(); k < simu.robots().size(); ++k)
						check_status(simu, (Prey*)(simu.robots()[k]), dead_preys, k, vec_ind.size());
					
					// We remove the dead preys
					while(!dead_preys.empty())
					{
						int index = dead_preys.back();

						Prey::type_prey type = ((Prey*)simu.robots()[index])->get_type();
						Posture pos;

						int nb_blocked = ((Prey*)simu.robots()[index])->get_nb_blocked();

// #ifdef BEHAVIOUR_LOG
//  					// Is the first robot the first one on the target ?
//  					bool first_robot = (((Prey*)simu.robots()[index])->get_leader_first() == 1) == (((Hunter*)simu.robots()[0])->is_leader());

// 					if(this->mode() == fit::mode::view)
// 					{
// 						// std::string fileDump = _file_behaviour + boost::lexical_cast<std::string>(cpt_files + 1) + ".bmp";
//      				simu.add_dead_prey(index, alone, first_robot);
//      				// cpt_files++;
// 					}
// #endif

						dead_preys.pop_back();
						simu.remove_robot(index);

						if(type == Prey::HARE)
						{
							Posture pos;
		
							if(simu.get_random_initial_position(Params::simu::hare_radius, pos))
							{
								Hare* r = new Hare(Params::simu::hare_radius, pos, HARE_COLOR);
								
								simu.add_robot(r);
							}
						}
						else if(type == Prey::SMALL_STAG)
						{
							Posture pos;

							if(simu.get_random_initial_position(Params::simu::big_stag_radius, pos))
							{
								int fur_color = 0;

								Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);
									
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
									
								simu.add_robot(r);
							}
						}
					} // *** end of dead_preys while look ***
				} // *** end of step ***



#if defined(BEHAVIOUR_LOG)
	 			if(this->mode() == fit::mode::view)
	 			{
					std::string fileDump = _file_behaviour + ".bmp";
		 				simu.dump_behaviour_log(fileDump.c_str());
	 			}
#endif

	 			for(size_t i = 0; i < vec_ind.size(); ++i)
	 			{
	 				Hunter* hunter = (Hunter*)simu.robots()[i];

	 				for(size_t k = 0; k < Params::simu::nb_hunters; ++k)
	 				{
	 					vec_mean_nb_hares[i][k] += hunter->nb_hares_hunted()[k];
	 					vec_mean_nb_sstags[i][k] += hunter->nb_small_stags_hunted()[k];
	 					vec_mean_nb_bstags[i][k] += hunter->nb_big_stags_hunted()[k];
	 				}

	 				vec_mean_food[i] += hunter->get_food_gathered();
	 			}

	 			_nb_leader_first += _nb_leader_first_trial;
	 			_nb_preys_killed_coop_leader += _nb_preys_killed_coop_leader_trial;

	     	if(_nb_preys_killed_coop_leader_trial > 0)
	       	proportion_leader += fabs(1.0f - (_nb_leader_first_trial/_nb_preys_killed_coop_leader_trial));//*(_nb_preys_killed_coop_leader_trial/max_hunts);

	    } // *** end of trial ***
		
#ifdef NOT_AGAINST_ALL	
			int nb_encounters = Params::pop::nb_opponents*Params::pop::nb_eval;
#elif defined(ALTRUISM)
			int nb_encounters = 1;
#else
			int nb_encounters = Params::pop::size - 1;
#endif

			float nb_simulations = nb_encounters * Params::simu::nb_trials;
			_nb_leader_first /= nb_simulations;
			_nb_preys_killed_coop_leader /= nb_simulations;
			proportion_leader /= nb_simulations;

			for(size_t i = 0; i < vec_ind.size(); ++i)
			{
				if(is_evaluated[i])
				{
					for(size_t j = 0; j < Params::simu::nb_hunters; ++j)
					{
						vec_ind[i]->add_nb_hares(vec_mean_nb_hares[i][j]/nb_simulations, j);
						vec_ind[i]->add_nb_sstags(vec_mean_nb_sstags[i][j]/nb_simulations, j);
						vec_ind[i]->add_nb_bstags(vec_mean_nb_bstags[i][j]/nb_simulations, j);
					}

					vec_ind[i]->add_nb_leader_first(_nb_leader_first);
					vec_ind[i]->add_nb_preys_killed_coop(_nb_preys_killed_coop_leader);
					vec_ind[i]->add_proportion_leader(proportion_leader);

					vec_ind[i]->fit().add_fitness(vec_mean_food[i]/nb_simulations);
				}
			}
    } // *** end of eval ***

    
    template<typename Simu, typename Phen>
      void init_simu(Simu& simu, const std::vector<boost::shared_ptr<Phen> >& vec_ind)
      // void init_simu(Simu& simu, pop_t& pop)
    {
  		// Preparing the environment
      prepare_env(simu, vec_ind);
      
      // Visualisation mode
			if(this->mode() == fit::mode::view)
			{
			  simu.init_view(true);
				
#if defined(BEHAVIOUR_VIDEO)
				simu.set_file_video(_file_video);
#endif
			}
      
      stop_eval = false;
      reinit = false;
    }

    // Prepare environment
    template<typename Simu, typename Phen>
      void prepare_env(Simu& simu, const std::vector<boost::shared_ptr<Phen> >& vec_ind)
      // void prepare_env(Simu& simu, pop_t& pop)
    {
      using namespace fastsim;

      simu.init();
      simu.map()->clear_illuminated_switches();
			
		  // Sizes
	    width=simu.map()->get_real_w();
	    height=simu.map()->get_real_h();

#ifdef POS_CLOSE
	    std::vector<Posture> vec_pos_init;

	    for(int i = 0; i < vec_ind.size(); ++i)
	    {
	    	int signe = 1;
	    	if((i % 2) == 0)
	    		signe = -1;

				vec_pos_init.push_back(Posture(width/2 + (40 * signe) + (80 * signe * i), 80, M_PI/2));
	    }
#endif


			bool first_leader = misc::flip_coin();

			// Robots :
			// First the robots for the individuals
			for(int i = 0; i < vec_ind.size(); ++i)
			{
				Posture pos;

#ifdef POS_CLOSE
				pos = vec_pos_init[i];

				if(true)
#else
				if(simu.map()->get_random_initial_position(Params::simu::hunter_radius + 5, pos, 1000, false))
#endif
				{
						Hunter* r;

					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR);
					// r->set_weights(vec_ind[i]->data());

					bool leader = first_leader == (i == 0);

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
						// r->use_camera(LinearCamera(M_PI/3.6, Params::simu::nb_camera_pixels));

						// r->set_bool_leader(leader);
					}

					simu.add_robot(r);
				}
			}
					
			// Then the hares
			int nb_big_stags = Params::simu::ratio_big_stags*Params::simu::nb_big_stags;
			int nb_small_stags = Params::simu::nb_big_stags - nb_big_stags;

			for(int i = 0; i < Params::simu::nb_hares; ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::big_stag_radius + 5, pos, 1000, false))
				{
					Hare* r = new Hare(Params::simu::hare_radius, pos, HARE_COLOR);
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

				if(simu.map()->get_random_initial_position(Params::simu::big_stag_radius + 5, pos, 1000, false))
				{
					Stag* r = new Stag(Params::simu::big_stag_radius, pos, BIG_STAG_COLOR, Stag::big, fur_color);
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
    	void check_status(Simu &simu, Prey* prey, std::vector<int>& dead_preys, int position, int vec_ind_size)
   	{
   		using namespace fastsim;
   		
   		// We compute the distance between this prey and each of its hunters
   		std::vector<Hunter*> hunters;
   		float px = prey->get_pos().x();
   		float py = prey->get_pos().y();
   		
   		for(int i = 0; i < vec_ind_size; ++i)
   		{
   			Hunter* hunter = (Hunter*)(simu.robots()[i]);
   			float hx = hunter->get_pos().x();
   			float hy = hunter->get_pos().y();
   			float dist = sqrt(pow(px - hx, 2) + pow(py - hy, 2));
   			
   			// The radius must not be taken into account
   			if((dist - prey->get_radius() - hunter->get_radius()) <= CATCHING_DISTANCE)
   				hunters.push_back(hunter);
   		}

   		prey->blocked_by_hunters(hunters.size());

   		if(hunters.size() == 1)
   		{
#ifdef COM_NN
   			// If the individual got first on the prey, we change the nn of the other one
   			for(int i = 0; i < vec_ind_size; ++i)
   			{
	   			Hunter* hunter = (Hunter*)(simu.robots()[i]);

	   			if(hunter != hunters[0])
	   			{
	   				if(hunter->nn1_chosen())
	   					hunter->change_nn(1);
	   			}
	   			else
	   				_num_compas = i;
   			}
#endif

   			if(prey->get_leader_first() == -1)
   			{
	   			if(hunters[0]->is_leader())
	   				prey->set_leader_first(1);
	   			else
	   				prey->set_leader_first(0);
	   		}
   		}

   		// And then we check if the prey is dead and let the hunters
   		// have a glorious feast on its corpse. Yay !
   		if(prey->is_dead())
   		{
   			float food = 0;
   			
	   		food = prey->feast();
	   		
   			Prey::type_prey type = prey->get_type();
   			dead_preys.push_back(position);

				bool alone = (prey->get_nb_blocked() > 1) ? false : true;

				_nb_preys_killed++;
				bool leader_kill = false;

   			for(int i = 0; i < hunters.size(); ++i)
   			{
   				hunters[i]->add_food(food);

   				if(type == Prey::HARE)
   					hunters[i]->eat_hare(prey->get_nb_blocked());
   				else if(type == Prey::SMALL_STAG)
   					hunters[i]->eat_small_stag(prey->get_nb_blocked());
   				else
   					hunters[i]->eat_big_stag(prey->get_nb_blocked());

   				if(hunters[i]->is_leader())
   					leader_kill = true;
   			}

				if(!alone && leader_kill)
				{
					_nb_preys_killed_coop_leader_trial++;

					if(prey->get_leader_first() == 1)
						_nb_leader_first_trial++;
				}

#ifdef COM_NN
   			for(int i = 0; i < vec_ind_size; ++i)
	   			((Hunter*)(simu.robots()[i]))->change_nn(0);
	   		_num_compas = -1;
#endif
   		}
   	}


		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool reinit;

		int _num_leader;

		float _nb_leader_first;
		float _nb_preys_killed;
		float _nb_preys_killed_coop;
		float _nb_preys_killed_coop_leader;

		float _nb_leader_first_trial;
		float _nb_preys_killed_coop_leader_trial;

		std::string res_dir;
		size_t gen;

		float nb_cooperate, nb_defect;

#ifdef COM_NN
		int _num_compas;
#endif
		
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
#ifdef ELITIST
  typedef gen::ElitistGen<Params::nn::genome_size, Params> gen_t;
#else
  typedef gen::EvoFloat<Params::nn::genome_size, Params> gen_t;
#endif
  
  // PHENOTYPE
  typedef phen::PhenChasseur<gen_t, fit_t, Params> phen_t;

	// EVALUATION
#ifdef PAIRING
	typedef eval::StagHuntEvalParallelPairing<Params> eval_t;
#else
	typedef eval::StagHuntEvalParallel<Params> eval_t;
#endif

  // STATS 
  typedef boost::fusion::vector<
		  sferes::stat::BestFitEval<phen_t, Params>,
		  // sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
		  sferes::stat::BestLeadershipEval<phen_t, Params>,

// #ifdef PAIRING
// 		  sferes::stat::BestFitEvalPairing<phen_t, Params>,
// 		  sferes::stat::AllFitEvalStatPairing<phen_t, Params>,
// #endif

#ifndef POP100
		  sferes::stat::AllLeadershipEvalStat<phen_t, Params>,
#ifdef GENOME_TRACES
		  sferes::stat::AllGenomesTraceStat<phen_t, Params>,
#endif
#endif
#ifdef BEHAVIOUR_VIDEO
// #ifdef PAIRING
// 		  sferes::stat::BestFitBehaviourVideoPairing<phen_t, Params>,
// #else
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
// #endif
#endif
		  sferes::stat::StopEval<Params>
    >  stat_t;
  
  //MODIFIER
  typedef modif::Dummy<Params> modifier_t;


	// EVOLUTION ALGORITHM
#ifdef FITPROP
  typedef ea::FitnessProp<phen_t, eval_t, stat_t, modifier_t, Params> ea_t; 
#elif defined(CMAES)
  typedef ea::Cmaes<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#elif defined(ELITIST)
#ifdef PAIRING
  typedef ea::ElitistPairing<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#else
  typedef ea::Elitist<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
#endif
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
