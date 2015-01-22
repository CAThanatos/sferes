#define BOOST_TEST_DYN_LINK 
#define BOOST_TEST_MODULE evo_neuro2
#include <iostream>
#include <boost/test/unit_test.hpp>
#include <sferes/fit/fitness.hpp>
#include <sferes/gen/evo_float.hpp>
#include <sferes/phen/parameters.hpp>

#include "gen_evo_neuro.hpp"
#include "phen_evo_neuro.hpp"
#include "lpds.hpp"

using namespace sferes;
using namespace sferes::gen::dnn;
using namespace sferes::gen::evo_float;

struct Params
{
  struct evo_float
  {
    static const float mutation_rate = 0.1f;
    static const float cross_rate = 0.1f;
    static const mutation_t mutation_type = polynomial;
    static const cross_over_t cross_over_type = sbx;
    static const float eta_m = 15.0f;
    static const float eta_c = 15.0f;
  };
  struct parameters
  {
    // maximum value of parameters
    static const float min = -5.0f;
    // minimum value
    static const float max = 5.0f;
  };


  struct dnn
  {
    static const size_t nb_inputs	= 1;
    static const size_t nb_outputs	= 1;
    static const float  max_weight	= 1.0f;
    static const float  max_bias	= 1.0f;
    
    static const size_t min_nb_neurons	= 3;
    static const size_t max_nb_neurons	= 4;
    static const size_t min_nb_conns	= 3;
    static const size_t max_nb_conns	= 4;

    static const float m_rate_add_conn	= 1.0f;
    static const float m_rate_del_conn	= 0.3f;
    static const float m_rate_change_conn = 1.0f;
    static const float m_rate_add_neuron  = 1.0f;
    static const float m_rate_del_neuron  = 0.2f;

    static const float weight_sigma	= 0.5f;
    static const float vect_sigma	= 0.5f;
    static const float m_rate_weight	= 1.0f;
    static const float m_rate_fparams   = 1.0f;
    static const int io_param_evolving  = 1; 

    static const init_t init = random_topology;
  };
  struct evo_neuro
  {
    typedef nn::Neuron<nn::PfWSum<>, nn::AfLpds<> >  neuron_t;
    typedef nn::Connection<> connection_t;
    static const size_t map_size	= 5;
    static const float  max_weight	= 5.0f;
  };
};


BOOST_AUTO_TEST_CASE(gen_evo_neuro)
{
  srand(time(0));
  typedef phen::Parameters<gen::EvoFloat<4, Params>, fit::FitDummy<>, Params> node_label_t;
  typedef phen::Parameters<gen::EvoFloat<3, Params>, fit::FitDummy<>, Params> conn_label_t;
  typedef gen::EvoNeuro<node_label_t, conn_label_t, Params> gen_t;
  
  gen_t gen1, gen2, gen3, gen4;
      
  gen1.random();
  for (size_t i = 0; i < 20; ++i)
    gen1.mutate();
  gen1.init();
}

BOOST_AUTO_TEST_CASE(phen_evo_neuro)
{
  srand(time(0));  
  typedef phen::Parameters<gen::EvoFloat<4, Params>, fit::FitDummy<>, Params> node_label_t;
  typedef phen::Parameters<gen::EvoFloat<3, Params>, fit::FitDummy<>, Params> conn_label_t;
  typedef gen::EvoNeuro<node_label_t, conn_label_t, Params> gen_t;
  typedef phen::EvoNeuro<gen_t, fit::FitDummy<>, Params> phen_t;

  phen_t indiv;
  indiv.random();
  for (size_t i = 0; i < 5; ++i)
    indiv.mutate();
  indiv.develop();
  indiv.nn().init();
  std::vector<float> in(Params::evo_neuro::map_size);
  for (size_t i = 0; i < 100; ++i)
    indiv.nn().step(in);
  BOOST_CHECK(indiv.nn().get_nb_inputs() == Params::evo_neuro::map_size);
  BOOST_CHECK(indiv.nn().get_nb_outputs() == Params::evo_neuro::map_size);
  std::ofstream ofs("/tmp/nn.dot");
  indiv.show(ofs);
  std::ofstream ofs2("/tmp/nn_gen.dot");
  //indiv.gen().write(ofs2);
}
