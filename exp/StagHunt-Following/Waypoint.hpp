#ifndef WAYPOINT_HPP_
#define WAYPOINT_HPP_

#include <modules/fastsim_multi2/illuminated_switch.hpp>

#include "defparams.hpp"

using namespace fastsim;

namespace sferes
{
	class Waypoint : public IlluminatedSwitch
	{
		public :
			Waypoint(int color, float radius, float x, float y, int id, bool on = true) : IlluminatedSwitch(color + id, radius, x, y, on, color/100), _id(id), _leader_first(-1), _completed(false) { }

			~Waypoint() {}

			void set_id(int id) { _id = id; }
			int get_id() const  { return _id; }

			void set_leader_first(int leader_first) { _leader_first = leader_first; }
			int get_leader_first() { return _leader_first; }

			void set_completed(bool completed) { _completed = completed; }
			bool is_completed() { return _completed; }

		protected :
			int _id;
			int _leader_first;
			bool _completed;
	};
}

#endif