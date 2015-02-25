#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#ifndef FITPROP
#define ELITIST
#endif

#define GAUSSIAN_MUTATION
#define MLP_PERSO

#define NO_BOOLEAN

#ifdef LARGE_POP
#define OPPONENTS10
#define TRIALS1
#define NESTED
#endif

#ifndef ALTRUISM
#define NOT_AGAINST_ALL
#endif

#ifdef NOT_AGAINST_ALL
#define OPPONENTS5
#endif

struct Params
{
	struct simu
	{
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Leadership/map800x800.pbm");
		static const float real_w = 2400.0f;
		
		static const float hunter_radius = 20.0f;
		
		static const float waypoint_radius = 30.0f;

#ifdef WAYPOINTS18
		static const int nb_waypoints = 18;
#elif defined(WAYPOINTS12)
		static const int nb_waypoints = 12;
#elif defined(WAYPOINTS7)
		static const int nb_waypoints = 7;
#elif defined(WAYPOINTS5)
		static const int nb_waypoints = 5;
#elif defined(WAYPOINTS4)
		static const int nb_waypoints = 4;
#elif defined(WAYPOINTS3)
		static const int nb_waypoints = 3;
#elif defined(WAYPOINTS2)
		static const int nb_waypoints = 2;
#elif defined(WAYPOINTS1)
		static const int nb_waypoints = 1;
#else
		static const int nb_waypoints = 3;
#endif

		static const float nb_steps = 10000;
		
		static const int nb_trials = 5;
		
		static const int nb_lasers = 12;

		static const int nb_bumpers = 0;
		
		static const int nb_camera_pixels = 12;
	};
	
	struct nn
	{
		static const size_t nb_info_by_pixel = 4;

#ifdef ID_LEADER
		static const size_t nb_inputs_leadership = 1;
#else
		static const size_t nb_inputs_leadership = 0;
#endif

#ifdef SCREAM
		static const size_t nb_inputs_scream = 1;
		static const size_t nb_outputs_scream = 1;
#else
		static const size_t nb_inputs_scream = 0;
		static const size_t nb_outputs_scream = 0;
#endif

#ifdef COMPAS_FOLLOWER
		static const size_t nb_inputs_compas = 2;
#else
		static const size_t nb_inputs_compas = 0;
#endif

		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn::nb_inputs_leadership + Params::nn::nb_inputs_scream + Params::nn::nb_inputs_compas;

		static const size_t nb_hidden = 8;
		
		static const size_t nb_outputs = 2 + Params::nn::nb_outputs_scream;
	};
	
#ifdef CMAES
	struct cmaes
	{
		static const float max_value =-1e-10;
		
		static const float sigma = 0.5f;
		
		static const float lower_bound = 0.0f;
		
		static const float upper_bound = 1.0f;
	};
#endif
	
  struct evo_float
  {
    // the mutation rate of the real-valued vector
    static const float mutation_rate = 0.003f;

#ifndef GAUSSIAN_MUTATION
    // we choose the polynomial mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::polynomial;
    
    // a parameter of the polynomial mutation
    static const float eta_m = 15.0f;
#else
    // we choose the gaussian mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::gaussian;
    
#ifdef STD1
    static const float sigma = 0.1f;
#elif defined(STD05)
    static const float sigma = 0.05f;
#else
    static const float sigma = 0.01f;
#endif
#endif
    
    // we choose the polynomial cross-over type
    static const sferes::gen::evo_float::cross_over_t cross_over_type = sferes::gen::evo_float::sbx;
    
    // the cross rate of the real-valued vector
    static const float cross_rate = 0.5f;

    // a parameter of the polynomial cross-over
    static const float eta_c = 10.0f;
  };
  
  struct pop
  {
    // size of the population
    static const unsigned size = 20;
    
    // number of generations
    static const unsigned nb_gen = 4500;
    
    // how often should the result file be written (here, each 50
    // generation)
    static const int dump_period = 10;
    
    // how many individuals should be created during the random
    // generation process?
    static const int initial_aleat = 1;
    
    // used by RankSimple to select the pressure
    static const float coeff = 1.1f;
    
    // the number of individuals that are kept from on generation to
    // another (elitism) (but are still mutated)
    static const float keep_rate = 1.0f;
    
    // The budget in a number of evaluations for the simulation
    static const int budget = 50000; //Params::pop::size * 850;

#ifdef ELITIST
		static const unsigned mu = Params::pop::size/2;
		static const unsigned lambda = Params::pop::size/2;
#endif

#ifdef OPPONENTS1
		static const unsigned nb_opponents = 1;		
#elif defined(OPPONENTS2)
		static const unsigned nb_opponents = 2;		
#elif defined(OPPONENTS5)
		static const unsigned nb_opponents = 5;		
#elif defined(OPPONENTS10)
		static const unsigned nb_opponents = 10;		
#elif defined(OPPONENTS20)
		static const unsigned nb_opponents = 20;		
#else
		static const unsigned nb_opponents = 5;		
#endif

#ifdef EVAL5
		static const unsigned nb_eval = 5;
#else
		static const unsigned nb_eval = 1;
#endif
  };
  
  struct trajectory
  {  	
  };
  
  struct parameters
  {
    // minimum value
    static const float min = -1.0f;
    // maximum value of parameters
    static const float max = 1.0f;
  };
  
  struct fitness
  {
    static const unsigned int nb_step_watch=4000; // diversity/novelty computed on nb_step_watch number of steps 

    static const unsigned int nb_bits = 10; 
  };
};


#define HUNTER_COLOR 100
#define HARE_COLOR 200
#define SMALL_STAG_COLOR 400
#define BIG_STAG_COLOR 500

#define EA_EVAL_ALL

#define NOSTOP

//#define PRED_CONF

#define BEHAVIOUR_LOG

#define BEHAVIOUR_VIDEO

#define TEST_VARIANCE_TRIALS

#define CMAES_BOUNDARIES

#ifdef ELITIST
#define EVAL_PARENTS
#define N_PLUS_N_REPLACEMENT
#endif

#endif
