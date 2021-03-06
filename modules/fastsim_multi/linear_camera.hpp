#ifndef FASTSIM_LINEAR_CAMERA_HPP_
#define FASTSIM_LINEAR_CAMERA_HPP_

#include <boost/shared_ptr.hpp>
#include "posture.hpp"
#include "map.hpp"

#define SYMETRIE_CAMERA

namespace fastsim
{
  class LinearCamera
  {
    public:
    LinearCamera() : _angular_range(M_PI / 2), _pixels(12), _dist(12)
    { std::fill(_pixels.begin(), _pixels.end(), -1); std::fill(_dist.begin(), _dist.end(), 0); }
    LinearCamera(float angular_range, int nb_pixels) :
      _angular_range(angular_range), _pixels(nb_pixels), _dist(nb_pixels)
    { std::fill(_pixels.begin(), _pixels.end(), -1); std::fill(_dist.begin(), _dist.end(), 0); }
   
    void update(const Posture& pos,
	       const boost::shared_ptr<Map>& map);
    const std::vector<int>& pixels() const { return _pixels; }
    const std::vector<float>& dist() const { return _dist; }
    float get_angular_range() const { return _angular_range; }
  protected:
    float _angular_range;
    std::vector<int> _pixels;
    std::vector<float> _dist;
  };
}
#endif
