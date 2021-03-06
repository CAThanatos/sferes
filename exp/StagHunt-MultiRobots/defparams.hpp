#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#ifndef FITPROP
#define ELITIST
#endif

#ifndef POLYNOMIAL
#define GAUSSIAN_MUTATION
#endif

#ifndef ELMAN
#define MLP_PERSO
#endif

#ifdef CONTROL3
#define MLP_COR
#endif

#ifdef SCREAM_PREY
#define NEW_COMPAS
#define NO_DECAY
#endif

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

struct Params
{
	struct simu
	{
#ifdef MAP800
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-MultiRobots/map800x800.pbm");
		static const float real_w = 2400.0f;
#elif defined(MAP1600)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-MultiRobots/map1600x1600.pbm");
		static const float real_w = 4800.0f;
#elif defined(MAP2400)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-MultiRobots/map2400x2400.pbm");
		static const float real_w = 7200.0f;
#else
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-MultiRobots/map800x800.pbm");
		static const float real_w = 2400.0f;
#endif
		
		static const float hunter_radius = 20.0f;

#ifdef HUNTERS5
		static const int nb_hunters = 5;
#elif defined(HUNTERS2)
		static const int nb_hunters = 2;
#else
		static const int nb_hunters = 3;
#endif
		
		static const float hare_radius = 30.0f;

#ifdef PREYS1
		static const int total_preys = 1;
#elif defined(PREYS2)
		static const int total_preys = 2;
#elif defined(PREYS6)
		static const int total_preys = 6;
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
#elif defined(NO_PREYS)
		static const int total_preys = 0;
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
	static const int nb_big_stags = total_preys/2;
	static const int nb_hares = total_preys/2;
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


		static const float small_stag_radius = 30.0f;
		
		static const int nb_small_stags = 0;
		
#ifdef RADIUS30
		static const float big_stag_radius = 30.0f;
#elif defined(RADIUS40)
		static const float big_stag_radius = 40.0f;
#elif defined(RADIUS50)
		static const float big_stag_radius = 50.0f;
#else
		static const float big_stag_radius = 30.0f;
#endif

		
		static const int nb_levels = 2;

#ifdef STAMINA3200
		static const float nb_steps = 40000;
#else
		static const float nb_steps = 20000;
#endif
		
#ifdef TRACE_ONLY
		static const int nb_trials = 20;
#elif defined(TRIALS10)
		static const int nb_trials = 10;
#else
		static const int nb_trials = 5;
#endif
		
		static const int nb_lasers = 12;

		static const int nb_bumpers = 0;
		
		static const int nb_camera_pixels = 12;

		static const int threshold_hamming = 0.5f;

		static const int nb_hunters_coop_hares_max = Params::simu::nb_hunters;

		static const int nb_hunters_coop_sstags_max = Params::simu::nb_hunters;
		
		static const int nb_hunters_coop_bstags_max = Params::simu::nb_hunters;
	};
	
	struct nn
	{
#ifdef LEADER_COLOR
		static const size_t nb_info_by_pixel = 5;
#else
		static const size_t nb_info_by_pixel = 4;
#endif

#ifdef ID_LEADER
		static const size_t nb_inputs_leadership = 1;
#else
		static const size_t nb_inputs_leadership = 0;
#endif

		static const size_t nb_inputs_scream = 0;
		static const size_t nb_outputs_scream = 0;

#ifdef COM_COMPAS
		static const size_t nb_inputs_compas = 3;
#else
		static const size_t nb_inputs_compas = 0;
#endif

		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn::nb_inputs_leadership + Params::nn::nb_inputs_scream + Params::nn::nb_inputs_compas;

		static const size_t nb_hidden = 8;
		
		static const size_t nb_outputs = 2 + Params::nn::nb_outputs_scream;

#if defined(DOUBLE_NN) && !defined(DUPLICATION)
		static const size_t genome_size = ((Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs)*2;
#else
		static const size_t genome_size = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;
#endif
	};
	
#ifdef NOVELTY
	struct novelty
	{
		static const float nov_min = 0.1;
		static const float k = 5;
	};
#endif

#ifdef CMAES
	struct cmaes
	{
		static const float max_value = -1e-10;
		
		static const float sigma = 0.5f;
		
		static const float lower_bound = 0.0f;
		
		static const float upper_bound = 1.0f;
	};
#endif
	
  struct evo_float
  {
    // the mutation rate of the real-valued vector
#ifdef RATE1
    static const float mutation_rate = 0.002f;
#elif defined RATE10
    static const float mutation_rate = 0.02f;
#elif defined RATE0
    static const float mutation_rate = 0.0f;
#else
    static const float mutation_rate = 0.003f;
#endif

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
    
#ifdef STD1
    static const float sigma = 0.1f;
#elif defined(STD05)
    static const float sigma = 0.05f;
#elif defined(STD06)
    static const float sigma = 0.06f;
#elif defined(STD07)
    static const float sigma = 0.07f;
#elif defined(STD08)
    static const float sigma = 0.08f;
#elif defined(STD09)
    static const float sigma = 0.09f;
#elif defined(STD11)
    static const float sigma = 0.11f;
#elif defined(STD12)
    static const float sigma = 0.12f;
#elif defined(STD13)
    static const float sigma = 0.13f;
#elif defined(STD14)
    static const float sigma = 0.14f;
#elif defined(STD15)
    static const float sigma = 0.15f;
#elif defined(STD16)
    static const float sigma = 0.16f;
#elif defined(STD17)
    static const float sigma = 0.17f;
#elif defined(STD18)
    static const float sigma = 0.18f;
#elif defined(STD19)
    static const float sigma = 0.19f;
#elif defined(STD2)
    static const float sigma = 0.2f;
#else
    static const float sigma = 0.01f;
#endif
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
#ifdef POP100
    static const unsigned size = 100;
#elif defined(POP20)
    static const unsigned size = 20;
#elif defined(POP36)
    static const unsigned size = 36;
#else
    static const unsigned size = 20;
#endif

#ifdef POP_INIT20
    static const int pop_init = 20;
#elif defined(POP_INIT24)
    static const int pop_init = 24;
#else
    // Initial population is equal to pop size (or mu) by default
    static const int pop_init = -1;
#endif
    
    // number of generations
    static const unsigned nb_gen = 20000;
    
    // how often should the result file be written
#ifdef POP100
    static const int dump_period = 10;
#else
    static const int dump_period = 50;
#endif
    
    // how often should the video be done
    static const int video_dump_period = 100;
    
#ifdef PAIRING
#ifdef NICHE4
    static const int nb_niches = 4;
#elif defined(NICHE2)
    static const int nb_niches = 2;
#elif defined(NICHE3)
    static const int nb_niches = 3;
#elif defined(NICHE8)
    static const int nb_niches = 8;
#elif defined(NICHE10)
    static const int nb_niches = 10;
#else
    static const int nb_niches = 4;
#endif

#ifdef EVOL_PAIRING
		static const int nb_offsprings_evol_pairing = 5;
		static const int evolve_pairing_period = 50;
		static const float proba_mut_pairing = 0.25;
#endif

#ifdef PRUNING
#ifdef EVAL_PRUNING1000
		static const int pruning_eval_period = 1000;
#elif defined(EVAL_PRUNING200)
		static const int pruning_eval_period = 200;
#elif defined(EVAL_PRUNING100)
		static const int pruning_eval_period = 100;
#else
		static const int pruning_eval_period = 500;
#endif
#endif
#endif

    // how many individuals should be created during the random
    // generation process?
    static const int initial_aleat = 1;
    
    // used by RankSimple to select the pressure
    static const float coeff = 1.1f;
    
    // the number of individuals that are kept from one generation to
    // another (elitism) (but are still mutated)
    static const float keep_rate = 1.0f;
    
    // The budget in a number of evaluations for the simulation
    static const int budget = 50000; //Params::pop::size * 850;

#ifdef ELITIST
#ifdef MU6
		static const unsigned mu = 6;
#elif defined(MU9)
		static const unsigned mu = 9;
#elif defined(MU18)
		static const unsigned mu = 18;
#else
		static const unsigned mu = Params::pop::size/2;
#endif

#ifdef LAMBDA6
		static const unsigned lambda = 6;
#elif defined(LAMBDA9)
		static const unsigned lambda = 9;
#elif defined(LAMBDA18)
		static const unsigned lambda = 18;
#else
		static const unsigned lambda = Params::pop::size/2;
#endif
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
#ifdef PARAMS10
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
#define SMALL_STAG_COLOR 400
#define BIG_STAG_COLOR 500

#ifdef NO_STAMINA
#define STAMINA 1
#elif defined(STAMINA800)
#define STAMINA 800
#elif defined(STAMINA1600)
#define STAMINA 1600
#elif defined(STAMINA3200)
#define STAMINA 3200
#else
#define STAMINA 1600
#endif

#ifdef NO_COOP
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP_LOW 50
#define FOOD_HARE_COOP_HIGH 50

#define FOOD_SMALL_STAG_SOLO 500
#define FOOD_SMALL_STAG_COOP_LOW 500
#define FOOD_SMALL_STAG_COOP_HIGH 500

#define FOOD_BIG_STAG_SOLO 5000
#define FOOD_BIG_STAG_COOP_LOW 5000
#define FOOD_BIG_STAG_COOP_HIGH 5000

#else
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP_LOW 50
#define FOOD_HARE_COOP_HIGH 50

#define FOOD_SMALL_STAG_SOLO 50
#ifdef SSTAG1000
#ifdef NO_LEVELS
#define FOOD_SMALL_STAG_COOP_LOW 1000
#define FOOD_SMALL_STAG_COOP_HIGH 1000
#else
#define FOOD_SMALL_STAG_COOP_LOW 125
#define FOOD_SMALL_STAG_COOP_HIGH 1000
#endif
#elif defined(SSTAG500)
#ifdef NO_LEVELS
#define FOOD_SMALL_STAG_COOP_LOW 500
#define FOOD_SMALL_STAG_COOP_HIGH 500
#else
#define FOOD_SMALL_STAG_COOP_LOW 125
#define FOOD_SMALL_STAG_COOP_HIGH 500
#endif
#elif defined(SSTAG250)
#ifdef NO_LEVELS
#define FOOD_SMALL_STAG_COOP_LOW 250
#define FOOD_SMALL_STAG_COOP_HIGH 250
#else
#define FOOD_SMALL_STAG_COOP_LOW 125
#define FOOD_SMALL_STAG_COOP_HIGH 250
#endif
#elif defined(SSTAG150)
#ifdef NO_LEVELS
#define FOOD_SMALL_STAG_COOP_LOW 150
#define FOOD_SMALL_STAG_COOP_HIGH 150
#else
#define FOOD_SMALL_STAG_COOP_LOW 100
#define FOOD_SMALL_STAG_COOP_HIGH 150
#endif
#else
#define FOOD_SMALL_STAG_COOP_LOW 100
#define FOOD_SMALL_STAG_COOP_HIGH 150
#endif

#ifdef BSTAG_SOLO500
#define FOOD_BIG_STAG_SOLO 500
#elif defined(BSTAG_SOLO50)
#define FOOD_BIG_STAG_SOLO 50
#else
#define FOOD_BIG_STAG_SOLO 0
#endif

#define FOOD_BIG_STAG_COOP_LOW 0

#ifdef BSTAG3000
#define FOOD_BIG_STAG_COOP_HIGH 3000
#elif defined(BSTAG2500)
#define FOOD_BIG_STAG_COOP_HIGH 2500
#elif defined(BSTAG1500)
#define FOOD_BIG_STAG_COOP_HIGH 1500
#elif defined(BSTAG1000)
#define FOOD_BIG_STAG_COOP_HIGH 1000
#elif defined(BSTAG500)
#define FOOD_BIG_STAG_COOP_HIGH 500
#elif defined(BSTAG250)
#define FOOD_BIG_STAG_COOP_HIGH 250
#elif defined(BSTAG175)
#define FOOD_BIG_STAG_COOP_HIGH 175
#elif defined(BSTAG100)
#define FOOD_BIG_STAG_COOP_HIGH 100
#elif defined(BSTAG0)
#define FOOD_BIG_STAG_COOP_HIGH 0
#else
#define FOOD_BIG_STAG_COOP_HIGH 500
#endif
#endif

#define CATCHING_DISTANCE 10

#ifndef NEVAL_ALL
#define EA_EVAL_ALL
#endif

#define NOSTOP

//#define PRED_CONF

// #define BEHAVIOUR_LOG

// #define BEHAVIOUR_VIDEO

#ifndef COEVO
#define GENOME_TRACES
#endif

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

#endif
