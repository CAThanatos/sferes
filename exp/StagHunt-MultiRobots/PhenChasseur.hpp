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




#ifndef PHEN_CHASSEUR_HPP_
#define PHEN_CHASSEUR_HPP_

#include <vector>
#include <sferes/phen/indiv.hpp>
#include <boost/foreach.hpp>
#include <tbb/atomic.h>

namespace sferes
{
  namespace phen
  {
    SFERES_INDIV(PhenChasseur, Indiv)
    {
		  template<typename G, typename F, typename P, typename E> 
		    friend std::ostream& operator<<(std::ostream& output, const PhenChasseur< G, F, P, E >& e);
		  public:
#ifdef EIGEN_CORE_H
		    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
#endif
		    PhenChasseur() : _params((*this)._gen.size()), _nb_leader_first(0), _nb_preys_killed_coop(0), _pop_pos(-1), _developed(false) {
		    }
		    
		    typedef float type_t;
		    static const float max_p = Params::parameters::max;
		    static const float min_p = Params::parameters::min;

		    void develop()
		    {
#if defined(DOUBLE_NN) && defined(DUPLICATION)
		    	_params.resize((*this)._gen.size());
#endif
					for (unsigned i = 0; i < _params.size(); ++i)
						_params[i] = this->_gen.data(i) * (max_p - min_p) + min_p;
						
					_nb_hares.clear();
					_nb_hares.resize(Params::simu::nb_hunters);
					_nb_sstags.clear();
					_nb_sstags.resize(Params::simu::nb_hunters);
					_nb_bstags.clear();
					_nb_bstags.resize(Params::simu::nb_hunters);

					// _nb_hares = 0;
					// _nb_hares = 0;
					// _nb_sstags = 0;
					// _nb_sstags = 0;
					// _nb_bstags = 0;
					// _nb_bstags = 0;

					_nb_leader_first = 0;
					_nb_preys_killed_coop = 0;
					_proportion_leader = 0;
					_nb_ind1_leader_first = 0;
					_developed = true;

					_nb_hares_at.clear();
					_nb_hares_at.resize(Params::simu::nb_hunters);
					_nb_sstags_at.clear();
					_nb_sstags_at.resize(Params::simu::nb_hunters);
					_nb_bstags_at.clear();
					_nb_bstags_at.resize(Params::simu::nb_hunters);

					// _nb_hares_at = 0;
					// _nb_hares_at = 0;
					// _nb_sstags_at = 0;
					// _nb_sstags_at = 0;
					// _nb_bstags_at = 0;
					// _nb_bstags_at = 0;

					_nb_leader_first_at = 0;
					_nb_preys_killed_coop_at = 0;
					_proportion_leader_at = 0;
					_nb_ind1_leader_first_at = 0;
					this->fit().fitness_at = 0;

					for(size_t i = 0; i < Params::simu::nb_hunters; ++i)
					{
						_nb_hares[i] = 0.0f;
						_nb_hares_at[i] = 0.0f;
						_nb_sstags[i] = 0.0f;
						_nb_sstags_at[i] = 0.0f;
						_nb_bstags[i] = 0.0f;
						_nb_bstags_at[i] = 0.0f;
					}
				}

				float data(size_t i) const { assert(i < size()); return _params[i]; }

				size_t genome_size() const { return this->_gen.size(); }

				size_t size() const { return _params.size(); }

				const std::vector<float>& data() const { return _params; }

				// squared Euclidean distance
				float dist(const PhenChasseur& chasseur) const
				{
					assert(chasseur.size() == size());
					float d = 0.0f;
					for (size_t i = 0; i < _params.size(); ++i)
						{
							float x = _params[i] - chasseur._params[i];
							d += x * x;
						}
					return d;
		    }

		    void show(std::ostream& os) const
		    {
		    	for(size_t i = 0; i << this->_gen.size(); ++i)
		    	{
		    		os << this->_gen.data(i) << ",";
		    	}
		    	os << std::endl;
					BOOST_FOREACH(float p, _params)
						os<<p<<",";
					os<<std::endl;
		    }

		    float nb_hares(int index) { return _nb_hares[index]; }
		    void set_nb_hares(float nb_hares, int nb_hunters) { _nb_hares[nb_hunters] = nb_hares; }

		    float nb_hares_at(int index) { return _nb_hares_at[index]; }
		    void add_nb_hares(float nb_hares, int nb_hunters) { _nb_hares_at[nb_hunters].fetch_and_store(_nb_hares_at[nb_hunters] + nb_hares); }

		    
		    float nb_sstags(int index) { return _nb_sstags[index]; }
		    void set_nb_sstags(float nb_sstags, int nb_hunters) { _nb_sstags[nb_hunters] = nb_sstags; } // std::cout << "SET NB SSTAGS : [" << nb_hunters - 1 << "] -> " << nb_sstags << std::endl; }

		    float nb_sstags_at(int index) { return _nb_sstags_at[index]; }
		    void add_nb_sstags(float nb_sstags, int nb_hunters) { _nb_sstags_at[nb_hunters].fetch_and_store(_nb_sstags_at[nb_hunters] + nb_sstags); }


		    float nb_bstags(int index) { return _nb_bstags[index]; }
		    void set_nb_bstags(float nb_bstags, int nb_hunters) { _nb_bstags[nb_hunters] = nb_bstags; }

		    float nb_bstags_at(int index) { return _nb_bstags_at[index]; }
		    void add_nb_bstags(float nb_bstags, int nb_hunters) { _nb_bstags_at[nb_hunters].fetch_and_store(_nb_bstags_at[nb_hunters] + nb_bstags); }


		    // float nb_hares(int index) { return _nb_hares; }
		    // void set_nb_hares(float nb_hares, int nb_hunters) { _nb_hares = nb_hares; }

		    // float nb_hares_at(int index) { return _nb_hares_at; }
		    // void add_nb_hares(float nb_hares, int nb_hunters) { _nb_hares_at.fetch_and_store(_nb_hares_at + nb_hares); }

		    
		    // float nb_sstags(int index) { return _nb_sstags; }
		    // void set_nb_sstags(float nb_sstags, int nb_hunters) { _nb_sstags = nb_sstags; }

		    // float nb_sstags_at(int index) { return _nb_sstags_at; }
		    // void add_nb_sstags(float nb_sstags, int nb_hunters) { _nb_sstags_at.fetch_and_store(_nb_sstags_at + nb_sstags); }


		    // float nb_bstags(int index) { return _nb_bstags; }
		    // void set_nb_bstags(float nb_bstags, int nb_hunters) { _nb_bstags = nb_bstags; }

		    // float nb_bstags_at(int index) { return _nb_bstags_at; }
		    // void add_nb_bstags(float nb_bstags, int nb_hunters) { _nb_bstags_at.fetch_and_store(_nb_bstags_at + nb_bstags); }


		    
		    float proportion_leader() const { return _proportion_leader; }
		    void set_proportion_leader(float proportion_leader) { _proportion_leader = proportion_leader; }

		    float proportion_leader_at() const { return _proportion_leader_at; }
		    void add_proportion_leader(float proportion_leader) { _proportion_leader_at.fetch_and_store(_proportion_leader_at + proportion_leader); }


		    float nb_leader_first() const { return _nb_leader_first; }
		    void set_nb_leader_first(float nb_leader_first) { _nb_leader_first = nb_leader_first; }
		    
		    float nb_leader_first_at() const { return _nb_leader_first_at; }
		    void add_nb_leader_first(float nb_leader_first) { _nb_leader_first_at.fetch_and_store(_nb_leader_first_at + nb_leader_first); }


		    float nb_preys_killed_coop() const { return _nb_preys_killed_coop; }
		    void set_nb_preys_killed_coop(float nb_preys_killed_coop) { _nb_preys_killed_coop = nb_preys_killed_coop; }
		    
		    float nb_preys_killed_coop_at() const { return _nb_preys_killed_coop_at; }
		    void add_nb_preys_killed_coop(float nb_preys_killed_coop) { _nb_preys_killed_coop_at.fetch_and_store(_nb_preys_killed_coop_at + nb_preys_killed_coop); }


		    float nb_ind1_leader_first() const { return _nb_ind1_leader_first; }
		    void set_nb_ind1_leader_first(float nb_ind1_leader_first) { _nb_ind1_leader_first = nb_ind1_leader_first; }
		    
		    float nb_ind1_leader_first_at() const { return _nb_ind1_leader_first_at; }
		    void add_nb_ind1_leader_first(float nb_ind1_leader_first) { _nb_ind1_leader_first_at.fetch_and_store(_nb_ind1_leader_first_at + nb_ind1_leader_first); }


		    int nb_simulations_at() const { return _nb_simulations_at; }
		    void add_nb_simulations(int nb_simulations) { _nb_simulations_at.fetch_and_store(_nb_simulations_at + nb_simulations); }
		    bool enough_simulations() { return (_nb_simulations_at >= (Params::simu::nb_opponents * Params::simu::nb_eval)); }


		    int pop_pos() const { return _pop_pos; }
		    void set_pop_pos(int pop_pos) { _pop_pos = pop_pos; }

				bool developed() const { return _developed; }
				void set_developed(bool developed) { _developed = developed; }
				bool developed_at() const { return _developed_at; }
				void set_developed_at(bool developed) { _developed_at = developed; }
				
				boost::shared_ptr<PhenChasseur> clone()
				{
					boost::shared_ptr<PhenChasseur> new_indiv = boost::shared_ptr<PhenChasseur>(new PhenChasseur());

#if defined(DOUBLE_NN) && defined(DUPLICATION)
					if(this->_gen.size() > new_indiv->_gen.size())
						new_indiv->_gen.resize(this->_gen.size());
#endif

					for(unsigned i = 0; i < this->_gen.size(); ++i)
						new_indiv->_gen.data(i, this->_gen.data(i));
						
					return new_indiv;
				}
      
		  protected:
		  	int _nb_simulations;
		  	tbb::atomic<int> _nb_simulations_at;

		    std::vector<float> _params;
		    
		    // // Number of hares caughted
		    std::vector<float> _nb_hares;
		    std::vector<tbb::atomic<float> >  _nb_hares_at;
		    
		    // // Number of small stags caughted
		    std::vector<float> _nb_sstags;
		    std::vector<tbb::atomic<float> >  _nb_sstags_at;
		    
		    // // Number of big stags caughted
		    std::vector<float> _nb_bstags;
		    std::vector<tbb::atomic<float> >  _nb_bstags_at;
		    
		    // // Number of hares caughted
		    // float _nb_hares;
		    // tbb::atomic<float> _nb_hares_at;
		    
		    // // Number of small stags caughted
		    // float _nb_sstags;
		    // tbb::atomic<float> _nb_sstags_at;
		    
		    // // Number of big stags caughted
		    // float _nb_bstags;
		    // tbb::atomic<float> _nb_bstags_at;
		    
		    // Number of times the leader arrived first on a prey
		    float _nb_leader_first;
		    tbb::atomic<float> _nb_leader_first_at;
		    
		    // Total number of cooperative hunts
		    float _nb_preys_killed_coop;
		    tbb::atomic<float> _nb_preys_killed_coop_at;

		    // Proportion of times the designated leader hunted first
		    float _proportion_leader;
		    tbb::atomic<float> _proportion_leader_at;

		    // Proportion of times this particular individual arrived first on a prey
		    float _nb_ind1_leader_first;
		    tbb::atomic<float> _nb_ind1_leader_first_at;
		    
		    int _pop_pos;
		    
		    bool _developed;
		    tbb::atomic<bool> _developed_at;
    };
    
    template<typename G, typename F, typename P, typename E> 
    std::ostream& operator<<(std::ostream& output, const PhenChasseur< G, F, P, E >& e) {
      for (size_t i = 0; i < e.size();++i)
        output <<" "<<e.data(i) ;

			output << std::endl;
      output << "Fitness = " << e.fit().value() << std::endl;
      output << "#Hares = " << e.nb_hares() << "/#Hares Solo = " << e.nb_hares_solo() << "/#Small Stags = " << e.nb_sstag() << "/#Small Stags Solo = " << e.nb_sstag_solo() << "/#Big Stags = " << e.nb_bstag() << "/#Big Stags Solo = " << e.nb_bstag_solo() << std::endl;
      output << "Movement fitness = " << e.fit_mov() << std::endl;
      return output;
    }
  }
}

#endif
