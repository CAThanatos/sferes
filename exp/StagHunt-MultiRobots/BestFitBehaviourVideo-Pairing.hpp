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




#ifndef BEST_FIT_BEHAVIOUR_VIDEO_PAIRING_
#define BEST_FIT_BEHAVIOUR_VIDEO_PAIRING_

#include <boost/serialization/shared_ptr.hpp>
#include <boost/serialization/nvp.hpp>
#include <sferes/stat/stat.hpp>

namespace sferes
{
  namespace stat
  {
    // assume that the population is sorted !
    SFERES_STAT(BestFitBehaviourVideoPairing, Stat)
    {
    public:
      typedef boost::shared_ptr<Phen > indiv_t;
      typedef typename std::vector<indiv_t> pop_t;
      typedef typename pop_t::iterator it_t;

      template<typename E>
				void refresh(const E& ea)
      {
        float best_fit = 0.0f;
        int best_niche = 0;
        for(size_t i = 0; i < ea.vec_niches().size(); ++i)
        {
          for(size_t j = 0; j < ea.vec_niches()[i].size(); ++j)
          {
            if(ea.vec_niches()[i][j]->fit().value() > best_fit)
            {
              best_fit = ea.vec_niches()[i][j]->fit().value();
              best_niche = i;
            }
          }
        }

        _best_niche = ea.vec_niches()[best_niche];

        int niche_opp = 0;
        for(size_t i = 0; i < ea.vec_pairing()[best_niche].size(); ++i)
        {
          if(ea.vec_pairing()[best_niche][i])
          {
            niche_opp = i;
            break;
          }
        }

        _best_niche_opp = ea.vec_niches()[niche_opp];

        if (ea.dump_enabled() && (ea.gen() % Params::pop::video_dump_period == 0))
				{
          _best_niche[0]->fit().set_mode(fit::mode::view);

          std::string video_dir = ea.res_dir() + "/behaviourVideoGen_" + boost::lexical_cast<std::string>(ea.gen());
          boost::filesystem::path my_path(video_dir);
          boost::filesystem::create_directory(my_path);

					std::string file_video = video_dir + "/behaviourVideoFrame_";
					_best_niche[0]->fit().set_file_video(file_video);
					_best_niche[0]->fit().eval_compet(*(_best_niche[0]), *(_best_niche_opp[0]));

					// We delete the existing archive
					std::string command;
					int retour;
					if(ea.gen() > 0)
					{
						std::string archive_prefix = ea.res_dir() + "/behaviourVideo*.tar.gz";
						command = "rm -f " + archive_prefix;
						retour = system(command.c_str());
					}

					// We create a compressed archive of the images					
					std::string name_archive = video_dir + ".tar.gz";
					command = "tar -zcf " + name_archive + " " + video_dir;
					retour = system(command.c_str());
					
					command = "rm -rf " + video_dir;
					retour = system(command.c_str());
  
 					_best_niche[0]->fit().set_mode(fit::mode::eval);
				}
      }

      void show(std::ostream& os, size_t k)
      {
      }

      const pop_t best() const { return _best_niche; }
      template<class Archive>
      void serialize(Archive & ar, const unsigned int version)
      {
        // ar & BOOST_SERIALIZATION_NVP(_best_pair);
      }
    protected:
      pop_t _best_niche;
      pop_t _best_niche_opp;
    };
  }
}
#endif
