// THIS IS A GENERATED FILE - DO NOT EDIT
#define SETTING13
#define ELITIST
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

			clock_t deb = clock();
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
			} // *** end of step ***
			clock_t fin = clock();
			std::cout << "HE : " << (fin - deb)/(double) CLOCKS_PER_SEC << std::endl;

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

				if(simu.map()->get_random_initial_position(Params::simu::big_stag_radius + 5, pos, 1000, false))
				{
						Hunter* r;

					r = new Hunter(Params::simu::hunter_radius, pos, HUNTER_COLOR);
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
						// r->use_camera(LinearCamera(M_PI/2, Params::simu::nb_camera_pixels));
						r->use_camera(LinearCamera(M_PI/3.6, Params::simu::nb_camera_pixels));
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
  	    
		float width, height;
		bool stop_eval;                                  // Stops the evaluation
		int _nb_eval;                                    // Number of evaluation (until the robot stands still)
		bool reinit;

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
		typedef eval::StagHuntEvalParallelPop<Params> eval_t;

  // STATS 
  typedef boost::fusion::vector<
/*		  sferes::stat::BestFitEval<phen_t, Params>,
		  sferes::stat::MeanFitEval<phen_t, Params>,
		  sferes::stat::BestEverFitEval<phen_t, Params>,
		  sferes::stat::AllFitEvalStat<phen_t, Params>,
		  sferes::stat::BestLeadershipEval<phen_t, Params>,
		  sferes::stat::AllLeadershipEvalStat<phen_t, Params>,

#ifdef BEHAVIOUR_VIDEO
		  sferes::stat::BestFitBehaviourVideo<phen_t, Params>,
#endif*/
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
