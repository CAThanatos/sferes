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
		    PhenChasseur() : _params((*this)._gen.size()), _nb_hares(0), _nb_hares_solo(0), _nb_sstag(0), _nb_sstag_solo(0), _nb_bstag(0), _nb_bstag_solo(0), _fit_mov(0), _pop_pos(-1), _developed(false) 					{
		    }
		    
		    typedef float type_t;
		    static const float max_p = Params::parameters::max;
		    static const float min_p = Params::parameters::min;

		    void develop()
		    {
					for (unsigned i = 0; i < _params.size(); ++i)
						_params[i] = this->_gen.data(i) * (max_p - min_p) + min_p;
						
					_nb_hares = 0;
					_nb_hares_solo = 0;
					_nb_sstag = 0;
					_nb_sstag_solo = 0;
					_nb_bstag = 0;
					_nb_bstag_solo = 0;
					_fit_mov = 0;
					
					this->fit().vec_fitness.clear();
					_developed = true;

					_nb_hares_at = 0;
					_nb_hares_solo_at = 0;
					_nb_sstag_at = 0;
					_nb_sstag_solo_at = 0;
					_nb_bstag_at = 0;
					_nb_bstag_solo_at = 0;
					this->fit().fitness_at = 0;
				}

				float data(size_t i) const { assert(i < size()); return _params[i]; }

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
		    
		    float nb_hares() const { return _nb_hares; }
        float nb_hares_solo() const { return _nb_hares_solo; }
		    void set_nb_hares(float nb_hares, float solo) { _nb_hares = nb_hares; _nb_hares_solo = solo; }

		    float nb_hares_at() const { return _nb_hares_at; }
        float nb_hares_solo_at() const {return _nb_hares_solo_at; }
		    void add_nb_hares(float nb_hares, float solo) { _nb_hares_at.fetch_and_store(_nb_hares_at + nb_hares); _nb_hares_solo_at.fetch_and_store(_nb_hares_solo_at + solo); }

		    
		    float nb_sstag() const { return _nb_sstag; }
		    float nb_sstag_solo() const { return _nb_sstag_solo; }
		    void set_nb_sstag(float nb_sstag, float solo) { _nb_sstag = nb_sstag; _nb_sstag_solo = solo; }
		    
		    float nb_sstag_at() const { return _nb_sstag_at; }
		    float nb_sstag_solo_at() const { return _nb_sstag_solo_at; }
		    void add_nb_sstag(float nb_sstag, float solo) { _nb_sstag_at.fetch_and_store(_nb_sstag_at + nb_sstag); _nb_sstag_solo_at.fetch_and_store(_nb_sstag_solo_at + solo); }


		    float nb_bstag() const { return _nb_bstag; }
		    float nb_bstag_solo() const { return _nb_bstag_solo; }
		    void set_nb_bstag(float nb_bstag, float solo) { _nb_bstag = nb_bstag; _nb_bstag_solo = solo; }
		    
		    float nb_bstag_at() const { return _nb_bstag_at; }
		    float nb_bstag_solo_at() const { return _nb_bstag_solo_at; }
		    void add_nb_bstag(float nb_bstag, float solo) { _nb_bstag_at.fetch_and_store(_nb_bstag_at + nb_bstag); _nb_bstag_solo_at.fetch_and_store(_nb_bstag_solo_at + solo); }
				

		    float fit_mov() const { return _fit_mov; }
		    void set_fit_mov(float fit_mov) { _fit_mov = fit_mov; }
		    int pop_pos() const { return _pop_pos; }
		    void set_pop_pos(int pop_pos) { _pop_pos = pop_pos; }

				bool developed() const { return _developed; }
				void set_developed(bool developed) { _developed = developed; }
				bool developed_at() const { return _developed_at; }
				void set_developed_at(bool developed) { _developed_at = developed; }
				
				boost::shared_ptr<PhenChasseur> clone()
				{
					boost::shared_ptr<PhenChasseur> new_indiv = boost::shared_ptr<PhenChasseur>(new PhenChasseur());
					for(unsigned i = 0; i < this->_gen.size(); ++i)
						new_indiv->_gen.data(i, this->_gen.data(i));
						
					return new_indiv;
				}
      
		  protected:
		    std::vector<float> _params;
		    
		    // Number of hares caughted
		    float _nb_hares;
        float _nb_hares_solo;
        
		    tbb::atomic<float>  _nb_hares_at;
        tbb::atomic<float>  _nb_hares_solo_at;
		    
		    // Number of small stags caughted
		    float _nb_sstag;
		    float _nb_sstag_solo;

		    tbb::atomic<float> _nb_sstag_at;
		    tbb::atomic<float> _nb_sstag_solo_at;
		    
		    // Number of big stags caughted
		    float _nb_bstag;
		    float _nb_bstag_solo;

		    tbb::atomic<float> _nb_bstag_at;
		    tbb::atomic<float> _nb_bstag_solo_at;
		    
		    float _fit_mov;
		    
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
