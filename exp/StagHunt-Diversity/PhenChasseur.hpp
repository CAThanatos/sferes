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
		    PhenChasseur() : _params((*this)._gen.size()), _nb_hares(0), _nb_hares_solo(0), _nb_sstag(0), _nb_sstag_solo(0), _nb_bstag(0), _nb_bstag_solo(0), _fit_mov(0), _pop_pos(-1), _developed(false)
		    {}
		    
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

					_vector_diversity_init = false;
					_vector_diversity.clear();

#ifdef SIMILARITY
					_vec_similarity_at.clear();
					_vec_similarity_at.resize(Params::simu::size_sim_vector);
					_vec_similarity.clear();
					_vec_similarity.resize(Params::simu::size_sim_vector);
#endif

#ifdef DIVSM
					_vec_sm_at.clear();
					_vec_sm_at.resize((Params::nn::nb_inputs + Params::nn::nb_outputs)*Params::simu::nb_trials);
					// _vec_sm_at.resize(Params::nn::nb_inputs + Params::nn::nb_outputs);
					_vec_sm.clear();
					_vec_sm.resize((Params::nn::nb_inputs + Params::nn::nb_outputs)*Params::simu::nb_trials);
					// _vec_sm.resize(Params::nn::nb_inputs + Params::nn::nb_outputs);
#endif

#ifdef PROXIMITY
					_proximity = 0.0f;
					_proximity_at = 0.0f;
#endif
				}

				float data(size_t i) const { assert(i < size()); return _params[i]; }

				size_t size() const { return _params.size(); }

				const std::vector<float>& data() const { return _params; }

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

		    const std::vector<float>& vector_diversity() const { return _vector_diversity; }
		    void set_vector_diversity(size_t index, float value)
		    {
		    	assert(index < _vector_diversity.size());
		    	_vector_diversity[index] = value;
		    }

		    bool is_vector_diversity_init() { return _vector_diversity_init; }

				void create_vector_diversity()
				{
#if defined(SIMILARITY) && !defined(DIVSM)
					_vector_diversity.resize(Params::simu::size_sim_vector);
					for(size_t i = 0; i < _vec_similarity.size(); ++i)
						_vector_diversity[i] = _vec_similarity[i];
#elif defined(DIVSM)
					_vector_diversity.resize(_vec_sm.size());
					for(size_t i = 0; i < _vec_sm.size(); ++i)
						_vector_diversity[i] = _vec_sm[i];
#elif defined(PROXIMITY)
					_vector_diversity.resize(1);
					_vector_diversity[0] = _proximity;
#elif defined(DIVSTAG)
					_vector_diversity.resize(2);

					if(_nb_hares + _nb_bstag > 0.0f)
						_vector_diversity[0] = _nb_bstag/(_nb_hares + _nb_bstag);
					else
						_vector_diversity[0] = 0.0f;

					if(_nb_bstag > 0.0f)
						_vector_diversity[1] = (_nb_bstag - _nb_bstag_solo)/_nb_bstag;
					else
						_vector_diversity[1] = 0.0f;
#elif defined(DIVCOOP)
					_vector_diversity.resize(1);

					float max_hunts = Params::simu::nb_steps/STAMINA;
					_vector_diversity[0] = std::min(_nb_bstag - _nb_bstag_solo, max_hunts)/max_hunts;
#elif defined(FREQCOOP)
					_vector_diversity.resize(4);

#ifdef TOTALRATIO
					float max_hunts = Params::simu::nb_steps/STAMINA;
					_vector_diversity[0] = std::min(_nb_hares, max_hunts)/max_hunts;
					_vector_diversity[1] = std::min(_nb_bstag, max_hunts)/max_hunts;
#else
					if(_nb_hares + _nb_bstag > 0.0f)
					{
						_vector_diversity[0] = _nb_hares/(_nb_hares + _nb_bstag);
						_vector_diversity[1] = _nb_bstag/(_nb_hares + _nb_bstag);
					}
					else
					{
						_vector_diversity[0] = 0.0f;
						_vector_diversity[1] = 0.0f;
					}
#endif

#ifdef TOTALCOOP
					_vector_diversity[2] = std::min(_nb_hares - _nb_hares_solo, max_hunts)/max_hunts;
					_vector_diversity[3] = std::min(_nb_bstag - _nb_bstag_solo, max_hunts)/max_hunts;
#else
					if(_nb_hares > 0.0f)
						_vector_diversity[2] = (_nb_hares - _nb_hares_solo)/_nb_hares;
					else
						_vector_diversity[2] = 0.0f;

					if(_nb_bstag > 0.0f)
						_vector_diversity[3] = (_nb_bstag - _nb_bstag_solo)/_nb_bstag;
					else
						_vector_diversity[3] = 0.0f;
#endif
#else
					_vector_diversity.resize(2);

					if(_nb_hares + _nb_bstag > 0.0f)
					{
						_vector_diversity[0] = _nb_hares/(_nb_hares + _nb_bstag);
						_vector_diversity[1] = _nb_bstag/(_nb_hares + _nb_bstag);
					}
					else
					{
						_vector_diversity[0] = 0.0f;
						_vector_diversity[1] = 0.0f;
					}
#endif
				}

				// It is assumed here that each component in vector_diversity is in [0,1]
				float dist_diversity(const PhenChasseur& chasseur)
				{
					float dist = 0.0f;
					for(size_t i = 0; i < _vector_diversity.size(); ++i)
					{
						assert(0.0f <= _vector_diversity[i]);
						assert(_vector_diversity[i] <= 1.0f);

						assert(0.0f <= chasseur.vector_diversity()[i]);
						assert(chasseur.vector_diversity()[i] <= 1.0f);

						float x = _vector_diversity[i] - chasseur.vector_diversity()[i];
						dist += x * x;
					}

					return sqrtf(dist)/sqrt(_vector_diversity.size());
				}

				float dist_hamming_diversity(const PhenChasseur& chasseur)
				{
					float dist = 0.0f;
					for(size_t i = 0; i < _vector_diversity.size(); ++i)
					{
						assert(0.0f <= _vector_diversity[i]);
						assert(_vector_diversity[i] <= 1.0f);

						assert(0.0f <= chasseur.vector_diversity()[i]);
						assert(chasseur.vector_diversity()[i] <= 1.0f);

						dist += abs((int)_vector_diversity[i] - (int)chasseur.vector_diversity()[i]);
					}

					return dist/(float)_vector_diversity.size();
				}

#ifdef SIMILARITY
				void add_similarity(float similarity, int index) 
				{ 
					assert(index < _vec_similarity_at.size());
					_vec_similarity_at[index].fetch_and_store(_vec_similarity_at[index] + similarity);
				}

				void set_similarity()
				{
					for(size_t i = 0; i < _vec_similarity_at.size(); ++i)
						_vec_similarity[i] = _vec_similarity_at[i];
				}

				float _similarity(int index)
				{
					assert(index < _vec_similarity_at.size());
					return _vec_similarity_at[index];
				}

				float similarity_value()
				{
					float total = 0.0f;
					for(size_t i = 0; i < _vec_similarity.size(); ++i)
						total += _vec_similarity[i];

					return total/(float)_vec_similarity.size();
				}
#endif

#ifdef DIVSM
				void add_vec_sm(float value, int index)
				{
					assert(index < _vec_sm_at.size());
					_vec_sm_at[index].fetch_and_store(_vec_sm_at[index] + value);
				}

				void set_vec_sm()
				{
					_vec_sm.resize(_vec_sm_at.size());
					for(size_t i = 0; i < _vec_sm_at.size(); ++i)
					{
						_vec_sm[i] = _vec_sm_at[i];
						_vec_sm[i] = (_vec_sm[i] > Params::simu::threshold_hamming) ? 1 : 0;
					}
				}

				float vec_sm(int index)
				{
					assert(index < _vec_sm_at.size());
					return _vec_sm_at[index];
				}
#endif

#ifdef PROXIMITY
				void set_proximity(float proximity) { _proximity = proximity; }
				float proximity_at() const { return _proximity_at; }
				void add_proximity(float proximity) { _proximity_at.fetch_and_store(_proximity_at + proximity); }
#endif

      
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

		    std::vector<float> _vector_diversity;
		    bool _vector_diversity_init;

#ifdef SIMILARITY
		    std::vector<tbb::atomic<float> > _vec_similarity_at;
		    std::vector<float> _vec_similarity;
#endif

#ifdef DIVSM
		    std::vector<tbb::atomic<float> > _vec_sm_at;
		    std::vector<float> _vec_sm;
#endif

#ifdef PROXIMITY
		    tbb::atomic<float> _proximity_at;
		    float _proximity;
#endif
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
