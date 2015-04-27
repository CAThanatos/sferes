// THIS IS A GENERATED FILE - DO NOT EDIT
#define CONTROL1
#line 1 "/home/arthur/sferes2-0.99/exp/StagHunt-Invasion/StagHunt.cpp"
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

#ifndef MLP_PERSO
      nn1.set_all_weights(ind1.data());
      nn2.set_all_weights(ind2.data());

      nn1.init();
      nn2.init();
#endif

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

			// clock_t deb = clock();

#ifdef DIVERSITY
			std::vector<float> vec_sm;
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
				hunter1->set_weights(ind1.data());
				hunter2->set_weights(ind2.data());
#endif
	
				float food_trial = 0;

#ifdef DIVERSITY
				std::vector<float> vec_sm_trial;
#endif

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

#ifdef DIVERSITY
							if (0 == num)
								for(size_t l = 0; l < action.size(); ++l)
									vec_sm_trial.push_back(action[l]);
#endif
						}
					}

#ifdef DIVERSITY
					std::vector<float>& vec_inputs_rob = ((Hunter*)(simu.robots()[0]))->get_last_inputs();

					for (size_t l = 0; l < vec_inputs_rob.size(); ++l)
						vec_sm_trial.push_back(vec_inputs_rob[l]);
#endif

					update_simu(simu);

					// And then we update their status : food gathered, prey dead
					// For each prey, we check if there are hunters close
					std::vector<int> dead_preys;

					for(int k = 2; k < simu.robots().size(); ++k)
						check_status(simu, (Prey*)(simu.robots()[k]), dead_preys, k);
					
					// We remove the dead preys
					while(!dead_preys.empty())
					{
						int index = dead_preys.back();
	
						Prey::type_prey type = ((Prey*)simu.robots()[index])->get_type();
						Posture pos;

						int nb_blocked = ((Prey*)simu.robots()[index])->get_nb_blocked();
						bool alone = (nb_blocked > 1) ? false : true;

#ifdef BEHAVIOUR_LOG
   					// Is the first robot the first one on the target ?
   					bool first_robot = (((Prey*)simu.robots()[index])->get_leader_first() == 1) == (((Hunter*)simu.robots()[0])->is_leader());

						if(this->mode() == fit::mode::view)
						{
							// std::string fileDump = _file_behaviour + boost::lexical_cast<std::string>(cpt_files + 1) + ".bmp";
       				simu.add_dead_prey(index, alone, first_robot);
       				// cpt_files++;
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
					}
				}

				// clock_t fin = clock();
				// std::cout << "HE : " << (fin - deb)/(double) CLOCKS_PER_SEC << std::endl;

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

#ifdef DIVERSITY
	      for (size_t l = 0; l < vec_sm_trial.size(); ++l)
	      	vec_sm.push_back(vec_sm_trial[l]);
#endif


#if defined(BEHAVIOUR_LOG)
	 			if(this->mode() == fit::mode::view)
	 			{
					std::string fileDump = _file_behaviour + ".bmp";
 	 				simu.dump_behaviour_log(fileDump.c_str());
	 			}
#endif


#if defined(BEHAVIOUR_VIDEO)
				if(this->mode() == fit::mode::view)
				{
					return;
				}
#endif
			}
			
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
		
			ind1.set_payoff(ind2.pop_pos(), food1);
			ind2.set_payoff(ind1.pop_pos(), food2);
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
	typedef gen::EvoFloat<Params::nn::genome_size, Params> gen_t;
  
  // PHENOTYPE
  typedef phen::PhenInvasion<gen_t, fit_t, Params> phen_t;

	// EVALUATION
	typedef eval::EvalInvasion<Params> eval_t;

  // STATS 
  typedef boost::fusion::vector<
#ifdef COEVO
		  sferes::stat::BestFitEvalCoEvo<phen_t, Params>,
		  sferes::stat::AllFitEvalStatCoEvo<phen_t, Params>,
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideoCoEvo<phen_t, Params>,
#endif
#else
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
#endif
#endif
#ifdef DIVERSITY
		  sferes::stat::BestDiversityEval<phen_t, Params>,
		  sferes::stat::AllDiversityEvalStat<phen_t, Params>,
#endif
		  sferes::stat::StopEval<Params>
    >  stat_t;
  
  //MODIFIER
  typedef modif::Dummy<Params> modifier_t;

	// EVOLUTION ALGORITHM
	typedef ea::InvasionEa<phen_t, eval_t, stat_t, modifier_t, Params> ea_t;

  ea_t ea;

  // RUN EA
  time_t exec = time(NULL);
  run_ea(argc, argv, ea);
	std::cout << "Temps d'exécution : " << time(NULL) - exec;

  return 0;
}
