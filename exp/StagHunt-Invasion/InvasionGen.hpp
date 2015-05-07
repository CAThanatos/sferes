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




#ifndef GEN_INVASION_HPP_
#define GEN_INVASION_HPP_

#include <fstream>

#include <vector>
#include <limits>
#include <boost/foreach.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/nvp.hpp>
#include <sferes/stc.hpp>
#include <sferes/misc.hpp>
#include <sferes/dbg/dbg.hpp>
#include <iostream>
#include <cmath>

namespace sferes
{
  namespace gen
  {
    /// in range [0;1]
    template<int Size, typename Params, typename Exact = stc::Itself> 
    class InvasionGen : public stc::Any<Exact>
    {
    public:
      typedef Params params_t;
      typedef InvasionGen<Size, Params, Exact> this_t;

      InvasionGen() : _data(Size) {}

      //@{
      void mutate() 
      { 
#ifdef GAUSSIAN_MUTATION
      	float mutation_rate = Params::evo_float::mutation_rate;

#ifdef BIG_MUTATION_RATE
      	float rand_big_rate = misc::rand<float>();

      	if(rand_big_rate < 0.01f)
      		mutation_rate = Params::evo_float::big_mutation_rate;
#endif

      	float sigma = Params::evo_float::sigma;
				for (size_t i = 0; i < Size; i++)
					if (misc::rand<float>() < mutation_rate)
					{
						float f = _data[i] + misc::gaussian_rand<float>(0, sigma * sigma);
						_data[i] = misc::put_in_range(f, 0.0f, 1.0f);
	  			}
#else
				static const float eta_m = Params::evo_float::eta_m;
				assert(eta_m != -1.0f);
				for (size_t i = 0; i < Size; i++)
					if (misc::rand<float>() < Params::evo_float::mutation_rate)
					{
						float ri = misc::rand<float>();
						float delta_i = ri < 0.5 ?
							pow(2.0 * ri, 1.0 / (eta_m + 1.0)) - 1.0 :
							1 - pow(2.0 * (1.0 - ri), 1.0 / (eta_m + 1.0));
						assert(!std::isnan(delta_i));
						assert(!std::isinf(delta_i));
						float f = _data[i] + delta_i;
						_data[i] = misc::put_in_range(f, 0.0f, 1.0f);
					}
#endif

				_check_invariant();
      }

    //   void cross(const InvasionGen& o, InvasionGen& c1, InvasionGen& c2)
    //   {
				// if (Params::evo_float::cross_over_type != evo_float::no_cross_over && 
				//     misc::rand<float>() < Params::evo_float::cross_rate)
				//   _cross_over_op(*this, o, c1, c2);
				// else if (misc::flip_coin())
			 //  {
			 //    c1 = *this;
			 //    c2 = o;
			 //  }
				// else
			 //  {
			 //    c1 = o;
			 //    c2 = *this;
			 //  }
				// _check_invariant();
    //   }

      void random() 
      { 
				#ifdef ZEROWEIGHTS
					BOOST_FOREACH(float &v, _data) v = 0.0f; 
				#else
					BOOST_FOREACH(float &v, _data) v = misc::rand<float>(); 
				#endif
					_check_invariant(); 
      }
      //@}
      
      //@{
      float data(size_t i) const 
      { 
				assert(_data.size());
				assert(i < _data.size()); 
				_check_invariant(); 
				return _data[i]; 
      }

      void  data(size_t i, float v)
      { 
				assert(_data.size());
				assert(i < _data.size()); 
				_data[i] = v; 
				_check_invariant(); 
      }

      size_t size() const { return Size; }

      //@}
      template<class Archive>
      void serialize(Archive & ar, const unsigned int version)
      {
        ar & BOOST_SERIALIZATION_NVP(_data);
      }
    protected:
      std::vector<float> _data;

      void _check_invariant() const
      {
			#ifdef DBG_ENABLED
				BOOST_FOREACH(float p, _data)
				  {
				    assert(!std::isnan(p)); 
				    assert(!std::isinf(p)); 
				    assert(p >= 0 && p <= 1); 
				  }
			#endif
      }
    };
  } // gen
} // sferes


#endif
