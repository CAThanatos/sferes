// THIS IS A GENERATED FILE - DO NOT EDIT
#define EXP
#line 1 "/home/abernard/sferes2-0.99/exp/StagHunt-PartnerSelection/StagHunt.cpp"
#include "includes.hpp"
#include "defparams.hpp"

namespace sferes
{
  using namespace nn;
  
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
      void eval_compet(const std::vector<boost::shared_ptr<Phen> >& pop) 
      // void eval_compet(pop_t& pop) 
    {
      typedef simu::FastsimMulti<Params> simu_t;
      typedef fastsim::Map map_t;

      using namespace fastsim;	
      
      //this->set_mode(fit::mode::eval);
      // this->set_mode(fit::mode::view);

      // *** Main Loop *** 

			// clock_t deb = clock();

    	// init
			map_t map(Params::simu::map_name(), Params::simu::real_w);
			simu_t simu(map, (this->mode() == fit::mode::view));
			init_simu(simu, pop);


#ifdef BEHAVIOUR_LOG
			_file_behaviour = "behaviourTrace";
			cpt_files = 0;
#endif

			nb_cooperate = 0.0f;
			nb_defect = 0.0f;

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

				for(int k = pop.size(); k < simu.robots().size(); ++k)
					check_status(simu, (Prey*)(simu.robots()[k]), dead_preys, k, pop.size());
				
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
     				simu.add_dead_prey(index, alone);
#endif

					dead_preys.pop_back();
					simu.remove_robot(index);

					if(type == Prey::FOOD)
					{
						Posture pos;
	
						if(simu.get_random_initial_position(Params::simu::food_radius, pos))
						{
							Food* r = new Food(Params::simu::food_radius, pos, FOOD_COLOR);							
							simu.add_robot(r);
						}
					}
				}
			} // *** end of step ***

#if defined(BEHAVIOUR_LOG)
 			if(this->mode() == fit::mode::view)
 			{
				std::string fileDump = _file_behaviour + ".bmp";
	 				simu.dump_behaviour_log(fileDump.c_str());
 			}
#endif

 			for(size_t i = 0; i < pop.size(); ++i)
 			{
 				Hunter* hunter = (Hunter*)simu.robots()[i];
 				float mean_cooperation = hunter->nb_cooperate()/(float)Params::simu::nb_trials;
 				pop[i]->add_nb_cooperate(mean_cooperation);

 				float mean_defection = hunter->nb_defect()/(float)Params::simu::nb_trials;
 				pop[i]->add_nb_defect(mean_defection);

 				float mean_food = hunter->get_food_gathered()/(float)Params::simu::nb_trials;
 				pop[i]->fit().add_fitness(mean_food);
 			}
    } // *** end of eval ***

    
    template<typename Simu, typename Phen>
      void init_simu(Simu& simu, const std::vector<boost::shared_ptr<Phen> >& pop)
      // void init_simu(Simu& simu, pop_t& pop)
    {
  		// Preparing the environment
      prepare_env(simu, pop);
      
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
      void prepare_env(Simu& simu, const std::vector<boost::shared_ptr<Phen> >& pop)
      // void prepare_env(Simu& simu, pop_t& pop)
    {
      using namespace fastsim;

      simu.init();
      simu.map()->clear_illuminated_switches();
			
		  // Sizes
	    width=simu.map()->get_real_w();
	    height=simu.map()->get_real_h();

			// Robots :
			// First the robots for the individuals

			for(int i = 0; i < pop.size(); ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::hunter_radius + 5, pos, 1000, false))
				{
						Hunter* r;

					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR, i);
					r->set_weights(pop[i]->data());

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
					}

					simu.add_robot(r);
				}
			}

			// Then the food

			for(int i = 0; i < Params::simu::total_food; ++i)
			{
				Posture pos;

				if(simu.map()->get_random_initial_position(Params::simu::food_radius + 5, pos, 1000, false))
				{
					Food* r = new Food(Params::simu::food_radius, pos, FOOD_COLOR);
		
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
    	void check_status(Simu &simu, Prey* prey, std::vector<int>& dead_preys, int position, int pop_size)
   	{
   		using namespace fastsim;
   		
   		// We compute the distance between this prey and each of its hunters
   		std::vector<Hunter*> hunters;
   		float px = prey->get_pos().x();
   		float py = prey->get_pos().y();
   		
   		for(int i = 0; i < pop_size; ++i)
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
   	
   		// And then we check if the prey is dead and let the hunters
   		// have a glorious feast on its corpse. Yay !
   		if(prey->is_dead())
   		{
   			float food = 0;

   			dead_preys.push_back(position);
   			
   			// We choose the individual responsible for the sharing among the hunters
   			int sharer_index = misc::rand<int>(0, hunters.size());
   			Hunter* sharer = hunters[sharer_index];

#ifdef NO_SHARING
 				for(int i = 0; i < hunters.size(); ++i)
	   			hunters[i]->add_interaction(REWARD_COOP, sharer);
#else
   			bool decision = sharer->decide_sharing();

   			if(decision)
   			{
   				// The hunter has decided to share, everybody gets the lesser reward
   				food = REWARD_COOP;

   				for(int i = 0; i < hunters.size(); ++i)
   				{
   					hunters[i]->add_interaction(food, sharer);

   					if(i == sharer_index)
   						hunters[i]->add_cooperation();
   				}
   			}
   			else
   			{
   				// The hunter keeps it for itself, he gets the bigger reward and the others get nothing
   				food = REWARD_DEFECT;

   				for(int i = 0; i < hunters.size(); ++i)
   					if(i != sharer_index)
   						hunters[i]->add_interaction(0, sharer);
   					else
   					{
   						hunters[i]->add_interaction(food, sharer);
   						hunters[i]->add_defection();
   					}
   			}
#endif
   		}
   	}


		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool reinit;

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
  typedef gen::ElitistGen<Params::evo_float::genome_size, Params> gen_t;
#else
  typedef gen::EvoFloat<Params::evo_float::genome_size, Params> gen_t;
#endif
  
  // PHENOTYPE
  typedef phen::PhenChasseur<gen_t, fit_t, Params> phen_t;

	// EVALUATION
		typedef eval::StagHuntEvalParallelPop<Params> eval_t;

  // STATS 
  typedef boost::fusion::vector<
		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,

#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::AllFitBehaviourVideo<phen_t, Params>,
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
