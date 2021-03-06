//| This file is a part of the sferes2 framework.
//| Copyright 2009, ISIR / Universite Pierre et Marie Curie (UPMC)
//| Main contributor(s): Jean-Baptiste Mouret, mouret@isir.fr
//|
//| This software is a computer program whose purpose is to facilitate
//| experiments in evolutionary computation and evolutionary robotics.
//|
//| This software is governed by the CeCILL license under French law
//| and abiding by the rules of distribution of free software.  You
//| can use, modify and/ or redistribute the software under the terms
//| of the CeCILL license as circulated by CEA, CNRS and INRIA at the
//| following URL "http://www.cecill.info".
//|
//| As a counterpart to the access to the source code and rights to
//| copy, modify and redistribute granted by the license, users are
//| provided only with a limited warranty and the software's author,
//| the holder of the economic rights, and the successive licensors
//| have only limited liability.
//|
//| In this respect, the user's attention is drawn to the risks
//| associated with loading, using, modifying and/or developing or
//| reproducing the software by the user in light of its specific
//| status of free software, that may mean that it is complicated to
//| manipulate, and that also therefore means that it is reserved for
//| developers and experienced professionals having in-depth computer
//| knowledge. Users are therefore encouraged to load and test the
//| software's suitability as regards their requirements in conditions
//| enabling the security of their systems and/or data to be ensured
//| and, more generally, to use and operate it in the same conditions
//| as regards security.
//|
//| The fact that you are presently reading this means that you have
//| had knowledge of the CeCILL license and that you accept its terms.




#ifndef EA_HPP_
#define EA_HPP_

#include <iostream>
#include <vector>
#include <fstream>
#include <string>

#include <boost/fusion/container.hpp>
#include <boost/fusion/algorithm.hpp>
#include <boost/mpl/vector.hpp>
#include <boost/fusion/support/is_sequence.hpp>
#include <boost/fusion/include/is_sequence.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/xml_oarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/xml_iarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/filesystem.hpp>

#include <sferes/dbg/dbg.hpp>
#include <sferes/misc.hpp>
#include <sferes/stc.hpp>

namespace sferes
{
  namespace ea
  {

    template<typename E>
    struct RefreshStat_f
    {
      RefreshStat_f(const E &ea) : _ea(ea) {
      }
      const E& _ea;
      template<typename T>
      void operator() (T & x) const
      {
        x.refresh(_ea);
      }
    };
    template<typename A>
    struct WriteStat_f
    {
      WriteStat_f(A & a) : _archive(a) {
      }
      A& _archive;
      template<typename T>
      void operator() (const T &x) const
      {
        std::string version(SVN_VERSION);
        _archive << boost::serialization::make_nvp("svn_version",
                                                   version);
        _archive << BOOST_SERIALIZATION_NVP(x);
      }
    };

    template<typename A>
    struct ReadStat_f
    {
      ReadStat_f(A & a) : _archive(a) {
      }
      A& _archive;
      template<typename T>
      void operator() (T & x) const
      {
        std::cout << "MAAAAAAAAAAIS" << std::endl;
        std::string version;
        _archive >> boost::serialization::make_nvp("svn_version", version);
        if (version != std::string(SVN_VERSION))
          std::cerr << "WARNING: your are loading a file made with sferes version "
                    << version << " while the current version is:"
                    << SVN_VERSION
                    << std::endl;
        _archive >> BOOST_SERIALIZATION_NVP(x);
      }
    };

    struct ShowStat_f
    {
      ShowStat_f(unsigned n, std::ostream & os, size_t k) :
        _n(n), _i(0), _os(os), _k(k) {
      }
      template<typename T>
      void operator() (T & x) const
      {
        if (_i == _n)
          x.show(_os, _k);

        ++_i;
      }
      int _n;
      mutable int _i;
      std::ostream& _os;
      size_t _k;
    };


    template<typename E>
    struct ApplyModifier_f
    {
      ApplyModifier_f(E &ea) : _ea(ea) {
      }
      E& _ea;
      template<typename T>
      void operator() (T & x) const
      {
        x.apply(_ea);
      }
    };

    template<typename Phen, typename Eval, typename Stat, typename FitModifier,
             typename Params,
             typename Exact = stc::Itself>
    class Ea : public stc::Any<Exact>
    {
      public:
        typedef Phen phen_t;
        typedef Eval eval_t;
        typedef Stat stat_t;
        typedef Params params_t;
        typedef typename
        boost::mpl::if_<boost::fusion::traits::is_sequence<FitModifier>,
                        FitModifier,
                        boost::fusion::vector<FitModifier> >::type modifier_t;
        typedef std::vector<boost::shared_ptr<Phen> > pop_t;

        Ea() : _pop(Params::pop::size), _gen(0), _save_gen(false)
        {
          _make_res_dir();
        }

        void run()
        {
          dbg::trace trace("ea", DBG_HERE);
          random_pop();
          update_stats();

          for (_gen = 0; _gen < Params::pop::nb_gen; ++_gen)
          {
            epoch();
            update_stats();

            if (_gen % Params::pop::dump_period == 0)
            {
              _write(_gen);
              
              if(_save_gen)
              	_write_gen(_gen);
            }
          }
        }
        void continue_run(const std::string& fname)
        {
        	dbg::trace trace("ea", DBG_HERE);
					load_gen(fname);
					_eval.set_nb_eval(_gen);

					for(_gen; _gen < Params::pop::nb_gen; ++_gen)
					{
						epoch();
						update_stats();
						if (_gen % Params::pop::dump_period == 0)
						{
							_write(_gen);
							_write_gen(_gen);
						}
					}
        }
        void play_run(const std::string& fname)
        {
#if defined(ELITIST) or defined(FITPROP)
          dbg::trace trace("ea", DBG_HERE);
          stc::exact(this)->play_run();
#else
          std::cerr << "play_run() not implemented with these ea parameters." << std::endl;
          exit(1);
#endif
        }
        void random_pop()
        {
          dbg::trace trace("ea", DBG_HERE);
          stc::exact(this)->random_pop();
        }
        void epoch()
        {
          dbg::trace trace("ea", DBG_HERE);
          stc::exact(this)->epoch();
        }
        const pop_t& pop() const { return _pop; };
        pop_t& pop() { return _pop; };
#ifdef COEVO
        const pop_t& pop_co() const { return _pop_co; };
        pop_t& pop_co() { return _pop_co; };
#endif
        const eval_t& eval() const { return _eval; }
        eval_t& eval() { return _eval; }
        const stat_t& stat() const { return _stat; }
        const modifier_t& fit_modifier() const { return _fit_modifier; }

         // modifiers
        void apply_modifier()
        { boost::fusion::for_each(_fit_modifier, ApplyModifier_f<Exact>(stc::exact(*this))); }

         // stats
        template<int I>
        const typename boost::fusion::result_of::value_at_c<Stat, I>::type& stat() const
        { return boost::fusion::at_c<I>(_stat); }
        void load(const std::string& fname) { _load(fname); }
        void show_stat(unsigned i, std::ostream& os, size_t k = 0)
        { boost::fusion::for_each(_stat, ShowStat_f(i, os, k)); }
        void update_stats()
        { boost::fusion::for_each(_stat, RefreshStat_f<Exact>(stc::exact(*this))); }

				void set_save_gen(bool save_gen)
				{
					_save_gen = save_gen;
				}

        const std::string& res_dir() const { return _res_dir; }
        size_t gen() const { return _gen; }
        size_t nb_eval() const { return _eval.nb_eval(); }
        bool dump_enabled() const { return Params::pop::dump_period != -1; }
        void write() const { _write(gen()); }
        void write(size_t g) const { _write(g); }
        
        void write_gen() const { _write_gen(gen()); }
        void write_gen(size_t g) const { _write_gen(g); }
        void load_gen(const std::string& fname) { _load_gen(fname); }
        
        void set_seed(time_t seed) { _seed = seed; }
      protected:
        pop_t _pop;
#ifdef COEVO
        pop_t _pop_co;
#endif
        eval_t _eval;
        stat_t _stat;
        modifier_t _fit_modifier;
        std::string _res_dir;
        size_t _gen;
        bool _save_gen;
        time_t _seed;

        void _make_res_dir()
        {
          if (Params::pop::dump_period == -1)
            return;

          _res_dir = misc::hostname() + "_" + misc::date() + "_" + misc::getpid();
          boost::filesystem::path my_path(_res_dir);
          boost::filesystem::create_directory(my_path);
        }
        void _write(int gen) const
        {
          dbg::trace trace("ea", DBG_HERE);
          if (Params::pop::dump_period == -1)
            return;
          std::string fname = _res_dir + std::string("/gen_")
                              + boost::lexical_cast<std::string>(gen);
          std::ofstream ofs(fname.c_str());
          typedef boost::archive::xml_oarchive oa_t;
          oa_t oa(ofs);
          boost::fusion::for_each(_stat, WriteStat_f<oa_t>(oa));
          std::cout << fname << " written" << std::endl;
        }
        void _load(const std::string& fname)
        {
          dbg::trace trace("ea", DBG_HERE);
          std::cout << "loading " << fname << std::endl;
          std::ifstream ifs(fname.c_str());
          if (ifs.fail())
          {
            std::cerr << "Cannot open :" << fname
                      << "(does file exist ?)" << std::endl;
            exit(1);
          }
          typedef boost::archive::xml_iarchive ia_t;
          ia_t ia(ifs);
          boost::fusion::for_each(_stat, ReadStat_f<ia_t>(ia));
        }
        void _write_gen(int gen)
        {
          dbg::trace trace("ea", DBG_HERE);
          if (Params::pop::dump_period == -1)
            return;
            
          std::string fname = _res_dir + std::string("/popGen_")
                              + boost::lexical_cast<std::string>(gen);
          std::ofstream ofs(fname.c_str());
          typedef boost::archive::binary_oarchive oa_t;
          oa_t oa(ofs);
          oa << BOOST_SERIALIZATION_NVP(_seed);
	        oa << BOOST_SERIALIZATION_NVP(_pop);

#ifdef COEVO
          oa << BOOST_SERIALIZATION_NVP(_pop_co);
#endif

          std::cout << fname << " written" << std::endl;

          
          // We use a new seed
					time_t t = time(0) + ::getpid();
					srand(t);
					set_seed(t);
        }
        void _load_gen(const std::string& fname)
        {
          dbg::trace trace("ea", DBG_HERE);
          std::cout << "loading " << fname << std::endl;
          std::ifstream ifs(fname.c_str());
          if (ifs.fail())
          {
            std::cerr << "Cannot open :" << fname
                      << "(does file exist ?)" << std::endl;
            exit(1);
          }
          
					_gen = atof(fname.substr(fname.find_last_of("_") + 1, fname.length() - 1).c_str()) + 1;
          
          typedef boost::archive::binary_iarchive ia_t;
          ia_t ia(ifs);
          ia >> BOOST_SERIALIZATION_NVP(_seed);

// #ifdef RESEEDING
//           time_t curTime = time(0) + ::getpid();
//           srand(curTime);
//           set_seed(curTime);
// #endif

	        ia >> BOOST_SERIALIZATION_NVP(_pop);

#if defined(FITPROP)
          if(_pop.size() < Params::pop::size)
            stc::exact(this)->fill_pop();
#elif defined(ELITIST)
          if(_pop.size() < Params::pop::mu)
            stc::exact(this)->fill_pop();
#endif

#if defined(ELITISTINV) || defined(FINITE) || defined(INFINITE)
          stc::exact(this)->load_genotypes();
#endif

#ifdef COEVO
          ia >> BOOST_SERIALIZATION_NVP(_pop_co);
#endif

#ifdef PAIRING
          // stc::exact(this)->load_niches(fname);
#endif

          // for(int i = 0; i < _pop.size(); ++i)
          // {
          //   for(int j = 0; j < _pop[i]->gen().size(); ++j)
          //     std::cout << _pop[i]->gen().data(j) << ",";
          //   std::cout << std::endl;
          // }

          // Add a particular individual to the population
          std::string path = fname.substr(0, fname.find_last_of("/") + 1);
          std::ifstream ifs2((path + "genome.dat").c_str());

#if defined(ELITISTINV) || defined(FINITE) || defined(INFINITE) || defined(FITPROP)
          stc::exact(this)->load_genome(fname);
#else
          if (!ifs2.fail())
          {
            std::cout << "Adding individual(s) with genotype in genome.dat..." << std::endl;
            
            int numIndiv = 0;
            while(ifs2.good())
            {
              std::string line;
              std::getline(ifs2, line);

              std::stringstream ss(line);
              std::string gene;
              int cpt = 0;
              while(std::getline(ss, gene, ','))
              {
                _pop[_pop.size() - numIndiv - 1]->gen().data(cpt, std::atof(gene.c_str()));
                cpt++;
              }

              numIndiv++;
            }
          }
#endif

#ifdef DUPLOAD
          int nb_genes = (Params::nn::nb_inputs + 1) * Params::nn::nb_hidden + Params::nn::nb_outputs * Params::nn::nb_hidden + Params::nn::nb_outputs;
          for(size_t i = 0; i < _pop.size(); ++i)
          {
            _pop[i]->gen().resize(nb_genes + 2);
#ifdef DIFFLOAD
            _pop[i]->gen().data(nb_genes, misc::rand<float>(0.0f, 0.5f));
            _pop[i]->gen().data(nb_genes + 1, misc::rand<float>(0.5f, 1.0f));
#else
            _pop[i]->gen().data(nb_genes, misc::rand<float>());
            _pop[i]->gen().data(nb_genes + 1, misc::rand<float>());
#endif
            _pop[i]->gen().duplicate_nn();
          }
#endif

	        
//	        srand(_seed);

          // We use a new seed
					time_t t = time(0) + ::getpid();
					srand(t);
					set_seed(t);
        }
    };
  }
}

#define SFERES_EA(Class, Parent)                                                               \
  template<typename Phen, typename Eval, typename Stat, typename FitModifier, typename Params, \
           typename Exact = stc::Itself>                                                       \
  class Class : public Parent < Phen, Eval, Stat, FitModifier, Params,                         \
  typename stc::FindExact<Class<Phen, Eval, Stat, FitModifier, Params, Exact>, Exact>::ret >

#endif
