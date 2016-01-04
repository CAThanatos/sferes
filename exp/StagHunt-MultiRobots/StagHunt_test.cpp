// THIS IS A GENERATED FILE - DO NOT EDIT
#define TEST
#line 1 "/home/abernard/sferes2-0.99/exp/StagHunt-MultiRobots/StagHunt.cpp"
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
      void eval_compet(const std::vector<boost::shared_ptr<Phen> >& vec_ind) 
      // void eval_compet(pop_t& pop) 
    {
      typedef simu::FastsimMulti<Params> simu_t;
      typedef fastsim::Map map_t;

      using namespace fastsim;	
      
      //this->set_mode(fit::mode::eval);
      // this->set_mode(fit::mode::view);

      // *** Main Loop *** 

			// clock_t deb = clock();

      std::vector<float> vec_mean_nb_hares(vec_ind.size(), 0.0f);
      std::vector<float> vec_mean_nb_hares_solo(vec_ind.size(), 0.0f);
      std::vector<float> vec_mean_nb_sstags(vec_ind.size(), 0.0f);
      std::vector<float> vec_mean_nb_sstags_solo(vec_ind.size(), 0.0f);
      std::vector<float> vec_mean_nb_bstags(vec_ind.size(), 0.0f);
      std::vector<float> vec_mean_nb_bstags_solo(vec_ind.size(), 0.0f);

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

				StagHuntRobot* robot1 = (StagHuntRobot*)(simu.robots()[0]);
				StagHuntRobot* robot2 = (StagHuntRobot*)(simu.robots()[1]);
				Hunter* hunter1 = (Hunter*)robot1;
				Hunter* hunter2 = (Hunter*)robot2;

#ifdef DOUBLE_NN
				float max_rand = 0.0f;
				int max_ind = -1;
				for (size_t k = 0; k < vec_ind.size(); ++k)
				{
					float rand_ind = misc::rand(1.0f);

					if(rand_ind >= max_rand)
					{
						max_rand = rand_ind
						max_ind = k;
					}
				}

				assert(max_ind > -1);

				int nb_weights = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;
				for(size_t k = 0; k < vec_ind.size(); ++k)
				{
					StagHuntRobot* robot = (StagHuntRobot*)(simu.robots()[k]);
					Hunter* = (Hunter*)robot;

					if(max_ind == k)
					{
						hunter->set_bool_leader(true);
						hunter->choose_nn(0, vec_ind[k].data())
					}
					else
					{
						hunter->set_bool_leader(false);

						if(vec_ind[max_ind].data().size() == (nb_weights + 1))
						{
							if((vec_ind[k].data().size() == (nb_weights + 1)) || (misc::rand<float>() < 0.5f))
								hunter2->choose_nn(0, vec_ind[k].data());
							else
								hunter2->choose_nn(1, vec_ind[k].data());
						}
						else
						{
							if((vec_ind[k].data().size() == (nb_weights + 1)) && (misc::rand<float>() < 0.5f))
								hunter2->choose_nn(0, vec_ind[k].data());
							else
								hunter2->choose_nn(1, vec_ind[k].data());
						}
					}
				}
#endif

				_nb_leader_first_trial = 0;
				_nb_preys_killed_coop_trial = 0;

				for (size_t i = 0; i < Params::simu::nb_steps && !stop_eval; ++i)
				{
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
						bool alone = (nb_blocked >= Params::simu::nb_hunters_coop) ? false : true;

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
	 				vec_mean_nb_hares[i] += hunter->nb_hares_hunted();
	 				vec_mean_nb_hares_solo[i] += hunter->nb_hares_hunted_solo();
	 				vec_mean_nb_sstags[i] += hunter->nb_small_stags_hunted();
	 				vec_mean_nb_sstags_solo[i] += hunter->nb_small_stags_hunted_solo();
	 				vec_mean_nb_bstags[i] += hunter->nb_big_stags_hunted();
	 				vec_mean_nb_bstags_solo[i] += hunter->nb_big_stags_hunted_solo();

	 				vec_mean_food[i] += hunter->get_food_gathered();
	 			}

	 			_nb_leader_first += _nb_leader_first_trial;
	 			_nb_preys_killed_coop += _nb_preys_killed_coop_trial;

	     	if(_nb_preys_killed_coop_trial > 0)
	       	proportion_leader += fabs((1.0f/Params::simu::nb_hunters_coop) - (_nb_leader_first_trial/_nb_preys_killed_coop_trial));//*(_nb_preys_killed_coop_trial/max_hunts);
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
			_nb_preys_killed_coop /= nb_simulations;
			proportion_leader /= nb_simulations;

			// Mean on all the trials
			for(size_t i = 0; i < vec_ind.size(); ++i)
			{
				vec_ind[i]->add_nb_hares(vec_mean_nb_hares[i]/nb_simulations, vec_mean_nb_hares_solo[i]/nb_simulations);
				vec_ind[i]->add_nb_sstags(vec_mean_nb_sstags[i]/nb_simulations, vec_mean_nb_sstags_solo[i]/nb_simulations);
				vec_ind[i]->add_nb_bstags(vec_mean_nb_bstags[i]/nb_simulations, vec_mean_nb_bstags_solo[i]/nb_simulations);

				vec_ind[i]->add_nb_leader_first(_nb_leader_first);
				vec_ind[i]->add_nb_preys_killed_coop(_nb_preys_killed_coop);
				vec_ind[i]->add_proportion_leader(proportion_leader);

				vec_ind[i]->fit().add_fitness(vec_mean_food[i]/nb_simulations);
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

			bool first_leader = misc::flip_coin();

			// Robots :
			// First the robots for the individuals
			for(int i = 0; i < vec_ind.size(); ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::hunter_radius + 5, pos, 1000, false))
				{
						Hunter* r;

					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR);
					r->set_weights(vec_ind[i]->data());

					bool leader = first_leader == (i == 0);

					if(!r->is_deactivated())
					{	
						// 12 lasers range sensors 
						r->add_laser(Laser(0, 50));
						r->add_laser(Laser(M_PI / 6, 50));
						r->add_laser(Laser(M_PI / 3, 50));
						r->add_laser(Laser(M_PI, 50));
						r->add_laser(Laser(-M_PI / 3, 50));
						r->add_laser(Laser(-M_PI / 6, 50));
			
						// 1 linear camera
						r->use_camera(LinearCamera(M_PI/2, Params::simu::nb_camera_pixels));
						// r->use_camera(LinearCamera(M_PI/3.6, Params::simu::nb_camera_pixels));

						r->set_bool_leader(leader);
					}

					simu.add_robot(r);
				}
			}
					
			// Then the hares std::vector<Posture> vec_pos;
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

				bool alone;
				if(prey->get_nb_blocked() < Params::simu::nb_hunters_coop)
					alone = true;
				else
					alone = false;

				_nb_preys_killed++;

				if(!alone)
				{
					_nb_preys_killed_coop_trial++;

					if(prey->get_leader_first() == 1)
						_nb_leader_first_trial++;
				}

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
		bool reinit;

		float _nb_leader_first;
		float _nb_preys_killed;
		float _nb_preys_killed_coop;

		float _nb_leader_first_trial;
		float _nb_preys_killed_coop_trial;

		std::string res_dir;
		size_t gen;

		float nb_cooperate, nb_defect;
		
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
		typedef eval::StagHuntEvalParallel<Params> eval_t;

  // STATS 
  typedef boost::fusion::vector<
		  sferes::stat::BestFitEval<phen_t, Params>,
		  // sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
		  sferes::stat::BestLeadershipEval<phen_t, Params>,

#ifndef POP100
		  sferes::stat::AllLeadershipEvalStat<phen_t, Params>,
#ifdef GENOME_TRACES
		  sferes::stat::AllGenomesTraceStat<phen_t, Params>,
#endif
#endif
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
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
