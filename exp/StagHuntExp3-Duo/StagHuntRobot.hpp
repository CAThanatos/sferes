#ifndef STAGHUNTROBOT_HPP_
#define STAGHUNTROBOT_HPP_

#include <modules/fastsim_multi/robot.hpp>
#include <modules/fastsim_multi/posture.hpp>

namespace sferes
{
	class StagHuntRobot : public fastsim::Robot
	{
		public :
			StagHuntRobot() : fastsim::Robot(), _sens_max(0) {}
			StagHuntRobot(float radius, const fastsim::Posture& pos, unsigned int color, unsigned int color_alt = 0) : fastsim::Robot(radius, pos, color, ((color_alt == 0)?-1:color_alt)), _sens_max(0) {}

			virtual ~StagHuntRobot() { }
						
			virtual std::vector<float> step_action() = 0;
			
			float sens_max() { return _sens_max; }
			void set_sens_max(float sens_max) { _sens_max = sens_max; }
		protected :
			float _sens_max;
	};
}

#endif
