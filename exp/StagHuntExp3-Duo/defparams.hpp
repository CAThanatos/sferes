#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#define CAMERA_TYPE
#define CAMERA_DIST
#define NORMALIZE_INPUTS

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
#endif

/*#ifdef FITPROP
#define LARGE_POP
#endif*/

#ifdef LARGE_POP
#define OPPONENTS10
#define TRIALS1
#define NESTED
#endif

#ifdef CAMERA_TYPE
#define ZERO_INPUT
#endif

#ifdef NEW_CAMERA
#define NEW_TYPES
#define RANGE_COR
#endif

#ifdef CONFUSION
#undef NEW_TYPES
#endif

#ifndef ALTRUISM
#define NOT_AGAINST_ALL
#endif

#ifndef BOOLEAN
#define NO_BOOLEAN
#endif

#ifdef NOT_AGAINST_ALL
#if !defined(OPPONENTS1) && !defined(OPPONENTS2) && !defined(OPPONENTS10) && !defined(OPPONENTS20)
#define OPPONENTS5
#endif
#endif

#ifdef PRED_IMMOBILE
#define NO_COOP
#define OPPONENTS1
#endif

#define NO_BUMPERS
#define MORE_SENSORS

#ifdef SIMSENSORS
#define SIMULARITY_SM
#endif

#if defined(SIMULARITY_SM) || defined(SIMULARITY_HUNT)
#define SIMULARITY
#endif

struct Params
{
	struct simu
	{
#ifdef MAP400
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHuntExp3-Duo/map400x400.pbm");
		static const float real_w = 1200.0f;
#elif defined(MAP568)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHuntExp3-Duo/map568x568.pbm");
		static const float real_w = 1704.0f;
#elif defined(MAP800)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHuntExp3-Duo/map800x800.pbm");
		static const float real_w = 2400.0f;
#elif defined(MAP1600)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHuntExp3-Duo/map1600x1600.pbm");
		static const float real_w = 4800.0f;
#else
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHuntExp3-Duo/map200x200.pbm");
		static const float real_w = 600.0f;
#endif
		
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
#if defined(RATIO_BSTAGS95)
	static const int nb_hares = total_preys - 1;
	static const int nb_big_stags = 1;
#else
	static const int nb_hares = total_preys/2;
	static const int nb_big_stags = total_preys/2;
#endif
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

#ifdef STEPS10000
		static const float nb_steps = 10000;
#elif defined(STEPS15000)
		static const float nb_steps = 15000;
#elif defined(STEPS20000)
		static const float nb_steps = 20000;
#elif defined(STEPS25000)
		static const float nb_steps = 25000;
#elif defined(STEPS40000)
		static const float nb_steps = 40000;
#else
		static const float nb_steps = 5000;
#endif
		
#ifdef TRIALS1
		static const int nb_trials = 1;
#elif defined(TRIALS2)
		static const int nb_trials = 2;
#elif defined(TRIALS5)
		static const int nb_trials = 5;
#elif defined(TRIALS20)
		static const int nb_trials = 20;
#else
		static const int nb_trials = 10;
#endif
		
#ifdef MORE_SENSORS
		static const int nb_lasers = 12;
#else
		static const int nb_lasers = 6;
#endif

#ifndef NO_BUMPERS
		static const int nb_bumpers = 2;
#else
		static const int nb_bumpers = 0;
#endif
		
#ifdef PIXELS24
		static const int nb_camera_pixels = 24;
#elif defined PIXELS18
		static const int nb_camera_pixels = 18;
#else
		static const int nb_camera_pixels = 12;
#endif
		
#ifdef SCREAM
		static const float scream_threshold = 0.5;
		static const int scream_decay = 50;
#endif

#ifdef CONFUSIONPREY
#ifdef CONFP1
		static const float confusion_prey = 0.01;
#elif defined(CONFP10)
		static const float confusion_prey = 0.1;
#elif defined(CONFP25)
		static const float confusion_prey = 0.25;
#elif defined(CONFP50)
		static const float confusion_prey = 0.5;
#endif
#endif

#ifdef CONFUSION
#ifdef KCONF01
		static const float k_confusion = 0.1;
#elif defined(KCONF015)
		static const float k_confusion = 0.15;
#elif defined(KCONF025)
		static const float k_confusion = 0.25;
#elif defined(KCONF05)
		static const float k_confusion = 0.5;
#elif defined(KCONF1)
		static const float k_confusion = 1;
#elif defined(KCONF10)
		static const float k_confusion = 10;
#else
		static const float k_confusion = 0.5;
#endif
#endif
	};
	
	struct nn
	{
#ifdef DIR_CLOSE
		static const size_t nb_info_by_pixel = 6;
#elif defined(TYPEB)
		static const size_t nb_info_by_pixel = 6;
#else
		static const size_t nb_info_by_pixel = 5;
#endif

#ifdef LEADERSHIP
		static const size_t nb_inputs_leadership = 1;
#else
		static const size_t nb_inputs_leadership = 0;
#endif

#ifdef SCREAM
		static const size_t nb_inputs_scream = 1;
#else
		static const size_t nb_inputs_scream = 0;
#endif

#if defined(COMPAS_SCR) || defined(COMPAS_PRED) || defined(COMPAS_LANDMARK)
		static const size_t nb_inputs_compas = 2;
#elif defined(COMPAS_LF) || defined(COMPAS_DIR)
		static const size_t nb_inputs_compas = 1;
#else
		static const size_t nb_inputs_compas = 0;
#endif

#ifdef CAMERA_TYPE
		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn::nb_inputs_leadership + Params::nn::nb_inputs_scream + Params::nn::nb_inputs_compas;
#else
#ifdef CAMERA_DIST
		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*3 + Params::simu::nb_bumpers;
#else
		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*2 + Params::simu::nb_bumpers;
#endif
#endif

#ifdef HIDDEN12
		static const size_t nb_hidden = 12;
#elif defined(HIDDEN16)
		static const size_t nb_hidden = 16;
#elif defined(HIDDEN24)
		static const size_t nb_hidden = 24;
#elif defined(HIDDEN32)
		static const size_t nb_hidden = 32;
#else
		static const size_t nb_hidden = 8;
#endif
		
#ifdef SCREAM
		static const size_t nb_outputs = 3;
#else
		static const size_t nb_outputs = 2;
#endif
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
#ifdef MUT30
    static const float mutation_rate = 0.3f;
#elif defined(MUT10)
    static const float mutation_rate = 0.1f;
#elif defined(MUT1)
    static const float mutation_rate = 0.01f;
#elif defined(MUT03)
    static const float mutation_rate = 0.003f;
#elif defined(MUT01)
    static const float mutation_rate = 0.001f;
#else
    static const float mutation_rate = 0.003f;
#endif

#ifdef GAUSSIAN_MUTATION
    // we choose the gaussian mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::gaussian;
    
#ifdef STD1
    static const float sigma = 0.1f;
#elif defined(STD5)
    static const float sigma = 0.5f;
#elif defined(STD08)
    static const float sigma = 0.08f;
#elif defined(STD05)
    static const float sigma = 0.05f;
#elif defined(STD01)
    static const float sigma = 0.01f;
#elif defined(STD10E5)
    static const float sigma = 0.00001f;
#elif defined(STD10E6)
    static const float sigma = 0.000001f;
#else
    static const float sigma = 0.01f;
#endif
#else
    // we choose the polynomial mutation type
    static const sferes::gen::evo_float::mutation_t mutation_type = sferes::gen::evo_float::polynomial;
    
    // a parameter of the polynomial mutation
    static const float eta_m = 15.0f;
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
#ifdef LARGE_POP
#ifdef POP1000
    static const unsigned size = 1000;
#elif defined(POP500)
    static const unsigned size = 500;
#else
    static const unsigned size = 100;
#endif
#else
    static const unsigned size = 20;
#endif
    
    // number of generations
    static const unsigned nb_gen = 10000;
    
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
#ifdef NO_ELITISM
    static const float keep_rate = 0.5f;
#else
    static const float keep_rate = 1.0f;
#endif
    
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
#ifdef LARGE_PARAMS
    // minimum value
    static const float min = -10.0f;
    // maximum value of parameters
    static const float max = 10.0f;
#else
    // minimum value
    static const float min = -1.0f;
    // maximum value of parameters
    static const float max = 1.0f;
#endif
  };
  
  struct fitness
  {
    static const unsigned int nb_step_watch=4000; // diversity/novelty computed on nb_step_watch number of steps 

    static const unsigned int nb_bits = 10; 
  };
};


#define HUNTER_COLOR 100
#define HARE_COLOR 200
/*#define SMALL_STAG_COLOR 300
#define BIG_STAG_COLOR 400*/
#define SMALL_STAG_COLOR 400
#define BIG_STAG_COLOR 500

#ifdef HIGH_STAMINA
#define STAMINA 800
#elif defined(STAMINA600)
#define STAMINA 600
#elif defined(STAMINA400)
#define STAMINA 400
#elif defined(STAMINA200)
#define STAMINA 200
#else
#define STAMINA 200
#endif

#ifdef NO_COOP
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP 50

#define FOOD_SMALL_STAG_SOLO 500
#define FOOD_SMALL_STAG_COOP 500

#define FOOD_BIG_STAG_SOLO 5000
#define FOOD_BIG_STAG_COOP 5000
#else
#define FOOD_HARE_SOLO 50

#ifdef HARE500
#define FOOD_HARE_COOP 500
#else
#define FOOD_HARE_COOP 50
#endif

#ifdef SSTAG_SOLO0
#define FOOD_SMALL_STAG_SOLO 0
#elif defined(SSTAG_SOLO50)
#define FOOD_SMALL_STAG_SOLO 50
#elif defined(SSTAG_SOLO150)
#define FOOD_SMALL_STAG_SOLO 150
#elif defined(SSTAG_SOLO250)
#define FOOD_SMALL_STAG_SOLO 250
#else
#define FOOD_SMALL_STAG_SOLO 50
#endif

#ifdef SSTAG1250
#define FOOD_SMALL_STAG_COOP 1250
#elif defined(SSTAG1000)
#define FOOD_SMALL_STAG_COOP 1000
#elif defined(SSTAG750)
#define FOOD_SMALL_STAG_COOP 750
#elif defined(SSTAG500)
#define FOOD_SMALL_STAG_COOP 500
#elif defined(SSTAG250)
#define FOOD_SMALL_STAG_COOP 250
#elif defined(SSTAG150)
#define FOOD_SMALL_STAG_COOP 150
#elif defined(SSTAG100)
#define FOOD_SMALL_STAG_COOP 100
#elif defined(SSTAG50)
#define FOOD_SMALL_STAG_COOP 50
#else
#define FOOD_SMALL_STAG_COOP 1000
#endif

#ifdef BSTAG_SOLO50
#define FOOD_BIG_STAG_SOLO 50
#elif defined BSTAG_SOLO100
#define FOOD_BIG_STAG_SOLO 100
#else
#define FOOD_BIG_STAG_SOLO 0
#endif

#ifdef BSTAG1500
#define FOOD_BIG_STAG_COOP 1500
#elif defined(BSTAG1000)
#define FOOD_BIG_STAG_COOP 1000
#elif defined(BSTAG500)
#define FOOD_BIG_STAG_COOP 500
#elif defined(BSTAG250)
#define FOOD_BIG_STAG_COOP 250
#elif defined(BSTAG100)
#define FOOD_BIG_STAG_COOP 100
#else
#define FOOD_BIG_STAG_COOP 1000
#endif
#endif


#define CATCHING_DISTANCE 10

#define EA_EVAL_ALL

#define NOSTOP

//#define DEFINED_POSITIONS
//#define TRIAL_POSITIONS

//#define PRED_CONF

//#define BEHAVIOUR_LOG

#define BEHAVIOUR_VIDEO

#define TEST_VARIANCE_TRIALS

#define CMAES_BOUNDARIES

#ifdef BLOCK_BSTAG
#define COUNT_TIME
#endif

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

#endif
