#ifndef DEFPARAMS_HPP_
#define DEFPARAMS_HPP_

#include <sferes/gen/evo_float.hpp>

#ifdef COEVO
#define NO_LISTMATCH
#endif

#ifndef NO_LISTMATCH
#define LISTMATCH
#endif

#ifndef FITPROP
#define ELITIST
#endif

#ifndef POLYNOMIAL
#define GAUSSIAN_MUTATION
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

#ifdef DIVERSITY
#define DIVSM
#define DIST_HAMMING
#endif

struct Params
{
	struct simu
	{
#ifdef MAP800
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Followup/map800x800.pbm");
		static const float real_w = 2400.0f;
#elif defined(MAP1600)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Followup/map1600x1600.pbm");
		static const float real_w = 4800.0f;
#elif defined(MAP2400)
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Followup/map2400x2400.pbm");
		static const float real_w = 7200.0f;
#else
		SFERES_STRING(map_name, SFERES_ROOT "/exp/StagHunt-Followup/map800x800.pbm");
		static const float real_w = 2400.0f;
#endif
		
		static const float hunter_radius = 20.0f;
		
		static const float hare_radius = 20.0f;

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
#ifdef RATIO75
	static const int nb_big_stags = 0.75*total_preys;
	static const int nb_hares = total_preys - nb_big_stags;
#elif defined(RATIO25)
	static const int nb_hares = 0.75*total_preys;
	static const int nb_big_stags = total_preys - nb_hares;
#elif defined(RATIO65)
	static const int nb_big_stags = 0.65*total_preys;
	static const int nb_hares = total_preys - nb_big_stags;
#elif defined(RATIO35)
	static const int nb_hares = 0.65*total_preys;
	static const int nb_big_stags = total_preys - nb_hares;
#else
	static const int nb_big_stags = total_preys/2;
	static const int nb_hares = total_preys/2;
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
#ifdef RATIO75
	static const float ratio_big_stags = 0.75;
#elif defined(RATIO25)
	static const float ratio_big_stags = 0.25;
#elif defined(RATIO65)
	static const float ratio_big_stags = 0.65;
#elif defined(RATIO35)
	static const float ratio_big_stags = 0.35;
#else
	static const float ratio_big_stags = 0.5;
#endif
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

		static const float nb_steps = 20000;
		
		static const int nb_trials = 5;
		
		static const int nb_lasers = 12;

		static const int nb_bumpers = 0;
		
		static const int nb_camera_pixels = 12;

		static const int threshold_hamming = 0.5f;
	};
	
	struct nn
	{
		static const size_t nb_info_by_pixel = 4;

#ifdef ID_LEADER
		static const size_t nb_inputs_leadership = 1;
#else
		static const size_t nb_inputs_leadership = 0;
#endif

		static const size_t nb_inputs_scream = 0;
		static const size_t nb_outputs_scream = 0;

		static const size_t nb_inputs_compas = 0;

		static const size_t nb_inputs = Params::simu::nb_lasers + Params::simu::nb_camera_pixels*nb_info_by_pixel + Params::simu::nb_bumpers 
													+ Params::nn::nb_inputs_leadership + Params::nn::nb_inputs_scream + Params::nn::nb_inputs_compas;

		static const size_t nb_hidden = 8;
		
		static const size_t nb_outputs = 2 + Params::nn::nb_outputs_scream;

#ifdef PARTNER_SELECT
#ifdef FIXED_CHOICE
		static const size_t genome_size = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs + 1;
#elif defined(NETWORK_DOUBINPUTS)
		static const size_t genome_size = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs + 4;
#elif defined(WEIGHTS_CHOICE)
		static const size_t genome_size = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs + Params::nn::nb_hidden * Params::nn::nb_outputs + 1;
#else
		static const size_t genome_size = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs + 3;
#endif
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
		static const float max_value =-1e-10;
		
		static const float sigma = 0.5f;
		
		static const float lower_bound = 0.0f;
		
		static const float upper_bound = 1.0f;
	};
#endif
	
  struct evo_float
  {
#ifdef MUT_APP_RATE
#ifdef RATE5
  	static const float mutant_apparition_rate = 0.05;
#elif defined(RATE25)
  	static const float mutant_apparition_rate = 0.25;
#endif
#endif

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
    static const sferes::gen::evo_float::cross_over_t cross_over_type = sferes::gen::evo_float::no_cross_over;
    
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

#ifdef RANDOM_MUTANT
    static const float random_mutant_probability = 0.01f;
#endif

#ifdef TUPLE_SWAP
    static const float tuple_swap_probability = 0.1f;
#endif
  };
  
  struct pop
  {
    // size of the population
#ifdef POP100
    static const unsigned size = 100;
#elif defined(POP200)
    static const unsigned size = 200;
#elif defined(POP40)
    static const unsigned size = 40;
#elif defined(MU2) && defined(LAMBDA2)
    static const unsigned size = 4;
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

    // number of generations
    static const unsigned nb_gen = 2000;
    
    // how often should the result file be written
#if defined(POP100) || defined(POP200)
    static const int dump_period = 10;
#else
    static const int dump_period = 50;
#endif
    
    // how often should the video be done
    static const int video_dump_period = 100;
    
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

    static const float dist_threshold = 0.2;
    static const float diversity_threshold = 0.2;

#ifdef RESTART
    static const float prop_restart = 0.8;
#endif


#ifdef ELITIST
#ifdef MU20
		static const unsigned mu = 20;
#elif defined(MU8)
		static const unsigned mu = 8;
#elif defined(MU4)
		static const unsigned mu = 4;
#elif defined(MU2)
		static const unsigned mu = 2;
#elif defined(MU1)
		static const unsigned mu = 1;
#else
		static const unsigned mu = Params::pop::size/2;
#endif

#ifdef LAMBDA20
		static const unsigned lambda = 20;
#elif defined(LAMBDA8)
		static const unsigned lambda = 8;
#elif defined(LAMBDA4)
		static const unsigned lambda = 4;
#elif defined(LAMBDA2)
		static const unsigned lambda = 2;
#elif defined(LAMBDA1)
		static const unsigned lambda = 1;
#else
		static const unsigned lambda = Params::pop::size/2;
#endif
#endif

#ifdef TUPLES
		static const unsigned nb_opponents = 1;		
#else
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
#endif

#ifdef EVAL5
		static const unsigned nb_eval = 5;
#else
		static const unsigned nb_eval = 1;
#endif

		static const unsigned size_list_pref = 5;
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
#elif defined(STAMINA50)
#define STAMINA 50
#elif defined(STAMINA100)
#define STAMINA 100
#else
#define STAMINA 800
#endif

#ifdef NO_COOP
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP 50

#define FOOD_SMALL_STAG_SOLO 500
#define FOOD_SMALL_STAG_COOP 500

#define FOOD_BIG_STAG_SOLO 5000
#define FOOD_BIG_STAG_COOP 5000
#else
#ifdef HARE_BAD
#define FOOD_HARE_SOLO 0
#define FOOD_HARE_COOP 0
#else
#define FOOD_HARE_SOLO 50
#define FOOD_HARE_COOP 50
#endif

#define FOOD_SMALL_STAG_SOLO 50

#ifdef SSTAG250
#define FOOD_SMALL_STAG_COOP 250
#elif defined(SSTAG125)
#define FOOD_SMALL_STAG_COOP 125
#elif defined(SSTAG500)
#define FOOD_SMALL_STAG_COOP 500
#elif defined(SSTAG50)
#define FOOD_SMALL_STAG_COOP 50
#else
#define FOOD_SMALL_STAG_COOP 250
#endif

#ifdef BSTAG_SOLO500
#define FOOD_BIG_STAG_SOLO 500
#elif defined(BSTAG_SOLO50)
#define FOOD_BIG_STAG_SOLO 50
#else
#define FOOD_BIG_STAG_SOLO 0
#endif

#ifdef BSTAG2500
#define FOOD_BIG_STAG_COOP 2500
#elif defined(BSTAG1000)
#define FOOD_BIG_STAG_COOP 1000
#elif defined(BSTAG500)
#define FOOD_BIG_STAG_COOP 500
#elif defined(BSTAG250)
#define FOOD_BIG_STAG_COOP 250
#elif defined(BSTAG175)
#define FOOD_BIG_STAG_COOP 175
#elif defined(BSTAG100)
#define FOOD_BIG_STAG_COOP 100
#elif defined(BSTAG0)
#define FOOD_BIG_STAG_COOP 0
#else
#define FOOD_BIG_STAG_COOP 500
#endif
#endif


#ifdef SCREAM
#define SCREAM_MAX 100
#define SCREAM_DECAY 10
#endif

#ifdef STAG_STUN
#define STUN_TIME 5000
#endif


#define CATCHING_DISTANCE 10

#ifndef NEVAL_ALL
#define EA_EVAL_ALL
#endif

#define NOSTOP

//#define PRED_CONF

// #define BEHAVIOUR_LOG

#define BEHAVIOUR_VIDEO

#ifndef COEVO
#define GENOME_TRACES
#endif

#define TEST_VARIANCE_TRIALS

#define CMAES_BOUNDARIES

#ifdef ELITIST
#ifndef NEVAL_PARENTS
#define EVAL_PARENTS
#endif

#ifndef ONE_PLUS_ONE_REPLACEMENT
#define N_PLUS_N_REPLACEMENT
#endif
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
