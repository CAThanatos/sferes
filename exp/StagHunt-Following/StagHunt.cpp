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

#ifdef COEVO
    template<typename Indiv>
      void eval_compet(Indiv& ind1, Indiv& ind2, int num_leader = 1) 
#else
    template<typename Indiv>
      void eval_compet(Indiv& ind1, Indiv& ind2) 
#endif
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
      float similarity = 0.0f;

#ifdef COEVO
     	_num_leader = num_leader;
#endif

     	_nb_leader_first = 0;
     	_nb_waypoints_coop = 0;
			float proportion_leader = 0.0f;

			// clock_t deb = clock();
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

	     	_nb_leader_first_trial = 0;
	     	_nb_waypoints_coop_trial = 0;

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

					// We check if each individual crossed a waypoint
					check_status(simu);
				}

				// clock_t fin = clock();
				// std::cout << "HE : " << (fin - deb)/(double) CLOCKS_PER_SEC << std::endl;

				// We check that they crossed the waypoints in the same order
	 			Hunter* hunter1 = (Hunter*)(simu.robots()[0]);
	 			Hunter* hunter2 = (Hunter*)(simu.robots()[1]);
	 			int longest_sequence = 0, current_sequence = 0;
	 			int k = 0, l = 0;

#ifdef NO_COORD
	 			similarity += hunter1->get_waypoints_order().size()/(float)Params::simu::nb_waypoints;
#else
	 			while(k < hunter1->get_waypoints_order().size())
	 			{
	 				if(l >= hunter2->get_waypoints_order().size())
	 					break;

	 				if(hunter2->get_waypoints_order()[l] != hunter1->get_waypoints_order()[k])
	 				{
	 					l++;
	 					current_sequence = 0;
	 				}
	 				else
	 				{
	 					k++;
	 					l++;

	 					current_sequence++;
	 					if(current_sequence > longest_sequence)
	 						longest_sequence = current_sequence;
	 				}
	 			}

	 			// Their fitness is the longest sequence they did divided by the longest sequence they could do
	 			similarity += longest_sequence/(float)Params::simu::nb_waypoints;
#endif

	 			if(_nb_waypoints_coop_trial > 0)
		 			proportion_leader += fabs(0.5 - (_nb_leader_first_trial/_nb_waypoints_coop_trial))*((float)_nb_waypoints_coop_trial/(float)Params::simu::nb_waypoints);

	 			_nb_leader_first += _nb_leader_first_trial;
	 			_nb_waypoints_coop += _nb_waypoints_coop_trial;


#if defined(BEHAVIOUR_VIDEO)
				if(this->mode() == fit::mode::view)
					return;
#endif
			}

			similarity /= Params::simu::nb_trials;

			_nb_leader_first /= Params::simu::nb_trials;
			_nb_waypoints_coop /= Params::simu::nb_trials;
			proportion_leader /= Params::simu::nb_trials;

		
#ifdef NOT_AGAINST_ALL	
			int nb_encounters = Params::pop::nb_opponents*Params::pop::nb_eval;
#elif defined(ALTRUISM)
			int nb_encounters = 1;
#else
			int nb_encounters = Params::pop::size - 1;
#endif

			similarity /= nb_encounters;

			_nb_leader_first /= nb_encounters;
			_nb_waypoints_coop /= nb_encounters;
			proportion_leader /= nb_encounters;
			proportion_leader /= 0.5f;


			ind1.fit().add_fitness(similarity);

			ind1.add_nb_leader_first(_nb_leader_first);
			ind1.add_nb_waypoints_coop(_nb_waypoints_coop);
			ind1.add_proportion_leader(proportion_leader);
			
#if !defined(NOT_AGAINST_ALL) && !defined(ALTRUISM)
			ind2.fit().add_fitness(similarity);
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
				
#if defined(BEHAVIOUR_VIDEO)
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
#elif defined(POS_CENTER)
			pos_init.push_back(Posture(width/2, height/2 - 80, M_PI/2));
			pos_init.push_back(Posture(width/2, height/2 + 80, -M_PI/2));
#else
			pos_init.push_back(Posture(width/2, 80, M_PI/2));
			pos_init.push_back(Posture(width/2, height - 80, -M_PI/2));
#endif

			invers_pos = false;
			
#ifdef COEVO
			bool first_leader = (_num_leader == 1);
#else
			bool first_leader = misc::flip_coin();
			_num_leader = first_leader?1:2;
#endif

			for(int i = 0; i < 2; ++i)
			{
				Hunter* r;				
				Posture pos = (invers_pos) ? pos_init[(i + 1)%2] : pos_init[i];

				// Simple NXOR : if first hunter is supposed to be leader and this is
				// the first hunter we're creating -> true
				//							 if first hunter isn't supposed to be leader and this is
				// not the first hunter we're creating -> true
				// 							 else -> false
				bool leader = first_leader == (i == 0);
		
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
					r->set_bool_leader(leader);
				}
		
				simu.add_robot(r);
			}
					
			// Then the waypoints
			_vec_waypoints.clear();
			for(int i = 0; i < Params::simu::nb_waypoints; ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::waypoint_radius + 5, pos, 0.0f, (float)width, 100.0f, (float)height))
				{
					boost::shared_ptr<Waypoint> w = boost::shared_ptr<Waypoint>(new Waypoint(SMALL_STAG_COLOR, Params::simu::waypoint_radius, pos.x(), pos.y(), i));
					simu.add_illuminated_switch(w);
					_vec_waypoints.push_back(w);
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
	   	void check_status(Simu &simu)
   	{
   		using namespace fastsim;
   		
   		// We compute the distance between this waypoint and each of the hunters
   		std::vector<Hunter*> hunters;

   		for(int i = 0; i < _vec_waypoints.size(); ++i)
   		{
   			float wx = _vec_waypoints[i]->get_x();
   			float wy = _vec_waypoints[i]->get_y();
   			int id = _vec_waypoints[i]->get_id();

   			for(int j = 0; j < simu.robots().size(); ++j)
   			{
	   			Hunter* hunter = (Hunter*)(simu.robots()[j]);

	   			if(!hunter->get_waypoints()[id])
	   			{
		   			float hx = hunter->get_pos().x();
		   			float hy = hunter->get_pos().y();
		   			float dist = sqrt(pow(wx - hx, 2) + pow(wy - hy, 2));
		   			
		   			if(dist < _vec_waypoints[i]->get_radius())
		   			{
		   				hunter->add_waypoint(id);

		   				// First time this waypoint is crossed by any hunter
		   				if(_vec_waypoints[i]->get_leader_first() == -1)
		   				{
		   					if(hunter->is_leader())
		   						_vec_waypoints[i]->set_leader_first(1);
		   					else
		   						_vec_waypoints[i]->set_leader_first(0);
		   				}
		   				else
		   				{
		   					// This waypoint has already been crossed by another hunter
		   					_nb_waypoints_coop_trial++;

		   					if(_vec_waypoints[i]->get_leader_first() == 1)
		   						_nb_leader_first_trial++;
		   				}
		   			}
	   			}
   			}
   		}

   		// If the two hunters have crossed all the waypoints, we stop the trial
 			Hunter* hunter1 = (Hunter*)(simu.robots()[0]);
 			Hunter* hunter2 = (Hunter*)(simu.robots()[1]);

 			if((hunter1->get_nb_waypoints_done() == Params::simu::nb_waypoints) && (hunter2->get_nb_waypoints_done() == Params::simu::nb_waypoints))
 				stop_eval = true;
   	}
   	    
		
		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool invers_pos;
		bool reinit;
		int nb_invers_pos, nb_spawn;

		std::vector<boost::shared_ptr<Waypoint> > _vec_waypoints;

		int _num_leader;

		float _nb_leader_first_trial;
		float _nb_waypoints_coop_trial;

		float _nb_leader_first;
		float _nb_waypoints_coop;

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
  typedef phen::PhenTraveler<gen_t, fit_t, Params> phen_t;

	// EVALUATION
	#ifdef COEVO
		typedef eval::StagHuntEvalParallelCoEvo<Params> eval_t;
	#else
		typedef eval::StagHuntEvalParallel<Params> eval_t;
	#endif

  // STATS 
  typedef boost::fusion::vector<
#ifdef COEVO
		  sferes::stat::BestFitEvalCoEvo<phen_t, Params>,
		  sferes::stat::MeanFitEvalCoEvo<phen_t, Params>,
		  sferes::stat::BestEverFitEvalCoEvo<phen_t, Params>,
		  sferes::stat::AllFitEvalStatCoEvo<phen_t, Params>,
		  sferes::stat::BestLeadershipEvalCoEvo<phen_t, Params>,
		  sferes::stat::AllLeadershipEvalStatCoEvo<phen_t, Params>,
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideoCoEvo<phen_t, Params>,
#endif
#else
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
		  sferes::stat::BestLeadershipEval<phen_t, Params>,
		  sferes::stat::AllLeadershipEvalStat<phen_t, Params>,
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
#endif
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
#ifdef COEVO
  typedef ea::ElitistCoEvo<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;
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
