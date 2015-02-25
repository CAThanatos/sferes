#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#ifndef FITPROP
#define ELITIST
#endif

#define GAUSSIAN_MUTATION
#define MLP_PERSO

#define NO_BOOLEAN

#if defined(SETTING1) || defined(SETTING2) || defined(SETTING3) || defined(SETTING4) || defined(SETTING5) || defined(SETTING6) || defined(SETTING7) || defined(SETTING8) || defined(SETTING13)
#define HARE_PRES
#endif
#if defined(SETTING1) || defined(SETTING2) || defined(SETTING3) || defined(SETTING4) || defined(SETTING9) || defined(SETTING10) || defined(SETTING11) || defined(SETTING12) || defined(SETTING14)
#define SSTAG_PRES
#endif
#if defined(SETTING5) || defined(SETTING6) || defined(SETTING7) || defined(SETTING8) || defined(SETTING9) || defined(SETTING10) || defined(SETTING11) || defined(SETTING12) || defined(SETTING15)
#define BSTAG_PRES
#endif

#ifdef CONTROL1
#define HARE_PRES
#define BSTAG_PRES
#elif defined(CONTROL2)
#define SSTAG_PRES
#elif defined(CONTROL3)
#define SSTAG_PRES
#define BSTAG_PRES
#elif defined(CONTROL4)
#define HARE_PRES
#define SSTAG_PRES
#elif defined(EXP)
#define HARE_PRES
#define SSTAG_PRES
#define BSTAG_PRES
#else
#define HARE_PRES
#define BSTAG_PRES
#endif

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


#if defined(FITSIM) || defined(MULTI_SIM)
#define SIMSENSORS
#endif

#ifdef MULTI_ACTIVITY
#define SIMILARITY_ACTIVITY
#endif

#ifdef SIMSENSORS
#define SIMILARITY_SM
#endif

#if defined(SIMILARITY_SM) || defined(SIMILARITY_HUNT) || defined(SIMILARITY_ACTIVITY)
#define SIMILARITY
#endif

#ifdef SIM_MEAN
#define SIM_WINDOW
#endif

#ifdef TOTALCOOP
#define TOTALRATIO
#endif

#ifdef DIVSM
#define DIST_HAMMING
#endif

struct Params
{
	struct simu
	{
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Diversity/map800x800.pbm");
		static const float real_w = 2400.0f;
		
		static const float hunter_radius = 20.0f;
		
		static const float hare_radius = 20.0f;

#ifdef PREYS1
		static const int total_preys = 1;
#elif defined(PREYS2)
		static const int total_preys = 2;
#elif defined(PREYS8)
		static const int total_preys = 8;
#elif defined(PREYS9)
		static const int total_preys = 9;
#elif defined(PREYS12)
		static const int total_preys = 12;
#elif defined(PREYS18)
		static const int total_preys = 18;
#elif defined(PREYS36)
		static const int total_preys = 36;
#else
		static const int total_preys = 18;
#endif

#if defined(HARE_PRES)
#if defined(SSTAG_PRES)
#if defined(BSTAG_PRES)
	static const int nb_hares = total_preys/3;
	static const int nb_big_stags = 2*total_preys/3;
	static const float ratio_big_stags = 0.5;
#else
	static const int nb_hares = total_preys/2;
	static const int nb_big_stags = total_preys/2;
	static const float ratio_big_stags = 0;
#endif
#else
#if defined(BSTAG_PRES)
	static const int nb_hares = total_preys/2;
	static const int nb_big_stags = total_preys/2;
	static const float ratio_big_stags = 1;
#else
	static const int nb_hares = total_preys;
	static const int nb_big_stags = 0;
	static const float ratio_big_stags = 0;
#endif
#endif
#else
#if defined(SSTAG_PRES)
#if defined(BSTAG_PRES)
	static const int nb_hares = 0;
	static const int nb_big_stags = total_preys;
	static const float ratio_big_stags = 0.5;
#else
	static const int nb_hares = 0;
	static const int nb_big_stags = total_preys;
	static const float ratio_big_stags = 0;
#endif
#else
#if defined(BSTAG_PRES)
	static const int nb_hares = 0;
	static const int nb_big_stags = total_preys;
	static const float ratio_big_stags = 1;
#else
	static const int nb_hares = 0;
	static const int nb_big_stags = 0;
	static const float ratio_big_stags = 0;
#endif
#endif
#endif


		static const float small_stag_radius = 20.0f;
		
		static const int nb_small_stags = 0;
		
		static const float big_stag_radius = 20.0f;

		
		static const int nb_levels = 2;

		static const int nb_steps = 20000;
		
#ifdef TRIALS1
		static const int nb_trials = 1;
#else
		static const int nb_trials = 5;
#endif
		
		static const int nb_lasers = 12;

		static const int nb_bumpers = 0;
		
		static const int nb_camera_pixels = 12;

#ifdef SIMILARITY_SM
#ifdef SIMSENSORS
#ifdef SIM_MEAN
		static const int size_sim_vector = 1;
#else
		static const int size_sim_vector = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*5;
#endif
#else
		static const int size_sim_vector = 2;
#endif
#elif defined(SIMILARITY_HUNT)
		static const int size_sim_vector = 1;
#elif defined(SIMILARITY_ACTIVITY)
		static const int size_sim_vector = 1;
#endif

#ifdef SIMILARITY_ACTIVITY
#ifdef RATIO_ACT01
		static const float ratio_steps_activity = 0.01f;
#elif defined(RATIO_ACT1)
		static const float ratio_steps_activity = 0.1f;
#else
		static const float ratio_steps_activity = 0.1f;
#endif
#endif

#ifdef SIM_WINDOW
#ifdef RATIO_SIM01
		static const float ratio_steps_similarity = 0.01f;
#elif defined(RATIO_SIM05)
		static const float ratio_steps_similarity = 0.05f;
#elif defined(RATIO_SIM1)
		static const float ratio_steps_similarity = 0.1f;
#else
		static const float ratio_steps_similarity = 0.1f;
#endif

#ifdef SLIDING_WINDOW
#ifdef RATIO_SIM01
		static const int sim_window_size = 400;
#elif defined(RATIO_SIM1)
		static const int sim_window_size = 4000;
#else
		static const int sim_window_size = 4000;
#endif
#endif
#endif

		static const int threshold_hamming = 0.5f;
	};
	
	struct nn
	{
		static const size_t nb_info_by_pixel = 5;

		static const size_t nb_inputs_leadership = 0;

		static const size_t nb_inputs_scream = 0;

		static const size_t nb_inputs_compas = 0;

		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn::nb_inputs_leadership + Params::nn::nb_inputs_scream + Params::nn::nb_inputs_compas;

		static const size_t nb_hidden = 8;
		
		static const size_t nb_outputs = 2;
	};
	
	struct novelty
	{
#ifdef NOV01
		static const float nov_min = 0.1;
#elif defined(NOV02)
		static const float nov_min = 0.2;
#elif defined(NOV05)
		static const float nov_min = 0.5;
#else
		static const float nov_min = 0.1;
#endif

#ifdef NB2
		static const float k = 2;
#elif defined(NB5)
		static const float k = 5;
#elif defined(NB10)
		static const float k = 10;
#else
		static const float k = 5;
#endif
	};
	
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
    
#ifdef NO_CROSSOVER
    static const sferes::gen::evo_float::cross_over_t cross_over_type = sferes::gen::evo_float::no_cross_over;
#else
    // we choose the polynomial cross-over type
    static const sferes::gen::evo_float::cross_over_t cross_over_type = sferes::gen::evo_float::sbx;
#endif
    
    // the cross rate of the real-valued vector
    static const float cross_rate = 0.5f;

    // a parameter of the polynomial cross-over
    static const float eta_c = 10.0f;
  };
  
  struct pop
  {
#ifdef SIZE100
    // size of the population
    static const unsigned size = 100;
#elif defined(SIZE200)
    // size of the population
    static const unsigned size = 200;
#else
    // size of the population
    static const unsigned size = 20;
#endif
    
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

#define STAMINA 800

#ifdef NO_COOP
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP 50

#define FOOD_SMALL_STAG_SOLO 500
#define FOOD_SMALL_STAG_COOP 500

#define FOOD_BIG_STAG_SOLO 5000
#define FOOD_BIG_STAG_COOP 5000
#else
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP 50

#define FOOD_SMALL_STAG_SOLO 50
#define FOOD_SMALL_STAG_COOP 250

#ifdef BSTAG_SOLO50
#define FOOD_BIG_STAG_SOLO 50
#else
#define FOOD_BIG_STAG_SOLO 0
#endif

#ifdef BSTAG500
#define FOOD_BIG_STAG_COOP 500
#elif defined(BSTAG250)
#define FOOD_BIG_STAG_COOP 250
#elif defined(BSTAG100)
#define FOOD_BIG_STAG_COOP 100
#else
#define FOOD_BIG_STAG_COOP 500
#endif
#endif


#define CATCHING_DISTANCE 10

#define EA_EVAL_ALL

#define NOSTOP

//#define PRED_CONF

//#define BEHAVIOUR_LOG

#define BEHAVIOUR_VIDEO

#define TEST_VARIANCE_TRIALS

#define CMAES_BOUNDARIES

#ifdef ELITIST
#define EVAL_PARENTS
#define N_PLUS_N_REPLACEMENT
#endif

#if defined(SETTING2) || defined(SETTING4) || defined(SETTING6) || defined(SETTING8) || defined(SETTING13)
#define COOP_HARE
#define TEST_COOP
#endif

#if defined(SETTING3) || defined(SETTING4) || defined(SETTING10) || defined(SETTING12) || defined(SETTING14)
#define COOP_SSTAG
#define TEST_COOP
#endif

#if defined(SETTING7) || defined(SETTING8) || defined(SETTING11) || defined(SETTING12) || defined(SETTING15)
#define COOP_BSTAG
#define TEST_COOP
#endif

#define MAX_DIST_STEP 6

#endif
