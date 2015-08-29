#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#ifndef FITPROP
#define ELITIST
#endif

#define GAUSSIAN_MUTATION

#define NO_BOOLEAN

struct Params
{
	struct simu
	{
#ifdef MAP800
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-PartnerSelection/map800x800.pbm");
		static const float real_w = 2400.0f;
#elif defined(MAP1600)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-PartnerSelection/map1600x1600.pbm");
		static const float real_w = 4800.0f;
#elif defined(MAP2400)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-PartnerSelection/map2400x2400.pbm");
		static const float real_w = 7200.0f;
#else
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-PartnerSelection/map1600x1600.pbm");
		static const float real_w = 4800.0f;
#endif
		
		static const float hunter_radius = 20.0f;
		
		static const float food_radius = 20.0f;

		static const int total_food = 10;

		static const float nb_steps = 20000;
		
#ifdef TRACE_ONLY
		static const int nb_trials = 20;
#else
		static const int nb_trials = 5;
#endif
		
		static const int nb_lasers = 6;

		static const int nb_bumpers = 0;
		
		static const int nb_camera_pixels = 12;

		static const int threshold_hamming = 0.5f;

		static const int nb_hunters_needed = 2;
	};
	
	struct nn_move
	{
		static const size_t nb_info_by_pixel = 4;

#ifdef SCREAM
		static const size_t nb_inputs_scream = 1;
		static const size_t nb_outputs_scream = 1;
#else
		static const size_t nb_inputs_scream = 0;
		static const size_t nb_outputs_scream = 0;
#endif

		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn_move::nb_inputs_scream;

		static const size_t nb_hidden = 8;
		
		static const size_t nb_outputs = 2 + Params::nn_move::nb_outputs_scream;

    static const size_t nn_size = (Params::nn_move::nb_inputs + 1) * Params::nn_move::nb_hidden + Params::nn_move::nb_outputs * Params::nn_move::nb_hidden + Params::nn_move::nb_outputs;
	};

  struct nn_reputation
  {
    static const size_t nb_inputs = 2;

    static const size_t nb_hidden = 0;

    static const size_t nb_outputs = 1;

    static const size_t nn_size = (Params::nn_reputation::nb_inputs + 1) * Params::nn_reputation::nb_hidden + Params::nn_reputation::nb_outputs * Params::nn_reputation::nb_hidden + Params::nn_reputation::nb_outputs;
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
    static const size_t genome_size = Params::nn_move::nn_size + Params::nn_reputation::nn_size + 1;

    // the mutation rate of the real-valued vector
    static const float mutation_rate = 0.003f;

#ifdef STRONG_MUTATION
    static const float strong_mutation_rate = 0.001f;
#endif

#ifndef GAUSSIAN_MUTATION
    // we choose the polynomial mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::polynomial;
    
    // a parameter of the polynomial mutation
    static const float eta_m = 15.0f;
#else
    // we choose the gaussian mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::gaussian;
    
    static const float sigma = 0.01f;
#endif
    
    // we choose the polynomial cross-over type
    static const sferes::gen::evo_float::cross_over_t cross_over_type = sferes::gen::evo_float::sbx;
    
    // the cross rate of the real-valued vector
    static const float cross_rate = 0.05f;

    // a parameter of the polynomial cross-over
    static const float eta_c = 10.0f;

#if defined(DOUBLE_NN) && defined(DUPLICATION)
#ifdef DUP10
    static const float duplication_rate = 0.1f;
#elif defined(DUP5)
    static const float duplication_rate = 0.05f;
#elif defined(DUP1)
    static const float duplication_rate = 0.01f;
#else
    static const float duplication_rate = 0.05f;
#endif
    static const float deletion_rate = 0.005f;
#endif
  };
  
  struct pop
  {
    // size of the population
    static const unsigned size = 20;
    
    // number of generations
    static const unsigned nb_gen = 10000;
    
    // how often should the result file be written (here, each 10
    // generation)
    static const int dump_period = 100;
    
    // how often should the video be done
    static const int video_dump_period = 100;
    
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
#define FOOD_COLOR 200

#define STAMINA 800

#define REWARD_COOP 50
#define REWARD_DEFECT 500

#define FOOD_SMALL_STAG_SOLO 50


#ifdef SCREAM
#define SCREAM_MAX 100
#define SCREAM_DECAY 10
#endif


#define CATCHING_DISTANCE 10

#ifndef NEVAL_ALL
#define EA_EVAL_ALL
#endif

#define NOSTOP

//#define PRED_CONF

// #define BEHAVIOUR_LOG

#define BEHAVIOUR_VIDEO

#define TEST_VARIANCE_TRIALS

#define CMAES_BOUNDARIES

#ifdef ELITIST
#define N_PLUS_N_REPLACEMENT
#endif

#endif
